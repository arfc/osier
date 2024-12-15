from osier import OsierModel
from osier.utils import get_tech_names
from copy import deepcopy
from unyt import unyt_array
import pandas as pd
import numpy as np
import warnings

LARGE_NUMBER = 1e20


class LogicDispatchModel(OsierModel):

    def __init__(self, 
                 technology_list, 
                 net_demand,
                 allow_blackout=False,
                 curtailment=True,
                 verbosity=50,
                 *args, **kwargs):
        super().__init__(technology_list=technology_list, 
                         net_demand=net_demand,
                         *args, **kwargs)
        self.technology_list = technology_list
        self.technology_list.sort()
        self.original_order = get_tech_names(self.technology_list)
        self.cost_history = np.zeros(len(net_demand))
        self.covered_demand = None
        self.objective = None
        self.results = None
        self.verbosity=verbosity
        self.allow_blackout = allow_blackout
        self.curtailment = curtailment

    def _reset_all(self):
        for t in self.technology_list:
            t.reset_history()
        return

    def _format_results(self):
        data = {}
        for t in self.technology_list:
            print(f"formatting results for {t}")
            data[f"{t.technology_name}"] = unyt_array(t.power_history).to_ndarray()
            if t.technology_type == 'storage':
                data[f"{t.technology_name}_level"] = unyt_array(t.storage_history).to_ndarray()
                data[f"{t.technology_name}_charge"] = unyt_array(t.charge_history).to_ndarray()
        data["Curtailment"] = np.array([v  if v <=0 else 0 for v in self.covered_demand])
        data["Shortfall"] = np.array([v if v > 0 else 0 for v in self.covered_demand])
        self.results = pd.DataFrame(data)
        return

    def _calculate_objective(self):
        self.objective = sum(np.array(t.power_history).sum()
                                        *t.variable_cost.to_value() 
                                        for t in self.technology_list)
        return

    def solve(self):
        """
        This function executes the model solve with a rule-based approach.
        Net demand is copied, then the technology histories are reset.
        """
        self.covered_demand = self.net_demand.copy()
        self._reset_all()
        print('model prepared')
        try:
            print('executing solve')
            for i, v in enumerate(self.covered_demand):
                for t in self.technology_list:
                    power_out = t.power_output(v, time_delta=self.time_delta)
                    print(f"{t.technology_name} produced {power_out}")
                    v -= power_out

                self.covered_demand[i] = v
                if not self.allow_blackout and (v>0):
                    print('solve failed -- unmet demand')
                    raise ValueError

                if not self.curtailment and (v<0):
                    print('solve failed -- too much overproduction (no curtailment allowed)')
                    raise ValueError
                
            self._format_results()
            self._calculate_objective()
        except ValueError:
            if self.verbosity <= 30:
                warnings.warn(
                    f"Infeasible or no solution. Objective set to {LARGE_NUMBER}")
            self.objective = LARGE_NUMBER

        return