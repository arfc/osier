from osier import DispatchModel
from osier import Technology
import numpy as np
import pytest

@pytest.fixture
def technology_set():
    nuclear = Technology(technology_name='Nuclear',
                     technology_type='clean',
                     capacity=1e3,
                     capital_cost=6,
                     om_cost_variable=20,
                     om_cost_fixed=50,
                     fuel_cost=5
                    )
    natural_gas = Technology(technology_name='NaturalGas',
                        technology_type='fossil',
                        capacity=1e3,
                        capital_cost=1,
                        om_cost_variable=12,
                        om_cost_fixed=30,
                        fuel_cost=20
                        )

    return [nuclear, natural_gas]


def test_dispatch_model(technology_set):
    model = DispatchModel(technology_set, net_demand=np.ones(24))
