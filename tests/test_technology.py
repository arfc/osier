import pytest
import unyt
import numpy as np
import pandas as pd
import osier
from unyt import kW, MW, hr, BTU, Horsepower, day, kg, GW, megatonnes, MWh
from osier import Technology
from osier.technology import _validate_unit, _validate_quantity
from unyt.exceptions import UnitParseError
from osier.tech_library import *

TECH_NAME = "PlanetExpress"
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
mass_energy_str = "kg*BTU**-1"
spec_energy_str = "10 (MW*hr)**-1"
power_str = "10 MW"
spec_power_str = "10 MW**-1"
time_str = "10 hr"
unknown_str = "10 fortnights"
dict_type = {"value": 10,
             "unit": MW}
time_series_list = list(range(10))
time_series_np = np.array(time_series_list)
time_series_pd = pd.Series(time_series_list)
time_series_unyt = np.array(time_series_list) * time_unyt


@pytest.fixture
def advanced_tech():
    PLANET_EXPRESS = Technology(TECH_NAME)
    return PLANET_EXPRESS


def test_validate_unit():
    assert _validate_unit("MW", 'power').same_dimensions_as(Horsepower)
    assert _validate_unit("BTU", 'energy').same_dimensions_as(MW * hr)
    assert _validate_unit("day", 'time').same_dimensions_as(hr)
    assert _validate_unit(
        mass_energy_str,
        'mass_per_energy').same_dimensions_as(
        kg * BTU**-1)
    assert _validate_unit(
        "Horsepower**-1",
        'specific_power').same_dimensions_as(
        MW**-1)
    assert _validate_unit(
        (Horsepower * day)**-1,
        'specific_energy').same_dimensions_as(
        (MW * hr)**-1)

    with pytest.raises(UnitParseError) as e:
        _validate_unit("darkmatter", "energy")

    with pytest.raises(KeyError) as e:
        _validate_unit("darkmatter", "fuel")


def test_validate_quantity():
    assert _validate_quantity(power_unyt, 'power') == 10 * (MW)
    assert _validate_quantity(energy_unyt, 'energy') == 10 * (MW * hr)
    assert _validate_quantity(time_unyt, 'time') == 1 * (hr)
    assert _validate_quantity("10 Horsepower**-1",
                              'specific_power') == 10 * (Horsepower**-1)
    assert _validate_quantity(10 * (Horsepower * day)**-1,
                              'specific_energy') == 10 * ((Horsepower * day)**-1)

    with pytest.raises(TypeError) as e:
        _validate_quantity(10 * MW, "energy")
    with pytest.raises(UnitParseError) as e:
        _validate_quantity("10 darkmatter", "energy")

    with pytest.raises(KeyError) as e:
        _validate_quantity("10 darkmatter", "fuel")


def test_validate_quantity_time_series():
    assert (
        _validate_quantity(
            time_series_list,
            'time') == time_series_unyt).all()
    assert (
        _validate_quantity(
            time_series_np,
            'time') == time_series_unyt).all()
    assert (
        _validate_quantity(
            time_series_pd,
            'time') == time_series_unyt).all()
    assert (
        _validate_quantity(
            time_series_unyt,
            'time') == time_series_unyt).all()


def test_initialize(advanced_tech):
    assert advanced_tech.technology_name == TECH_NAME
    assert advanced_tech.technology_type == 'production'
    assert advanced_tech.technology_category == 'base'
    assert advanced_tech.capacity == 0.0
    assert advanced_tech.capital_cost == 0.0
    assert advanced_tech.om_cost_fixed == 0.0
    assert advanced_tech.om_cost_variable == 0.0
    assert advanced_tech.fuel_cost == 0.0
    assert advanced_tech.unit_power == MW
    assert advanced_tech.unit_time == hr
    assert advanced_tech.unit_energy == MW * hr
    assert advanced_tech.unit_mass == megatonnes
    assert advanced_tech.annual_fixed_cost == 0.0
    assert advanced_tech.total_capital_cost == 0.0
    assert advanced_tech.efficiency == 1.0


def test_total_capital_cost(advanced_tech):
    advanced_tech.capital_cost = spec_power_unyt
    advanced_tech.capacity = power_unyt
    assert advanced_tech.total_capital_cost == 100

    advanced_tech.capacity = 0.5 * power_unyt
    assert advanced_tech.total_capital_cost == 50


def test_variable_cost(advanced_tech):
    advanced_tech.fuel_cost = spec_energy_unyt
    advanced_tech.om_cost_variable = spec_energy_unyt
    assert advanced_tech.variable_cost == 2 * spec_energy_unyt


def test_attribute_types(advanced_tech):
    assert isinstance(advanced_tech.capacity, unyt.array.unyt_quantity)
    assert isinstance(advanced_tech.capital_cost, unyt.array.unyt_quantity)
    assert isinstance(advanced_tech.om_cost_fixed, unyt.array.unyt_quantity)
    assert isinstance(advanced_tech.om_cost_variable, unyt.array.unyt_quantity)
    assert isinstance(advanced_tech.fuel_cost, unyt.array.unyt_quantity)
    assert isinstance(advanced_tech.co2_rate, unyt.array.unyt_quantity)
    assert isinstance(advanced_tech.unit_power, unyt.unit_object.Unit)
    assert isinstance(advanced_tech.unit_energy, unyt.unit_object.Unit)
    assert isinstance(advanced_tech.unit_time, unyt.unit_object.Unit)
    assert isinstance(advanced_tech.unit_mass, unyt.unit_object.Unit)


def test_capacity(advanced_tech):
    with pytest.raises(ValueError) as e:
        advanced_tech.capacity = dict_type
    with pytest.raises(UnitParseError) as e:
        advanced_tech.capacity = unknown_str
    with pytest.raises(AssertionError) as e:
        advanced_tech.capacity = energy_str

    advanced_tech.capacity = power_unyt
    assert advanced_tech.capacity.value == 10.0
    assert advanced_tech.capacity.units == MW

    advanced_tech.capacity = power_str
    assert advanced_tech.capacity.value == 10.0
    assert advanced_tech.capacity.units == MW

    advanced_tech.capacity = int_val
    assert advanced_tech.capacity.value == 10
    assert advanced_tech.capacity.units == MW

    advanced_tech.capacity = str_val
    assert advanced_tech.capacity.value == 10.0
    assert advanced_tech.capacity.units == MW

    advanced_tech.capacity = float_val * other_power_unyt
    assert advanced_tech.capacity.value == pytest.approx(0.007457, 0.005)
    assert advanced_tech.capacity.units == MW

    advanced_tech.unit_power = "kW"
    assert advanced_tech.capacity.units == kW


def test_capital_cost(advanced_tech):
    with pytest.raises(ValueError) as e:
        advanced_tech.capital_cost = dict_type
    with pytest.raises(UnitParseError) as e:
        advanced_tech.capital_cost = unknown_str
    with pytest.raises(AssertionError) as e:
        advanced_tech.capital_cost = energy_str

    advanced_tech.capital_cost = spec_power_unyt
    assert advanced_tech.capital_cost.value == 10.0
    assert advanced_tech.capital_cost.units == MW**-1

    advanced_tech.capital_cost = spec_power_str
    assert advanced_tech.capital_cost.value == 10.0
    assert advanced_tech.capital_cost.units == MW**-1

    advanced_tech.capital_cost = int_val
    assert advanced_tech.capital_cost.value == 10
    assert advanced_tech.capital_cost.units == MW**-1

    advanced_tech.capital_cost = str_val
    assert advanced_tech.capital_cost.value == 10.0
    assert advanced_tech.capital_cost.units == MW**-1

    advanced_tech.capital_cost = float_val / other_power_unyt
    assert advanced_tech.capital_cost.value == pytest.approx(13410.220, 0.005)
    assert advanced_tech.capital_cost.units == MW**-1

    advanced_tech.unit_power = "kW"
    assert advanced_tech.capital_cost.units == (kW)**-1


def test_om_cost_fixed(advanced_tech):
    with pytest.raises(ValueError) as e:
        advanced_tech.om_cost_fixed = dict_type
    with pytest.raises(UnitParseError) as e:
        advanced_tech.om_cost_fixed = unknown_str
    with pytest.raises(AssertionError) as e:
        advanced_tech.om_cost_fixed = energy_str

    advanced_tech.om_cost_fixed = spec_power_unyt
    assert advanced_tech.om_cost_fixed.value == 10.0
    assert advanced_tech.om_cost_fixed.units == MW**-1

    advanced_tech.om_cost_fixed = spec_power_str
    assert advanced_tech.om_cost_fixed.value == 10.0
    assert advanced_tech.om_cost_fixed.units == MW**-1

    advanced_tech.om_cost_fixed = int_val
    assert advanced_tech.om_cost_fixed.value == 10
    assert advanced_tech.om_cost_fixed.units == MW**-1

    advanced_tech.om_cost_fixed = str_val
    assert advanced_tech.om_cost_fixed.value == 10.0
    assert advanced_tech.om_cost_fixed.units == MW**-1

    advanced_tech.om_cost_fixed = float_val / other_power_unyt
    assert advanced_tech.om_cost_fixed.value == pytest.approx(13410.220, 0.005)
    assert advanced_tech.om_cost_fixed.units == MW**-1

    advanced_tech.unit_power = "kW"
    assert advanced_tech.om_cost_fixed.units == (kW)**-1


def test_om_cost_variable(advanced_tech):
    with pytest.raises(ValueError) as e:
        advanced_tech.om_cost_variable = dict_type
    with pytest.raises(UnitParseError) as e:
        advanced_tech.om_cost_variable = unknown_str
    with pytest.raises(AssertionError) as e:
        advanced_tech.om_cost_variable = power_str
    with pytest.raises(ValueError) as e:
        advanced_tech.om_cost_variable = spec_energy_str
    assert advanced_tech.om_cost_variable.value == 0.0
    assert advanced_tech.om_cost_variable.units == (MW * hr)**-1

    advanced_tech.om_cost_variable = spec_energy_unyt
    assert advanced_tech.om_cost_variable.value == 10.0
    assert advanced_tech.om_cost_variable.units == (MW * hr)**-1

    advanced_tech.om_cost_variable = int_val
    assert advanced_tech.om_cost_variable.value == 10
    assert advanced_tech.om_cost_variable.units == (MW * hr)**-1

    advanced_tech.om_cost_variable = str_val
    assert advanced_tech.om_cost_variable.value == 10.0
    assert advanced_tech.om_cost_variable.units == (MW * hr)**-1

    advanced_tech.om_cost_variable = float_val / other_energy_unyt
    assert advanced_tech.om_cost_variable.value == pytest.approx(
        3412141.5, 0.5)
    assert advanced_tech.om_cost_variable.units == (MW * hr)**-1

    advanced_tech.unit_power = "kW"
    advanced_tech.unit_time = "day"
    assert advanced_tech.om_cost_variable.units == (kW * day)**-1


def test_fuel_cost(advanced_tech):
    with pytest.raises(ValueError) as e:
        advanced_tech.fuel_cost = dict_type
    with pytest.raises(UnitParseError) as e:
        advanced_tech.fuel_cost = unknown_str
    with pytest.raises(AssertionError) as e:
        advanced_tech.fuel_cost = power_str
    with pytest.raises(ValueError) as e:
        advanced_tech.fuel_cost = spec_energy_str

    advanced_tech.fuel_cost = spec_energy_unyt
    assert advanced_tech.fuel_cost.value == 10.0
    assert advanced_tech.fuel_cost.units == (MW * hr)**-1

    advanced_tech.fuel_cost = int_val
    assert advanced_tech.fuel_cost.value == 10
    assert advanced_tech.fuel_cost.units == (MW * hr)**-1

    advanced_tech.fuel_cost = str_val
    assert advanced_tech.fuel_cost.value == 10.0
    assert advanced_tech.fuel_cost.units == (MW * hr)**-1

    advanced_tech.fuel_cost = float_val / other_energy_unyt
    assert advanced_tech.fuel_cost.value == pytest.approx(
        3412141.47989694, 0.5)
    assert advanced_tech.fuel_cost.units == (MW * hr)**-1

    advanced_tech.unit_power = "kW"
    advanced_tech.unit_time = "day"
    assert advanced_tech.fuel_cost.units == (kW * day)**-1


def test_co2_rate(advanced_tech):
    expected_unit = megatonnes * (MW * hr)**-1
    with pytest.raises(ValueError) as e:
        advanced_tech.co2_rate = dict_type
    with pytest.raises(UnitParseError) as e:
        advanced_tech.co2_rate = unknown_str
    with pytest.raises(AssertionError) as e:
        advanced_tech.co2_rate = power_str
    with pytest.raises(ValueError) as e:
        advanced_tech.co2_rate = spec_energy_str
    assert advanced_tech.co2_rate.value == 0.0
    assert advanced_tech.co2_rate.units == expected_unit

    advanced_tech.co2_rate = megatonnes * spec_energy_unyt
    assert advanced_tech.co2_rate.value == 10.0
    assert advanced_tech.co2_rate.units == expected_unit

    advanced_tech.co2_rate = int_val
    assert advanced_tech.co2_rate.value == 10
    assert advanced_tech.co2_rate.units == expected_unit

    advanced_tech.co2_rate = str_val
    assert advanced_tech.co2_rate.value == 10.0
    assert advanced_tech.co2_rate.units == expected_unit

    advanced_tech.co2_rate = float_val * megatonnes / other_energy_unyt
    assert advanced_tech.co2_rate.value == pytest.approx(
        3412141.5, 0.5)
    assert advanced_tech.co2_rate.units == expected_unit

    advanced_tech.unit_power = "kW"
    advanced_tech.unit_time = "day"
    assert advanced_tech.co2_rate.units == megatonnes * (kW * day)**-1

    advanced_tech.unit_power = "GW"
    advanced_tech.unit_time = "hr"
    advanced_tech.unit_mass = "ton"
    advanced_tech.co2_rate = 1e-2 * megatonnes * (GW * hr)**-1
    assert advanced_tech.co2_rate == pytest.approx(11023.113, 0.1)


def test_unit_power(advanced_tech):
    with pytest.raises(UnitParseError) as e:
        advanced_tech.unit_power = "darkmatter"
    with pytest.raises(AssertionError) as e:
        advanced_tech.unit_power = BTU
    with pytest.raises(AssertionError) as e:
        advanced_tech.unit_power = "BTU"
    with pytest.raises(ValueError) as e:
        advanced_tech.unit_power = 10
    advanced_tech.unit_power = Horsepower
    assert advanced_tech.unit_power == Horsepower

    advanced_tech.unit_power = "Horsepower"
    assert advanced_tech.unit_power == Horsepower


def test_unit_time(advanced_tech):
    with pytest.raises(UnitParseError) as e:
        advanced_tech.unit_time = "darkmatter"
    with pytest.raises(AssertionError) as e:
        advanced_tech.unit_time = MW
    with pytest.raises(AssertionError) as e:
        advanced_tech.unit_time = "MW"
    with pytest.raises(ValueError) as e:
        advanced_tech.unit_time = 10
    advanced_tech.unit_time = day
    assert advanced_tech.unit_time == day

    advanced_tech.unit_time = "day"
    assert advanced_tech.unit_time == day


def test_unit_energy(advanced_tech):
    advanced_tech.unit_energy = "darkmatter"
    assert advanced_tech.unit_energy == MW * hr
    advanced_tech.unit_energy = BTU
    assert advanced_tech.unit_energy == MW * hr
    advanced_tech.unit_energy = "MW"
    assert advanced_tech.unit_energy == MW * hr
    advanced_tech.unit_energy = 10
    assert advanced_tech.unit_energy == MW * hr
    advanced_tech.unit_energy = Horsepower * day
    assert advanced_tech.unit_energy == MW * hr
    advanced_tech.unit_energy = "Horsepower*day"
    assert advanced_tech.unit_energy == MW * hr


def test_comparison_operators(advanced_tech):
    NIMBUS = Technology(technology_name="The Nimbus",
                        om_cost_variable=1.0)

    assert advanced_tech < NIMBUS
    assert advanced_tech <= NIMBUS
    assert NIMBUS >= advanced_tech

    ships = [NIMBUS, advanced_tech]
    ships.sort()

    assert ships == [advanced_tech, NIMBUS]


def test_single_power_output():
    capacity = 18 * GW
    natural_gas.capacity = capacity
    assert natural_gas.capacity == capacity

    demand = 10 * GW
    output = natural_gas.power_output(demand)
    print(output)
    assert output == demand
    assert natural_gas.power_level == demand
    assert len(natural_gas.power_history) == 1

    demand = 17 * GW
    output = natural_gas.power_output(demand)
    assert output == demand
    assert natural_gas.power_level == demand
    assert len(natural_gas.power_history) == 2

    demand = 20 * GW
    output = natural_gas.power_output(demand)
    assert output == capacity
    assert natural_gas.power_level == capacity
    assert len(natural_gas.power_history) == 3


def test_reset_history():
    natural_gas.reset_history()
    assert len(natural_gas.power_history) == 0


def test_multiple_power_output():
    capacity = 18 * GW
    natural_gas.capacity = capacity
    assert natural_gas.capacity == capacity

    demand = np.array([10, 17, 20]) * GW
    output = unyt_array(np.zeros(len(demand))) * demand.units
    expected = unyt_array([demand[0], demand[1], capacity])
    for i, d in enumerate(demand):
        out = natural_gas.power_output(d)
        output[i] = out
    assert np.all(output == expected)
    assert len(natural_gas.power_history) == 3


def test_thermal_power_output():
    capacity = 18 * GW
    ramp_rate = 0.25 * hr**-1
    nuclear_adv.capacity = capacity
    nuclear_adv.ramp_up_rate = ramp_rate
    nuclear_adv.ramp_down_rate = ramp_rate
    assert nuclear_adv.capacity == capacity
    assert nuclear_adv.ramp_up_rate == ramp_rate
    assert nuclear_adv.ramp_down_rate == ramp_rate

    demand = np.array([5, 17, 20]) * GW
    output = unyt_array(np.zeros(len(demand))) * demand.units
    expected = unyt_array([13.5, 17, 18]) * GW
    for i, d in enumerate(demand):
        out = nuclear_adv.power_output(d)
        output[i] = out
    assert np.all(output == expected)
    assert np.all(unyt_array(nuclear_adv.power_history) == expected)


def test_storage_charge():
    capacity = 1e3 * MW
    initial_storage = 100 * MW * hour
    storage_duration = 4 * hour
    battery.capacity = capacity
    battery.initial_storage = initial_storage
    battery.storage_duration = storage_duration
    assert battery.capacity == capacity
    assert battery.storage_capacity == storage_duration * capacity

    # charging
    demand = np.array([-400, -500, -1000, -3500, -1000, -5]) * MW
    for i, d in enumerate(demand):
        battery.charge(d)
    expected_storage = np.array([500, 1000, 2000, 3000, 4000, 4000]) * MWh
    expected_charge = -np.array([400, 500, 1000, 1000, 1000, 0]) * MW
    expected_power = np.zeros(len(demand)) * MW
    assert np.all(battery.storage_history == expected_storage)
    assert np.all(battery.power_history == expected_power)
    assert np.all(battery.charge_history == expected_charge)


def test_storage_power_out():
    # discharging
    demand = np.array([1e3, 1e3, 1e3, 500, 1e3]) * MW
    for i, d in enumerate(demand):
        battery.power_output(d)
    expected_storage = np.array([3000, 2000, 1000, 500, 0.0]) * MWh
    expected_power = np.array([1e3, 1e3, 1e3, 500, 500]) * MW
    print(battery.storage_history[6:])
    print(battery.power_history[6:])
    assert np.all(battery.storage_history[6:] == expected_storage)
    assert np.all(battery.power_history[6:] == expected_power)
