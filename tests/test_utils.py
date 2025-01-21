from osier.utils import *
from unyt import kW, MW, minute, hour
import numpy as np
import pandas as pd
import pytest
from scipy.spatial.distance import pdist
from scipy.spatial.distance import squareform
import itertools as it

# pymoo imports
from pymoo.problems import get_problem
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.optimize import minimize


@pytest.fixture
def pymoo_problem():
    """
    This fixture uses an example problem from `pymoo` as a test
    set.
    """
    problem = get_problem("bnh")

    pop_size = 100
    n_gen = 200
    algorithm = NSGA2(pop_size=pop_size)

    res = minimize(problem,
                   algorithm,
                   ('n_gen', n_gen),
                   seed=1,
                   verbose=False,
                   save_history=True
                   )

    return problem, res


@pytest.fixture
def technology_set_1():
    """
    This fixture creates technologies directly from the :class:`Technology`
    class.
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
    Tests that the synchronize units function makes all of the units in a list
    of technologies the same.
    """
    u_p = kW
    u_t = minute
    u_e = u_p * u_t

    synced = synchronize_units(technology_set_1, unit_power=u_p, unit_time=u_t)
    assert synced == technology_set_1
    assert [t.unit_power for t in synced] == [u_p, u_p]
    assert [t.unit_time for t in synced] == [u_t, u_t]
    assert [t.unit_energy for t in synced] == [u_e, u_e]


def test_apply_slack():
    """
    Tests that the function to apply slack values works as expected for a single
    objective, multiple objectives, and raises exceptions..
    """

    slack_values = np.array([0.1, 0.05, 0.2, 0.01])
    n_objectives = len(slack_values)
    pf1D = np.arange(20, 0, -1)
    pf4D = np.array([pf1D for i in range(n_objectives)]).T

    for slack in slack_values:
        assert np.all(pf1D * (1 + slack) ==
                      apply_slack(pf1D, slack, sense='minimize'))

    assert np.all(pf4D * (np.ones(n_objectives) + slack_values)
                  == apply_slack(pf4D, slack_values))

    with pytest.raises(ValueError) as e:
        apply_slack(pf1D, slack_values)


def test_distance_matrix_2D():
    """
    Tests the distance matrix function.
    """

    N_techs = 5
    population = 10
    measure = 'euclidean'

    rng = np.random.default_rng(seed=1234)

    data = rng.multivariate_normal(mean=np.array([1]),
                                   cov=np.diag([2]),
                                   size=(population, N_techs))
    data = data.reshape((population, N_techs))

    D = distance_matrix(data, metric=measure)
    test_matrix = squareform(pdist(data, metric=measure))

    assert np.allclose(D, test_matrix)


def test_check_if_interior_1():
    """
    Tests the `check_if_interior` function with a simple
    grid of points and specific test points.
    """
    x = np.arange(3)
    grid = np.array(list(it.product(x, x)))

    pf = np.array([[0, 0]])
    sf = np.array([[2, 0], [1, 1], [0, 2]])
    test_points = np.array([[0.5, 0.5], [1.5, 1.5]])

    int_idx = check_if_interior(test_points, pf, sf)

    assert np.all(int_idx == [0])


def test_check_if_interior_2():
    """
    Tests the `check_if_interior` function with a
    simple grid of points and some random test points.
    """
    x = np.arange(3)
    grid = np.array(list(it.product(x, x)))

    N = 100
    pf = np.array([[0, 0]])
    sf = np.c_[np.linspace(2, 0, N), np.linspace(0, 2, N)]

    rng = np.random.default_rng(seed=1234)
    test_points = rng.uniform(low=0, high=2, size=(10, 2))
    int_idx = check_if_interior(test_points, pf, sf)

    assert len(int_idx) == 3
    assert np.all(int_idx == [2, 3, 8])
