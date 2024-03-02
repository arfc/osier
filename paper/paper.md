---
title: '`Osier`: A Python package for multi-objective energy system optimization'
tags:
    - Python
    - energy systems
    - genetic algorithms
    - multi-objective optimization
authors:
    - name: Samuel G. Dotson
      orcid: 0000-0002-8662-0336
      affiliation: 1 
      corresponding: true
affiliations:
    - name: Felix T. Adler Fellow, Department of Nuclear, Plasma, and Radiological Engineering, University of Illinois Urbana-Champaign, USA
      index: 1
date: 20 February 2024
bibliography: paper.bib
---

# Summary
Transitioning to a clean energy economy will require expanded energy
infrastructure and an equitable, or just, transition further requires the
recognition of the people and communities directly affected by this transition.
However, public preferences may be ignored during decision-making processes
related to nearby energy infrastructure due to a lack of technical rigor and
expertise [@johnson:2021]. 

The challenge is more complicated by the fact that people have and express
preferences over many dimensions simultaneously. `osier` was designed to help
localized communities articulate their energy preferences in a technical manner
without requiring extensive technical expertise. In order to facilitate more
robust tradeoff analysis, `osier` generates a set of  technology portfolios,
called a Pareto front, with multi-objective optimization using evolutionary
algorithms. `osier` also implements a novel algorithm that extends the common
modelling-to-generate-alternatives (MGA) algorithm into many dimensions,
allowing users to investigate the near-optimal for appealing alternative
solutions. In this way, `osier` may address challenges with procedural and
recognition justice.

# Statement of Need
There are myriad open- and closed-source energy system optimization models
(ESOMs) available [@pfenninger:2022]. ESOMs can be used for a variety of tasks
but are most frequently used for prescriptive analyses meant to guide
decision-makers in planning processes. However, despite the many available
models, all of these tools share a fundamental characteristic: Optimization over
a single economic objective (e.g., total cost or social welfare).
Simultaneously, there is growing awareness of energy justice and calls for its
inclusion in energy models [@pfenninger:2014, @vagero:2023]. Some studies
attempted to incorporate local preferences into energy system design through
multi-criteria decision analysis (MCDA) and community focus groups
[@bertsch:2016, @mckenna:2018, @zelt2019]. Although @prina:2020 created a
bespoke multi-objective energy model, a flexible and extensible framework has
not yet been developed. `osier` fills this gap.

# Design and Implementation
In order to run `osier`, users are only required to supply an energy demand time
series. Users can optionally provide weather data to incorporate solar or wind
energy. The fundamental object in `osier` is an `osier.Technology` object, which
contain all of the necessary cost and performance data for different technology
classes. `osier` comes pre-loaded with a variety of technologies described in
the National Renewable Energy Laboratory's (NREL) Annual Technology Baseline
(ATB) dataset [@nationalrenewableenergylaboratory:2023]. 

A set of `osier.Technology` objects, along with user-supplied demand data, can
be tested independently with the `osier.DispatchModel`. The
`osier.DispatchModel` is a linear programming model implemented with the `pyomo`
library. For investment decisions and tradeoff analysis, users can pass their
portfolio of `osier.Technology` objects, energy demand, and their desired
objectives to the `osier.CapacityExpansion` model, the highest level model in
`osier`. The `osier.CapacityExpansion` model is implemented with the
multi-objective optimization framework, `pymoo`. \autoref{fig:osier-flow}
overviews the flow of data through `osier`.

![The flow of data into and within `osier`
\label{fig:osier-flow}](osier_flow.png)

## Key Features
In addition to being the first and only open-source multi-objective energy
modelling framework, `osier` has a few key features that further distinguishes
it from other modelling frameworks. First, since `osier.Technology` objects are
Python objects, users can modify values and assumptions, or assign new
attributes to the tested technologies. Second, contrary to conventional energy
system models, `osier` has no required objectives. While users may choose from a
variety of pre-defined objectives, they may also declare their own objectives
based on any quantifiable metric. The example code below illustrates the pattern
that `osier` expects. The requirements for a bespoke objective are: 

1. The first argument must be a list of `osier.Technology` objects.
2. The second argument must be the results from an `osier.DispatchModel`. But
   this may be a simple placeholder with a default value of `None` as shown
   below.
3. The function must return a numerical value.

These two features acknowledge that a modeler cannot know *a priori* all
possible objectives or parameters of interest. Allowing users to define their
own objectives and modify technology objects (or simply build their own by
inheriting from the `osier.Technology` class) accounts for this limitation and
expands the potential for incorporating localized preferences.

Lastly, in order to account for unmodeled or unmodelable objectives, `osier` extends the conventional MGA algorithm into N-dimensions by using a farthest-first-traversal

## Documentation

`osier` offers robust documentation with detailed usage examples at
[osier.readthedocs.io](https://osier.readthedocs.io).

# References


