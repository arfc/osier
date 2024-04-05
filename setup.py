from __future__ import absolute_import, division, print_function
from os.path import join as pjoin
import sys
from setuptools import setup, find_packages


# Format expected by setup.py and doc/source/conf.py: string of form "X.Y.Z"
_version_major = 0
_version_minor = 3
_version_micro = 0  # use '' for first of series, number for 1 and above
# _version_extra = 'dev'
_version_extra = ''  # Uncomment this for full releases

# Construct full version string from these.
_ver = [_version_major, _version_minor]
if _version_micro:
    _ver.append(_version_micro)
if _version_extra:
    _ver.append(_version_extra)

__version__ = '.'.join(map(str, _ver))

CLASSIFIERS = ["Development Status :: 3 - Alpha",
               "Environment :: Console",
               "Intended Audience :: Science/Research",
               "License :: OSI Approved :: BSD License",
               "Operating System :: OS Independent",
               "Programming Language :: Python",
               "Topic :: Scientific/Engineering"]

# Description should be a one-liner:
description = "osier: A justice oriented energy system optimization tool"
# Long description will go up on the pypi page

NAME = "osier"
MAINTAINER = "Samuel Dotson"
MAINTAINER_EMAIL = "samgdotson@gmail.com"
DESCRIPTION = description
with open("README.md", encoding="utf-8") as f:
    LONG_DESCRIPTION = f.read()
LONG_DESCRIPTION_CONTENT_TYPE = 'text/markdown'
URL = "https://osier.readthedocs.io/en/latest/"
DOWNLOAD_URL = "http://github.com/arfc/osier"
LICENSE = "BSD-3"
AUTHOR = "Samuel Dotson"
AUTHOR_EMAIL = "sgd2@illinois.edu"
PLATFORMS = "OS Independent"
MAJOR = _version_major
MINOR = _version_minor
MICRO = _version_micro
VERSION = __version__
PACKAGE_DATA = {'osier': [pjoin('data', '*')]}
REQUIRES = [
    'numpy',
    'pandas',
    'matplotlib',
    'pytest',
    'dill',
    'openpyxl',
    'nrelpy',
    'unyt',
    'pymoo',
    'pyentrp',
    'deap',]
EXTRAS_REQUIRE = {
    'doc': [
        'sphinx>=5.1',
        'sphinx-autobuild',
        'myst-parser',
        "sphinx_design",
        "sphinx-autodoc-typehints",
        'numpydoc',
        'pydata_sphinx_theme',
        'nbsphinx',
        'pandoc'
        ]}
PYTHON_REQUIRES = ">= 3.6"

PACKAGES = find_packages()

ENTRY_POINTS = {}

SETUP_REQUIRES = ['setuptools >= 24.2.0']
# This enables setuptools to install wheel on-the-fly
SETUP_REQUIRES += ['wheel'] if 'bdist_wheel' in sys.argv else []

opts = dict(name=NAME,
            maintainer=MAINTAINER,
            maintainer_email=MAINTAINER_EMAIL,
            description=DESCRIPTION,
            long_description=LONG_DESCRIPTION,
            long_description_content_type=LONG_DESCRIPTION_CONTENT_TYPE,
            url=URL,
            download_url=DOWNLOAD_URL,
            license=LICENSE,
            classifiers=CLASSIFIERS,
            author=AUTHOR,
            author_email=AUTHOR_EMAIL,
            platforms=PLATFORMS,
            version=VERSION,
            packages=PACKAGES,
            package_data=PACKAGE_DATA,
            install_requires=REQUIRES,
            extras_require=EXTRAS_REQUIRE,
            python_requires=PYTHON_REQUIRES,
            setup_requires=SETUP_REQUIRES,
            requires=REQUIRES,
            entry_points=ENTRY_POINTS)


if __name__ == '__main__':
    setup(**opts)
