from abc import ABC, abstractmethod
import numpy as np

class OsierEquation(ABC):

    def __init__(self) -> None:
        pass        

    @abstractmethod
    def _do(self, technology_list, X):
        pass


def get_dispatchable_techs(technology_list):
    """
    Parameters
    ----------
    technology_list : list of :class:`osier.Technology` objects
        The list of technologies.
    dispatch_results : :class:`pandas.DataFrame`
        The results dispatch results for each technology in 
        :attr:`technology_list` from a :class:`osier.DispatchModel` run.
    """

    dispatchable_techs = [t for t in technology_list if t.dispatchable]

    return dispatchable_techs


def annualized_capital_cost(technology_list, dispatch_results=None):
    """
    Parameters
    ----------
    technology_list : list of :class:`osier.Technology` objects
        The list of technologies.
    dispatch_results : :class:`pandas.DataFrame`
        The results dispatch results for each technology in 
        :attr:`technology_list` from a :class:`osier.DispatchModel` run.
    """
    capital_cost = np.array([t.total_capital_cost / t.lifetime 
                            for t in technology_list]).sum()

    return capital_cost


def annualized_fixed_cost(technology_list, dispatch_results=None):
    """
    Parameters
    ----------
    technology_list : list of :class:`osier.Technology` objects
        The list of technologies.
    dispatch_results : :class:`pandas.DataFrame`
        The results dispatch results for each technology in 
        :attr:`technology_list` from a :class:`osier.DispatchModel` run.
    """
    fixed_cost = np.array([t.annual_fixed_cost
                            for t in technology_list]).sum()

    return fixed_cost


def annual_emissions(technology_list, dispatch_results, emission='co2'):
    """
    Parameters
    ----------
    technology_list : list of :class:`osier.Technology` objects
        The list of technologies.
    dispatch_results : :class:`pandas.DataFrame`
        The results dispatch results for each technology in 
        :attr:`technology_list` from a :class:`osier.DispatchModel` run.
    """
    
    

    return

def calculate_total_cost(technology_list, dispatch_results):
    """
    This function calculates the total system cost for a given 
    set of technologies and their corresponding dispatch.
    
    Parameters
    ----------
    technology_list : list of :class:`osier.Technology` objects
        The list of technologies.
    dispatch_results : :class:`pandas.DataFrame`
        The results dispatch results for each technology in 
        :attr:`technology_list` from a :class:`osier.DispatchModel` run.
    
    Returns
    -------
    total_cost : float
        The total system cost.
    """

    return

