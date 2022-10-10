# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.3] - 2022-10-04
### Added
- Adds `__init__.py` file to `osier.models` so the submodule can be imported.
### Fixed
- Changes `pip install -e .[doc]` in the github workflow to `pip install .[doc]` 
to catch installation issues.

## [0.1.2] - 2022-10-04
### Fixed
- Fixes a path issue in the `conf.py` file so that Sphinx can find `osier`.

## [0.1.1] - 2022-10-04
### Added
- Updates the `README` to include information about PyPI and `readthedocs`.

## [0.1.0] - 2022-10-04
The first release of `osier` on PyPI and publication of documentation on 
[readthedocs](https://osier.readthedocs.io/en/latest/).

### Added 
- `osier.Technology` class that stores data about technologies and handles units.
- `osier.DispatchModel` class that generates a simple a dispatch model when users pass 
`osier.Technology` objects.
- Publishes documentation on [readthedocs](https://osier.readthedocs.io/en/latest/).