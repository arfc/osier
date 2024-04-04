# osier
/ˈōZHər/ <br>
Open source multi-objective energy system framework

[![Build Status](https://github.com/arfc/osier/actions/workflows/CI.yml/badge.svg)](https://github.com/arfc/osier/actions/workflows/CI.yml)
[![Documentation Status](https://readthedocs.org/projects/osier/badge/?version=latest)](https://osier.readthedocs.io/en/latest/?badge=latest)



## Installation

`osier` is available through [PyPI](https://pypi.org/project/osier/). It may be installed with 
```bash
python -m pip install osier pyomo==6.4.1
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

# followed by 
pip install pyomo==6.4.1
```


```{note}
Although `pyomo` is a dependency, the current version of `pyomo` (6.7.1, as of 2/29/24) has a bug
that prints erroneous errors during an `osier` simulation. Therefore, users are recommended to 
install a specific version of `pyomo` after the main installation of `osier`. There is an open issue [#50](https://github.com/arfc/osier/issues/50) 
related to this concern.
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


## Contributing

Contributions to `osier` are welcome. For details on how to make bug reports, pull requests, and other information, check the [contributing page](docs/source/contrib.md).


## Credits
Some of the documentation infrastructure was inspired by and borrowed from the [`watts` documentation](https://watts.readthedocs.io/en/latest/index.html).
