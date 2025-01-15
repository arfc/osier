import numpy as np
import pandas as pd
from copy import deepcopy
import dill
import unyt as u
from unyt import unyt_array
import functools
import time

from osier import DispatchModel, LogicDispatchModel

from pymoo.core.problem import ElementwiseProblem

LARGE_NUMBER = 1e20

dispatch_models = {
                   'optimal':DispatchModel,
                   'logical': LogicDispatchModel
                   }


class CapacityExpansion(ElementwiseProblem):
    """
    The :class:`CapacityExpansion` class inherits from the
    :class:`pymoo.core.problem.ElementwiseProblem` class. This problem
    determines the technology mix that _minimizes_ the provided objectives.

    Parameters
    ----------
    technology_list : list of :class:`osier.Technology` objects
        Defines the technologies used in the model and the number of decision
        variables.
    demand : :class:`numpy.ndarray`
        The demand curve that needs to be met by the technology mix.
    objectives : list of str or functions
        Specifies the number and type of objectives. A list of strings must
        correspond to preset objective functions. Users may optionally write
        their own functions and pass them to `osier` as items in the list.
    constraints : dictionary of string : float or function : float
        Specifies the number and type of constraints. String key names must
        correspond to preset constraints functions. Users may optionally write
        their own functions and pass them to `osier` as keys in the list. The
        values must be numerical and represent the value that the function
        should not exceed. See notes for more information about constraints.
    prm : Optional, float
        The "planning reserve margin" (`prm`) specifies the amount of excess
        capacity needed to meet reliability standards. See
        :attr:`capacity_requirement`. Default is 0.0.
    solar : Optional, :class:`numpy.ndarray`
        The curve that defines the solar power provided at each time step.
        Automatically normalized with the infinity norm (i.e. divided by the
        maximum value).
    wind : Optional, :class:`numpy.ndarray`
        The curve that defines the wind power provided at each time step.
        Automatically normalized with the infinity norm (i.e. divided by the
        maximum value).
    power_units : str, :class:`unyt.unit_object`
        Specifies the units for the power demand. The default is :attr:`MW`. Can
        be overridden by specifying a unit with the value.
    penalty : Optional, float
        The penalty for infeasible solutions. If a particular set produces an
        infeasible solution for the :class:`osier.DispatchModel`, the
        corresponding objectives take on this value.
    curtailment : boolean
        Indicates if the model should enable a curtailment option.
    allow_blackout : boolean
        If True, a "reliability" technology is added to the dispatch model that
        will fulfill the mismatch in supply and demand. This reliability
        technology has a variable cost of 1e4 $/MWh. The value must be higher
        than the variable cost of any other technology to prevent a pathological
        preference for blackouts. Default is False.
    verbosity : Optional, int
        Sets the logging level for the simulation. Accepts `logging.LEVEL` or
        integer where LEVEL is {10:DEBUG, 20:INFO, 30:WARNING, 40:ERROR,
        50:CRITICAL}.
    solver : str
        Indicates which solver to use. May require separate installation.
        Accepts: ['cplex', 'cbc', 'glpk']. Other solvers will be added in the
        future.
    model_engine : str
        Determines which dispatch algorithm to use.
        Accepts: ['optimal', 'logical'] where 'optimal' will use a linear
        program and 'logical' will use a myopic rule-based approach.
        Default is 'optimal'.

    Notes
    -----
    **Constraints**:

    `Pymoo` constraints are not strict in the sense that `Pymoo` prefers
    feasibility over respecting constraints. However, all `Pymoo` algorithms
    will minimize the "constraint violation (CV)."
    """

    def __init__(self,
                 technology_list,
                 demand,
                 objectives,
                 constraints={},
                 solar=None,
                 wind=None,
                 prm=0.0,
                 lower_bound=0.0,
                 upper_bound=1.0,
                 penalty=LARGE_NUMBER,
                 power_units=u.MW,
                 curtailment=True,
                 allow_blackout=False,
                 verbosity=50,
                 solver='cbc',
                 model_engine='optimal',
                 **kwargs):
        self.technology_list = deepcopy(technology_list)
        self.demand = demand
        self.prm = prm

        self.objectives = objectives
        self.constraints = constraints
        self.penalty = penalty
        self.curtailment = curtailment
        self.allow_blackout = allow_blackout
        self.verbosity = verbosity
        self.model_engine = model_engine.lower()
        self.solver = solver

        if isinstance(demand, unyt_array):
            self.power_units = demand.units
        else:
            self.power_units = power_units

        self.max_demand = float(demand.max()) * self.power_units
        self.capacity_requirement = self.max_demand * (1 + self.prm)

        if solar is not None:
            self.solar_ts = solar / solar.max()
        else:
            self.solar_ts = np.zeros(len(self.demand))
        if wind is not None:
            self.wind_ts = wind / wind.max()
        else:
            self.wind_ts = np.zeros(len(self.demand))

        super().__init__(n_var=len(self.technology_list),
                         n_obj=len(self.objectives),
                         n_constr=len(self.constraints),
                         xl=lower_bound,
                         xu=upper_bound,
                         **kwargs)

    def print_problem_formulation(self):
        """
        Prints the problem formulation.
        """

        print("===========================")
        print("CapacityExpansion Problem")
        print("===========================")
        print("Technologies:\n")
        print("Technology Name | Capacity \n")
        for t in self.technology_list:
            print(t)

        print("\nElectricity Demand:\n")
        print(self.demand)

        return

    @property
    def capacity_credit(self):
        return np.array([t.capacity_credit for t in self.technology_list])

    @property
    def dispatchable_techs(self):
        return [t for t in self.technology_list if t.dispatchable]

    def _evaluate(self, x, out, *args, **kwargs):
        capacities = self.capacity_requirement * x
        solar_capacity = 0
        wind_capacity = 0
        firm_capacity = 0
        for capacity, tech in zip(capacities, self.technology_list):
            tech.capacity = capacity
            if tech.renewable:
                if tech.fuel_type == 'solar':
                    solar_capacity += capacity
                elif tech.fuel_type == 'wind':
                    wind_capacity += capacity
            elif ((tech.dispatchable) and (tech.technology_name != 'Battery')):
                firm_capacity += capacity

        solar_gen = self.solar_ts * solar_capacity
        wind_gen = self.wind_ts * wind_capacity

        renewable_df = pd.DataFrame({'SolarPanel': solar_gen,
                                     'WindTurbine': wind_gen})

        net_demand = self.demand \
            - wind_gen \
            - solar_gen

        dispatch_model = dispatch_models[self.model_engine]
        model = dispatch_model(technology_list=self.dispatchable_techs,
                               net_demand=net_demand,
                               power_units=self.power_units,
                               curtailment=self.curtailment,
                               allow_blackout=self.allow_blackout,
                               solver=self.solver,
                               verbosity=self.verbosity)
        model.solve()

        if model.results is not None:

            model.results = pd.concat([model.results, renewable_df], axis=1)

            out_obj = []
            for obj_func in self.objectives:
                out_obj.append(obj_func(technology_list=self.technology_list,
                                        solved_dispatch_model=model))

            if self.n_constr > 0:
                out_constr = []
                for constr_func, val in self.constraints.items():
                    out_constr.append(
                        constr_func(
                            technology_list=self.technology_list,
                            solved_dispatch_model=model) - val)

        else:
            out_obj = np.ones(self.n_obj) * self.penalty
            if self.n_constr > 0:
                out_constr = np.ones(self.n_constr) * self.penalty

        out["F"] = out_obj

        if self.n_constr > 0:
            out["G"] = out_constr
