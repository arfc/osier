from osier import OsierModel
from osier.utils import get_tech_names
from copy import deepcopy
from unyt import unyt_array, MW
import pandas as pd
import numpy as np
import warnings

LARGE_NUMBER = 1e20


class LogicDispatchModel(OsierModel):
    """
    The :class:`LogicDispatchModel` class creates and solves a basic dispatch
    model from the perspective of a "grid operator." 
    
    Parameters
    ----------
    technology_list : list of :class:`osier.Technology`
        The list of :class:`Technology` objects to dispatch -- i.e. decide
        how much energy each technology should produce.
    net_demand : list, :class:`numpy.ndarray`, :class:`unyt.array.unyt_array`, :class:`pandas.DataFrame`
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
    power_units : str, :class:`unyt.unit_object`
        Specifies the units for the power demand. The default is :attr:`MW`.
        Can be overridden by specifying a unit with the value.
    verbosity : Optional, int
        Sets the logging level for the simulation. Accepts `logging.LEVEL`
        or integer where LEVEL is {10:DEBUG, 20:INFO, 30:WARNING, 40:ERROR, 50:CRITICAL}.
    curtailment : boolean
        Indicates if the model should enable a curtailment option.
    allow_blackout : boolean
        If True, a "reliability" technology is added to the model that will
        fulfill the mismatch in supply and demand. This reliability technology
        has a variable cost of 1e4 $/MWh. The value must be higher than the
        variable cost of any other technology to prevent a pathological
        preference for blackouts. Default is False.

    Attributes
    ----------
    objective : float
        The result of the model's objective function. Only instantiated
        after :meth:`DispatchModel.solve()` is called.
    technology_list : list of :class:`osier.Technology`
        A _sorted_ list of technologies.
    original_order : list of str
        A list of technology names to preserve the intended order of the
        technologies.
    """
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
        self.original_order = get_tech_names(technology_list)
        self.cost_history = np.zeros(len(net_demand))
        self.covered_demand = None
        self.objective = None
        self.results = None
        self.verbosity = verbosity
        self.allow_blackout = allow_blackout
        self.curtailment = curtailment

    def _reset_all(self):
        for t in self.technology_list:
            t.reset_history()
        return

    def _format_results(self):
        data = {}
        for t in self.technology_list:
            data[f"{t.technology_name}"] = unyt_array(
                t.power_history).to_ndarray()
            if t.technology_type == 'storage':
                data[f"{t.technology_name}_level"] = unyt_array(
                    t.storage_history).to_ndarray()
                data[f"{t.technology_name}_charge"] = unyt_array(
                    t.charge_history).to_ndarray()
        data["Curtailment"] = np.array(
            [v if v <= 0 else 0 for v in self.covered_demand])
        data["LoadLoss"] = np.array(
            [v if v > 0 else 0 for v in self.covered_demand])
        self.results = pd.DataFrame(data)
        return

    def _calculate_objective(self):
        self.objective = sum(np.array(t.power_history).sum()
                             * t.variable_cost.to_value()
                             for t in self.technology_list)
        return

    def solve(self):
        """
        This function executes the model solve with a rule-based approach.
        """
        self.covered_demand = self.net_demand.copy()
        self._reset_all()
        try:
            for i, v in enumerate(self.covered_demand):
                for t in self.technology_list:
                    power_out = t.power_output(v, time_delta=self.time_delta)
                    v -= power_out

                self.covered_demand[i] = v
                if not self.allow_blackout and (v > 0):
                    if self.verbosity <= 20:
                        print('solve failed -- unmet demand')
                    raise ValueError

                if not self.curtailment and (v < 0):
                    if self.verbosity <= 20:
                        print(
                            ('solve failed -- '
                            'too much supply '
                            '(no curtailment allowed)'))
                    raise ValueError

            self._format_results()
            self._calculate_objective()
        except ValueError:
            if self.verbosity <= 30:
                warnings.warn(
                    (f"Infeasible or no solution." 
                     f"Objective set to {LARGE_NUMBER}")
                    )
            self.objective = LARGE_NUMBER

        return
