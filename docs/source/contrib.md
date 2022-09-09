# Contributing

Thank you for contributing to `osier`! All contributions, bug reports, bug fixes, documentation 
improvements, enhancements and ideas are welcome.

The [GitHub "Issues" tab](https://github.com/arfc/osier/issues) contains open issues. Some issues
are labeled "Difficulty:1-Beginner" and are good first issues to tackle for new contributers to 
`osier`. You can even sort by "label" to find precisely those issues!

## Bug reports
Bug reports from users are an important for identifying unforeseen issues. If you find a bug please
open a new issue with the following:
1. An explanation of the problem with enough details for others to reproduce the problem. Some 
common information needed is
    * Operating system
    * Python version
    * Any commands executed (perhaps a python snippet)
    * An error message from the terminal
2. An explanation of the expected behavior. For example
    * I ran `numpy.add(1,2)` which gave me an output of `-999`, but I expected `3`. 


## Development Environment
In order to add new features to `osier` you need to set up a working development environment.
First, you must create a [fork](https://github.com/arfc/osier/fork). Then use the following 
commands. "your-fork" is a placeholder for the location of your fork of `osier`.

```bash
# 1. Download source code
git clone git@github.com:your-fork/osier.git  # requires ssh-keys
# or 
git clone https://github.com/your-fork/osier.git
cd osier
git remote add arfc https://github.com/arfc/osier.git  # the official repository
git pull arfc main  # pull down the up-to-date version of osier
pip install -e .[doc]
```
The `-e` flag creates an editable installation so you don't have to reinstall everytime a
feature is changed.

## Making a pull request
A good pull request requires the following, along with a new feature (where applicable)
1. All functions should have docstrings using the [Numpydoc style](https://numpydoc.readthedocs.io/en/latest/format.html)
2. All new functions should have corresponding unit tests (and should be small enough that unit-testing makes sense).
3. All tests must pass on your machine by running `pytest` in the top level directory.
4. All new features must be appropriately documented.
5. Code should follow [PEP8 style](http://www.python.org/dev/peps/pep-0008/). [`autopep8`](https://pypi.org/project/autopep8/)
is a helpful tool for ensuring consistent style.