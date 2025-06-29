import pandas as pd
import numpy as np
from unyt import unyt_array, hr, MW, kW, GW
import itertools as it
from osier import Technology
from osier.technology import _validate_quantity, _validate_unit
from osier.utils import synchronize_units
import warnings
import logging

_freq_opts = {'D': 'day',
              'H': 'hour',
              'S': 'second',
              'T': 'minute'}


class OsierModel():
    """
    A class for instantiating energy models in Osier.
    """

    def __init__(self,
                 technology_list,
                 net_demand,
                 time_delta=None,
                 power_units=MW,
                 **kwargs):
        self.net_demand = net_demand
        self.time_delta = time_delta
        self.results = None
        self.objective = None

        if isinstance(net_demand, unyt_array):
            self.power_units = net_demand.units
        elif isinstance(net_demand, (np.ndarray, list)):
            self.power_units = power_units
            self.net_demand = np.array(self.net_demand) * self.power_units
        elif isinstance(net_demand, pd.core.series.Series):
            self.power_units = power_units
            self.net_demand = np.array(self.net_demand) * self.power_units
        else:
            self.power_units = power_units

        self.technology_list = technology_list

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
