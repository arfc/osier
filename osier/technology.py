import unyt
from unyt import MW, kW, hr
from unyt import unyt_quantity
from unyt.exceptions import UnitParseError, UnitConversionError

import numpy as np


_dim_opts = {'time': hr,
             'power': MW,
             'energy': MW * hr,
             'spec_time': hr**-1,
             'spec_power': MW**-1,
             'spec_energy': (MW * hr)**-1}


def _validate_unit(value, dimension):
    """
    This function checks that a unit has the correct
    dimensions. Used in :class:`Technology` to set
    units.

    Parameters
    ----------
    value : string, float, int, or :class:`unyt.unit_object.Unit`
        The value being tested. Should be a unit symbol.
    dimension : string
        The expected dimensions of `value`.
        Currently accepts: ['time', 'energy', 'power', 'spec_power', 'spec_energy'].

    Returns
    -------
    valid_unit : :class:`unyt.unit_object.Unit`
        The validated unit.
    """
    try:
        exp_dim = _dim_opts[dimension]
    except KeyError:
        raise KeyError(f"Key <{dimension}> not accepted. Try: {_dim_opts}")

    valid_unit = None
    if isinstance(value, unyt.unit_object.Unit):
        assert value.same_dimensions_as(exp_dim)
        valid_unit = value
    elif isinstance(value, str):
        try:
            unit = unyt_quantity.from_string(value).units
            assert unit.same_dimensions_as(exp_dim)
            valid_unit = unit
        except UnitParseError:
            raise UnitParseError(f"Could not interpret <{value}>.")
        except AssertionError:
            raise AssertionError(f"{value} lacks units of {dimension}.")
    else:
        raise ValueError(f"Value of type <{type(value)}> passed.")

    return valid_unit


def _validate_quantity(value, dimension):
    """
    This function checks that a quantity has the correct
    dimensions. Used in :class:`Technology` to set
    data attributess.

    Parameters
    ----------
    value : string, float, int, or :class:`unyt.unyt_quantity`
        The value being tested. Should be something like

        >>> _validate_quantity("10 MW", dimension='power')
        unyt_quantity(10., 'MW')

    dimension : string
        The expected dimensions of `value`.
        Currently accepts: ['time', 'energy', 'power', 'spec_power', 'spec_energy'].

    Returns
    -------
    valid_quantity : :class:`unyt.unyt_quantity`
        The validated quantity.
    """
    try:
        exp_dim = _dim_opts[dimension]
    except KeyError:
        raise KeyError(f"Key <{dimension}> not accepted. Try: {_dim_opts}")

    valid_quantity = None
    if isinstance(value, unyt_quantity):
        try:
            valid_quantity = value.to(exp_dim)
        except UnitConversionError:
            raise TypeError(f"Cannot convert {value.units} to {exp_dim}")
    elif isinstance(value, float):
        valid_quantity = value * exp_dim
    elif isinstance(value, int):
        valid_quantity = value * exp_dim
    elif isinstance(value, str):
        try:
            valid_quantity = float(value) * exp_dim
        except ValueError:
            try:
                unyt_value = unyt_quantity.from_string(value)
                assert unyt_value.units.same_dimensions_as(exp_dim)
                valid_quantity = unyt_value
            except UnitParseError:
                raise UnitParseError(f"Could not interpret <{value}>.")
            except AssertionError:
                raise AssertionError(f"{value} lacks units of {dimension}.")
    else:
        raise ValueError(f"Value of type <{type(value)}> passed.")
    return valid_quantity


class Technology(object):
    """
    The :class:`Technology` base class contains the minimum required
    data to solve an energy systems problem. All other technologies in
    :mod:`osier` inherit from this class.

    Parameters
    ----------
    technology_name : str
        The name identifier of the technology.
    technology_type : str
        The string identifier for the type of technology.
        Two common types are: ["production", "storage"].
    technology_category : str
        The string identifier the the technology category.
        For example: "renewable," "fossil," or "nuclear."
    dispatchable : bool
        Indicates whether the technology can be dispatched by a
        grid operator, or if it produces variable electricity
        that must be used or stored the moment it is produced.
        For example, solar panels and wind turbines are not
        dispatchable, but nuclear and biopower are dispatchable.
        Default value is true.
    renewable : bool
        Indicates whether the technology is considered "renewable."
        Useful for determining if a technology will contribute to
        a renewable portfolio standard (RPS).
    capital_cost : float or :class:`unyt.array.unyt_quantity`
        Specifies the capital cost. If float,
        the default unit is $/MW.
    om_cost_fixed : float or :class:`unyt.array.unyt_quantity`
        Specifies the fixed operating costs.
        If float, the default unit is $/MW.
    om_cost_variable : float or :class:`unyt.array.unyt_quantity`
        Specifies the variable operating costs.
        If float, the default unit is $/MWh.
    fuel_cost : float or :class:`unyt.array.unyt_quantity`
        Specifies the fuel costs.
        If float, the default unit is $/MWh.
    fuel_type : str
        Specifies the type of fuel consumed by the technology.
    capacity : float or :class:`unyt.array.unyt_quantity`
        Specifies the technology capacity.
        If float, the default unit is MW
    efficiency : float
        The technology's energy conversion efficiency expressed as
        a fraction. Default is 1.0.
    default_power_units : str or :class:`unyt.unit_object.Unit`
        An optional parameter, specifies the units
        for power. Default is megawatts [MW].
    default_time_units : str or :class:`unyt.unit_object.Unit`
        An optional parameter, specifies the units
        for time. Default is hours [hr].
    default_energy_units : str or :class:`unyt.unit_object.Unit`
        An optional parameter, specifies the units
        for energy. Default is megawatt-hours [MWh]
        Currently, `default_energy_units` is derived from the
        time and power units.

    Notes
    -----
    Cost values are listed in the docs as [$ / physical unit]. However,
    :class:`osier` does not currently have a currency handler, therefore the
    units are technically [1 / physical unit].

    The :class:`unyt` library may not be able to interpret strings for
    inverse units. For example:

    >>> my_unit = "10 / MW"
    >>> my_unit = unyt_quantity.from_string(my_unit)
    ValueError: Received invalid quantity expression '10/MW'.

    Instead, try the more explicit approach:

    >>> my_unit = "10 MW**-1"
    >>> my_unit = unyt_quantity.from_string(my_unit)
    unyt_quantity(10., '1/MW')

    However, inverse MWh cannot be converted from a string.
    """

    def __init__(self,
                 technology_name,
                 technology_type='production',
                 technology_category='base',
                 dispatchable=True,
                 renewable=False,
                 capital_cost=0.0,
                 om_cost_fixed=0.0,
                 om_cost_variable=0.0,
                 fuel_cost=0.0,
                 fuel_type=None,
                 capacity=0.0,
                 efficiency=1.0,
                 default_power_units=MW,
                 default_time_units=hr,
                 default_energy_units=None) -> None:

        self.technology_name = technology_name
        self.technology_type = technology_type
        self.technology_category = technology_category
        self.dispatchable = dispatchable
        self.renewable = renewable
        self.fuel_type = fuel_type

        self.unit_power = default_power_units
        self.unit_time = default_time_units
        self.unit_energy = default_energy_units

        self.capacity = capacity
        self.efficiency = efficiency
        self.capital_cost = capital_cost
        self.om_cost_fixed = om_cost_fixed
        self.om_cost_variable = om_cost_variable
        self.fuel_cost = fuel_cost

    @property
    def unit_power(self):
        return self._unit_power

    @unit_power.setter
    def unit_power(self, value):
        self._unit_power = _validate_unit(value, dimension="power")

    @property
    def unit_time(self):
        return self._unit_time

    @unit_time.setter
    def unit_time(self, value):
        self._unit_time = _validate_unit(value, dimension="time")

    @property
    def unit_energy(self):
        return self._unit_power * self._unit_time

    @unit_energy.setter
    def unit_energy(self, value):
        self._unit_energy = self._unit_power * self._unit_time

    @property
    def capacity(self):
        return self._capacity.to(self._unit_power)

    @capacity.setter
    def capacity(self, value):
        valid_quantity = _validate_quantity(value, dimension="power")
        self._capacity = valid_quantity.to(self._unit_power)

    @property
    def capital_cost(self):
        return self._capital_cost.to(self._unit_power**-1)

    @capital_cost.setter
    def capital_cost(self, value):
        self._capital_cost = _validate_quantity(value, dimension="spec_power")

    @property
    def om_cost_fixed(self):
        return self._om_cost_fixed.to(self._unit_power**-1)

    @om_cost_fixed.setter
    def om_cost_fixed(self, value):
        self._om_cost_fixed = _validate_quantity(value, dimension="spec_power")

    @property
    def om_cost_variable(self):
        return self._om_cost_variable.to(self.unit_energy**-1)

    @om_cost_variable.setter
    def om_cost_variable(self, value):
        self._om_cost_variable = _validate_quantity(
            value, dimension="spec_energy")

    @property
    def fuel_cost(self):
        return self._fuel_cost.to(self.unit_energy**-1)

    @fuel_cost.setter
    def fuel_cost(self, value):
        self._fuel_cost = _validate_quantity(value, dimension="spec_energy")

    @property
    def total_capital_cost(self):
        return self.capacity * self.capital_cost

    @property
    def annual_fixed_cost(self):
        return self.capacity * self.om_cost_fixed

    @property
    def variable_cost(self):
        return self.fuel_cost + self.om_cost_variable

    def variable_cost_ts(self, size):
        """
        Returns the total variable cost as a time series of
        length :attr:`size`.

        .. warning::
            The current implementation assumes a single constant cost
            for the variable cost. In the future, users will be able to
            pass their own time series data.

        Parameters
        ----------
        size : int
            The number of periods, i.e. length, of the
            time series.

        Returns
        -------
        var_cost_ts : :class:`numpy.ndarray`
            The variable cost time series.
        """
        var_cost_ts = np.ones(size) * self.variable_cost
        return var_cost_ts


class RampingTechnology(Technology):
    """
    The :class:`RampingTechnology` class extends the :class:`Technology`
    class by adding ramping attributes that correspond to a technology's
    ability to increase or decrease its power level a specified rate.

    Parameters
    ----------
    ramp_up_rate : float, :class:`unyt_quantity`
        The rate at which a technology can increase its power, expressed as
        a percentage of its capacity. For example, if `ramp_up` equals 0.5,
        then the technology may ramp up its power level by 50% per unit time.
        The default is 1.0 (i.e. there is no constraint on ramping up).

    ramp_down_rate : float, :class:`unyt_quantity`
        The rate at which a technology can decrease its power, expressed as
        a percentage of its capacity. For example, if `ramp_down` equals 0.5,
        then the technology may ramp down its power level by 50% per unit time.
        The default is 1.0 (i.e. there is no constraint on ramping down).


    Notes
    -----
    It is common for a ramping technology to have different ramp up and ramp
    down rates. Consider a light-water nuclear reactor that can quickly reduce
    its power level by inserting control rods, but must wait much longer to
    increase its power by the same amount due to a build up of neutron
    absorbing isotopes.
    """

    def __init__(
            self,
            technology_name,
            technology_type='production',
            technology_category='ramping',
            dispatchable=True,
            renewable=False,
            capital_cost=0,
            om_cost_fixed=0,
            om_cost_variable=0,
            fuel_cost=0,
            fuel_type=None,
            capacity=0,
            efficiency=1.0,
            default_power_units=MW,
            default_time_units=hr,
            default_energy_units=None,
            ramp_up_rate=1.0 * hr**-1,
            ramp_down_rate=1.0 * hr**-1) -> None:
        super().__init__(
            technology_name,
            technology_type,
            technology_category,
            dispatchable,
            renewable,
            capital_cost,
            om_cost_fixed,
            om_cost_variable,
            fuel_cost,
            fuel_type,
            capacity,
            efficiency,
            default_power_units,
            default_time_units,
            default_energy_units)

        self.ramp_up_rate = _validate_quantity(ramp_up_rate,
                                               dimension='spec_time')
        self.ramp_down_rate = _validate_quantity(ramp_down_rate,
                                                 dimension='spec_time')

    @property
    def ramp_up(self):
        return (
            self.capacity *
            self.ramp_up_rate).to(
            self.unit_power *
            self.unit_time**-1
        )

    @property
    def ramp_down(self):
        return (
            self.capacity *
            self.ramp_down_rate).to(
            self.unit_power *
            self.unit_time**-1
        )


class StorageTechnology(Technology):
    """
    The :class:`StorageTechnology` extends the :class:`Technology` by
    adding storage parameters.

    Parameters
    ----------
    energy_capacity : float, :class:`unyt.array.unyt_quantity`
        The maximum amount of energy storable by the technology.
    initial_storage : float, :class:`unyt.array.unyt_quantity`
        The initial stored energy. Cannot exceed :attr:`energy_capacity`.
    """

    def __init__(
            self,
            technology_name,
            technology_type='production',
            technology_category='storage',
            dispatchable=True,
            renewable=False,
            capital_cost=0,
            om_cost_fixed=0,
            om_cost_variable=0,
            fuel_cost=0,
            fuel_type=None,
            capacity=0,
            efficiency=1.0,
            energy_capacity=0,
            initial_storage=0,
            default_power_units=MW,
            default_time_units=hr,
            default_energy_units=None) -> None:
        super().__init__(
            technology_name,
            technology_type,
            technology_category,
            dispatchable,
            renewable,
            capital_cost,
            om_cost_fixed,
            om_cost_variable,
            fuel_cost,
            fuel_type,
            capacity,
            efficiency,
            default_power_units,
            default_time_units,
            default_energy_units)

        self.energy_capacity = energy_capacity
        self.initial_storage = initial_storage

    @property
    def energy_capacity(self):
        return self._energy_capacity
    
    @energy_capacity.setter
    def energy_capacity(self, value):
        valid_quantity = _validate_quantity(value, dimension='energy')
        self._energy_capacity = valid_quantity

    @property
    def initial_storage(self):
        return self._initial_storage
    
    @initial_storage.setter
    def initial_storage(self, value):
        valid_quantity = _validate_quantity(value, dimension='energy')
        self._initial_storage = valid_quantity


class ThermalTechnology(RampingTechnology):
    """
    The :class:`ThermalTechnology` class extends the :class:`RampingTechnology`
    class by adding a heat rate.

    Parameters
    ----------
    heat_rate : int, float
        The heat rate of a given technology.
    """

    def __init__(
            self,
            technology_name,
            technology_type='production',
            technology_category='thermal',
            dispatchable=True,
            renewable=False,
            capital_cost=0,
            om_cost_fixed=0,
            om_cost_variable=0,
            fuel_cost=0,
            fuel_type=None,
            capacity=0,
            efficiency=1.0,
            default_power_units=MW,
            default_time_units=hr,
            default_energy_units=None,
            heat_rate=None,
            ramp_up_rate=1.0 * hr**-1,
            ramp_down_rate=1.0 * hr**-1) -> None:
        super().__init__(
            technology_name,
            technology_type,
            technology_category,
            dispatchable,
            renewable,
            capital_cost,
            om_cost_fixed,
            om_cost_variable,
            fuel_cost,
            fuel_type,
            capacity,
            efficiency,
            default_power_units,
            default_time_units,
            default_energy_units,
            ramp_up_rate,
            ramp_down_rate)

        self.heat_rate = heat_rate
