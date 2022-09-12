from pymoo.core.problem import Problem


class Model(object):
    """
    The `Model` object contains all of the metadata and
    parameters to solve a genetic algorithm with pymoo.
    """

    def __init__(self, technologies, algorithm='NSGA2', pymoo_problem='Problem', **kwargs) -> None:
        """
        Initializes the Model class.

        Parameters
        ----------
        technologies : list of strings or `osier`

        algorithm : string or `pymoo` algorithm module  
            Specifies the algorithm used to solve the problem.
            Default is `NSGA2`.
        pymoo_problem : string or `pymoo` problem class
            Specifies the type of `pymoo` problem the model should execute.
            Default is `Problem`. Accepts ['FunctionalProblem', 'ElementwiseProblem','Problem']
        """
        self.technologies = technologies
        self.algorithm = algorithm
        self.pymoo_problem = pymoo_problem