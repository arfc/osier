```{eval-rst}
:class:`osier` is intended to be extremely user friendly and most problems
should be solvable without an external solver. However, the current implementation
of the :class:`osier.DispatchModel` as a linear program requires an external solver
such as CPLEX, CBC, GLPK, or Gurobi (since these are all supported by :class:`pyomo`). A dispatch model that does not depend on an external solver is currently in the works.

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



## Installing CPLEX

### Debian/Ubuntu

Once you have obtained an academic CPLEX license from IBM and downloaded the binaries,
follow these steps to install it.

1. Open your terminal and install a java virtual machine

```bash
$ sudo apt install -y openjdk-18-jre
```

2. Navigate to the folder location in your terminal with the CPLEX binaries.

```bash
$ cd Downloads/
```

3. Run the installer file and follow the command-line instructions.

```bash
$ sudo bash ILOG_COS_20.10_LINUX_X86_64.bin
```

4. Check that CPLEX was properly installed by typing `cplex` in your command line interface.

```bash
$ cplex

Welcome to IBM(R) ILOG(R) CPLEX(R) Interactive Optimizer 20.1.0.0
  with Simplex, Mixed Integer & Barrier Optimizers
5725-A06 5725-A29 5724-Y48 5724-Y49 5724-Y54 5724-Y55 5655-Y21
Copyright IBM Corp. 1988, 2020.  All Rights Reserved.

Type 'help' for a list of available commands.
Type 'help' followed by a command name for more
information on commands.

CPLEX> q
```

#### Troubleshooting

If the CPLEX installer cannot find the java virtual machine, find the location of the JVM and tell CPLEX where to find it.

```bash
$ which java
# usr/bin/java
$ sudo bash ILOG_COS_20.10_LINUX_X86_64.bin LAX_VM usr/bin/java
```

If `cplex` command is not found, try explicitly adding it to your path.

```bash
$ export CPLEX_STUDIO_BINARIES=/opt/ibm/ILOG/CPLEX_Studio201/cplex/bin/x86-64_linux/
$ export PATH=$PATH:$CPLEX_STUDIO_BINARIES
```
In order to make this change permanent, add these lines to the bottom of your `.bashrc` file and the run `$ source ~/.bashrc` to enact the changes.

## Windows

The easiest way to install CPLEX on Windows is with the GUI that is automatically shipped with the Windows binaries. Just follow the instructions in the GUI and you should be good to go!
