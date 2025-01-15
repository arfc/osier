import unyt
from unyt import MW, hr, kg, km, m, megatonnes, MWh
from unyt import unyt_quantity, unyt_array
from unyt.exceptions import UnitParseError
from collections import OrderedDict

import numpy as np
import pandas as pd


_dim_opts = {'time': hr,
             'power': MW,
             'energy': MWh,
             'mass': kg,
             'length': km,
             'area': km**2,
             'volume': m**3,
             'specific_time': hr**-1,
             'specific_mass': kg**-1,
             'specific_power': MW**-1,
             'specific_energy': (MWh)**-1,
             'mass_per_energy': megatonnes * (MWh)**-1,
             'area_per_power': km**2 * MW**-1}

_constant_types = (int, float, unyt_quantity)
_array_types = (unyt.unyt_array, pd.core.series.Series, np.ndarray, list)


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
        Accepted values listed in `_dim_opts`.

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
        Accepted values listed in `_dim_opts`.

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
            assert value.units.same_dimensions_as(exp_dim)
            valid_quantity = value
        except AssertionError:
            raise TypeError(
                f"{value} has dimensions {value.units.dimensions}. "
                f"Expected {exp_dim.dimensions}")
    elif isinstance(value, unyt_array):
        try:
            assert value.units.same_dimensions_as(exp_dim)
            valid_quantity = value
        except AssertionError:
            raise TypeError(
                f"{value} has dimensions {value.units.dimensions}. "
                f"Expected {exp_dim.dimensions}")
    elif isinstance(value, np.ndarray):
        valid_quantity = value * exp_dim
    elif isinstance(value, pd.core.series.Series):
        valid_quantity = value.values * exp_dim
    elif isinstance(value, list):
        valid_quantity = np.array(value) * exp_dim
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
    data to solve an energy systems problem. Many optional data are
    included here as well. All other technologies in
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
    om_cost_variable : float, :class:`unyt.array.unyt_quantity`, or array-like
        Specifies the variable operating costs. Users may pass timeseries data.
        However, :class:`pandas.DataFrame` is not supported by this feature.
        If float, the default unit is $/MWh.
    fuel_cost : float, :class:`unyt.array.unyt_quantity`, or array-like
        Specifies the fuel costs. Users may pass timeseries data.
        However, :class:`pandas.DataFrame` is not supported by this feature.
        If float, the default unit is $/MWh.
    fuel_type : str
        Specifies the type of fuel consumed by the technology.
    capacity : float or :class:`unyt.array.unyt_quantity`
        Specifies the technology capacity.
        If float, the default unit is MW
    capacity_factor : Optional, float
        Specifies the 'usable' fraction of a technology's capacity.
        Default is 1.0, i.e. all of the technology's capacity is
        usable all of the time.
    capacity_credit : Optional, float
        Specifies the fraction of a technology's capacity that counts
        towards reliability requirements. Most frequently used for
        renewable technologies. For example, a solar farm might have
        a capacity credit of 0.2. This means that in order to meet a
        capacity requirement of 1 GW, 1.25 GW of solar would need to
        be installed.
        Default is 1.0, i.e. all of the technology's capacity contributes
        to capacity requirements.
    co2_rate : float or :class:`unyt.array.unyt_quantity`
        Specifies the rate at which carbon dioxide is emitted during operation.
        Generally only applicable for fossil fueled plants.
        If float, the default units are megatonnes per MWh
    lifecycle_co2_rate : float or :class:`unyt.array.unyt_quantity`
        Specifies the rate at which of CO2eq emissions over a typical lifetime.
        Unless you are reading this in a future where the economy is fully
        decarbonized, all technologies should have a non-zero value for this
        attribute.
        If float, the default units are megatonnes per MWh
    land_intensity : float or :class:`unyt.array.unyt_quantity`
        The amount of land required per unit capacity. May be either lifecycle
        land use or from direct use. However, consistency between
        technologies is incumbent on the user.
    efficiency : float
        The technology's energy conversion efficiency expressed as
        a fraction. Default is 1.0.
    lifetime : float
        The technology's operational lifetime in years. Default is 25 years.
    default_power_units : str or :class:`unyt.unit_object.Unit`
        An optional parameter, specifies the units
        for power. Default is megawatts [MW].
    default_time_units : str or :class:`unyt.unit_object.Unit`
        An optional parameter, specifies the units
        for time. Default is hours [hr].
    default_mass_units : str or :class:`unyt.unit_object.Unit`
        An optional parameter, specifies the units
        for mass. Default is hours [kg].
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
                 capacity_factor=1.0,
                 capacity_credit=1.0,
                 co2_rate=0.0,
                 lifecycle_co2_rate=0.0,
                 land_intensity=0.0,
                 efficiency=1.0,
                 lifetime=25.0,
                 default_power_units=MW,
                 default_time_units=hr,
                 default_energy_units=None,
                 default_length_units=km,
                 default_volume_units=m**3,
                 default_mass_units=megatonnes) -> None:

        self.technology_name = technology_name
        self.technology_type = technology_type
        self.technology_category = technology_category
        self.dispatchable = dispatchable
        self.renewable = renewable
        self.fuel_type = fuel_type
        self.lifetime = lifetime

        self.unit_power = default_power_units
        self.unit_time = default_time_units
        self.unit_energy = default_energy_units
        self.unit_length = default_length_units
        self.unit_volume = default_volume_units
        self.unit_mass = default_mass_units

        self.capacity = capacity
        self.capacity_factor = capacity_factor
        self.capacity_credit = capacity_credit
        self.efficiency = efficiency
        self.capital_cost = capital_cost
        self.om_cost_fixed = om_cost_fixed
        self.om_cost_variable = om_cost_variable
        self.fuel_cost = fuel_cost
        self.power_level = self.capacity
        self.co2_rate = co2_rate
        self.lifecycle_co2_rate = lifecycle_co2_rate
        self.land_intensity = land_intensity

        self.power_history = []

    def __repr__(self) -> str:
        return (f"{self.technology_name}: {self.capacity}")

    def __eq__(self, tech) -> bool:
        """Test technology equality"""
        if ((self.technology_name == tech.technology_name)
                and (self.capacity == tech.capacity)
                and (self.variable_cost == tech.variable_cost)):
            return True
        else:
            return False

    def __ge__(self, tech) -> bool:
        """Tests greater or equal to."""
        if (self.variable_cost == tech.variable_cost):
            return self.efficiency >= tech.efficiency
        else:
            return self.variable_cost >= tech.variable_cost

    def __le__(self, tech) -> bool:
        """Tests less or equal to."""
        if (self.variable_cost == tech.variable_cost):
            return self.efficiency <= tech.efficiency
        else:
            return self.variable_cost <= tech.variable_cost

    def __lt__(self, tech) -> bool:
        """Tests less than."""
        if (self.variable_cost == tech.variable_cost):
            return self.efficiency < tech.efficiency
        else:
            return self.variable_cost < tech.variable_cost

    def __gt__(self, tech) -> bool:
        """Tests greater than."""

        if (self.variable_cost == tech.variable_cost):
            return self.efficiency > tech.efficiency
        else:
            return self.variable_cost > tech.variable_cost

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
    def unit_mass(self):
        return self._unit_mass

    @unit_mass.setter
    def unit_mass(self, value):
        self._unit_mass = _validate_unit(value, dimension="mass")

    @property
    def unit_length(self):
        return self._unit_length

    @unit_length.setter
    def unit_length(self, value):
        self._unit_length = _validate_unit(value, dimension="length")

    @property
    def unit_area(self):
        return self._unit_length**2

    @unit_area.setter
    def unit_area(self, value):
        self._unit_area = self._unit_length**2

    @property
    def unit_volume(self):
        return self._unit_volume

    @unit_volume.setter
    def unit_volume(self, value):
        self._unit_volume = _validate_unit(value, dimension="volume")

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
        self.power_level = self._capacity

    @property
    def capital_cost(self):
        return self._capital_cost.to(self._unit_power**-1)

    @capital_cost.setter
    def capital_cost(self, value):
        self._capital_cost = _validate_quantity(
            value, dimension="specific_power")

    @property
    def om_cost_fixed(self):
        return self._om_cost_fixed.to(self._unit_power**-1)

    @om_cost_fixed.setter
    def om_cost_fixed(self, value):
        self._om_cost_fixed = _validate_quantity(
            value, dimension="specific_power")

    @property
    def om_cost_variable(self):
        if isinstance(self._om_cost_variable, _constant_types):
            return self._om_cost_variable.to(self.unit_energy**-1)
        elif isinstance(self._om_cost_variable, _array_types):
            if isinstance(self._om_cost_variable, unyt.unyt_array):
                return self._om_cost_variable.to(self.unit_energy**-1)
            else:
                return np.array(self._om_cost_variable) * \
                    (self.unit_energy**-1)

    @om_cost_variable.setter
    def om_cost_variable(self, value):
        self._om_cost_variable = _validate_quantity(
            value, dimension="specific_energy")

    @property
    def fuel_cost(self):
        if isinstance(self._fuel_cost, _constant_types):
            return self._fuel_cost.to(self.unit_energy**-1)
        elif isinstance(self._fuel_cost, _array_types):
            if isinstance(self._fuel_cost, unyt.unyt_array):
                return self._fuel_cost.to(self.unit_energy**-1)
            else:
                return np.array(self._fuel_cost) * (self.unit_energy**-1)

    @fuel_cost.setter
    def fuel_cost(self, value):
        self._fuel_cost = _validate_quantity(
            value, dimension="specific_energy")

    @property
    def co2_rate(self):
        return self._co2_rate.to(self.unit_mass * self.unit_energy**-1)

    @co2_rate.setter
    def co2_rate(self, value):
        self._co2_rate = _validate_quantity(value, dimension="mass_per_energy")

    @property
    def lifecycle_co2_rate(self):
        return self._lifecycle_co2_rate.to(
            self.unit_mass * self.unit_energy**-1)

    @lifecycle_co2_rate.setter
    def lifecycle_co2_rate(self, value):
        self._lifecycle_co2_rate = _validate_quantity(
            value, dimension="mass_per_energy")

    @property
    def land_intensity(self):
        return self._land_intensity.to(self.unit_area * self.unit_power**-1)

    @land_intensity.setter
    def land_intensity(self, value):
        self._land_intensity = _validate_quantity(
            value, dimension="area_per_power")

    @property
    def total_capital_cost(self):
        return self.capacity * self.capital_cost

    @property
    def annual_fixed_cost(self):
        return self.capacity * self.om_cost_fixed

    @property
    def variable_cost(self):
        """
        Combines the fuel and variable operating costs into a total variable cost
        associated with technology usage.

        Notes
        -----
        This function will attempt to merge the two values, even if they have
        different sizes and types. Therefore it is recommended that users
        pass values of the same size and type to prevent unexpected behavior.
        """
        if (isinstance(self.fuel_cost, _constant_types)
                and isinstance(self.om_cost_variable, _constant_types)):
            return self.fuel_cost + self.om_cost_variable
        elif (isinstance(self.fuel_cost, _array_types) and isinstance(self.om_cost_variable, _constant_types)):
            return self.fuel_cost + \
                np.ones(len(self.fuel_cost)) * self.om_cost_variable
        elif (isinstance(self.fuel_cost, _constant_types) and isinstance(self.om_cost_variable, _array_types)):
            return self.fuel_cost * \
                np.ones(len(self.om_cost_variable)) + self.om_cost_variable
        elif (isinstance(self.fuel_cost, _constant_types) and isinstance(self.om_cost_variable, _array_types)):
            return self.fuel_cost * \
                np.ones(len(self.om_cost_variable)) + self.om_cost_variable
        elif (isinstance(self.fuel_cost, _array_types) and isinstance(self.om_cost_variable, _array_types)):
            min_len = min(len(self.fuel_cost), len(self.om_cost_variable))
            return self.fuel_cost[:min_len] + self.om_cost_variable[:min_len]
        else:
            raise TypeError(
                f"Fuel cost has type <{type(self.fuel_cost)}>.\n" +
                f"OM variable cost has type <{type(self.om_cost_variable)}>.\n"
                "One or both of these types are unknown.")

    def variable_cost_ts(self, size):
        """
        Returns the total variable cost as an array of
        length :attr:`size`.

        .. warning::
            The current implementation will only select the
            first N values, where N = `size`. It is recommended
            that users only pass the subset of data they wish
            to use.

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
        if isinstance(self.variable_cost, _constant_types):
            var_cost_ts = np.ones(size) * self.variable_cost
            return var_cost_ts

        elif isinstance(self.variable_cost, _array_types):
            try:
                var_cost_ts = self.variable_cost[:size]
                assert len(var_cost_ts) == size
            except AssertionError as e:
                raise AssertionError(
                    f"Variable cost data too short ({len(var_cost_ts)} < {size})")
            return var_cost_ts

    def to_dataframe(self, cast_to_string=True):
        """
        Writes all technology attributes to a :class:`pandas.DataFrame` for export
        and manipulation.
        """

        tech_data = OrderedDict()
        tech_data['technology_name'] = [self.technology_name]
        tech_data['technology_category'] = [self.technology_category]
        tech_data['technology_type'] = [self.technology_type]
        tech_data['dispatchable'] = [str(self.dispatchable)]
        tech_data['renewable'] = [str(self.renewable)]
        tech_data['fuel_type'] = [str(self.fuel_type)]

        for key, value in self.__dict__.items():
            if key in tech_data:
                continue
            elif value is None:
                col = key.strip('_')
                tech_data[col] = [str(value)]
            else:
                if isinstance(value, unyt.unit_object.Unit):
                    continue
                elif isinstance(value, unyt_quantity):
                    col = f"{key.strip('_')} ({value.units})"
                    if cast_to_string:
                        tech_data[col] = ["{:.3g}".format(value.to_value())]
                    else:
                        tech_data[col] = [np.round(value.to_value(), 10)]
                elif isinstance(value, (int, float)):
                    col = key.strip('_')
                    if cast_to_string:
                        tech_data[col] = ["{:.3g}".format(value)]
                    else:
                        tech_data[col] = [np.round(value, 10)]
                else:
                    continue

        tech_dataframe = pd.DataFrame(tech_data).set_index('technology_name')

        return tech_dataframe

    def reset_history(self):
        """
        Resets the technology's power history for a new simulation.
        """
        self.power_history = []
        self.power_level = self.capacity

    def power_output(self,
                     demand: unyt_quantity,
                     **kwargs):
        """
        Raise or lower the power level to meet demand. Returns
        current power level and appends to power history.

        Parameters
        ----------
        demand : :class:`unyt.unyt_quantity`
            The demand at a particular timestep. Must be a :class:`unyt.unyt_quantity`
            to avoid ambiguity.
        
        Returns
        -------
        power_level : :class:`unyt.unyt_quantity`
            The current power level of the technology.
        """
        assert isinstance(demand, unyt_quantity)
        self.power_level = max(0 * demand.units, min(demand, self.capacity))
        self.power_history.append(self.power_level.copy())
        return self.power_level


class RampingTechnology(Technology):
    """
    The :class:`RampingTechnology` class extends the :class:`Technology`
    class by adding ramping attributes that correspond to a technology's
    ability to increase or decrease its power level at a specified rate.

    Parameters
    ----------
    ramp_up_rate : float or :class:`unyt_quantity`
        The rate at which a technology can increase its power, expressed as
        a percentage of its capacity. For example, if `ramp_up_rate` equals 0.5,
        then the technology may ramp up its power level by 50% per unit time.
        The default is 1.0 (i.e. there is no constraint on ramping up).

    ramp_down_rate : float or :class:`unyt_quantity`
        The rate at which a technology can decrease its power, expressed as
        a percentage of its capacity. For example, if `ramp_down_rate` equals 0.5,
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
            technology_type='production',
            technology_category='ramping',
            ramp_up_rate=1.0 * hr**-1,
            ramp_down_rate=1.0 * hr**-1,
            *args,
            **kwargs) -> None:
        self.ramp_up_rate = _validate_quantity(ramp_up_rate,
                                               dimension='specific_time')
        self.ramp_down_rate = _validate_quantity(ramp_down_rate,
                                                 dimension='specific_time')
        super().__init__(technology_type=technology_type,
                         technology_category=technology_category,
                         *args, **kwargs)

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

    def max_power(self, time_delta: unyt_quantity = 1 * hr):
        """
        Calculates the maximum achievable power for a technology
        in the next timestep.

        Parameters
        ----------
        time_delta : :class:`unyt.unyt_quantity`
            The difference between two timesteps. Default is one hour.

        Returns
        -------
        max_power : :class:`unyt.unyt_quantity`
            The maximum achievable power level.
        """

        output = self.power_level + self.ramp_up * time_delta
        return min(self.capacity, output)

    def min_power(self, time_delta: unyt_quantity = 1 * hr):
        """
        Calculates the minimum achievable power for a technology
        in the next timestep.

        Parameters
        ----------
        time_delta : :class:`unyt.unyt_quantity`
            The difference between two timesteps. Default is one hour.

        Returns
        -------
        min_power : :class:`unyt.unyt_quantity`
            The minimum achievable power level.
        """

        output = self.power_level - self.ramp_down * time_delta
        return max(0 * self.unit_power, output)

    def power_output(self,
                     demand: unyt_quantity,
                     time_delta: unyt_quantity = 1 * hr):
        """
        Raise or lower the power level to meet demand. Returns
        current power level and appends to power history.
        Checks if the power level can be achieved given the
        technology's ramp rate.

        Parameters
        ----------
        demand : :class:`unyt.unyt_quantity`
            The demand at a particular timestep. Must be a :class:`unyt.unyt_quantity`
            to avoid ambiguity.
        time_delta : :class:`unyt.unyt_quantity`
            The difference between two timesteps. Default is one hour.

        Returns
        -------
        power_level : :class:`unyt.unyt_quantity`
            The current power level of the technology.
        """

        assert isinstance(demand, unyt_quantity)
        if self.power_level > demand:  # power must be lowered
            self.power_level = max(
                self.min_power(time_delta),
                demand).to(
                demand.units)
        elif (self.power_level <= demand) and \
             (self.capacity >= demand):  # power must be raised
            self.power_level = (min(self.max_power(time_delta),
                                    demand)).to(demand.units)
        elif (self.power_level <= demand) and \
             (self.capacity <= demand):
            self.power_level = self.max_power(time_delta).to(demand.units)

        self.power_history.append(self.power_level)
        return self.power_level


class ThermalTechnology(RampingTechnology):
    """
    The :class:`ThermalTechnology` class extends the :class:`RampingTechnology`
    class by adding a heat rate.

    Parameters
    ----------
    heat_rate : int or float
        The heat rate of a given technology.
    """

    def __init__(
            self,
            heat_rate=None,
            technology_type='production',
            technology_category='thermal',
            *args,
            **kwargs) -> None:
        super().__init__(technology_type=technology_type,
                         technology_category=technology_category,
                         *args, **kwargs)

        self.heat_rate = heat_rate
        self.power_level = self.capacity


class StorageTechnology(Technology):
    """
    The :class:`StorageTechnology` extends the :class:`Technology` by
    adding storage parameters.

    Parameters
    ----------
    storage_duration : float or :class:`unyt.array.unyt_quantity`
        The amount of time the battery could discharge continuously when full.
        Used to calculate the storage capacity.
    initial_storage : float or :class:`unyt.array.unyt_quantity`
        The initial stored energy. Cannot exceed :attr:`storage_capacity`.
    """

    def __init__(
            self,
            technology_type='storage',
            storage_duration=0,
            initial_storage=0,
            *args,
            **kwargs) -> None:
        super().__init__(technology_type=technology_type,
                         *args, **kwargs)

        self.storage_duration = storage_duration
        self.initial_storage = initial_storage
        self.storage_level = self.initial_storage
        self.storage_history = []
        self.charge_history = []

    @property
    def storage_duration(self):
        return self._storage_duration

    @storage_duration.setter
    def storage_duration(self, value):
        valid_quantity = _validate_quantity(value, dimension='time')
        self._storage_duration = valid_quantity

    @property
    def storage_capacity(self):
        return self._storage_duration * self._capacity

    @property
    def initial_storage(self):
        return self._initial_storage

    @initial_storage.setter
    def initial_storage(self, value):
        valid_quantity = _validate_quantity(value, dimension='energy')
        try:
            assert valid_quantity <= self.storage_capacity
        except AssertionError:
            raise AssertionError("Initial storage exceeds storage capacity.")

        self._initial_storage = valid_quantity
        self.storage_level = valid_quantity

    @property
    def max_rate(self):
        return self.capacity * self.unit_time

    def reset_history(self):
        """
        Resets the technology's power history for a new simulation.
        """
        self.storage_history = []
        self.storage_level = self._initial_storage
        self.power_history = []
        self.power_level = self.capacity
        self.charge_history = []

    def discharge(self, demand: unyt_quantity, time_delta=1 * hr):
        """
        Discharges the battery if there is a surplus of energy.

        Parameters
        ----------
        demand : :class:`unyt.unyt_quantity`
            Amount of surplus.
        time_delta : :class:`unyt.unyt_quantity`
            The real time passed between modeled timesteps.

        Returns
        -------
        power_level : :class:`unyt.unyt_quantity`
            The current power level of the technology.
        """
        # check that the battery has power to discharge fully.
        power_out = max(0 * demand.units, min(demand, self.capacity))

        # check that the battery has enough energy to meet demand.
        energy_out = min(power_out * time_delta, self.storage_level)

        out = self.storage_level - energy_out
        self.storage_level = out
        self.storage_history.append(out)
        self.power_level = energy_out / time_delta
        self.power_history.append(self.power_level)
        self.charge_history.append(0 * demand.units)
        return self.power_level.to(demand.units)

    def charge(self, surplus, time_delta=1 * hr):
        """
        Charges the battery if there is a surplus of energy.

        Parameters
        ----------
        surplus : :class:`unyt.unyt_quantity`
            Amount of surplus.
        time_delta : :class:`unyt.unyt_quantity`
            The real time passed between modeled timesteps.

        Returns
        -------
        power_level : :class:`unyt.unyt_quantity`
            The current power level of the technology.
        """
        # check that the battery has enough power to consume surplus.
        power_in = min(np.abs(min(0 * surplus.units, surplus)), self.capacity)

        # check that the battery has enough space to store surplus.
        energy_in = min((self.storage_capacity - self.storage_level),
                        power_in * time_delta)

        out = self.storage_level + energy_in
        self.storage_level = out
        self.storage_history.append(out)
        self.power_level = -energy_in / time_delta
        self.charge_history.append(self.power_level)
        self.power_history.append(0 * surplus.units)
        return self.power_level.to(surplus.units)

    def power_output(self, v, time_delta=1 * hr):
        """
        Calculates the power output given a demand value.
        
        Parameters
        ----------
        v : :class:`unyt.unyt_quantity`
            Voltage representing a demand or a surplus of energy.
        time_delta : :class:`unyt.unyt_quantity`
            The real time passed between modeled timesteps.
        
        Returns
        -------
        output : :class:`unyt.unyt_quantity`
            The current power level of the technology.
        """
        if v >= 0:
            output = self.discharge(demand=v, time_delta=time_delta)
        else:
            output = self.charge(surplus=v, time_delta=time_delta)
        return output
