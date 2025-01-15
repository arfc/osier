from osier import DispatchModel, LogicDispatchModel
from osier import Technology, ThermalTechnology, StorageTechnology, RampingTechnology
from unyt import unyt_array
import unyt
import numpy as np
import pandas as pd
import pytest
import sys

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

    return [nuclear, natural_gas]


@pytest.fixture
def technology_set_2():
    """
    This fixture creates technologies from
    the :class:`ThermalTechnology` subclass.
    """
    nuclear = ThermalTechnology(technology_name='Nuclear',
                                capacity=5,
                                capital_cost=6,
                                om_cost_variable=20,
                                om_cost_fixed=50,
                                fuel_cost=5,
                                ramp_up_rate=0.0,
                                ramp_down_rate=0.0,
                                )
    natural_gas = RampingTechnology(technology_name='NaturalGas',
                                    capacity=5,
                                    capital_cost=1,
                                    om_cost_variable=12,
                                    om_cost_fixed=30,
                                    fuel_cost=20,
                                    ramp_up_rate=0.9,
                                    ramp_down_rate=0.9,
                                    )

    return [nuclear, natural_gas]


@pytest.fixture
def technology_set_3():
    """
    This fixture creates technologies from
    the :class:`ThermalTechnology` subclass.
    """
    nuclear = ThermalTechnology(technology_name='Nuclear',
                                capacity=5,
                                capital_cost=6,
                                om_cost_variable=20,
                                om_cost_fixed=50,
                                fuel_cost=5,
                                ramp_up_rate=0.05,
                                ramp_down_rate=0.05,
                                )
    natural_gas = ThermalTechnology(technology_name='NaturalGas',
                                    capacity=5,
                                    capital_cost=1,
                                    om_cost_variable=12,
                                    om_cost_fixed=30,
                                    fuel_cost=20,
                                    ramp_up_rate=0.9,
                                    ramp_down_rate=0.9,
                                    )

    return [nuclear, natural_gas]


@pytest.fixture
def technology_set_4():
    """
    This fixture uses creates technologies from
    the :class:`ThermalTechnology` and :class`StorageTechnology`
    subclasses.
    """
    nuclear = ThermalTechnology(technology_name='Nuclear',
                                capacity=5,
                                capital_cost=6,
                                om_cost_variable=20,
                                om_cost_fixed=50,
                                fuel_cost=5,
                                ramp_up_rate=0.0,
                                ramp_down_rate=0.0,
                                )
    battery = StorageTechnology(technology_name='Battery',
                                capacity=5,
                                capital_cost=1,
                                om_cost_variable=0,
                                om_cost_fixed=15,
                                fuel_cost=0,
                                storage_duration=13,
                                efficiency=1.0,
                                initial_storage=24
                                )

    return [nuclear, battery]


@pytest.fixture
def net_demand():

    phase_shift = 0
    base_load = 1.5
    hours = np.linspace(0, N, N)
    demand = (np.sin((hours * np.pi / N_HOURS * 2 + phase_shift))
              * -1 + np.ones(N) * (base_load + 1))

    return demand


def test_dispatch_model_initialize(technology_set_1, net_demand):
    """
    Tests that the dispatch model is properly initialized.
    """
    model = DispatchModel(technology_set_1,
                          net_demand=net_demand,
                          solver=solver,
                          curtailment=False,
                          allow_blackout=False)
    assert model.technology_list == technology_set_1
    assert model.tech_set == [t.technology_name for t in technology_set_1]
    assert model.solver == solver
    assert len(model.capacity_dict) == len(technology_set_1)
    assert len(model.indices) == len(net_demand) * len(technology_set_1)
    assert model.time_delta == 1 * unyt.hour


@pytest.mark.filterwarnings("ignore")
def test_dispatch_model_time_delta(technology_set_1, net_demand):
    """
    Tests that the model properly initializes the time delta attribute.
    """
    t1 = pd.date_range('1/1/2022', '6/1/2022', freq='2D')[:N]
    t2 = pd.date_range('1/1/2022', '3/1/2070', freq='Y')[:N]
    df1 = pd.DataFrame({'data': net_demand}, index=t1)
    df2 = pd.DataFrame({'data': net_demand}, index=t2)

    model1 = DispatchModel(technology_set_1,
                           net_demand=df1,
                           solver=solver)
    model2 = DispatchModel(technology_set_1,
                           net_demand=df2,
                           solver=solver)
    model3 = DispatchModel(technology_set_1,
                           net_demand=net_demand,
                           solver=solver)

    assert model1.time_delta == 2 * unyt.day
    assert model2.time_delta == 1 * unyt.hour

    model3.time_delta = "2 hr"
    assert model3.time_delta == 2 * unyt.hour


def test_dispatch_model_solve_case1(technology_set_1, net_demand):
    """
    Tests that the dispatch model produces expected results. Where all
    the technologies are simply :class:`Technology` objects. The model
    should always choose the cheapest technology, as long as it has
    enough capacity to meet the demand.
    """
    model = DispatchModel(technology_set_1,
                          net_demand=net_demand,
                          solver=solver,
                          curtailment=False,
                          allow_blackout=False)
    model.solve()
    cheapest_tech = unyt_array(
        [t.variable_cost for t in technology_set_1]).min()
    expected_result = cheapest_tech * net_demand.sum()

    assert model.objective == pytest.approx(expected_result, rel=TOL)
    assert model.results['Nuclear'].sum(
    ) == pytest.approx(net_demand.sum(), TOL)
    assert model.results['NaturalGas'].sum() == pytest.approx(0.0, rel=TOL)


def test_dispatch_model_solve_case2(technology_set_2, net_demand):
    """
    Tests that the dispatch model produces expected results. The technologies
    are :class:`ThermalTechnology` objects. In this case, the `Nuclear`
    technology is not allowed to change its power level at all. Therefore
    we expect Nuclear to fulfill a "baseload" role, with all other demand met
    by natural gas.
    """
    nuclear, natgas = technology_set_2
    model = DispatchModel(technology_set_2,
                          net_demand=net_demand,
                          solver=solver,
                          curtailment=False)
    model.solve()
    expected_nuclear = net_demand.min() * np.ones(N)
    expected_natgas = net_demand - expected_nuclear
    expected_result = (expected_nuclear * nuclear.variable_cost
                       + expected_natgas * natgas.variable_cost).sum()
    assert model.objective == pytest.approx(expected_result, rel=TOL)


def test_dispatch_model_solve_case3(technology_set_3, net_demand):
    """
    Tests that a dispatch model with ramping constraints behaves
    as expected.
    """
    nuclear, natgas = technology_set_3
    model = DispatchModel(technology_set_3,
                          net_demand=net_demand,
                          solver=solver,
                          curtailment=False)
    model.solve()
    max_power_delta = ((model.results.Nuclear.diff())
                       / nuclear.capacity.to_value()).max()
    min_power_delta = ((model.results.Nuclear.diff())
                       / nuclear.capacity.to_value()).min()
    assert max_power_delta == pytest.approx(
        nuclear.ramp_up_rate.to_value(), abs=TOL)
    assert min_power_delta == pytest.approx(
        -nuclear.ramp_down_rate.to_value(), abs=TOL)


def test_dispatch_model_solve_case4(technology_set_4, net_demand):
    """
    Tests that storage constraints behave as expected.
    """

    model = DispatchModel(technology_set_4,
                          net_demand=net_demand,
                          solver=solver,
                          curtailment=False)
    model.solve()
    total_gen = model.results[['Nuclear',
                               'Battery',
                               'Battery_charge']].sum().sum()
    binary_charging = np.dot(model.results.Battery,
                             model.results.Battery_charge)
    assert (total_gen - net_demand.sum()) == pytest.approx(0, abs=TOL)
    assert binary_charging == pytest.approx(0, abs=TOL)


def test_dispatch_model_solve_case5(technology_set_4, net_demand):
    """
    Tests that the curtailment technology behaves as expected.
    """

    nuclear, battery = technology_set_4
    model = DispatchModel([nuclear],
                          net_demand=net_demand,
                          solver=solver)
    model.solve()
    total_gen = model.results[['Nuclear',
                               'Curtailment']].sum().sum()
    assert (total_gen - net_demand.sum()) == pytest.approx(0, abs=TOL)


def test_dispatch_model_solve_case6(technology_set_4, net_demand):
    """
    Tests that the reliability technology behaves as expected.
    """

    nuclear, battery = technology_set_4
    nuclear.capacity = 2
    model = DispatchModel([nuclear],
                          net_demand=net_demand,
                          solver=solver,
                          allow_blackout=True)
    model.solve()
    total_gen = model.results[['Nuclear',
                               'Curtailment',
                               'LoadLoss']].sum().sum()
    assert (total_gen - net_demand.sum()) == pytest.approx(0, abs=TOL)


def test_hierarchical_model_solve_case1(technology_set_1, net_demand):
    """
    Tests that the dispatch model produces expected results. Where all
    the technologies are simply :class:`Technology` objects. The model
    should always choose the cheapest technology, as long as it has
    enough capacity to meet the demand.
    """
    model = LogicDispatchModel(technology_list=technology_set_1,
                               net_demand=net_demand,
                               curtailment=False,
                               allow_blackout=False)
    model.solve()
    cheapest_tech = unyt_array(
        [t.variable_cost for t in technology_set_1]).min()
    expected_result = cheapest_tech * net_demand.sum()

    assert model.objective == pytest.approx(expected_result, rel=TOL)
    assert model.results['Nuclear'].sum(
    ) == pytest.approx(net_demand.sum(), TOL)
    assert model.results['NaturalGas'].sum() == pytest.approx(0.0, rel=TOL)
