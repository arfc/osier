import numpy as np
import pandas as pd
from osier import get_objective_names


def _apply_slack(pareto_front, slack):
    """
    This function applies a specified slack value to a given 
    Pareto front. Returns a :class:`numpy.ndarray` with the same
    shape as the Pareto front.

    Parameters
    ----------
    pareto_front : :class:`numpy.ndarray`
        A :class:`numpy.ndarray` with shape (population, N_objectives).

    slack : float or list of float
        The slack value for the sub-optimal front, expressed as a 
        decimal percentage. If `float` is passed, the same slack will
        be applied to all objectives. A `list` of slack values should
        have the same length as the list of objectives. The slack will
        be applied to objective with the same index (defined when users
        initialized the :class:`osier.CapacityExpansion` problem).

    Returns
    -------
    near_optimal_front : :class:`numpy.ndarray`
    """


    


def nmga(results_obj, n_points=10, slack=0.1, sense='minimize', how='random'):
    """
    N-dimensional modeling-to-generate-alternatives ():function:`nmga`)
    allows users to efficiently search decision space by relaxing the objective
    function(s) by a specified amount of slack. This implementation will identify
    all points inside of an N-polytope (a polygon in N-dimensions). Then a
    reduced subset of points will be selected. 

    
    Parameters
    ----------
    results_obj : :class:pymoo.Result
        The simulation results object containing all data and metadata.
    n_points : int
        The number of points to select from the near-optimal region.
        Default is 10.
    slack : float or list of float
        The slack value for the sub-optimal front, expressed as a 
        decimal percentage. If `float` is passed, the same slack will
        be applied to all objectives. A `list` of slack values should
        have the same length as the list of objectives. The slack will
        be applied to objective with the same index (defined when users
        initialized the :class:`osier.CapacityExpansion` problem).
    sense : str
        Indicates whether the optimization was a minimization 
        or maximization. If min, the sub-optimal front is greater
        than the Pareto front. If max, the sub-optimal front is 
        below the Pareto front. Default is "minimize." 
        
        
    .. warning::
        This method will produce duplicates in most cases since it
        checks the population history and the population history
        does not have unique values due to the nature of genetic
        algorithms (i.e. good solutions persist in the gene pool).
    """
    n_objs = results_obj.problem.n_obj
    
    
    pf = results_obj.F
    if sense.lower() == 'minimize':
        pf_slack = pf*(1+slack)
    elif sense.lower() == 'maximize':
        pf_slack = pf*(1-slack)
        
    



    checked_points = set()

    interior_dict = {n:[] for n in range(n_objs+1)}
    cols = get_objective_names(results_obj) + ['designs']
    
    # get list of all points
    for h in results_obj.history:
        # the history of each population, individual, 
        # and their corresponding design spaces.
        F_hist = h.pop.get("F")  # objective space
        X_hist = h.pop.get("X")  # design space
    
        for p, x in zip(F_hist, X_hist):
            if p in checked_points:
                continue
            else:
                checked_points.add(p)
                # check that all coordinates of a point are within the boundaries.
                cond1 = np.any((p < pf_slack).sum(axis=1)==n_objs)
                cond2 = np.any((p > pf).sum(axis=1)==n_objs)
                if cond1 and cond2:
                    for i,c in enumerate(p):
                        interior_dict[i].append(c)
                    interior_dict[n_objs].append(x)
    mga_df = pd.DataFrame(interior_dict)
    mga_df.columns = cols
    
    return mga_df


    for x,y,z in zip(F_hist[:,0], F_hist[:,1], X_hist):
        if (x,y) in checked_points:
            continue
        else: 
            if poly.contains(Point(x,y)):
                ax.scatter(x,y,color='tab:green')
                F1_sub.append(x)
                F2_sub.append(y)
                X_sub.append(z)
                checked_points.add((x,y))