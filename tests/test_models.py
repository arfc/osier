from osier import DispatchModel
from osier import Technology
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


def test_dispatch_model(technology_set, net_demand):
    model = DispatchModel(technology_set, 
                            net_demand=net_demand,
                            solver=solver)
    model.solve()
    assert model.objective == pytest.approx(371.41, 0.05)