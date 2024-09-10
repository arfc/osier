from osier.equations import (annualized_capital_cost, annualized_fixed_cost, total_cost, 
                             annual_emission, objective_from_energy, objective_from_capacity)
from osier import Technology, DispatchModel
import numpy as np
import pytest
import sys
import functools

if "win32" in sys.platform:
    solver = 'cbc'
elif "linux" in sys.platform:
    solver = "cbc"
else:
    solver = "cbc"

TOL = 1e-5
N_HOURS = 24
N_DAYS = 2
N = N_HOURS * N_DAYS


@pytest.fixture(scope="session")
def technology_set_1():
    """
    This fixture creates technologies directly from
    the :class:`Technology` class.
    """
    nuclear = Technology(technology_name='Nuclear',
                         technology_type='production',
                         capacity=5,
                         capital_cost=6,
                         om_cost_variable=20,
                         om_cost_fixed=50,
                         fuel_cost=5
                         )
    natural_gas = Technology(technology_name='NaturalGas',
                             technology_type='production',
                             capacity=5,
                             capital_cost=1,
                             om_cost_variable=12,
                             om_cost_fixed=30,
                             fuel_cost=20
                             )

    nuclear.co2_rate = 1.2e-5
    natural_gas.co2_rate = 4.9e-4

    return [nuclear, natural_gas]

@pytest.fixture
def net_demand():

    phase_shift = 0
    base_load = 1.5
    hours = np.linspace(0, N, N)
    demand = (np.sin((hours * np.pi / N_HOURS * 2 + phase_shift))
              * -1 + np.ones(N) * (base_load + 1))

    return demand


def test_annualized_capital_cost(technology_set_1):
    """
    Tests the annualized capital cost is calculated correctly.
    """
    nuclear, natural_gas = technology_set_1

    expected = (nuclear.total_capital_cost / nuclear.lifetime) \
               + (natural_gas.total_capital_cost / natural_gas.lifetime)
    actual = annualized_capital_cost(technology_list=technology_set_1)

    assert expected == pytest.approx(actual)


def test_annualized_fixed_cost(technology_set_1):
    """
    Tests the annualized fixed cost is calculated correctly.
    """
    nuclear, natural_gas = technology_set_1

    expected = (nuclear.annual_fixed_cost) + (natural_gas.annual_fixed_cost)
    actual = annualized_fixed_cost(technology_list=technology_set_1)

    assert expected == pytest.approx(actual)


def test_total_cost(technology_set_1, net_demand):
    """
    Tests that :func:`total_cost` produces expected results.
    """
    model = DispatchModel(technology_set_1,
                          net_demand=net_demand,
                          solver=solver,
                          curtailment=False,
                          allow_blackout=False)
    model.solve()

    expected = annualized_fixed_cost(technology_set_1) \
                + annualized_capital_cost(technology_set_1) \
                + model.objective
    actual = total_cost(technology_set_1, model)

    assert expected == pytest.approx(actual)


def test_annual_co2(technology_set_1, net_demand):
    """
    Tests that :func:`annual_co2` produces expected results.
    """
    nuclear, natural_gas = technology_set_1
    model = DispatchModel(technology_set_1,
                          net_demand=net_demand,
                          solver=solver,
                          curtailment=False,
                          allow_blackout=False)
    model.solve()

    expected = (model.results["Nuclear"].sum() * nuclear.co2_rate) \
                + (model.results["NaturalGas"].sum() * natural_gas.co2_rate)
    actual = annual_emission(technology_set_1, model, emission='co2_rate')

    assert expected == pytest.approx(actual)


def test_objective_from_capacity(technology_set_1, net_demand):
    """
    Tests that :func:`objective_from_capacity` produces expected results.
    """
    model = DispatchModel(technology_set_1,
                          net_demand=net_demand,
                          solver=solver,
                          curtailment=False,
                          allow_blackout=False)
    model.solve()

    func = functools.partial(objective_from_capacity, attribute='om_cost_fixed')
    expected = annualized_fixed_cost(technology_set_1, model)
    actual = func(technology_list=technology_set_1, 
                  solved_dispatch_model=model)

    assert expected == pytest.approx(actual)


def test_objective_from_energy(technology_set_1, net_demand):
    """
    Tests that :func:`objective_from_energy` produces expected results.
    """
    model = DispatchModel(technology_set_1,
                          net_demand=net_demand,
                          solver=solver,
                          curtailment=False,
                          allow_blackout=False)
    model.solve()

    func = functools.partial(objective_from_energy, attribute='co2_rate')
    expected = annual_emission(technology_set_1, model, emission='co2_rate')
    actual = func(technology_list=technology_set_1, 
                  solved_dispatch_model=model)

    assert expected == pytest.approx(actual)