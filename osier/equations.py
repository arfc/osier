from abc import ABC, abstractmethod
import numpy as np

class OsierEquation(ABC):

    def __init__(self) -> None:
        pass        

    @abstractmethod
    def _do(self, technology_list, X):
        pass


def get_tech_names(technology_list):
    """
    Parameters
    ----------
    technology_list : list of :class:`osier.Technology` objects
        The list of technologies.
    """

    tech_names = [t.technology_name for t in technology_list]

    return tech_names


def get_dispatchable_techs(technology_list):
    """
    Parameters
    ----------
    technology_list : list of :class:`osier.Technology` objects
        The list of technologies.
    """

    dispatchable_techs = [t for t in technology_list if t.dispatchable]

    return dispatchable_techs


def get_nondispatchable_techs(technology_list):
    """
    Parameters
    ----------
    technology_list : list of :class:`osier.Technology` objects
        The list of technologies.
    """

    dispatchable_techs = [t for t in technology_list if not t.dispatchable]

    return dispatchable_techs    


def get_dispatchable_names(technology_list):
    """
    Parameters
    ----------
    technology_list : list of :class:`osier.Technology` objects
        The list of technologies.
    """

    dispatchable_techs = [t.technology_name for t in technology_list if t.dispatchable]

    return dispatchable_techs


def annualized_capital_cost(technology_list, dispatch_model=None):
    """
    Parameters
    ----------
    technology_list : list of :class:`osier.Technology` objects
        The list of technologies.
    dispatch_model : :class:`osier.DispatchModel`
        A _solved_ dispatch model (i.e. with model results and objective
        attributes).
    """
    capital_cost = np.array([t.total_capital_cost / t.lifetime 
                            for t in technology_list]).sum()

    return capital_cost


def annualized_fixed_cost(technology_list, dispatch_model=None):
    """
    Parameters
    ----------
    technology_list : list of :class:`osier.Technology` objects
        The list of technologies.
    dispatch_model : :class:`osier.DispatchModel`
        A _solved_ dispatch model (i.e. with model results and objective
        attributes).
    """
    fixed_cost = np.array([t.annual_fixed_cost
                            for t in technology_list]).sum()

    return fixed_cost


def annual_co2(technology_list, solved_dispatch_model, emission='co2'):
    """
    Parameters
    ----------
    technology_list : list of :class:`osier.Technology` objects
        The list of technologies.
    solved_dispatch_model : :class:`osier.DispatchModel`
        A _solved_ dispatch model (i.e. with model results and objective
        attributes).
    """
    
    dispatch_techs = get_dispatchable_techs(technology_list)
    non_dispatch_techs = get_nondispatchable_techs(technology_list)
    column_names = get_tech_names(technology_list)
    dispatch_results = solved_dispatch_model.results

    emissions = np.array([getattr(t, emission) 
                         for t in dispatch_techs+non_dispatch_techs 
                         if hasattr(t,emission)])

    emissions_total = np.dot(emissions, dispatch_results[column_names].values.T).sum()

    return emissions_total


def total_cost(technology_list, solved_dispatch_model):
    """
    This function calculates the total system cost for a given 
    set of technologies and their corresponding dispatch.
    
    Parameters
    ----------
    technology_list : list of :class:`osier.Technology` objects
        The list of technologies.
    solved_dispatch_model : :class:`osier.DispatchModel`
        A _solved_ dispatch model (i.e. with model results and objective
        attributes).

    Returns
    -------
    total_cost : float
        The total system cost.
    """

    capital_cost = annualized_capital_cost(technology_list)
    fixed_cost = annualized_fixed_cost(technology_list)
    variable_cost = solved_dispatch_model.objective
    total_cost = capital_cost + fixed_cost + variable_cost

    return total_cost

