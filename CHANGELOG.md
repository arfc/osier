# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.4.1] - 2025-07-16
This update primarily fixes a bug related to the `LogicDispatchModel`.
There is also a bug fix related to the `utils.nmga` method.

### Fixed
- Previous versions of `Osier.CapacityExpansion` ran extremely slowly 
with the `LogicDispatchModel`. The issue was caused by repeated 
calls to `utils.synchronize_units` which should only happen once. This
redundancy has been removed and users can expect at least a 2x increase
in speed with the `LogicDispatchModel` over the standard `DispatchModel`.
- The `nmga` algorithm would not work when the number of objectives and 
decision variables did not match. This has been corrected.

## [0.4.0] - 2025-02-06
This update introduces some big new features to `Osier`.

### Added
- `Osier` includes a new "hierarchical dispatch" model for electricity dispatch (PR #71).
- A new `nmga` module was added to facilitate "n-dimensional modeling-to-generate alternatives." (PR #72)
- Two new tutorials in the documentation
    * "Constraint" tutorial - how to constrain an `Osier` model with objective functions.
    * "MGA" tutorial - how to perform MGA with `Osier`'s `nmga` module.
- The "dispatch" tutorial demonstrates the hierarchical dispatch algorithm.

### Fixed
- Fixes an issue with GitHub actions that tried setting up a `conda` environment via Mambaforge (now deprecated).
- Version listed in documentation is now linked with `pyproject.toml`.

## [0.3.1] - 2024-10-03
### Fixed
- Migrates the `setup.py` to a `pyproject.toml` configuration file.
- Updates tests to automatically use the `coincbc` solver.


## [0.3.0] - 2024-04-04
### Added
- Adds tests and examples
- Adds more objectives and methods in the `equations` module.
- Adds more helper functions in `utils`.

## Fixed
- Updates the `README` to instruct users on current installation procedures.

## [0.2.1] - 2022-11-01
### Fixed
- Fixes a bug where storage constraints were not initialized in the `DispatchModel`.
- Fixes the tolerances in the testing suite so that the tests pass. 
Previously, a single test was failing due to (-1e-9 == 0 &#177; 1e-12). 
This should pass, since 1e-9 is still close to zero.

## [0.2.0] - 2022-10-31
### Added
- Adds the following Technology subclasses
    * `StorageTechnology` which has storage attributes `initial_storage`, `storage_capacity`.
    * `RampingTechnology` which has ramping attributes `ramp_up` and `ramp_down`.
- Adds ramping and storage constraints to the `osier.DispatchModel` which correspond to the
`StorageTechnology` and `RampingTechnology` subclasses.

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