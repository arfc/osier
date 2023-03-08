# Getting Started

```{eval-rst}
:class:`osier` is intended to be extremely user friendly and most problems
should be solvable without an external solver. However, the current implementation
of the :class:`osier.DispatchModel` as a linear program requires an external solver
such as CPLEX, CBC, GLPK, or Gurobi (since these are all supported by :class:`pyomo`).

CPLEX and Gurobi are commercial solvers, however it is quite simple to obtain a free
academic license (instructions forthcoming). GLPK will work on Windows, but requires
installing external binaries. CBC is a good open-source solver for a unix operating
system such as Mac or Linux.
 ```
In order to use CBC on the latter two operating systems you must have a version
of [Anaconda/conda](https://www.anaconda.com/products/distribution) installed.
Then you can install it using

```bash
$ conda install -c conda-forge coincbc
```
