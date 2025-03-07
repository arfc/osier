from osier import Technology
from osier.technology import _validate_unit
from unyt import unit_object
import copy
from typing import Iterable
import pandas as pd
import numpy as np
import functools
import types
from scipy.spatial.distance import pdist
from scipy.spatial.distance import squareform
import warnings

from osier.technology import Technology


def synchronize_units(tech_list: Iterable[Technology],
                      unit_power: unit_object,
                      unit_time: unit_object) -> Iterable[Technology]:
    """
    This function ensures that all objects in the technology list have units
    consistent with the model's units. An :class:`osier.Technology` object (or
    sub-classes) have three unit settings.

        * :attr:`unit_power`
        * :attr:`unit_time`
        * :attr:`unit_energy`

    Only the :attr:`unit_power` and :attr:`unit_time` attributes can be
    specified with this function to prevent inconsistent units. E.g. Setting the
    :attr:`unit_energy` to ``MWh`` even though time is in minutes and power is
    in ``kW``.

    .. note::
        The objects in the original list are copied by default. This
        may result in slower run time.

    Parameters
    ----------
    tech_list : list of :class:`osier.Technology` objects
        The list of technology objects whose units need to be synchronized.

    Returns
    -------
    synced_list : list of :class:`osier.Technology` objects
        The list of technology objects that have synchronized units.
    """

    synced_list = [copy.deepcopy(t) for t in tech_list]

    for t in synced_list:
        t.unit_power = _validate_unit(unit_power, dimension="power")
        t.unit_time = _validate_unit(unit_time, dimension="time")

    return synced_list


def get_tech_names(technology_list):
    """
    Returns the a list of :class:`osier.Technology` name strings.

    Parameters
    ----------
    technology_list : list of :class:`osier.Technology` objects
        The list of technologies.

    Returns
    -------
    tech_names : list of str
        The list of technology names.
    """

    tech_names = [t.technology_name for t in technology_list]

    return tech_names


def get_dispatchable_techs(technology_list):
    """
    Returns a list of :class:`osier.Technology` objects where
    :attr:`dispatchable` is `True`.

    Parameters
    ----------
    technology_list : list of :class:`osier.Technology` objects
        The list of technologies.

    Returns
    -------
    dispatchable_techs : list of :class:`osier.Technology`
        The list of dispatchable technologies.
    """

    dispatchable_techs = [t for t in technology_list if t.dispatchable]

    return dispatchable_techs


def get_nondispatchable_techs(technology_list):
    """
    Returns a list of :class:`osier.Technology` objects where
    :attr:`dispatchable` is `False`.

    Parameters
    ----------
    technology_list : list of :class:`osier.Technology` objects
        The list of technologies.

    Returns
    -------
    non_dispatchable_techs : list of :class:`osier.Technology`
        The list of non dispatchable technologies.
    """

    non_dispatchable_techs = [t for t in technology_list if not t.dispatchable]

    return non_dispatchable_techs


def get_storage_techs(technology_list):
    """
    Returns a list of :class:`osier.Technology` objects
    that have the attribute :attr:`storage_level`.

    Parameters
    ----------
    technology_list : list of :class:`osier.Technology` objects
        The list of technologies.

    Returns
    -------
    storage_techs : list of :class:`osier.Technology`
        The list of storage technologies.
    """

    storage_techs = [t for t in technology_list
                     if hasattr(t, 'storage_level')]

    return storage_techs


def get_nonstorage_techs(technology_list):
    """
    Returns a list of :class:`osier.Technology` objects
    that do not have the attribute :attr:`storage_level`.

    Parameters
    ----------
    technology_list : list of :class:`osier.Technology` objects
        The list of technologies.

    Returns
    -------
    storage_techs : list of :class:`osier.Technology`
        The list of non-storage technologies.
    """

    nonstorage_techs = [t for t in technology_list
                        if not hasattr(t, 'storage_level')]

    return nonstorage_techs


def get_dispatchable_names(technology_list):
    """
    Returns a list of :class:`osier.Technology` name strings where
    :attr:`dispatchable` is `True`.

    Parameters
    ----------
    technology_list : list of :class:`osier.Technology` objects
        The list of technologies.

    Returns
    -------
    dispatchable_names : list of str
        The list of dispatchable technology names.
    """

    dispatchable_names = [
        t.technology_name for t in technology_list if t.dispatchable]

    return dispatchable_names


def get_objective_names(res_obj):
    """
    This function returns a list of named objectives based on the names of the
    functions passed to Osier. In the case of partial functions, the first
    keyword value is used.

    Parameters
    ----------
    res_obj : :class:`pymoo.Result`
        The simulation results object containing all data and metadata.

    Returns
    -------
    obj_columns : list of str
        A list of function name strings.
    """
    obj_columns = []
    for ofunc in res_obj.problem.objectives:
        if isinstance(ofunc, types.FunctionType):
            obj_columns.append(ofunc.__name__)
        elif isinstance(ofunc, functools.partial):
            obj_columns.append(list(ofunc.keywords.values())[0])
    return obj_columns


def technology_dataframe(technology_list, cast_to_string=True):
    """
    Returns a :class:`pandas.DataFrame` with a complete set of data for a given
    technology list.

    Parameters
    ----------
    technology_list : list of :class:`osier.Technology` objects
        The list of technologies.

    Returns
    -------
    technology_dataframe : :class:`pandas.DataFrame`
        A dataframe of all technology data.
    """

    frames = []

    for t in technology_list:
        frames.append(t.to_dataframe(cast_to_string=cast_to_string))

    technology_dataframe = pd.concat(frames, axis=0)

    return technology_dataframe


def apply_slack(pareto_front, slack, sense='minimize'):
    """
    This function applies a specified slack value to a given Pareto front.
    Returns a :class:`numpy.ndarray` with the same shape as the Pareto front.

    Parameters
    ----------
    pareto_front : :class:`numpy.ndarray`
        A :class:`numpy.ndarray` with shape (population, N_objectives).

    slack : float or list of float
        The slack value for the sub-optimal front, expressed as a decimal
        percentage. If `float` is passed, the same slack will be applied to all
        objectives. A `list` of slack values should have the same length as the
        list of objectives. The slack will be applied to objective with the same
        index (defined when users initialized the
        :class:`osier.CapacityExpansion` problem). Each slack value should be
        less than unity. If users that find a slack greater than unity desirable
        should consider rerunning the model with fewer or different objectives.

    sense : str
        Whether the objectives are maximized or minimized. 
        Accepts ['minimize', 'maximize']. Default is "minimize."

    Returns
    -------
    near_optimal_front : :class:`numpy.ndarray`
        The near-optimal front.
    """

    if sense.lower() not in ['minimize','maximize']:
        print(f"Did not understand sense '{sense}.'")
        print(f"Accepts: ['minimize', 'maximize']")
        raise ValueError

    try:
        n_objectives = pareto_front.shape[1]
    except IndexError as e:
        n_objectives = len(pareto_front)

    if isinstance(slack, (list, np.ndarray)):
        try:
            assert len(slack) == n_objectives
        except AssertionError:
            print("Number of slack values must equal number of objectives.")
            raise ValueError

        if sense.lower() == 'minimize':
            near_optimal_front = np.array(
                pareto_front) * (np.ones(n_objectives) + np.array(slack))
            return near_optimal_front
        elif sense.lower() == 'maximize':
            near_optimal_front = np.array(
                pareto_front) * (np.ones(n_objectives) - np.array(slack))
            return near_optimal_front

        return near_optimal_front
    elif isinstance(slack, float):
        if sense.lower() == 'minimize':
            near_optimal_front = np.array(pareto_front) * (1 + slack)
            return near_optimal_front
        elif sense.lower() == 'maximize':
            near_optimal_front = np.array(pareto_front) * (1 - slack)
            return near_optimal_front

    return


def distance_matrix(X, metric='euclidean'):
    """
    This function calculates the distance matrix for an MxN matrix and returns
    the symmetrical square form of the matrix.

    Parameters
    ----------
    X : :class:`numpy.ndarray`
        An MxN matrix.
    metric : str
        The string describing how the metric should be calculated.

        See the documentation for
        [`scipy.spatial.distance.pdist`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.distance.pdist.html)
        for a complete list of values. Default is 'euclidean.'

    Returns
    -------
    D : :class:`numpy.ndarray`
        An MxM matrix of distance values and zeros along the diagonal.
    """

    D = squareform(pdist(X, metric=metric))

    return D


def farthest_first(X, D, n_points, start_idx=None, seed=1234):
    """
    This function identifies the farthest first traversal order for an MxN
    matrix and returns an array of indices (ordered by the distance). If
    `n_points` exceeds the number of points in the dataset, all points will be
    returned.

    This implementation was modified from Hiroyuki Tanaka's [GitHub
    gist](https://gist.github.com/nkt1546789/8e6c46aa4c3b55f13d32).

    Parameters
    ----------
    X : :class:`numpy.ndarray`
        An MxN matrix.
    D : :class:`numpy.ndarray`
        An MxM distance matrix for the dataset, `X`.
    n_points : int
        The number of points to traverse.
    start_idx : int
        The index of the starting point. If `None`, a starting point will be
        chosen randomly. Default is `None`.
    seed : int
        Specifies the seed for a random number generator to ensure repeatable
        results. Default is 1234.

    Returns
    -------
    checked_points : :class:`numpy.ndarray`
        An array of points checked by the algorithm.


    Notes
    -----
    1. The algorithm will stop if the average distance is unchanging.
    """

    rows, cols = X.shape

    if n_points >= rows:
        return np.arange(rows)
    else:
        checked_points = []

        if not start_idx:
            rng = np.random.default_rng(seed)
            start_idx = rng.integers(low=0, high=rows - 1)

        checked_points.append(start_idx)
        prev_mean_dist = None
        while len(checked_points) < n_points:
            mean_distance = np.mean([D[i] for i in checked_points], axis=0)
            if np.all(mean_distance == prev_mean_dist):
                msg = f"Average distance is unchanging after {len(checked_points)} points."
                warnings.warn(msg, UserWarning)
                break
            else:
                sorted_dist = np.argsort(mean_distance)[::-1]
                for j in sorted_dist:
                    if j not in checked_points:
                        checked_points.append(j)
                        break
            prev_mean_dist = mean_distance

    return np.array(checked_points)


def check_if_interior(points, par_front, slack_front):
    """
    Checks if a point or set of points is inside the N-polytope created by the
    Pareto front and the slack front (a.k.a the near-optimal front).

    .. warning::
        If the Pareto front has only a few points there may false negatives.

    Parameters
    ----------
    points : :class:`numpy.ndarray`
        A point or set of points to test.
    par_front : :class:`numpy.ndarray`
        The set of points on the Pareto front.
    slack_front : :class:`numpy.ndarray`
        The set of points on the near-optimal front. Equal to
        `par_front*(1+slack)`.

    Returns
    -------
    interior_idxs : :class:`numpy.ndarray`
        The set of indices that are between the Pareto front and slack front.

    Examples
    --------
    >>> import itertools as it
    >>> x = np.arange(3)
    >>> grid = np.array(list(it.product(x,x)))

    >>> pf = np.array([[0,0]])
    >>> sf = np.array([[2,0], [1,1], [0,2]])

    >>> rng = np.random.default_rng(seed=1234)
    >>> test_points = rng.uniform(low=0, high=2, size=(10,2))
    >>> int_idx = check_if_interior(test_points, pf, sf)
    >>> int_points = test_points[int_idx]

    >>> import matplotlib.pyplot as plt

    >>> plt.scatter(grid[:,0],grid[:,1])
    >>> plt.scatter(test_points[:,0],test_points[:,1])
    >>> plt.scatter(int_points[:,0],int_points[:,1])
    >>> plt.show()
    """

    try:
        n_inds, n_objs = points.shape
    except ValueError:
        n_inds = points.shape[0]
        n_objs = 1

    interior_idxs = []

    checked_points = set()
    for i, p in enumerate(points):
        if tuple(p) in checked_points:
            continue
        else:
            checked_points.add(tuple(p))
            cond1 = np.any((p < slack_front).sum(axis=1) == n_objs)
            cond2 = np.any((p > par_front).sum(axis=1) == n_objs)
            if cond1 and cond2:
                interior_idxs.append(i)

    return np.array(interior_idxs)


def n_mga(results_obj,
          n_points=10,
          slack=0.1,
          sense='minimize',
          how='farthest',
          seed=1234,
          metric='euclidean',
          start_idx=None,
          wide_form=False):
    """
    N-dimensional modeling-to-generate-alternatives (n-mga) allows users to
    efficiently search decision space by relaxing the objective function(s) by a
    specified amount of slack. This implementation will identify all points
    inside of an N-polytope (a polygon in N-dimensions). Then a reduced subset
    of points will be selected.

    The algorithm is:

    1. Generate a near-optimal front based on the given slack values.

    2. Loop through each point in the model's history.

    3. Add each point to a set of checked points to prevent repeated calculations.

    4. Check if a point is inside the N-polytope bounded by the Pareto and
        near-optimal fronts.

    5. Select a subset of points based on a random selection or with a farthest first traversal.

    Parameters
    ----------
    results_obj : :class:pymoo.Result
        The simulation results object containing all data and metadata.
    n_points : int or str
        The number of points to select from the near-optimal region. Default is
        10. The only accepted string value is `'all'`, which will return all
        values in the near-optimal space.
    slack : float or list of float
        The slack value for the sub-optimal front, expressed as a decimal
        percentage. If `float` is passed, the same slack will be applied to all
        objectives. A `list` of slack values should have the same length as the
        list of objectives. The slack will be applied to objective with the same
        index (defined when users initialized the
        :class:`osier.CapacityExpansion` problem).
    sense : str
        Indicates whether the optimization was a minimization or maximization.
        If min, the sub-optimal front is greater than the Pareto front. If max,
        the sub-optimal front is below the Pareto front. Default is "minimize."
    how : str
        Sets the method used to traverse the near-optimal region. Accepts
        ['all','random','farthest'].

        * `'all'` : Returns all near-optimal points.

        * `'random'` : Returns a random selection a set of `n_points` from the near-optimal region.

        * `'farthest'` : Returns `n_points` from the near-optimal space by doing a farthest-first-traversal in the design space.
    seed : int
        Specifies the seed for a random number generator to ensure repeatable
        results. Default is 1234.
    metric : str
        The string describing how the metric should be calculated. See the
        documentation for
        [`scipy.spatial.distance.pdist`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.distance.pdist.html)
        for a complete list of values. Default is 'euclidean.'
    start_idx : int
        The index of the starting point. If `None`, a starting point will be
        chosen randomly. Default is `None`.
    wide_form : boolean
        If `True`, the designs will be unpacked and each decision variable will
        have its own column in the resulting dataframe. Default is `False`.

    Returns
    -------
    mga_df : :class:`pandas.DataFrame`
        Returns a dataframe with `n_points` rows and `N_objectives + 1` columns,
        where the rows are data for each solution selected by the MGA algorithm
        and the columns are the performance values for that solution, with an
        additional `designs` column that holds the capacity portfolio.

    Warnings
    --------
    The following may result in an infinite-loop when using a
    `farthest-first-traversal`:

    * a matrix of rank 1 (i.e., all rows are identical / non-unique /
      non-independent)

    If the average distance is unchanging, this means the algorithm found a
    point, or points, that is equidistant from every other point. The algorithm
    will stop when it reaches this point. In this case, it is recommended to
    use the `all` or the `random` options to generate alternative points. Or
    inspect their results.
    """
    if how.lower() not in ['all','random', 'farthest']:
        print(f"Did not understand how = '{how}.'")
        print(f"Accepts: ['all','random', 'farthest']")
        raise ValueError

    pf = results_obj.F
    xpf = results_obj.X
    try:
        n_inds, n_objs = pf.shape
    except ValueError:
        n_inds = pf.shape[0]
        n_objs = 1

    try:
        n_inds, n_vars = xpf.shape
    except ValueError:
        n_vars = xpf.shape[0]

    pop_size = results_obj.algorithm.pop_size
    n_gen = results_obj.algorithm.n_gen - 1

    pf_slack = apply_slack(pareto_front=pf,
                           slack=slack,
                           sense=sense)

    X_hist = np.array([hist.pop.get("X") for hist in results_obj.history]).reshape(
        n_gen * pop_size, n_vars)
    F_hist = np.array([hist.pop.get("F") for hist in results_obj.history]).reshape(
        n_gen * pop_size, n_objs)
    try:
        cols = get_objective_names(results_obj)
    except AttributeError:
        cols = [f'f{i}' for i in range(n_objs)]

    interior_idxs = check_if_interior(F_hist, pf, pf_slack)
    X_int = X_hist[interior_idxs]
    F_int = F_hist[interior_idxs]

    if how == 'all':
        selected_idxs = np.arange(len(interior_idxs))
    elif how == 'random':
        rng = np.random.default_rng(seed)
        selected_idxs = rng.integers(
            low=0, high=len(interior_idxs), size=n_points)
    elif how == 'farthest':
        distance = distance_matrix(X_int, metric=metric)
        selected_idxs = farthest_first(X_int,
                                       distance,
                                       n_points=n_points,
                                       start_idx=start_idx,
                                       seed=seed)
    X_select = X_int[selected_idxs]
    F_select = F_int[selected_idxs]
    mga_df = pd.DataFrame(dict(zip(cols, F_select.T)))

    if wide_form:
        try:
            x_cols = get_tech_names(results_obj.problem.technology_list)
        except AttributeError:
            try:
                n_xs = results_obj.X.shape[1]
            except ValueError:
                n_xs = 1
            x_cols = [f'x{i}' for i in range(n_xs)]
        x_df = pd.DataFrame(dict(zip(x_cols, X_select.T)))
        mga_df = pd.concat([mga_df, x_df], axis=1)
    else:
        mga_df['designs'] = [design for design in X_select]

    return mga_df
