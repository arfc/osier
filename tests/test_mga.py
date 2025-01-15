from scipy.spatial.distance import pdist
from scipy.spatial.distance import squareform
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import itertools as it
# pymoo imports
from pymoo.problems import get_problem
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.optimize import minimize

from osier import n_mga
from osier import distance_matrix, farthest_first, check_if_interior
from osier.utils import *

#===============PROBLEM SET UP==================
problem = get_problem("bnh")

seed = 45
pop_size = 100
n_gen = 200
algorithm = NSGA2(pop_size=pop_size)

res = minimize(problem,
            algorithm,
            ('n_gen', n_gen),
            seed=seed,
            verbose=False,
            save_history=True
            )
F = problem.pareto_front()
f1 = F[:,0]
f2 = F[:,1]
slack = 0.1
F1 = f1 * (1+slack)
F2 = f2 * (1+slack)
#===============MANUAL MGA FOR COMPARISON==================

X_hist = np.array([history.pop.get("X") for history in res.history]).reshape(n_gen*pop_size,2)
F_hist = np.array([history.pop.get("F") for history in res.history]).reshape(n_gen*pop_size,2)

slack_front = np.c_[F1,F2]

int_pts = check_if_interior(points=F_hist, par_front=F, slack_front=slack_front)
X_int = X_hist[int_pts]
F_int = F_hist[int_pts]

D = distance_matrix(X=X_int)

n_pts = 10
idxs = farthest_first(X=X_int, D=D, n_points=n_pts, seed=seed)

F_select = F_int[idxs]
X_select = X_int[idxs]


def test_nmga_integration():
    mga_results = n_mga(results_obj=res, seed=seed)
    assert(mga_results.shape == (10,3))


def test_nmga_wideform():
    mga_results = n_mga(results_obj=res, seed=seed, wide_form=True)
    assert(mga_results.shape == (10,4))


def test_nmga_all():
    mga_results = n_mga(results_obj=res, n_points='all', seed=seed, wide_form=True)
    assert(mga_results.shape == (len(F_int),4))
