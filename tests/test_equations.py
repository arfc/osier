from osier.equations import annualized_capital_cost, annualized_fixed_cost
from osier import Technology
import pytest


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


def test_annualized_capital_cost(technology_set_1):
    """
    Tests the annualized cost is calculated correctly.
    """
    nuclear, natural_gas = technology_set_1

    expected = (nuclear.total_capital_cost / nuclear.lifetime) \
               + (natural_gas.total_capital_cost / natural_gas.lifetime)
    actual = annualized_capital_cost(technology_list=technology_set_1)

    assert expected == pytest.approx(actual)


def test_annualized_fixed_cost(technology_set_1):
    """
    Tests the annualized cost is calculated correctly.
    """
    nuclear, natural_gas = technology_set_1

    expected = (nuclear.annual_fixed_cost) + (natural_gas.annual_fixed_cost)
    actual = annualized_fixed_cost(technology_list=technology_set_1)

    assert expected == pytest.approx(actual)