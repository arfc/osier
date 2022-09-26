from osier import DispatchModel
from osier import Technology
from unyt import unyt_array
import numpy as np
import pytest
import sys

if "win32" in sys.platform:
    solver = 'cplex'
elif "linux" in sys.platform:
    solver = "cbc"

@pytest.fixture
def technology_set():
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
def net_demand():
    n_hours = 24
    np.random.seed(123)
    x = np.arange(0,n_hours,1)
    y = np.sin(8*x*np.pi/180)+np.random.normal(loc=0, scale=0.1, size=n_hours)
    y[y<0] = 0
    return y


def test_dispatch_model_initialize(technology_set, net_demand):
    model = DispatchModel(technology_set, 
                            net_demand=net_demand,
                            solver=solver)
    assert model.technology_list == technology_set
    assert model.tech_set == [t.technology_name for t in technology_set]
    assert model.solver == solver
    assert len(model.capacity_dict) == len(technology_set)
    assert len(model.indices) == len(net_demand) * len(technology_set)


@pytest.mark.skip("Does not work with CI, yet. Requires CBC or CPLEX.")
def test_dispatch_model_solve(technology_set, net_demand):
    model = DispatchModel(technology_set, 
                            net_demand=net_demand,
                            solver=solver)
    model.solve()
    cheapest_tech = unyt_array([t.variable_cost for t in technology_set]).min()
    expected_result = cheapest_tech * net_demand.sum()

    assert model.objective == pytest.approx(expected_result, 0.001)
    assert model.results['Nuclear'].sum() == net_demand.sum()
    assert model.results['NaturalGas'].sum() == 0.0