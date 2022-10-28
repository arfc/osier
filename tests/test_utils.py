from osier.utils import *
from unyt import kW, MW, minute, hour
import pytest


@pytest.fixture
def technology_set_1():
    """
    This fixture uses creates technologies directly from
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


def test_synchronize_units(technology_set_1):
    """
    Tests that the synchronize units function makes
    all of the units in a list of technologies the
    same.
    """
    u_p = kW
    u_t = minute
    u_e = u_p * u_t

    synced = synchronize_units(technology_set_1, unit_power=u_p, unit_time=u_t)
    assert synced == technology_set_1
    assert [t.unit_power for t in synced] == [u_p, u_p]
    assert [t.unit_time for t in synced] == [u_t, u_t]
    assert [t.unit_energy for t in synced] == [u_e, u_e]
