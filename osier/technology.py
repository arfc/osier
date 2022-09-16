import unyt
from unyt import MW, hr
from unyt import unyt_quantity
from unyt.exceptions import UnitParseError


class Technology(object):
    """
    Parameters
    ----------
    technology_name : string
        The name identifier of the technology.
    technology_type : string
        The string identifier for the type of technology.
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
    capacity : float or :class:`unyt.array.unyt_quantity`
        Specifies the technology capacity.
        If float, the default unit is MW
    default_power_units : str or :class:`unyt.unit_object.Unit`
        An optional parameter, specifies the units
        for power. Default is megawatts [MW].
    default_time_units : str or :class:`unyt.unit_object.Unit`
        An optional parameter, specifies the units 
        for time. Default is hours [hr].
    default_energy_units : str or :class:`unyt.unit_object.Unit`
        An optional parameter, specifies the units 
        for energy. Default is megawatt-hours [MWh]

    Notes
    -----
    Cost values are listed in the docs as [$ / physical unit]. However,
    :class:`osier` does not currently have a currency handler, therefore the 
    units are technically [1 / physical unit].
    """
    
    def __init__(self, 
                technology_name,
                technology_type='base',
                capital_cost = 0.0,
                om_cost_fixed = 0.0,
                om_cost_variable = 0.0,
                fuel_cost = 0.0,
                capacity = 0.0,
                default_power_units = MW,
                default_time_units = hr,
                default_energy_units = MW*hr) -> None:


        self.technology_name = technology_name
        self.technology_type = technology_type
        
        self.unit_power = default_power_units
        self.unit_time = default_time_units
        self.unit_energy = default_energy_units

        self.capacity = capacity
        self.capital_cost = capital_cost
        self.om_cost_fixed = om_cost_fixed
        self.om_cost_variable = om_cost_variable
        self.fuel_cost = fuel_cost


    @property
    def unit_power(self):
        return self._unit_power


    @unit_power.setter
    def unit_power(self, value):
        if isinstance(value, unyt.unit_object.Unit):
            assert value.same_dimensions_as(MW)
            self._unit_power = value
        elif isinstance(value, str):
            try:
                unit = unyt_quantity.from_string(value).units
                assert unit.same_dimensions_as(MW)
                self._unit_power = unit
            except UnitParseError:
                raise UnitParseError(f"Could not interpret <{value}>.")
            except AssertionError:
                    raise AssertionError(f"{value} lacks units of power.")
        else:
            raise ValueError(f"Value of type <{type(value)}> passed.")


    @property
    def unit_time(self):
        return self._unit_time

    @unit_time.setter
    def unit_time(self, value):
        if isinstance(value, unyt.unit_object.Unit):
            assert value.same_dimensions_as(hr)
            self._unit_time = value
        elif isinstance(value, str):
            try:
                unit = unyt_quantity.from_string(value).units
                assert unit.same_dimensions_as(hr)
                self._unit_time = unit
            except UnitParseError:
                raise UnitParseError(f"Could not interpret <{value}>.")
            except AssertionError:
                    raise AssertionError(f"{value} lacks units of time.")
        else:
            raise ValueError(f"Value of type <{type(value)}> passed.")


    @property
    def unit_energy(self):
        return self._unit_energy


    @unit_energy.setter
    def unit_energy(self):
        self._unit_energy = self._unit_power * self._unit_time


    @property
    def capacity(self):
        return self._capacity


    @capacity.setter
    def capacity(self, value):
        if isinstance(value, unyt.array.unyt_quantity):
            self._capacity = value.to(self.unit_power)
        elif isinstance(value, float):
            self._capacity = value * self.unit_power
        elif isinstance(value, int):
            self._capacity = value * self.unit_power
        elif isinstance(value, str):
            try:
                self._capacity = float(value) / self.energy
            except ValueError:
                try:
                    unyt_value = unyt_quantity.from_string(value)
                    assert unyt_value.units.same_dimensions_as(self.unit_energy**-1)
                    self._fuel_cost = unyt_value
                except UnitParseError:
                    raise UnitParseError(f"Could not interpret <{value}>.")
                except AssertionError:
                    raise AssertionError(f"{value} lacks units of energy.")       
        else:
            raise ValueError(f"Value of type <{type(value)}> passed.")


    @property
    def capital_cost(self):
        return self._capital_cost


    @capital_cost.setter
    def capital_cost(self, value):
        if isinstance(value, unyt.array.unyt_quantity):
            self._capital_cost = value.to(1 / self.unit_power)
        elif isinstance(value, float):
            self._capital_cost = value / self.unit_power
        elif isinstance(value, int):
            self._capital_cost = value / self.unit_power
        elif isinstance(value, str):
            try:
                self._capital_cost = float(value) / self.unit_power
            except ValueError:
                try:
                    unyt_value = unyt_quantity.from_string(value)
                    assert unyt_value.units.same_dimensions_as(self.unit_power**-1)
                    self._capital_cost = unyt_value
                except UnitParseError:
                    raise UnitParseError(f"Could not interpret <{value}>.")
                except AssertionError:
                    raise AssertionError(f"{value} lacks units of 1/power.")
        else:
            raise ValueError(f"Value of type <{type(value)}> passed.")


    @property
    def om_cost_fixed(self):
        return self._om_cost_fixed


    @om_cost_fixed.setter
    def om_cost_fixed(self, value):
        if isinstance(value, unyt.array.unyt_quantity):
            self._om_cost_fixed = value.to(1 / self.unit_power)
        elif isinstance(value, float):
            self._om_cost_fixed = value / self.unit_power
        elif isinstance(value, int):
            self._om_cost_fixed = value / self.unit_power
        elif isinstance(value, str):
            try:
                self._om_cost_fixed = float(value) / self.unit_power
            except ValueError:
                try:
                    unyt_value = unyt_quantity.from_string(value)
                    assert unyt_value.units.same_dimensions_as(self.unit_power**-1)
                    self._om_cost_fixed = unyt_value
                except UnitParseError:
                    raise UnitParseError(f"Could not interpret <{value}>.")
                except AssertionError:
                    raise AssertionError(f"{value} lacks units of 1/power.")
        else:
            raise ValueError(f"Value of type <{type(value)}> passed.")


    @property
    def om_cost_variable(self):
        return self._om_cost_variable

    @om_cost_variable.setter
    def om_cost_variable(self, value):
        if isinstance(value, unyt.array.unyt_quantity):
            self._om_cost_variable = value.to(1 / self.unit_energy)
        elif isinstance(value, float):
            self._om_cost_variable = value / self.unit_energy
        elif isinstance(value, int):
            self._om_cost_variable = value / self.unit_energy
        elif isinstance(value, str):
            try:
                self._om_cost_variable = float(value) / self.unit_energy
            except ValueError:
                try:
                    unyt_value = unyt_quantity.from_string(value)
                    assert unyt_value.units.same_dimensions_as(self.unit_energy**-1)
                    self._om_cost_variable = unyt_value
                except UnitParseError:
                    raise UnitParseError(f"Could not interpret <{value}>.")
                except AssertionError:
                    raise AssertionError(f"{value} lacks units of energy.") 
        else:
            raise ValueError(f"Value of type <{type(value)}> passed.")
    

    @property
    def fuel_cost(self):
        return self._fuel_cost


    @fuel_cost.setter
    def fuel_cost(self, value):
        if isinstance(value, unyt.array.unyt_quantity):
            self._fuel_cost = value.to(1 / self.unit_energy)
        elif isinstance(value, float):
            self._fuel_cost = value / self.unit_energy
        elif isinstance(value, int):
            self._fuel_cost = value / self.unit_energy
        elif isinstance(value, str):
            try:
                self._fuel_cost = float(value) / self.unit_energy
            except ValueError:
                try:
                    unyt_value = unyt_quantity.from_string(value)
                    assert unyt_value.units.same_dimensions_as(self.unit_energy**-1)
                    self._fuel_cost = unyt_value
                except UnitParseError:
                    raise UnitParseError(f"Could not interpret <{value}>.")
                except AssertionError:
                    raise AssertionError(f"{value} lacks units of energy.")
        else:
            raise ValueError(f"Value of type <{type(value)}> passed.")