import pandas as pd
import numpy as np
import pyomo.environ as pe
import pyomo.opt as po
from pyomo.environ import ConcreteModel
from unyt import unyt_array, hr, MW, MWh
import itertools as it
from osier.technology import _validate_quantity, _validate_unit
from osier.utils import synchronize_units
import warnings

_freq_opts = {'D': 'day',
              'H': 'hour',
              'S': 'second',
              'T': 'minute'}

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
        x_{u,t} \\leq \\textbf{CAP}_{u}\\Delta t \\ \\forall \\ u,t \\in U,T

    3. Technologies may not exceed their ramp up rate.

    .. math::
        \\frac{x_{r,t} - x_{r,t-1}}{\\Delta t} = \\Delta P_{r,t} \\leq
        (\\text{ramp up})\\textbf{CAP}_u\\Delta t \\ \\forall \\ r,t
        \\in R \\subset U, T

    or ramp down rate

    .. math::
        \\frac{x_{r,t} - x_{r,t-1}}{\\Delta t} = \\Delta P_{r,t} \\leq
        -(\\text{ramp down})\\textbf{CAP}_u\\Delta t \\ \\forall \\ r,t
        \\in R \\subset U, T

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
    time_delta : str, :class:`unyt.unyt_quantity`, float, int
        Specifies the amount of time between two time slices. The default is
        one hour. Can be overridden by specifying a unit with the value. For
        example:

        >>> time_delta = "5 minutes"
        >>> from unyt import days
        >>> time_delta = 30*days

        would both work.
    power_units : str, :class:`unyt.unyt_quantity`, float, int
        Specifies the units for the power demand. The default is :attr:`MW`.
        Can be overridden by specifying a unit with the value.
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
    n_timesteps : int
        The number of timesteps in the model.
    upper_bound : float
        The upper bound for all decision variables. Chosen to be equal
        to the maximum capacity of all technologies in :attr:`tech_set`.
    storage_upper_bound : float
        The upper bound for storage decision variables.
    penalty : float
        The penalty applied to the objective function to eliminate
        simultaneous charging and discharging. Users may need to tune
        this parameter. Default is 1.0.


    Notes
    -----
    1. Technically, :attr:`solver` will accept any solver that :class:`pyomo`
    can use. We only list two solvers because those are the only solvers
    in the :mod:`osier` test suite.

    2. The default value for :attr:`time_delta` in :attr:`__init__` is
    `None`. This is replaced by a setter method in :class:`Dispatch`.

    3. This formulation uses a :attr:`penalty` parameter  to prevent unphysical
    behavior because it preserves the problem's linearity. Some formulations 
    may use a binary variable to prevent simultaneous charging and discharing.
    However, this changes the problem to a mixed-integer linear program which
    requires a more sophisticated solver such as ``gurobi``.
    """

    def __init__(self,
                 technology_list,
                 net_demand,
                 time_delta=None,
                 power_units=MW,
                 solver='cplex',
                 lower_bound=0.0,
                 oversupply=0.0,
                 undersupply=0.0,
                 penalty=1e-4):
        self.net_demand = net_demand
        self.time_delta = time_delta
        self.power_units = power_units
        self.lower_bound = lower_bound
        self.oversupply = oversupply
        self.undersupply = undersupply
        self.penalty = penalty
        self.model = ConcreteModel()
        self.solver = solver
        self.results = None
        self.objective = None


        self.technology_list = synchronize_units(technology_list, 
                                                unit_power=power_units, 
                                                unit_time=self.time_delta.units)

    @property
    def time_delta(self):
        return self._time_delta

    @time_delta.setter
    def time_delta(self, value):
        if value:
            valid_quantity = _validate_quantity(value, dimension='time')
            self._time_delta = valid_quantity
        else:
            if isinstance(self.net_demand, pd.DataFrame):
                try:
                    freq_list = list(self.net_demand.index.inferred_freq)
                    freq_key = freq_list[-1]
                    try:
                        value = float(freq_list[0])
                    except ValueError:
                        warnings.warn((f"Could not convert value "
                                       f"{freq_list[0]} to float. "
                                       "Setting to 1.0."),
                                      UserWarning)
                        value = 1.0
                    self._time_delta = _validate_quantity(
                        f"{value} {_freq_opts[freq_key]}", dimension='time')
                except KeyError:
                    warnings.warn(
                        (f"Could not infer time delta with freq {freq_key} "
                         "from pandas dataframe. Setting delta to 1 hour."),
                        UserWarning)
                    self._time_delta = 1 * hr
            else:
                self._time_delta = 1 * hr

    @property
    def power_units(self):
        return self._demand_units
    
    @power_units.setter
    def power_units(self, value):
        if value:
            valid_quantity = _validate_unit(value, dimension='power')
            self._demand_units = valid_quantity
        else:
            warnings.warn(f"Could not infer demand units. Unit set to MW.")

    @property
    def n_timesteps(self):
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
    def efficiency_dict(self):
        capacity_set = [t.efficiency for t in self.technology_list]
        return dict(zip(self.tech_set, capacity_set))

    @property
    def time_set(self):
        return range(self.n_timesteps)

    @property
    def indices(self):
        return list(it.product(self.tech_set, self.time_set))

    @property
    def cost_params(self):
        v_costs = np.array([
            (t.variable_cost_ts(self.n_timesteps))
            for t in self.technology_list
        ]).flatten()
        return dict(zip(self.indices, v_costs))

    @property
    def storage_techs(self):
        return [t.technology_name
                for t in self.technology_list
                if hasattr(t, "storage_capacity")]

    @property
    def storage_upper_bound(self):
        caps = unyt_array([t.storage_capacity
                           for t in self.technology_list
                           if hasattr(t, "storage_capacity")])
        return caps.max().to_value()

    @property
    def max_storage_params(self):
        storage_dict = {t.technology_name: t.storage_capacity.to_value()
                        for t in self.technology_list
                        if hasattr(t, "storage_capacity")}
        return storage_dict

    @property
    def initial_storage_params(self):
        storage_dict = {t.technology_name: t.initial_storage.to_value()
                        for t in self.technology_list
                        if hasattr(t, "initial_storage")}
        return storage_dict

    @property
    def ramping_techs(self):
        return [t.technology_name
                for t in self.technology_list
                if hasattr(t, 'ramp_up')]

    @property
    def ramp_up_params(self):
        rates_dict = {
            t.technology_name: (
                t.ramp_up *
                self.time_delta).to_value() for t in self.technology_list
            if hasattr(t, 'ramp_up')}
        return rates_dict

    @property
    def ramp_down_params(self):
        rates_dict = {
            t.technology_name: (
                t.ramp_down *
                self.time_delta).to_value() for t in self.technology_list
            if hasattr(t, 'ramp_up')}
        return rates_dict

    @property
    def upper_bound(self):
        caps = unyt_array([t.capacity for t in self.technology_list])
        return caps.max().to_value()

    def _create_model_indices(self):
        self.model.U = pe.Set(initialize=self.tech_set, ordered=True)
        self.model.T = pe.Set(initialize=self.time_set, ordered=True)
        if len(self.ramping_techs) > 0:
            self.model.R = pe.Set(initialize=self.ramping_techs,
                                  ordered=True,
                                  within=self.model.U)
        if len(self.storage_techs) > 0:
            self.model.StorageTech = pe.Set(initialize=self.storage_techs,
                                  ordered=True,
                                  within=self.model.U)

    def _create_demand_param(self):
        self.model.D = pe.Param(self.model.T, initialize=dict(
            zip(self.model.T, np.array(self.net_demand))))

    def _create_cost_param(self):
        self.model.C = pe.Param(
            self.model.U,
            self.model.T,
            initialize=self.cost_params)

    def _create_ramping_params(self):
        self.model.ramp_up = pe.Param(
            self.model.R, initialize=self.ramp_up_params)
        self.model.ramp_down = pe.Param(
            self.model.R, initialize=self.ramp_down_params)

    def _create_max_storage_params(self):
        self.model.storage_capacity = pe.Param(
            self.model.StorageTech, initialize=self.max_storage_params
        )

    def _create_init_storage_params(self):
        self.model.initial_storage = pe.Param(
            self.model.StorageTech, initialize=self.initial_storage_params
        )

    def _create_model_variables(self):
        self.model.x = pe.Var(self.model.U, self.model.T,
                              domain=pe.NonNegativeReals,
                              bounds=(self.lower_bound, self.upper_bound))

        if len(self.storage_techs) > 0:
            self.model.storage_level = pe.Var(self.model.StorageTech, self.model.T,
                                              domain=pe.NonNegativeReals,
                                              bounds=(self.lower_bound,
                                                      self.storage_upper_bound)
                                              )
            self.model.charge = pe.Var(self.model.StorageTech, self.model.T,
                                       domain=pe.NonNegativeReals,
                                       bounds=(self.lower_bound,
                                               self.upper_bound))

    def _objective_function(self):
        expr = sum(self.model.C[u, t] * self.model.x[u, t]
                   for u in self.model.U for t in self.model.T)
        if len(self.storage_techs) > 0:
            expr += sum(self.model.x[s,t] + self.model.charge[s,t]
                        for s in self.model.StorageTech for t in self.model.T) * self.penalty
        self.model.objective = pe.Objective(sense=pe.minimize, expr=expr)

    def _supply_constraints(self):
        self.model.oversupply = pe.ConstraintList()
        self.model.undersupply = pe.ConstraintList()
        for t in self.model.T:
            generation = sum(self.model.x[u, t] for u in self.model.U)
            if len(self.storage_techs) > 0:
                generation -= sum(self.model.charge[s, t] for s in self.model.StorageTech)
            over_demand = self.model.D[t] * (1 + self.oversupply)
            under_demand = self.model.D[t] * (1 - self.undersupply)
            self.model.oversupply.add(generation <= over_demand)
            self.model.undersupply.add(generation >= under_demand)

    def _generation_constraint(self):
        self.model.gen_limit = pe.ConstraintList()
        for u in self.model.U:
            unit_capacity = (self.capacity_dict[u]*self.time_delta).to_value()

            for t in self.model.T:
                unit_generation = self.model.x[u, t]
                self.model.gen_limit.add(unit_generation <= unit_capacity)

    def _ramping_constraints(self):
        self.model.ramp_up_limit = pe.ConstraintList()
        self.model.ramp_down_limit = pe.ConstraintList()

        for r in self.model.R:
            ramp_up = self.model.ramp_up[r]
            ramp_down = self.model.ramp_down[r]
            for t in self.model.T:
                if t != self.model.T.first():
                    t_prev = self.model.T.prev(t)
                    previous_gen = self.model.x[r, t_prev]
                    current_gen = self.model.x[r, t]
                    delta_power = (current_gen - previous_gen) / \
                        self.time_delta.to_value()
                    self.model.ramp_up_limit.add(delta_power <= ramp_up)
                    self.model.ramp_down_limit.add(delta_power >= -ramp_down)

    def _storage_constraints(self):
        self.model.discharge_limit = pe.ConstraintList()
        self.model.charge_limit = pe.ConstraintList()
        self.model.charge_rate_limit = pe.ConstraintList()
        self.model.storage_limit = pe.ConstraintList()
        self.model.set_storage = pe.ConstraintList()
        for s in self.model.StorageTech:
            efficiency = self.efficiency_dict[s]
            storage_cap = self.model.storage_capacity[s]
            unit_capacity = (self.capacity_dict[s]*self.time_delta).to_value()
            initial_storage = self.model.initial_storage[s]
            for t in self.model.T:
                self.model.charge_rate_limit.add(self.model.charge[s,t] <= unit_capacity)
                if t == self.model.T.first():
                    self.model.set_storage.add(self.model.storage_level[s, t]
                                               == initial_storage)
                    self.model.discharge_limit.add(
                        self.model.x[s, t] <= initial_storage)
                    self.model.charge_limit.add(self.model.charge[s, t]
                                                <= storage_cap
                                                - initial_storage)
                else:
                    t_prev = self.model.T.prev(t)
                    previous_storage = self.model.storage_level[s, t_prev]
                    current_discharge = self.model.x[s, t]
                    current_charge = self.model.charge[s, t]
                    self.model.set_storage.add(
                        self.model.storage_level[s, t]
                        == previous_storage
                        + np.sqrt(efficiency) * current_charge
                        - np.sqrt(efficiency) * current_discharge
                    )
                    self.model.charge_limit.add(
                        np.sqrt(efficiency) * current_charge
                        <= storage_cap - previous_storage)
                    self.model.discharge_limit.add(
                        current_discharge <= previous_storage)
                self.model.storage_limit.add(
                    self.model.storage_level[s, t] <= storage_cap)

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
            self._ramping_constraints()
        if len(self.storage_techs) > 0:
            self._create_init_storage_params()
            self._create_max_storage_params()
            self._storage_constraints()

    def _format_results(self):
        df = pd.DataFrame(index=self.model.T)
        for u in self.model.U:
            df[u] = [self.model.x[u, t].value for t in self.model.T]


        if len(self.storage_techs) > 0:
            for s in self.model.StorageTech:
                df[f"{s}_charge"] = [-1*self.model.charge[s, t].value
                                     for t in self.model.T]
                df[f"{s}_level"] = [self.model.storage_level[s, t].value
                                    for t in self.model.T]
        return df

    def solve(self):
        self._write_model_equations()
        solver = po.SolverFactory(self.solver)
        results = solver.solve(self.model, tee=True)
        try:
            self.objective = self.model.objective()
        except ValueError:
            warnings.warn("Infeasible solution. Objective set to 1e40.")
            self.objective = 1e40
        self.results = self._format_results()