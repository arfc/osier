import pytest
import unyt
from unyt import MW, hr
from osier import Technology

TECH_NAME = "PlanetExpress"
PLANET_EXPRESS = Technology(TECH_NAME)

class TestTechnology():

    def test_initialize(self):
        assert PLANET_EXPRESS.technology_name == TECH_NAME
        assert PLANET_EXPRESS.capacity == 0.0
        assert PLANET_EXPRESS.capital_cost == 0.0
        assert PLANET_EXPRESS.om_cost_fixed == 0.0
        assert PLANET_EXPRESS.om_cost_variable == 0.0
        assert PLANET_EXPRESS.fuel_cost == 0.0
        assert PLANET_EXPRESS.unit_power == MW
        assert PLANET_EXPRESS.unit_time == hr
        assert PLANET_EXPRESS.unit_energy == MW*hr
    
    def test_attribute_types(self):
        assert type(PLANET_EXPRESS.capacity) == unyt.array.unyt_quantity
        assert type(PLANET_EXPRESS.capital_cost) == unyt.array.unyt_quantity
        assert type(PLANET_EXPRESS.om_cost_fixed) == unyt.array.unyt_quantity
        assert type(PLANET_EXPRESS.om_cost_variable) == unyt.array.unyt_quantity
        assert type(PLANET_EXPRESS.fuel_cost) == unyt.array.unyt_quantity
        assert type(PLANET_EXPRESS.unit_power) == unyt.unit_object.Unit
        assert type(PLANET_EXPRESS.unit_energy) == unyt.unit_object.Unit
        assert type(PLANET_EXPRESS.unit_time) == unyt.unit_object.Unit

    