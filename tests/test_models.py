from osier import DispatchModel
from osier import Technology, ThermalTechnology
from unyt import unyt_array
import numpy as np
import pytest
import sys

if "win32" in sys.platform:
    solver = 'cplex'
elif "linux" in sys.platform:
    solver = "cbc"

TOL = 1e-5

@pytest.fixture
def technology_set_1():
    """
    This fixture uses creates technologies directly from
    the :class:`Technology` class.
    """
    nuclear = Technology(technology_name='Nuclear',
                         technology_type='production',
                         capacity=1e3,
                         capital_cost=6,
                         om_cost_variable=20,
                         om_cost_fixed=50,
                         fuel_cost=5
                         )
    natural_gas = Technology(technology_name='NaturalGas',
                             technology_type='production',
                             capacity=1e3,
                             capital_cost=1,
                             om_cost_variable=12,
                             om_cost_fixed=30,
                             fuel_cost=20
                             )

    return [nuclear, natural_gas]

@pytest.fixture
def technology_set_2():
    """
    This fixture uses creates technologies from
    the :class:`ThermalTechnology` subclass.
    """
    nuclear = ThermalTechnology(technology_name='Nuclear',
                         capacity=1e3,
                         capital_cost=6,
                         om_cost_variable=20,
                         om_cost_fixed=50,
                         fuel_cost=5,
                         ramp_up=0.5,
                         ramp_down=0.75,
                         )
    natural_gas = ThermalTechnology(technology_name='NaturalGas',
                             capacity=1e3,
                             capital_cost=1,
                             om_cost_variable=12,
                             om_cost_fixed=30,
                             fuel_cost=20,
                             ramp_up=0.9,
                             ramp_down=0.9,
                             )

    return [nuclear, natural_gas]


@pytest.fixture
def net_demand():
    n_hours = 24
    np.random.seed(123)
    x = np.arange(0, n_hours, 1)
    y = np.sin(8 * x * np.pi / 180) + \
        np.random.normal(loc=0, scale=0.1, size=n_hours)
    y[y < 0] = 0
    return y


def test_dispatch_model_initialize(technology_set_1, net_demand):
    """
    Tests that the dispatch model is properly initialized.
    """
    model = DispatchModel(technology_set_1,
                          net_demand=net_demand,
                          solver=solver)
    assert model.technology_list == technology_set_1
    assert model.tech_set == [t.technology_name for t in technology_set_1]
    assert model.solver == solver
    assert len(model.capacity_dict) == len(technology_set_1)
    assert len(model.indices) == len(net_demand) * len(technology_set_1)


def test_dispatch_model_solve_case1(technology_set_1, net_demand):
    """
    Tests that the dispatch model produces expected results.
    """
    model = DispatchModel(technology_set_1,
                          net_demand=net_demand,
                          solver=solver)
    model.solve()
    cheapest_tech = unyt_array([t.variable_cost for t in technology_set_1]).min()
    expected_result = cheapest_tech * net_demand.sum()

    assert model.objective == pytest.approx(expected_result, TOL)
    assert model.results['Nuclear'].sum() == pytest.approx(net_demand.sum(), TOL)
    assert model.results['NaturalGas'].sum() == pytest.approx(0.0, TOL)


def test_dispatch_model_solve_case2(technology_set_2, net_demand):
    """
    Tests that the dispatch model produces expected results.
    """
    model = DispatchModel(technology_set_2,
                          net_demand=net_demand,
                          solver=solver)
    model.solve()
    print(model.objective)
    # cheapest_tech = unyt_array([t.variable_cost for t in technology_set_2]).min()
    # expected_result = cheapest_tech * net_demand.sum()

    # assert model.objective == pytest.approx(expected_result, TOL)
    # assert model.results['Nuclear'].sum() == pytest.approx(net_demand.sum(), TOL)
    # assert model.results['NaturalGas'].sum() == pytest.approx(0.0, TOL)
