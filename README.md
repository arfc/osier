# osier
/ˈōZHər/ <br>
Open source multi-objective energy system framework

[![status](https://joss.theoj.org/papers/183a04edba2d4952fa1e30c419a844b3/status.svg)](https://joss.theoj.org/papers/183a04edba2d4952fa1e30c419a844b3)
[![Build Status](https://github.com/arfc/osier/actions/workflows/CI.yml/badge.svg)](https://github.com/arfc/osier/actions/workflows/CI.yml)
[![Documentation Status](https://readthedocs.org/projects/osier/badge/?version=latest)](https://osier.readthedocs.io/en/latest/?badge=latest)



## Installation

`osier` is available through [PyPI](https://pypi.org/project/osier/). It may be installed with 
```bash
python -m pip install osier
``` 
or by cloning this repository and building from source:

```bash
git clone git@github.com:arfc/osier.git  # requires ssh-keys
# or
git clone https://github.com/arfc/osier.git
cd osier
# for a basic installation
pip install .
# to also install the documentation dependencies
pip install .[doc]
```


## Documentation
The documentation for `osier` can be viewed [here](https://osier.readthedocs.io/en/latest/). 
You can also build the docs locally with:

```bash
cd osier/docs
make html
cd build/html
# to serve the documentation
python -m http.server
```

## Tests
`osier`'s tests can be run by executing `pytest` in the top-level directory 
of `osier`.

```{note}
The test package assumes the user has `coin-or-cbc` installed as the default solver. For Windows machines,
this may require some additional steps to install the solver. [Here](https://stackoverflow.com/questions/58868054/how-to-install-coincbc-using-conda-in-windows) is a helpful place to start.
```


## Contributing

Contributions to `osier` are welcome. For details on how to make bug reports, pull requests, and other information, check the [contributing page](docs/source/contrib.md).


## Credits
Some of the documentation infrastructure was inspired by and borrowed from the [`watts` documentation](https://watts.readthedocs.io/en/latest/index.html).
