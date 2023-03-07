from osier import OsierModel
from osier.utils import get_nonstorage_techs, get_storage_techs
from copy import deepcopy
import numpy as np


class LogicDispatchModel(OsierModel):

    def __init__(self, 
                 technology_list, 
                 net_demand, 
                 *args, **kwargs):
        super().__init__(technology_list=technology_list, 
                         net_demand=net_demand,
                         **args, **kwargs)
        
        self.storage_techs = get_storage_techs(self.technology_list)
        self.nonstorage_techs = get_nonstorage_techs(self.technology_list)
        self.cost_history = np.zeros(len(net_demand))


    def solve(self):
        covered_demand = self.net_demand.copy()
        nonstorage_techs = deepcopy(self.nonstorage_techs)
        nonstorage_techs.sort()

        storage_techs = deepcopy(self.storage_techs)
        storage_techs.sort()

        for i, v in enumerate(covered_demand):

            if v > 0:
                for t in nonstorage_techs:
                    power_out = t.power_output(v, 
                                               time_delta=self.time_delta)
                    v -= power_out
                    print(f"{t.technology_name} output {power_out}")
                    if v <= 0:
                        break
                    else:
                        continue
            if v > 0:
                for s in storage_techs:
                    power_out = s.power_output(v, 
                                               time_delta=self.time_delta)
                    v -= power_out
                    if v <= 0:
                        break
                    else:
                        continue

            if v < 0:
                for s in storage_techs:
                    power_in = s.charge(v, 
                                        time_delta=self.time_delta)
                    v += power_in
                    if v >= 0:
                        break
                    else:
                        continue

        covered_demand[i] = v

        n_hours_unmet = len(covered_demand[covered_demand.iloc[:,0] > 0])
    #     print(n_hours_unmet)
        lolp = n_hours_unmet / 8760
        
        return covered_demand, lolp