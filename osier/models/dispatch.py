import pandas as pd
import numpy as np
import pyomo.environ as pe
import pyomo.opt as po
from pyomo.environ import ConcreteModel
from unyt import unyt_array
import itertools as it


class DispatchModel():
    """
    The :class:`DispatchModel` class creates and solves a basic dispatch
    model from the perspective of a "grid operator." The model uses
    `pyomo <https://pyomo.readthedocs.io/en/stable/index.html>`_
    to create and solve a linear programming model.
    The mathematical formulation for this problem is:

    Minimize


    .. math::
        \\text{C}_{\\text{total}} = \\sum_t^T \\sum_u^U
        \\left[c^{\\text{fuel}}_{u,t} + c^{\\text{om,var}}_{u,t}\\right]x_{u,t}

    Such that,

    1. The generation meets demand within a user-specified tolerance
    (undersupply and oversupply)

    .. math::
        \\sum_u^Ux_{u,t} &\\geq \\left(1-\\text{undersupply}\\right)\\text{D}_t
        \\ \\forall \\ t \\in T

        \\sum_u^Ux_{u,t} &\\leq \\left(1+\\text{oversupply}\\right)\\text{D}_t 
        \\ \\forall \\ t \\in T

    2. A technology's generation (:math:`x_u`) does not exceed its capacity to
    generate at any time, :math:`t`.

    .. math::
        x_{u,t} \\leq \\textbf{CAP}_{u} \\ \\forall \\ u,t \\in U,T


    Parameters
    ----------
    technology_list : list of :class:`osier.Technology`
        The list of :class:`Technology` objects to dispatch -- i.e. decide
        how much energy each technology should produce.
    net_demand : list, :class:`numpy.ndarray`, :class:`unyt.array.unyt_array`, :class:`pandas.DataFrame`.
        The remaining energy demand to be fulfilled by the technologies in
        :attr:`technology_list`. The `values` of an object passed as 
        `net_demand` are used to create a supply constraint. See 
        :attr:`oversupply` and :attr:`undersupply`. 
        If a :class:`pandas.DataFrame` is passed, :mod:`osier` will try 
        inferring a `time_delta` from the dataframe index. Otherwise, the
        :attr:`time_delta` must be passed or the default is used.
    time_delta : string, :class:`unyt.unyt_quantity`, float, int
    solver : str
        Indicates which solver to use. May require separate installation.
        Accepts: ['cplex', 'cbc']. Other solvers will be added in the future.
    lower_bound : float
        The minimum amount of energy each technology can produce per time
        period. Default is 0.0.
    oversupply : float
        The amount of allowed oversupply as a percentage of demand.
        Default is 0.0 (no oversupply allowed).
    undersupply : float
        The amount of allowed undersupply as a percentage of demand.
        Default is 0.0 (no undersupply allowed).

    Attributes
    ----------
    model : :class:`pyomo.environ.ConcreteModel`
        The :mod:`pyomo` model class that converts python code into a
        set of linear equations.
    upperbound : float
        The upper bound for all decision variables. Chosen to be equal
        to the maximum capacity of all technologies in :attr:`tech_set`.

    Notes
    -----
    Technically, :attr:`solver` will accept any solver that :class:`pyomo`
    can use. We only list two solvers because those are the only solvers
    in the :mod:`osier` test suite.
    """

    def __init__(self,
                 technology_list,
                 net_demand,
                 solver='cplex',
                 lower_bound=0.0,
                 oversupply=0.0,
                 undersupply=0.0):
        self.net_demand = net_demand
        self.technology_list = technology_list
        self.lower_bound = lower_bound
        self.oversupply = oversupply
        self.undersupply = undersupply
        self.model = ConcreteModel()
        self.solver = solver
        self.results = None
        self.objective = None

    @property
    def n_hours(self):
        return len(self.net_demand)

    @property
    def tech_set(self):
        tech_names = [t.technology_name for t in self.technology_list]
        return tech_names

    @property
    def capacity_dict(self):
        capacity_set = unyt_array([t.capacity for t in self.technology_list])
        return dict(zip(self.tech_set, capacity_set))

    @property
    def time_set(self):
        return range(self.n_hours)

    @property
    def indices(self):
        return list(it.product(self.tech_set, self.time_set))

    @property
    def cost_params(self):
        v_costs = np.array([
            (t.variable_cost_ts(self.n_hours))
            for t in self.technology_list
        ]).flatten()
        return dict(zip(self.indices, v_costs))

    @property
    def ramping_techs(self):
        return [t.technology_name
                for t in self.technology_list 
                if t.technology_category == "thermal"]

    @property
    def ramp_up_params(self):
        rates_dict = {t.technology_name : t.ramp_up
                for t in self.technology_list 
                if t.technology_category == "thermal"}
        return rates_dict

    @property
    def ramp_down_params(self):
        rates_dict = {t.technology_name : t.ramp_down
                for t in self.technology_list 
                if t.technology_category == "thermal"}
        return rates_dict

    @property
    def upper_bound(self):
        caps = unyt_array([t.capacity for t in self.technology_list])
        return caps.max().to_value()

    def _create_model_indices(self):
        self.model.U = pe.Set(initialize=self.tech_set, ordered=True)
        self.model.T = pe.Set(initialize=self.time_set, ordered=True)
        self.model.R = pe.Set(initialize=self.ramping_techs, 
                                ordered=True, 
                                within=self.model.U)

    def _create_demand_param(self):
        self.model.D = pe.Param(self.model.T, initialize=dict(
            zip(self.model.T, self.net_demand)))

    def _create_cost_param(self):
        self.model.C = pe.Param(
            self.model.U,
            self.model.T,
            initialize=self.cost_params)
    
    def _create_ramping_params(self):
        self.model.ramp_up = pe.Param(self.model.R, initialize=self.ramp_up_params)
        self.model.ramp_down = pe.Param(self.model.R, initialize=self.ramp_down_params)

    def _create_model_variables(self):
        self.model.x = pe.Var(self.model.U, self.model.T,
                              domain=pe.Reals,
                              bounds=(self.lower_bound, self.upper_bound))

    def _objective_function(self):
        expr = sum(self.model.C[u, t] * self.model.x[u, t]
                   for u in self.model.U for t in self.model.T)
        self.model.objective = pe.Objective(sense=pe.minimize, expr=expr)

    def _supply_constraints(self):
        self.model.oversupply = pe.ConstraintList()
        self.model.undersupply = pe.ConstraintList()
        for t in self.model.T:
            generation = sum(self.model.x[u, t] for u in self.model.U)
            over_demand = self.model.D[t] * (1 + self.oversupply)
            under_demand = self.model.D[t] * (1 - self.undersupply)
            self.model.oversupply.add(generation <= over_demand)
            self.model.undersupply.add(generation >= under_demand)

    def _generation_constraint(self):
        self.model.gen_limit = pe.ConstraintList()
        for u in self.model.U:
            unit_capacity = self.capacity_dict[u].to_value()
            for t in self.model.T:
                unit_generation = self.model.x[u, t]
                self.model.gen_limit.add(unit_generation <= unit_capacity)
    
    # def _ramping_constraints(self):
    #     self.model.ramp_up_limit = pe.ConstraintList()
    #     self.model.ramp_down_limit = pe.ConstraintList()

    #     for r in self.model.R:
    #         ramp_up = self.model.ramp_up[r]
    #         ramp_down = self.model.ramp_down[r]
    #         for t in self.model.T:
    #             if t != self.model.T.first():
    #                 t_prev = self.model.T.prev(t) 
    #                 t_next = self.model.T.next(t)
    #                 # print('calculating previous generation')
    #                 previous_gen = self.model.x[r, t_prev]
    #                 next_gen = self.model.x[r, t_next]
    #                 current_gen = self.model.x[r, t]
    #                 self.model.ramp_up_limit.add(current_gen <= (1+ramp_up)*previous_gen)
    #                 self.model.ramp_down_limit.add(current_gen >= (1-ramp_down)*previous_gen)


    def _write_model_equations(self):

        self._create_model_indices()
        self._create_demand_param()
        self._create_cost_param()
        self._create_model_variables()
        self._objective_function()
        self._supply_constraints()
        self._generation_constraint()
        if len(self.ramping_techs) > 0:
            self._create_ramping_params()
        #     self._ramping_constraints()

        return

    def _format_results(self):
        df = pd.DataFrame(index=self.model.T)
        for u in self.model.U:
            df[u] = [self.model.x[u, t].value for t in self.model.T]

        return df

    def solve(self):
        self._write_model_equations()
        solver = po.SolverFactory(self.solver)

        # self.model.ramp_up_limit.pprint()

        results = solver.solve(self.model, tee=True)
        self.objective = self.model.objective()

        self.results = self._format_results()
