import numpy as np
from pathlib import Path
import dill
import random
import time


from pymoo.core.problem import ElementwiseProblem, Problem
from pymoo.util.ref_dirs import get_reference_directions
from deap import algorithms
from deap import base
from deap.benchmarks.tools import igd
from deap import creator
from deap import tools

from osier import *
from osier.tech_library import *


def uniform(low, up, size=None):
    """
    Generates a random starting population from
    a uniform distribution.
    """
    try:
        return [random.uniform(a, b) for a, b in zip(low, up)]
    except TypeError:
        return [random.uniform(a, b) for a, b in zip([low] * size, [up] * size)]


algorithm_options = {'nsga2':tools.selNSGA2,
                     'nsga3':tools.selNSGA3}

class OsierDEAP(object):
    """
    A DEAP algorithm object. Holds information and parameters to
    run a genetic algorithm using DEAP.

    Parameters
    ----------
    problem : :class:`Osier.CapacityExpansion`
        The problem to execute. In theory, this could be any object
        that has a method :meth:`evaluate` (for example, if it inherits 
        from :class:`pymoo.ElementwiseProblem`) and outputs a dictionary.
    algorithm : Optional, str
        Indicates the algorithm to use. Accepts ['nsga2', 'nsga3']. 
        NSGA2 is recommended for problems with three or fewer objectives.
        NSGA3 is recommended for problems with three or more objectives. 
    lower_bound : Optional, float, int
        The lower bound for each 'gene' in a candidate individual.
    upper_bound : Optional, float, int
        The upper bound for each 'gene' in a candidate individual.
    repair : Optional, :class:`pymoo.Repair`
        Adjusts the candidate individuals based on a user-defined procedure.
    hyper_params : Optional, dict
        Contains hyperparameters for the selection algorithm.
    save_directory : Optional, str
        Indicates the read/write directory.
    """
    def __init__(self, 
                 problem,
                 algorithm=None, 
                 lower_bound=0.0,
                 upper_bound=None,
                 repair=None,
                 hyper_params=None,
                 pop_size=100,
                 save_directory=None
                 ) -> None:
        self.problem = problem
        self.n_obj = self.problem.n_obj
        if algorithm:
            self.algorithm = algorithm.lower()
        elif self.n_obj < 3:
            self.algorithm = 'nsga2'
        elif self.n_obj >= 3:
            self.algorithm = 'nsga3' 
        self.n_dim = self.problem.n_var
        self.pop_size = pop_size
        self.repair = repair
        self.completed_generations = 0
        self.solve_time = 0.0
        self.last_population = None
        self.save_directory = Path(save_directory) if save_directory else None

        try: 
            assert isinstance(problem, (ElementwiseProblem, Problem))
        except AssertionError as e:
            raise AssertionError(f"Problem type <{type(problem)}> is not supported.")
        self.lower_bound = lower_bound

        if upper_bound:
            self.upper_bound = upper_bound
        else:
            self.upper_bound = 1/self.problem.capacity_credit.min()

        # Algorithm parameters
        self.mutation_eta = hyper_params['mating.mutation.eta'] if hyper_params else 20.0
        self.mutation_prob = hyper_params['mating.mutation.prob'] if hyper_params else 1.0
        self.crossover_eta = hyper_params['mating.crossover.eta'] if hyper_params else 30.0
        self.crossover_prob = hyper_params['mating.crossover.prob'] if hyper_params else 1.0

        # DEAP setup        
        creator.create("FitnessMin", base.Fitness, weights=(-1.0,) * self.n_obj)
        creator.create("Individual", list, fitness=creator.FitnessMin)
        
        self.toolbox = base.Toolbox()
        self.history = tools.History()
        self.logbook = tools.Logbook()
        self.logbook.header = "gen", "evals", "std", "min", "avg", "max"
        self.pareto_front = tools.ParetoFront()


        self.toolbox.register("attr_float", uniform, self.lower_bound, self.upper_bound, self.n_dim)
        self.toolbox.register("individual", tools.initIterate, creator.Individual, self.toolbox.attr_float)
        self.toolbox.register("population", tools.initRepeat, list, self.toolbox.individual)
        self.toolbox.register("evaluate", self.problem.evaluate, return_values_of=["F"])
        self.toolbox.register("mate", tools.cxSimulatedBinaryBounded, 
                              low=self.lower_bound, 
                              up=self.upper_bound, 
                              eta=self.crossover_eta)
        self.toolbox.register("mutate", tools.mutPolynomialBounded, 
                              low=self.lower_bound, 
                              up=self.upper_bound, 
                              eta=self.mutation_eta, 
                              indpb=1.0/self.n_dim)
        if self.algorithm == 'nsga3':
            self.ref_dirs = get_reference_directions('energy', self.n_obj, self.pop_size, seed=1)
            self.toolbox.register("select", algorithm_options[self.algorithm], ref_points=self.ref_dirs)
        elif self.algorithm == 'nsga2':
            self.ref_dirs = None
            self.toolbox.register("select", algorithm_options[self.algorithm])

        # Initialize statistics object
        self.stats = tools.Statistics(lambda ind: ind.fitness.values)
        self.stats.register("avg", np.mean, axis=0)
        self.stats.register("std", np.std, axis=0)
        self.stats.register("min", np.min, axis=0)
        self.stats.register("max", np.max, axis=0)


    def run(self, n_gen, seed=1234, init_pop=None, start_from_last=False):
        """
        Runs the genetic algorithm.

        Parameters
        ----------
        n_gen : int
            The number of generations to run.
        seed : int
            Sets the random seed.
        init_pop : :class:`deap.creator.Individual`
            Begins a simulation from a starting population.
        start_from_last : bool
            Begins a simulation from the last saved population.
        """
        random.seed(seed)

        if start_from_last and self.last_population:
            print('Starting from last population\n')
            pop = self.last_population
        elif init_pop:
            print('Starting from initialized population\n')
            pop = init_pop
        else:
            print('Starting from random population\n')
            pop = self.toolbox.population(n=self.pop_size)

        start = time.perf_counter()

        invalid_ind = [ind for ind in pop if not ind.fitness.valid]

        if self.repair and (len(invalid_ind) > 0):
            invalid_ind = self.repair._do(self.problem, np.array(invalid_ind))
            pop = [creator.Individual(ind) for ind in invalid_ind]
            invalid_ind = [ind for ind in pop if not ind.fitness.valid]

        try:
            fitnesses = self.toolbox.evaluate(np.array(invalid_ind))
            for ind, fit in zip(invalid_ind, fitnesses):
                ind.fitness.values = fit
        except AssertionError:
            print("Population already evaluated. Proceeding with genetic algorithm...")
        
        # Compile statistics about the population
        record = self.stats.compile(pop)
        self.logbook.record(gen=0, evals=len(pop), **record)
        self.history.update(pop)
        self.pareto_front.update(pop)
        self.last_population = pop
        print(self.logbook.stream)

        # Begin the generational process
        for gen in range(1, n_gen):
            offspring = algorithms.varAnd(pop, 
                                          self.toolbox, 
                                          self.crossover_prob, 
                                          self.mutation_prob)
            invalid_ind = [ind for ind in offspring if not ind.fitness.valid]

            # Evaluate the individuals with an invalid fitness
            if self.repair:
                invalid_ind = self.repair._do(self.problem, np.array(invalid_ind))
                offspring = [creator.Individual(ind) for ind in invalid_ind]
                invalid_ind = [ind for ind in offspring if not ind.fitness.valid]

            fitnesses = self.toolbox.evaluate(np.array(invalid_ind))
            for ind, fit in zip(invalid_ind, fitnesses):
                ind.fitness.values = fit

            # Select the next generation population from parents and offspring
            pop = self.toolbox.select(pop + offspring, self.pop_size)
            self.history.update(pop)
            self.pareto_front.update(pop)
            # Compile statistics about the new population
            record = self.stats.compile(pop)
            self.logbook.record(gen=gen, evals=len(invalid_ind), **record)
            self.last_population = pop
            self.completed_generations += 1
            print(self.logbook.stream)

        end = time.perf_counter()
        self.solve_time += (end-start)

        return self.last_population, self.logbook, self.pareto_front
    
    def save_model(self, fpath=None):
        """
        Serializes the model state in a binary file.
        """
        
        timestr = time.strftime("%Y%m%d-%H%M%S")
        save_name = f"{timestr}-OsierModel.pkl"
        if self.save_directory:
            fpath = self.save_directory / save_name
        else:
            fpath = save_name

        with open(fpath, "wb") as file:
            dill.dump(self.__dict__, file)
        

    def load_model(self, fpath):
        """
        Loads a serialized model into the current object.
        """

        with open(fpath, "rb") as file:
            tmp_dict = dill.load(file)
        
        self.__dict__.update(tmp_dict)