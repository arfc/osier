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
    - name: Madicken Munk
      orcid: 0000-0003-0117-5366
      affiliation: 1 
affiliations:
    - name: Department of Nuclear, Plasma, and Radiological Engineering, University of Illinois Urbana-Champaign, USA
      index: 1
date: 05 April 2024
bibliography: paper.bib
---

# Summary
Transitioning to a clean energy economy will require expanded energy
infrastructure. An equitable, or just, transition further requires the
recognition of the people and communities directly affected by this transition.
However, public preferences may be ignored during decision-making processes
related to energy infrastructure due to a lack of technical rigor or expertise
[@johnson:2021]. This challenge is further complicated by the fact that people
have and express preferences over many dimensions simultaneously.
Multi-objective optimization offers a method to help decision makers and
stakeholders understand the problem and analyze tradeoffs among solutions
[@liebman:1976]. Although, to date, no open-source multi-objective energy
modeling frameworks exist. Open-source multi-objective energy system framework
(`osier`) is a Python package for designing and optimizing energy systems across
an arbitrary number of dimensions. `osier` was designed to help localized
communities articulate their energy preferences in a technical manner without
requiring extensive technical expertise. In order to facilitate more robust
tradeoff analysis, `osier` generates a set of solutions, called a Pareto front,
that are composed of a number of technology portfolios. The Pareto front is
calculated using multi-objective optimization using evolutionary algorithms.
`osier` also extends the common modeling-to-generate-alternatives (MGA)
algorithm into N-dimensional objective space, as opposed to the conventional
single-objective MGA. This allows users to investigate the near-optimal space
for appealing alternative solutions. In this way, `osier` may aid modelers in
addressing procedural and recognition justice.

# Statement of Need
There are myriad open- and closed-source energy system optimization models
(ESOMs) available [@pfenninger:2022]. ESOMs can be used for a variety of tasks
but are most frequently used for prescriptive analyses meant to guide
decision-makers in planning processes. However, virtually all of these tools
share a fundamental characteristic: Optimization over a single economic
objective (e.g., total cost or social welfare). Simultaneously, there is growing
awareness of energy justice and calls for its inclusion in energy models
[@pfenninger:2014; @vagero:2023]. Two well known open-source ESOMs, Calliope
[@pfenninger:2018] and Python for Power Systems Analysis (PyPSA) [@brown:2018],
partially address equity issues by implementing MGA, but this does not resolve
the limitations of mono-objective optimization. Some studies incorporate local
preferences into energy system design through multi-criteria decision analysis
(MCDA) and community focus groups [@bertsch:2016; @mckenna:2018; @zelt:2019].
But these studies rely on tools with pre-defined objectives which are difficult
to modify. Without the ability to add objectives that reflect the concerns of a
community, the priorities of that community will remain secondary to those of
modelers and decision makers. A flexible and extensible multi-objective
framework that fulfills this need has not yet been developed. `osier`
closes this gap.

# Design and Implementation
The fundamental object in `osier` is an `osier.Technology` object, which
contains all of the necessary cost and performance data for different technology
classes. `osier` comes pre-loaded with a variety of technologies described in
the National Renewable Energy Laboratory's (NREL) Annual Technology Baseline
(ATB) dataset[@nationalrenewableenergylaboratory:2023] but users are also able
to define their own. In order to run `osier`, users are required to supply an
energy demand time series and a list of `osier.Technology` objects. Users can
optionally provide weather data to incorporate solar or wind energy. 

A set of `osier.Technology` objects, along with user-supplied demand data, can
be tested independently with the `osier.DispatchModel`. The
`osier.DispatchModel` is a linear programming model implemented with the `pyomo`
library [@hart:2011]. For investment decisions and tradeoff analysis, users can
pass their portfolio of `osier.Technology` objects, energy demand, and their
desired objectives to the `osier.CapacityExpansion` model, the highest level
model in `osier`. The `osier.CapacityExpansion` model is implemented with the
multi-objective optimization framework, `pymoo` [@blank:2020].
\autoref{fig:osier-flow} overviews the flow of data through `osier`.

![The flow of data into and within
`osier`.\label{fig:osier-flow}](osier_flow.png)

## Key Features
In addition to being the first and only open-source multi-objective energy
modeling framework, `osier` has a few key features that further distinguishes it
from other modeling frameworks. First, since `osier.Technology` objects are
Python objects, users can modify values and assumptions, or assign new
attributes to the tested technologies. Second, contrary to conventional energy
system models, `osier` has no required objectives. While users may choose from a
variety of pre-defined objectives, they may also declare their own objectives
based on any quantifiable metric. The requirements for a bespoke objective are: 

1. The first argument must be a list of `osier.Technology` objects.
2. The second argument must be the results from an `osier.DispatchModel`. But
   this may be a simple placeholder with a default value of `None`.
3. The function must return a single numerical value.
4. The final requirement, is that all `osier.Technology` objects possess the
   attribute being optimized.

These two features acknowledge that a modeler cannot know *a priori* all
possible objectives or parameters of interest. Allowing users to define their
own objectives and modify technology objects (or simply build their own by
inheriting from the `osier.Technology` class) accounts for this limitation and
expands the potential for incorporating localized preferences. Lastly, in order
to account for unmodeled or unmodelable objectives, `osier` extends the
conventional MGA algorithm into N-dimensions by using a farthest-first-traversal
in the design space.

## Sample Results and Interpretation

When solving a multi-objective problem, `osier` generates a set of co-optimal
solutions rather than a global optimum, called a Pareto front.
\autoref{fig:osier-results} shows a Pareto front from a problem that
simultaneously minimizes total cost and lifecylce carbon emissions.

![A Pareto front generated
by`osier`.\label{fig:osier-results}](images/osier-results.png)

Each point on this Pareto front represents a different technology portfolio
(i.e., different combination of wind, natural gas, and battery storage).
\autoref{fig:osier-tech-res} illustrates the variation in solutions from the
Pareto front in \autoref{fig:osier-results}. In this case, the range of wind
capacity is wider than the range of capacities for natural gas and battery
storage.

![The variance in technology options along a Pareto
front.\label{fig:osier-tech-res}](images/osier-tech-results.png)

## Documentation

`osier` offers robust documentation with detailed usage examples at
[osier.readthedocs.io](https://osier.readthedocs.io).

# Acknowledgements

Samuel Dotson, the corresponding and lead author of this publication is
responsible for the conceptualization of `osier`, developing `osier` as a
software, in preparing this manuscript for publication, and for performing
analysis to validate `osier`. Madicken Munk provided resources and supervision
for the work, as well as assisted in the review and editing of the manuscript.
Samuel Dotson was supported by the Nuclear Regulatory Commission Fellowship
program. This research was part of the Advanced Reactors and Fuel Cycles (ARFC)
group in the Department of Nuclear, Plasma, and Radiological Engineering (NPRE)
at the University of Illinois Urbana-Champaign. To that end, the authors would
like to acknowledge ARFC members Oleksander Yardas, Luke Seifert, Nathan Ryan,
Amanda Bachmann, and Sun Myung Park for their contributions in reviewing pull
requests supporting the creation of osier. Additionally, Samuel Dotson was
supported by the Felix T. Adler Fellowship through NPRE. Finally, the authors
would like to thank the JOSS reviewers for their time and commentary in
reviewing this manuscript. 

# References


