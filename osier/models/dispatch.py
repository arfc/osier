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

    .. math::
        \\sum_t^Tx_u &\\geq \\left(1-\\text{undersupply}\\right)\\text{D}_t \\
        \\forall \\ t \\in T

        \\sum_t^Tx_u &\\leq \\left(1+\\text{oversupply}\\right)\\text{D}_t \\
        \\forall \\ t \\in T
        

    Parameters
    ----------
    technology_list : list of :class:`osier.Technology`
        The list of :class:`Technology` objects to dispatch -- i.e. decide
        how much energy each technology should produce.
    net_demand : List, :class:`numpy.ndarray`, :class:`unyt.array.unyt_array`
        The remaining energy demand to be fulfilled by the technologies in
        :attr:`technology_list`. For example:

        >>> from osier import DispatchModel
        >>> from osier import Technology
        >>> wind = Technology("wind")
        >>> nuclear = Technology("nuclear")
        >>> import numpy as np
        >>> hours = np.arange(24)
        >>> demand = np.cos(hours*np.pi/180)
        >>> model = DispatchModel([wind, nuclear], demand)
        >>> model.solve()

    solver : str 
        Indicates which solver to use. May require separate installation.
        Accepts: ['cplex']. Other solvers will be added in the future.
    lower_bound : float
        The least amount of energy each technology can produce per time
        period. Default is 0.0.
    oversupply : float
        The amount of allowed oversupply as a percentage of demand.
        Default is 0.0 (no oversupply allowed). 
    undersupply : float
        The amount of allowed undersupply as a percentage of demand.
        Default is 0.0 (no undersupply allowed).
    """
    def __init__(self, 
                 technology_list,
                 net_demand,
                 solver='cplex',
                 lower_bound=0.0,
                 oversupply = 0.0,
                 undersupply = 0.0):
        self.net_demand = net_demand
        self.technology_list = technology_list
        self.lower_bound = lower_bound
        self.oversupply = oversupply
        self.undersupply = undersupply
        self.model = ConcreteModel()
        self.solver = solver
        self.results = None
    
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
    def upper_bound(self):
        caps = unyt_array([t.capacity for t in self.technology_list])
        return caps.max().to_value()
    
    def _create_model_indices(self):
        self.model.U = pe.Set(initialize=self.tech_set, ordered=True)
        self.model.T = pe.Set(initialize=self.time_set, ordered=True)
    
    def _create_demand_param(self):
        self.model.D = pe.Param(self.model.T, initialize=dict(zip(self.model.T, self.net_demand)))
    
    def _create_cost_param(self):
        self.model.C = pe.Param(self.model.U, self.model.T, initialize=self.cost_params)

    
    def _create_model_variables(self):
        self.model.x = pe.Var(self.model.U, self.model.T, 
                              domain=pe.Reals, 
                              bounds=(self.lower_bound, self.upper_bound))
        
    def _objective_function(self):
        expr = sum(self.model.C[u, t] * self.model.x[u, t]
                   for u in self.model.U for t in self.model.T)
        self.model.objective = pe.Objective(sense=pe.minimize, expr=expr)
        
    def _oversupply_constraint(self):
        self.model.oversupply = pe.ConstraintList()
        for t in self.model.T:
            generation = sum(self.model.x[u, t] for u in self.model.U)
            over_demand = self.model.D[t] * (1+self.oversupply)
            self.model.oversupply.add(generation <= over_demand)
            
    def _undersupply_constraint(self):
        self.model.undersupply = pe.ConstraintList()
        for t in self.model.T:
            generation = sum(self.model.x[u, t] for u in self.model.U)
            under_demand = self.model.D[t] * (1-self.undersupply)
            self.model.undersupply.add(generation >= under_demand)
            
    def _generation_constraint(self):
        self.model.gen_limit = pe.ConstraintList()
        for t in self.model.T:
            for u in self.model.U:
                unit_generation = self.model.x[u, t]
                unit_capacity = self.capacity_dict[u].to_value()
                self.model.gen_limit.add(unit_generation <= unit_capacity)

    
    def _write_model_equations(self):
        
        self._create_model_indices()
        self._create_demand_param()
        self._create_cost_param()
        self._create_model_variables()
        self._objective_function()
        self._oversupply_constraint()
        self._undersupply_constraint()
        self._generation_constraint()
        
        return
    
    def _format_results(self):
        df = pd.DataFrame(index=self.model.T)
        for u in self.model.U:
            df[u] = [self.model.x[u,t].value for t in self.model.T]
            
        return df
        
        
    def solve(self):
        self._write_model_equations()
        solver = po.SolverFactory(self.solver)
        results = solver.solve(self.model, tee=True)
        
        self.results = self._format_results()        