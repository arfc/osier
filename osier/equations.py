from osier.utils import (get_tech_names, 
                         get_dispatchable_techs, 
                         get_nondispatchable_techs, get_dispatchable_names)
from pyentrp.entropy import weighted_permutation_entropy
from functools import partial
import numpy as np
from unyt import unyt_array


def objective_from_capacity(technology_list,
                            attribute,
                            solved_dispatch_model=None):
    """
    This function calculates a general objective for a given
    set of technologies and their corresponding dispatch on a
    per-unit-capacity basis.

    The general objective function is

    .. math::
        \\mathcal{K} = \\sum_g^G \\textbf{CAP}_g \\kappa_g,

    .. math::
        \\textbf{CAP}_g = \\text{the capacity of the g-th technology}
        \\quad \\left[MW\\right].
        
    .. math::
        \\kappa_g = \\text{the power density of the g-th technology} 
        \\quad \\left[\\frac{-}{MW}\\right].

    .. warning::
        User-defined attributes are not validated by :class:`osier`.
        Verify the units are accurate and uniform across all
        technologies before running a simulation with this function.

    Parameters
    ----------
    technology_list : list of :class:`osier.Technology` objects
        The list of technologies.
    solved_dispatch_model : :class:`osier.DispatchModel`
        A _solved_ dispatch model (i.e. with model results and objective
        attributes).
    attribute : string
        The technology attribute to measure.

    Returns
    -------
    objective_value : float
        The objective value for a particular energy mix.

    Examples
    --------
    The simplest way to employ this function is with `functools.partial`.

    >>> import functools
    >>> from osier import per_unit_capacity
    >>> objectives_list = [functools.partial(objective_from_capacity, attribute='land_use'),
    ...                    functools.partial(objective_from_capacity, attribute='employment')]

    """
    objective_value = np.array([getattr(t, attribute) * t.capacity
                                for t in technology_list
                                if hasattr(t, attribute)]).sum()

    return objective_value


def objective_from_energy(technology_list, attribute, solved_dispatch_model):
    """
    This function calculates a general objective for a given
    set of technologies and their corresponding dispatch on a
    per-unit-energy basis.

    The general objective function is 
     
    .. math::
        \\mathcal{X} = \\sum_g^G \\xi_g \\sum_t^T x_{g,t},
    
    .. math::
        x_{g,t} = \\text{the energy produced by the g-th technology
         at time t}\\quad \\left[MWh\\right]

    .. math::
        \\xi_g = \\text{the energy density of the g-th technology}\\quad
        \\left[\\frac{-}{MWh}\\right].

        
    .. warning::
        User-defined attributes are not validated by :class:`osier`.
        Verify the units are accurate and uniform across all
        technologies before running a simulation with this function.

    Parameters
    ----------
    technology_list : list of :class:`osier.Technology` objects
        The list of technologies.
    solved_dispatch_model : :class:`osier.DispatchModel`
        A _solved_ dispatch model (i.e. with model results and objective
        attributes).
    attribute : string
        The technology attribute to measure.

    Returns
    -------
    objective_value : float
        The objective value for a particular energy mix.

    Examples
    --------
    The simplest way to employ this function is with `functools.partial`.

    >>> import functools
    >>> from osier import per_unit_capacity
    >>> objectives_list = [functools.partial(objective_from_energy, attribute='water_use'),
    ...                    functools.partial(objective_from_energy, attribute='death_rate')]

    """

    valid_techs = [t for t in technology_list if hasattr(t, attribute)]
    column_names = get_tech_names(valid_techs)
    dispatch_results = solved_dispatch_model.results
    power_units = solved_dispatch_model.power_units
    time_delta = solved_dispatch_model.time_delta
    dispatch_values = dispatch_results[column_names].values.T*power_units*time_delta
    
    mass_u = valid_techs[0].unit_mass
    attributes = unyt_array([getattr(t, attribute)
                           for t in valid_techs])
    
    attributes = attributes.to(mass_u*(power_units*time_delta.units)**-1)*time_delta.to_value()

    objective_value = np.dot(
        attributes,
        dispatch_values).sum()
    

    return objective_value.to_value()


def annualized_capital_cost(technology_list, solved_dispatch_model=None):
    """
    This function calculates the annual capital cost for a given
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
    capital_cost : float
        The annual capital cost of the technology set.
    """
    capital_cost = np.array([t.total_capital_cost / t.lifetime
                            for t in technology_list]).sum()

    return capital_cost


def annualized_fixed_cost(technology_list, solved_dispatch_model=None):
    """
    This function calculates the annual fixed cost for a given
    set of technologies.

    Parameters
    ----------
    technology_list : list of :class:`osier.Technology` objects
        The list of technologies.
    solved_dispatch_model : :class:`osier.DispatchModel`
        A _solved_ dispatch model (i.e. with model results and objective
        attributes).

    Returns
    -------
    fixed_cost : float
        The annual fixed cost of the technology set.
    """
    fixed_cost = np.array([t.annual_fixed_cost
                           for t in technology_list]).sum()

    return fixed_cost


def annual_emission(
        technology_list,
        solved_dispatch_model,
        emission='lifecycle_co2_rate'):
    """
    This function calculates the total system co2 emissions for a given
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
    emissions_total : float
        The total emissions of the technology set.
    """

    emissions_total = objective_from_energy(technology_list=technology_list, 
                                            solved_dispatch_model=solved_dispatch_model, 
                                            attribute=emission)

    return emissions_total

annual_co2 = partial(annual_emission, attribute='co2')  # for backwards compatibility

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


def volatility(technology_list,
               solved_dispatch_model,
               attribute='demand',
               m=3,
               tau=60,
               normalize=True):
    """
    This function calculates the volatility of the electricity prices
    or the electricity demand for a dispatch model with weighted 
    permutation entropy.

    Parameters
    ----------
    technology_list : list of :class:`osier.Technology` objects
        The list of technologies.
    solved_dispatch_model : :class:`osier.DispatchModel`
        A _solved_ dispatch model (i.e. with model results and objective
        attributes).
    attribute : {'demand', 'volatility'}
        Indicates whether to calculate the volatility of electricity demand
        or electricity price.
    m : int
        The embedding dimension for the cost time series. Typically
        determined using a false nearest neighbors algorithm.
        The default value is 3.
    tau : int
        The time delay for the cost time series. Typically determined
        by selecting the index of the first or second minimum of the
        time series' delayed mutual information.

    Returns
    -------
    wpe : float
        The weighted permutation entropy of the cost time series.

    Notes
    -----
    Users can modify the parameters for this function using :attr:`functools.partial`.

    >>> import functools
    >>> from osier import volatility
    >>> objectives_list = [functools.partial(volatility, m=4, tau=100)]
    """

    timeseries = {'price':solved_dispatch_model.results.Cost.values,
                  'demand':np.array(solved_dispatch_model.net_demand)}
    wpe = weighted_permutation_entropy(timeseries[attribute],
                                       order=m,
                                       delay=tau,
                                       normalize=normalize)

    return wpe
