# osier
/ˈōZHər/ <br>
Open source multi-objective energy system framework

[![Build Status](https://github.com/arfc/osier/actions/workflows/CI.yml/badge.svg)](https://github.com/arfc/osier/actions/workflows/CI.yml)


## Installation

`osier` is not currently on PyPI or Conda-forge (we hope this will change
soon). It may be installed by executing the following commands on the command
line:

```bash
git clone git@github.com:arfc/osier.git  # requires ssh-keys
# or
git clone https://github.com/arfc/osier.git
cd osier
# for a basic installation
pip install .
# to also build the documentation
pip install .[doc]
```

Someday, the `osier` documentation will be hosted on its own website. For
now the documentation may be built with

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

Contributions to `osier` are welcome. For details on how to make bug reports, issues to
work on, and other information, check the [contributing page](docs/source/contrib.md)