# Standard imports
import numpy as np
import pandas as pd
from copy import deepcopy
import dill

# Osier imports
from osier import DispatchModel

# Pymoo imports
from pymoo.core.problem import Problem
from pymoo.core.problem import ElementwiseProblem
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.termination import get_termination
from pymoo.optimize import minimize
from pymoo.termination.ftol import MultiObjectiveSpaceTermination
from pymoo.visualization.scatter import Scatter
from pymoo.operators.sampling.rnd import FloatRandomSampling
from pymoo.operators.crossover.sbx import SBX
from pymoo.operators.mutation.pm import PolynomialMutation
from pymoo.termination.robust import RobustTermination
from pymoo.core.parameters import set_params, hierarchical


LARGE_NUMBER = 1e40

class CapacityExpansion(ElementwiseProblem):
    """
    The :class:`CapacityExpansion` class inherits from the 
    :class:`pymoo.ElementwiseProblem` class. This problem
    determines the technology mix that _minimizes_ the provided
    objectives.

    Parameters
    ----------
    technology_list : list of :class:`osier.Technology` objects
        Defines the technologies used in the model and the number
        of decision variables.
    demand : :class:`numpy.ndarray`
        The demand curve that needs to be met by the technology mix.
    objectives : list of str or functions
        Specifies the number and type of objectives. A list of strings
        must correspond to preset objective functions. Users may optionally
        write their own functions and pass them to `osier` as items in the
        list.
    constraints : list of str or functions
        Specifies the number and type of constraints. A list of strings
        must correspond to preset constraints functions. Users may optionally
        write their own functions and pass them to `osier` as items in the
        list.
    prm : Optional, float
        The "planning reserve margin" (`prm`) specifies the amount
        of excess capacity needed to meet reliability standards.
        See :attr:`capacity_requirement`. Default is 0.0.
    solar : Optional, :class:`numpy.ndarray`
        The curve that defines the solar power provided at each time
        step. Automatically normalized with the infinity norm 
        (i.e. divided by the maximum value).
    wind : Optional, :class:`numpy.ndarray`
        The curve that defines the wind power provided at each time
        step. Automatically normalized with the infinity norm 
        (i.e. divided by the maximum value).
    penalty : Optional, float
        The penalty for infeasible solutions. If a particular set
        produces an infeasible solution for the :class:`osier.DispatchModel`,
        the corresponding objectives take on this value.
    """

    def __init__(self, 
                technology_list, 
                demand,
                objectives,
                constraints=[],
                solar=None, 
                wind=None, 
                prm=0.0,
                penalty=LARGE_NUMBER, 
                **kwargs):
        self.technology_list = deepcopy(technology_list)
        self.demand = demand
        self.prm = prm
        self.max_demand = demand.max()
        self.avg_lifetime = 25
        self.capacity_requirement = self.max_demand * (1+self.prm)

        self.objectives = objectives
        self.constraints = constraints
        self.penalty = penalty

        if solar:
            self.solar_ts = solar / solar.max()
        else:
            self.solar_ts = np.zeros(len(self.demand))
        if wind:
            self.wind_ts = wind / wind.max()
        else:
            self.wind_ts = np.zeros(len(self.demand))

        super().__init__(n_var=len(self.technology_list), 
                         n_obj=len(self.objectives), 
                         n_constr=len(self.constraints), 
                         xl=0.0, 
                         xu=1.0,  
                         **kwargs)

        
    @property
    def capital_cost(self):
        return np.array([t.capital_cost for t in self.technology_list])
    
    @property
    def capacity_credit(self):
        return np.array([t.cap_credit for t in self.technology_list])
    
    @property
    def om_cost_fixed(self):
        return np.array([t.om_cost_fixed for t in self.technology_list])

    @property
    def dispatchable_names(self):
        return [t.technology_name for t in self.technology_list 
                if t.dispatchable]
    @property
    def dispatchable_techs(self):
        return [t for t in self.technology_list if t.dispatchable]

    def _evaluate(self, x, out, *args, **kwargs):
        # x represents the fraction of the necessary portfolio
        # check that there is enough capacity before executing the model. 
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

            solar_gen = self.solar_ts*solar_capacity
            wind_gen = self.wind_ts*wind_capacity

        net_demand = self.demand \
                    - wind_gen \
                    - solar_gen
        
        model = DispatchModel(technology_list=self.dispatchable_techs,
                              net_demand=net_demand)
        model.solve()

        if model.results is not None:

            if solar_capacity > 0:
                model.results['Solar'] = solar_gen
            if wind_capacity > 0:
                model.results['Wind'] = wind_gen

            for obj in self.objectives:
                pass

            capital = np.dot(capacities, self.capital_cost) / self.avg_lifetime
            fixed = np.dot(capacities, self.om_cost_fixed)
            co2ls = np.array([t.co2 
                              for t 
                              in self.technology_list 
                              if t.dispatchable])

            carbon_total = np.dot(co2ls, model.results[self.dispatchable_techs].values.T).sum()
            # carbon_total += wind_gen.sum()*wind.co2 + solar_gen.sum()*solar.co2
        
            cost = model.objective + capital + fixed
        else: 
            out_obj = np.ones(self.n_obj) * self.penalty
                
        out["F"] = [cost, carbon_total]