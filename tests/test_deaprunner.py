import osier
from unyt import unyt_array
import unyt
import numpy as np
import pandas as pd
import pytest
import sys

TOL = 1e-5
N_HOURS = 24
N_DAYS = 2
N = N_HOURS * N_DAYS


@pytest.fixture
def net_demand():

    phase_shift = 0
    base_load = 1.5
    hours = np.linspace(0, N, N)
    demand = (np.sin((hours * np.pi / N_HOURS * 2 + phase_shift))
              * -1 + np.ones(N) * (base_load + 1))

    return demand

def test_deap_init(net_demand):
    """
    Tests that :class:`osier.models.deap_runner.OsierDEAP` is
    properly initialized.
    """
    techs = osier.all_technologies()
    objectives = [osier.total_cost, osier.annual_emission]
    problem = osier.CapacityExpansion(technology_list=techs,
                                      objectives=objectives,
                                      demand=net_demand,
                                      allow_blackout=False)
    model = osier.OsierDEAP(problem=problem,
                            pop_size=100)
    
    assert model.algorithm == 'nsga2'
    assert model.n_obj == 2
    assert model.completed_generations == 0
    assert model.n_dim == len(techs)
    assert model.solve_time == 0.0
    assert model.lower_bound == 0.0
    assert model.upper_bound == 1 / problem.capacity_credit.min()
    assert not model.repair
    assert not model.last_population
    assert not model.save_directory