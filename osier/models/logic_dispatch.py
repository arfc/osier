from osier import OsierModel
from osier.utils import get_nonstorage_techs, get_storage_techs, get_tech_names
from copy import deepcopy
import numpy as np


class LogicDispatchModel(OsierModel):

    def __init__(self, 
                 technology_list, 
                 net_demand, 
                 *args, **kwargs):
        super().__init__(technology_list=technology_list, 
                         net_demand=net_demand,
                         *args, **kwargs)
        
        self.storage_techs = get_storage_techs(self.technology_list)
        self.nonstorage_techs = get_nonstorage_techs(self.technology_list)
        self.technology_list = technology_list
        self.original_order = get_tech_names(self.technology_list)
        self.cost_history = np.zeros(len(net_demand))
        self.covered_demand = None
        self.objective

    def _reset_all(self):
        for t in self.nonstorage_techs+self.storage_techs:
            t.reset_history()

        return

    def _format_results(self):
        
        return


    def solve(self):
        self.covered_demand = self.net_demand.copy()
        self.nonstorage_techs.sort()
        self.storage_techs.sort()
        self.technology_list.sort()
        self._reset_all()

        for i, v in enumerate(self.covered_demand):
            for t in self.technology_list:
                power_out = t.power_output(v, time_delta=self.time_delta)
                v -= power_out


            # # there is unmet demand
            # # if v > 0:
            # for t in self.nonstorage_techs:
            #     power_out = t.power_output(v, 
            #                                 time_delta=self.time_delta)
            #     v -= power_out
            #     # print(f"{t.technology_name} output {power_out}")
            #     # if v <= 0:
            #     #     break
            #     # else:
            #     #     continue
            
            # # there is still unmet demand, dispatch storage technologies
            # if v > 0:
            #     for s in self.storage_techs:
            #         power_out = s.power_output(v, 
            #                                    time_delta=self.time_delta)
            #         v -= power_out
            #         # if v <= 0:
            #         #     break
            #         # else:
            #         #     continue
            
            # # there is excess energy (e.g., from renewables), store excess
            # if v < 0:
            #     for s in self.storage_techs:
            #         power_in = s.charge(v, 
            #                             time_delta=self.time_delta)
            #         v += power_in
            #         # if v >= 0:
            #         #     break
            #         # else:
            #         #     continue

            self.covered_demand[i] = v
        
        return