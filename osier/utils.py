from osier import Technology
from osier.technology import _validate_unit
from unyt import unit_object
import copy
from typing import Iterable
import pandas as pd

from osier.technology import Technology


def synchronize_units(tech_list: Iterable[Technology],
                      unit_power: unit_object,
                      unit_time: unit_object) -> Iterable[Technology]:
    """
    This function ensures that all objects in the technology list
    have units consistent with the model's units. An
    :class:`osier.Technology` object (or sub-classes) have three
    unit settings.

        * :attr:`unit_power`
        * :attr:`unit_time`
        * :attr:`unit_energy`

    Only the :attr:`unit_power` and :attr:`unit_time` attributes can
    be specified with this function to prevent inconsistent units.
    E.g. Setting the :attr:`unit_energy` to ``MWh`` even though time
    is in minutes and power is in ``kW``.

    .. note::
        The objects in the original list are copied by default. This
        may result in slower run time.

    Parameters
    ----------
    tech_list : list of :class:`osier.Technology` objects
        The list of technology objects whose units need to be
        synchronized.

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
    Returns a list of :class:`osier.Technology` objects 
    where :attr:`dispatchable` is `True`.

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
    Returns a list of :class:`osier.Technology` objects 
    where :attr:`dispatchable` is `False`.

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
    Returns a list of :class:`osier.Technology` name strings
    where :attr:`dispatchable` is `True`.

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


def technology_dataframe(technology_list, cast_to_string=True):
    """
    Returns a :class:`pandas.DataFrame` with a complete set
    of data for a given technology list.

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
    

