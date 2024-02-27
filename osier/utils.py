from osier import Technology
from osier.technology import _validate_unit
from unyt import unit_object
import copy
from typing import Iterable
import pandas as pd
import numpy as np
import functools
import types

from osier.technology import Technology


def synchronize_units(tech_list: Iterable[Technology],
                      unit_power: unit_object,
                      unit_time: unit_object) -> Iterable[Technology]:
    """
    This function ensures that all objects in the technology list have units
    consistent with the model's units. An :class:`osier.Technology` object (or
    sub-classes) have three unit settings.

        * :attr:`unit_power`
        * :attr:`unit_time`
        * :attr:`unit_energy`

    Only the :attr:`unit_power` and :attr:`unit_time` attributes can be
    specified with this function to prevent inconsistent units. E.g. Setting the
    :attr:`unit_energy` to ``MWh`` even though time is in minutes and power is
    in ``kW``.

    .. note::
        The objects in the original list are copied by default. This
        may result in slower run time.

    Parameters
    ----------
    tech_list : list of :class:`osier.Technology` objects
        The list of technology objects whose units need to be synchronized.

    Returns
    -------
    synced_list : list of :class:`osier.Technology` objects
        The list of technology objects that have synchronized units.
    """

    synced_list = [copy.deepcopy(t) for t in tech_list]

    for t in synced_list:
        t.unit_power = _validate_unit(unit_power, dimension="power")
        t.unit_time = _validate_unit(unit_time, dimension="time")

    return synced_list



def get_tech_names(technology_list):
    """
    Returns the a list of :class:`osier.Technology` name strings.

    Parameters
    ----------
    technology_list : list of :class:`osier.Technology` objects
        The list of technologies.

    Returns
    -------
    tech_names : list of str
        The list of technology names.
    """

    tech_names = [t.technology_name for t in technology_list]

    return tech_names


def get_dispatchable_techs(technology_list):
    """
    Returns a list of :class:`osier.Technology` objects where
    :attr:`dispatchable` is `True`.

    Parameters
    ----------
    technology_list : list of :class:`osier.Technology` objects
        The list of technologies.

    Returns
    -------
    tech_names : list of :class:`osier.Technology`
        The list of dispatchable technologies.
    """

    dispatchable_techs = [t for t in technology_list if t.dispatchable]

    return dispatchable_techs


def get_nondispatchable_techs(technology_list):
    """
    Returns a list of :class:`osier.Technology` objects where
    :attr:`dispatchable` is `False`.

    Parameters
    ----------
    technology_list : list of :class:`osier.Technology` objects
        The list of technologies.

    Returns
    -------
    non_dispatchable_techs : list of :class:`osier.Technology`
        The list of non dispatchable technologies.
    """

    non_dispatchable_techs = [t for t in technology_list if not t.dispatchable]

    return non_dispatchable_techs


def get_dispatchable_names(technology_list):
    """
    Returns a list of :class:`osier.Technology` name strings where
    :attr:`dispatchable` is `True`.

    Parameters
    ----------
    technology_list : list of :class:`osier.Technology` objects
        The list of technologies.

    Returns
    -------
    dispatchable_names : list of str
        The list of dispatchable technology names.
    """

    dispatchable_names = [
        t.technology_name for t in technology_list if t.dispatchable]

    return dispatchable_names


def get_objective_names(res_obj):
    """
    This function returns a list of named objectives based on the names of the
    functions passed to Osier. In the case of partial functions, the first
    keyword value is used.
    
    Parameters
    ----------
    res_obj : :class:`pymoo.Result`
        The simulation results object containing all data and metadata.
    
    Returns
    -------
    obj_columns : list of str
        A list of function name strings.
    """
    obj_columns=[]
    for ofunc in res_obj.problem.objectives:
        if isinstance(ofunc, types.FunctionType):
            obj_columns.append(ofunc.__name__)
        elif isinstance(ofunc, functools.partial):
            obj_columns.append(list(ofunc.keywords.values())[0]) 
    return obj_columns


def technology_dataframe(technology_list, cast_to_string=True):
    """
    Returns a :class:`pandas.DataFrame` with a complete set of data for a given
    technology list.

    Parameters
    ----------
    technology_list : list of :class:`osier.Technology` objects
        The list of technologies.

    Returns
    -------
    technology_dataframe : :class:`pandas.DataFrame`
        A dataframe of all technology data.
    """

    frames = []

    for t in technology_list:
        frames.append(t.to_dataframe(cast_to_string=cast_to_string))

    technology_dataframe = pd.concat(frames, axis=0)

    return technology_dataframe


def apply_slack(pareto_front, slack, sense='minimize'):
    """
    This function applies a specified slack value to a given Pareto front.
    Returns a :class:`numpy.ndarray` with the same shape as the Pareto front.

    Parameters
    ----------
    pareto_front : :class:`numpy.ndarray`
        A :class:`numpy.ndarray` with shape (population, N_objectives).

    slack : float or list of float
        The slack value for the sub-optimal front, expressed as a decimal
        percentage. If `float` is passed, the same slack will be applied to all
        objectives. A `list` of slack values should have the same length as the
        list of objectives. The slack will be applied to objective with the same
        index (defined when users initialized the :class:`osier.CapacityExpansion` problem).
        Each slack value should be less than unity. If users that find a 
        slack greater than unity desirable should consider rerunning the model with fewer
        or different objectives.

    Returns
    -------
    near_optimal_front : :class:`numpy.ndarray`
        The near-optimal front.
    """
    
    try:
        n_objectives = pareto_front.shape[1]
    except IndexError as e:
        n_objectives = len(pareto_front)
    
    if isinstance(slack, (list, np.ndarray)):
        try:
            assert len(slack) == n_objectives
        except AssertionError:
            print("Number of slack values must equal number of objectives.")
            raise ValueError

        near_optimal_front = (np.ones(n_objectives)+np.array(slack))*np.array(pareto_front)
        if sense.lower() == 'minimize':
            near_optimal_front = np.array(pareto_front)*(np.ones(n_objectives)+np.array(slack))
            return near_optimal_front
        elif sense.lower() == 'maximize':
            near_optimal_front = np.array(pareto_front)*(np.ones(n_objectives)-np.array(slack))
            return near_optimal_front
        
        return near_optimal_front
    elif isinstance(slack, float):
        if sense.lower() == 'minimize':
            near_optimal_front = np.array(pareto_front)*(1+slack)
            return near_optimal_front
        elif sense.lower() == 'maximize':
            near_optimal_front = np.array(pareto_front)*(1-slack)
            return near_optimal_front

    return

    


def nmga(results_obj, n_points=10, slack=0.1, sense='minimize', how='random'):
    """
    N-dimensional modeling-to-generate-alternatives (n-mga) allows users to
    efficiently search decision space by relaxing the objective function(s) by a
    specified amount of slack. This implementation will identify all points
    inside of an N-polytope (a polygon in N-dimensions). Then a reduced subset
    of points will be selected. 

    
    Parameters
    ----------
    results_obj : :class:pymoo.Result
        The simulation results object containing all data and metadata.
    n_points : int
        The number of points to select from the near-optimal region. Default is
        10.
    slack : float or list of float
        The slack value for the sub-optimal front, expressed as a decimal
        percentage. If `float` is passed, the same slack will be applied to all
        objectives. A `list` of slack values should have the same length as the
        list of objectives. The slack will be applied to objective with the same
        index (defined when users initialized the
        :class:`osier.CapacityExpansion` problem).
    sense : str
        Indicates whether the optimization was a minimization or maximization.
        If min, the sub-optimal front is greater than the Pareto front. If max,
        the sub-optimal front is below the Pareto front. Default is "minimize." 
    """
    n_objs = results_obj.problem.n_obj
    
    
    pf = results_obj.F

        
    
    checked_points = set()

    interior_dict = {n:[] for n in range(n_objs+1)}
    cols = get_objective_names(results_obj) + ['designs']
    
    # get list of all points
    for h in results_obj.history:
        # the history of each population, individual, and their corresponding
        # design spaces.
        F_hist = h.pop.get("F")  # objective space
        X_hist = h.pop.get("X")  # design space
    
        for p, x in zip(F_hist, X_hist):
            if p in checked_points:
                continue
            else:
                checked_points.add(p)
                # check that all coordinates of a point are within the
                # boundaries.
                cond1 = np.any((p < pf_slack).sum(axis=1)==n_objs)
                cond2 = np.any((p > pf).sum(axis=1)==n_objs)
                if cond1 and cond2:
                    for i,c in enumerate(p):
                        interior_dict[i].append(c)
                    interior_dict[n_objs].append(x)
    mga_df = pd.DataFrame(interior_dict)
    mga_df.columns = cols
    
    return mga_df
    

