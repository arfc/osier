from osier import Technology
from osier.technology import _validate_unit
from unyt import unit_object
import copy
from typing import Iterable

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
