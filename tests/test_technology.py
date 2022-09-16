from pickletools import pystring
import pytest
import unyt
from unyt import MW, hr, BTU, Horsepower, day
from osier import Technology
from unyt.exceptions import UnitParseError

TECH_NAME = "PlanetExpress"
PLANET_EXPRESS = Technology(TECH_NAME)

energy_unyt = 10.0 * MW * hr
other_energy_unyt = 10.0 * BTU
spec_energy_unyt = 10.0 * (MW * hr)**-1
power_unyt = 10.0 * MW
spec_power_unyt = 10.0 * MW**-1
other_power_unyt = Horsepower
time_unyt = 1 * hr
float_val = 10.0
int_val = 10
str_val = "10"
energy_str = "10 MW*hr"
spec_energy_str = "10 (MW*hr)**-1"
power_str = "10 MW"
spec_power_str = "10 MW**-1"
time_str = "10 hr"
unknown_str = "10 fortnights"
dict_type = {"value": 10,
             "unit": MW}


def test_initialize():
    assert PLANET_EXPRESS.technology_name == TECH_NAME
    assert PLANET_EXPRESS.technology_type == 'base'
    assert PLANET_EXPRESS.capacity == 0.0
    assert PLANET_EXPRESS.capital_cost == 0.0
    assert PLANET_EXPRESS.om_cost_fixed == 0.0
    assert PLANET_EXPRESS.om_cost_variable == 0.0
    assert PLANET_EXPRESS.fuel_cost == 0.0
    assert PLANET_EXPRESS.unit_power == MW
    assert PLANET_EXPRESS.unit_time == hr
    assert PLANET_EXPRESS.unit_energy == MW * hr


def test_attribute_types():
    assert isinstance(PLANET_EXPRESS.capacity, unyt.array.unyt_quantity)
    assert isinstance(PLANET_EXPRESS.capital_cost, unyt.array.unyt_quantity)
    assert isinstance(PLANET_EXPRESS.om_cost_fixed, unyt.array.unyt_quantity)
    assert isinstance(PLANET_EXPRESS.om_cost_variable, unyt.array.unyt_quantity)
    assert isinstance(PLANET_EXPRESS.fuel_cost, unyt.array.unyt_quantity)
    assert isinstance(PLANET_EXPRESS.unit_power, unyt.unit_object.Unit)
    assert isinstance(PLANET_EXPRESS.unit_energy, unyt.unit_object.Unit)
    assert isinstance(PLANET_EXPRESS.unit_time, unyt.unit_object.Unit)


def test_capacity():
    with pytest.raises(ValueError) as e:
        PLANET_EXPRESS.capacity = dict_type
    with pytest.raises(UnitParseError) as e:
        PLANET_EXPRESS.capacity = unknown_str
    with pytest.raises(AssertionError) as e:
        PLANET_EXPRESS.capacity = energy_str

    PLANET_EXPRESS.capacity = power_unyt
    assert PLANET_EXPRESS.capacity.value == 10.0
    assert PLANET_EXPRESS.capacity.units == MW

    PLANET_EXPRESS.capacity = power_str
    assert PLANET_EXPRESS.capacity.value == 10.0
    assert PLANET_EXPRESS.capacity.units == MW

    PLANET_EXPRESS.capacity = int_val
    assert PLANET_EXPRESS.capacity.value == 10
    assert PLANET_EXPRESS.capacity.units == MW

    PLANET_EXPRESS.capacity = str_val
    assert PLANET_EXPRESS.capacity.value == 10.0
    assert PLANET_EXPRESS.capacity.units == MW

    PLANET_EXPRESS.capacity = float_val * other_power_unyt
    assert PLANET_EXPRESS.capacity.value == pytest.approx(0.007457, 0.005)
    assert PLANET_EXPRESS.capacity.units == MW


def test_capital_cost():
    with pytest.raises(ValueError) as e:
        PLANET_EXPRESS.capital_cost = dict_type
    with pytest.raises(UnitParseError) as e:
        PLANET_EXPRESS.capital_cost = unknown_str
    with pytest.raises(AssertionError) as e:
        PLANET_EXPRESS.capital_cost = energy_str

    PLANET_EXPRESS.capital_cost = spec_power_unyt
    assert PLANET_EXPRESS.capital_cost.value == 10.0
    assert PLANET_EXPRESS.capital_cost.units == MW**-1

    PLANET_EXPRESS.capital_cost = spec_power_str
    assert PLANET_EXPRESS.capital_cost.value == 10.0
    assert PLANET_EXPRESS.capital_cost.units == MW**-1

    PLANET_EXPRESS.capital_cost = int_val
    assert PLANET_EXPRESS.capital_cost.value == 10
    assert PLANET_EXPRESS.capital_cost.units == MW**-1

    PLANET_EXPRESS.capital_cost = str_val
    assert PLANET_EXPRESS.capital_cost.value == 10.0
    assert PLANET_EXPRESS.capital_cost.units == MW**-1

    PLANET_EXPRESS.capital_cost = float_val / other_power_unyt
    assert PLANET_EXPRESS.capital_cost.value == pytest.approx(13410.220, 0.005)
    assert PLANET_EXPRESS.capital_cost.units == MW**-1


def test_om_cost_fixed():
    with pytest.raises(ValueError) as e:
        PLANET_EXPRESS.om_cost_fixed = dict_type
    with pytest.raises(UnitParseError) as e:
        PLANET_EXPRESS.om_cost_fixed = unknown_str
    with pytest.raises(AssertionError) as e:
        PLANET_EXPRESS.om_cost_fixed = energy_str

    PLANET_EXPRESS.om_cost_fixed = spec_power_unyt
    assert PLANET_EXPRESS.om_cost_fixed.value == 10.0
    assert PLANET_EXPRESS.om_cost_fixed.units == MW**-1

    PLANET_EXPRESS.om_cost_fixed = spec_power_str
    assert PLANET_EXPRESS.om_cost_fixed.value == 10.0
    assert PLANET_EXPRESS.om_cost_fixed.units == MW**-1

    PLANET_EXPRESS.om_cost_fixed = int_val
    assert PLANET_EXPRESS.om_cost_fixed.value == 10
    assert PLANET_EXPRESS.om_cost_fixed.units == MW**-1

    PLANET_EXPRESS.om_cost_fixed = str_val
    assert PLANET_EXPRESS.om_cost_fixed.value == 10.0
    assert PLANET_EXPRESS.om_cost_fixed.units == MW**-1

    PLANET_EXPRESS.om_cost_fixed = float_val / other_power_unyt
    assert PLANET_EXPRESS.om_cost_fixed.value == pytest.approx(13410.220, 0.005)
    assert PLANET_EXPRESS.om_cost_fixed.units == MW**-1


def test_om_cost_variable():
    with pytest.raises(ValueError) as e:
        PLANET_EXPRESS.om_cost_variable = dict_type
    with pytest.raises(UnitParseError) as e:
        PLANET_EXPRESS.om_cost_variable = unknown_str
    with pytest.raises(AssertionError) as e:
        PLANET_EXPRESS.om_cost_variable = power_str
    with pytest.raises(ValueError) as e:
        PLANET_EXPRESS.om_cost_variable = spec_energy_str
    # assert PLANET_EXPRESS.om_cost_variable.value == 10.0
    # assert PLANET_EXPRESS.om_cost_variable.units == (MW*hr)**-1

    PLANET_EXPRESS.om_cost_variable = spec_energy_unyt
    assert PLANET_EXPRESS.om_cost_variable.value == 10.0
    assert PLANET_EXPRESS.om_cost_variable.units == (MW * hr)**-1

    PLANET_EXPRESS.om_cost_variable = int_val
    assert PLANET_EXPRESS.om_cost_variable.value == 10
    assert PLANET_EXPRESS.om_cost_variable.units == (MW * hr)**-1

    PLANET_EXPRESS.om_cost_variable = str_val
    assert PLANET_EXPRESS.om_cost_variable.value == 10.0
    assert PLANET_EXPRESS.om_cost_variable.units == (MW * hr)**-1

    PLANET_EXPRESS.om_cost_variable = float_val / other_energy_unyt
    assert PLANET_EXPRESS.om_cost_variable.value == pytest.approx(
        3412141.5, 0.5)
    assert PLANET_EXPRESS.om_cost_variable.units == (MW * hr)**-1


def test_fuel_cost():
    with pytest.raises(ValueError) as e:
        PLANET_EXPRESS.fuel_cost = dict_type
    with pytest.raises(UnitParseError) as e:
        PLANET_EXPRESS.fuel_cost = unknown_str
    with pytest.raises(AssertionError) as e:
        PLANET_EXPRESS.fuel_cost = power_str
    with pytest.raises(ValueError) as e:
        PLANET_EXPRESS.fuel_cost = spec_energy_str
        # assert PLANET_EXPRESS.fuel_cost.value == 10.0
        # assert PLANET_EXPRESS.fuel_cost.units == (MW*hr)**-1

    PLANET_EXPRESS.fuel_cost = spec_energy_unyt
    assert PLANET_EXPRESS.fuel_cost.value == 10.0
    assert PLANET_EXPRESS.fuel_cost.units == (MW * hr)**-1

    PLANET_EXPRESS.fuel_cost = int_val
    assert PLANET_EXPRESS.fuel_cost.value == 10
    assert PLANET_EXPRESS.fuel_cost.units == (MW * hr)**-1

    PLANET_EXPRESS.fuel_cost = str_val
    assert PLANET_EXPRESS.fuel_cost.value == 10.0
    assert PLANET_EXPRESS.fuel_cost.units == (MW * hr)**-1

    PLANET_EXPRESS.fuel_cost = float_val / other_energy_unyt
    assert PLANET_EXPRESS.fuel_cost.value == pytest.approx(
        3412141.47989694, 0.5)
    assert PLANET_EXPRESS.fuel_cost.units == (MW * hr)**-1


def test_unit_power():
    with pytest.raises(UnitParseError) as e:
        PLANET_EXPRESS.unit_power = "darkmatter"
    with pytest.raises(AssertionError) as e:
        PLANET_EXPRESS.unit_power = BTU
    with pytest.raises(AssertionError) as e:
        PLANET_EXPRESS.unit_power = "BTU"
    with pytest.raises(ValueError) as e:
        PLANET_EXPRESS.unit_power = 10
    PLANET_EXPRESS.unit_power = Horsepower
    assert PLANET_EXPRESS.unit_power == Horsepower

    PLANET_EXPRESS.unit_power = "Horsepower"
    assert PLANET_EXPRESS.unit_power == Horsepower


def test_unit_time():
    with pytest.raises(UnitParseError) as e:
        PLANET_EXPRESS.unit_time = "darkmatter"
    with pytest.raises(AssertionError) as e:
        PLANET_EXPRESS.unit_time = MW
    with pytest.raises(AssertionError) as e:
        PLANET_EXPRESS.unit_time = "MW"
    with pytest.raises(ValueError) as e:
        PLANET_EXPRESS.unit_time = 10
    PLANET_EXPRESS.unit_time = day
    assert PLANET_EXPRESS.unit_time == day
    
    PLANET_EXPRESS.unit_time = "day"
    assert PLANET_EXPRESS.unit_time == day


def test_unit_energy():
    with pytest.raises(UnitParseError) as e:
        PLANET_EXPRESS.unit_energy = "darkmatter"
    with pytest.raises(AssertionError) as e:
        PLANET_EXPRESS.unit_energy = MW
    with pytest.raises(AssertionError) as e:
        PLANET_EXPRESS.unit_energy = "MW"
    with pytest.raises(ValueError) as e:
        PLANET_EXPRESS.unit_energy = 10
    PLANET_EXPRESS.unit_energy = Horsepower*day
    assert PLANET_EXPRESS.unit_energy == Horsepower*day

    PLANET_EXPRESS.unit_energy = "Horsepower*day"
    assert PLANET_EXPRESS.unit_energy == Horsepower*day

    

