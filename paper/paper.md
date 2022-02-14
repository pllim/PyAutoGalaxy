---
title: "`PyAutoGalaxy`: Open-Source Galaxy Modeling"
tags:
  - astronomy
  - Python
  - galaxy formation and evolution
  - galaxy morphology
  - interferometry
authors:
  - name: James. W. Nightingale
    orcid: 0000-0002-8987-7401
    affiliation: 1
  - name: Richard G. Hayes
    affiliation: 1
  - name: Aristeidis Amvrosiadis
    orcid: 0000-0002-4465-1564
    affiliation: 1 
  - name: Qiuhan He
    orcid: 0000-0003-3672-9365
    affiliation: 1   
  - name: Amy Etherington
    affiliation: 1 
  - name: XiaoYue Cao
    affiliation: 2               
  - name: Shaun Cole
    orcid: 0000-0002-5954-7903
    affiliation: 1
  - name: Andrea Enia
    orcid: 0000-0002-0200-2857
    affiliation: 5
  - name: Jonathan Frawley
    orcid: 0000-0002-9437-7399
    affiliation: 4    
  - name: Carlos S. Frenk
    orcid: 0000-0002-2338-716X
    affiliation: 1
  - name: Ashley Kelly
    orcid: 0000-0003-3850-4469
    affiliation: 1   
  - name: Sam Lange
    orcid: 0000-0003-3850-4469
    affiliation: 1   
  - name: Nan Li
    orcid: 0000-0001-6800-7389
    affiliation: 3    
  - name: Ran Li
    orcid: 0000-0003-3899-0612
    affiliation: 2
  - name: Richard J. Massey
    orcid:  0000-0002-6085-3780
    affiliation: 1
  - name: Mattia Negrello
    orcid: 0000-0002-7925-7663
    affiliation: 6
  - name: Andrew Robertson
    orcid: 0000-0002-0086-0524
    affiliation: 1
affiliations:
  - name: Institute for Computational Cosmology, Stockton Rd, Durham DH1 3LE
    index: 1
  - name: National Astronomical Observatories, Chinese Academy of Sciences, 20A Datun Road, Chaoyang District, Beijing 100012, China
    index: 2
  - name: Key Laboratory of Space Astronomy and Technology, National Astronomical Observatories, Chinese Academy of Sciences, Beijing 100101, China
    index: 3
  - name: Advanced Research Computing, Durham University, Durham DH1 3LE
    index: 4
  - name: Dipartimento di Fisica e Astronomia, Università degli Studi di Bologna, Via Berti Pichat 6/2, I-40127 Bologna, Italy
    index: 5
  - name: School of Physics and Astronomy, Cardiff University, The Parade, Cardiff CF24 3AA, UK
    index: 6

date: 26 October 2020
codeRepository: https://github.com/Jammy2211/PyAutoGalaxy
license: MIT
bibliography: paper.bib
---

# Summary

Nearly a century ago, Edwin Hubble famously classified galaxies into three distinct groups: ellipticals, spirals and 
irregulars. Today, by analysing millions of galaxies with advanced image processing techniques Astronomers have 
expanded on this picture and revealed the rich diversity of galaxy morphology both in the nearby and distant 
Universe. `PyAutoGalaxy` is an open-source Python 3.6+ package for analysing the morphologies and structures of large 
galaxy samples, with core features including fully automated Bayesian model-fitting of galaxy two-dimensional surface 
brightness profiles, support for imaging and interferometer datasets and comprehensive tools for simulating galaxy 
images. The software places a focus on **big data** analysis, including support for hierarchical models that 
simultaneously fit thousands of galaxies, massively parallel model-fitting and an SQLite3 database that allows large 
suites of modeling results to be loaded, queried and analysed. Accompanying `PyAutoGalaxy` is 
the [autogalaxy workspace](https://github.com/Jammy2211/autogalaxy_workspace), which includes example scripts, 
datasets and the `HowToGalaxy` lectures in Jupyter notebook format which introduce non-experts to studies of galaxy 
morphology using `PyAutoGalaxy`. Readers can  try `PyAutoGalaxy` right now by going 
to [the introduction Jupyter notebook on Binder](https://mybinder.org/v2/gh/Jammy2211/autogalaxy_workspace/release) or 
checkout the [readthedocs](https://pyautogalaxy.readthedocs.io/en/latest/) for a complete overview of `PyAutoGalaxy`'s 
features.

# Background

The study of galaxy morphology aims to understand the different luminous structures that galaxies are composed of.
Using large CCD imaging datasets of galaxies observed at ultraviolet, optical and near-infrared wavelengths from 
instruments like the Hubble Space Telescope (HST), Astronomers have uncovered the plentiful structures that make up 
a galaxy (e.g. bars, bulges, disks and rings) and revealed that evolving galaxies transition from disk-like structures 
to bulge-like elliptical galaxies. At sub-mm and radio wavelengths interferometer datasets from instruments like the 
Atacama LAM (ALMA) have revealed the integral role that dust plays in forming a galaxy in the distant Universe, early 
in its lifetime. Studies typically represent a galaxy's light using analytic functions such as the Sersic 
profile [@Sersic], which quantify the global appearance of most galaxies into one of three groups: (i) bulge-like 
structures which follow a dev Vaucouleurs profile; (ii) disk-like structures which follow an Exponential profile 
or; (iii) irregular morphologies which are difficult to quantify with symmetric and smooth analytic profiles. Galaxies 
are often composed of many sub-components which may be a combination of these different structures.

Figure 1 shows example `PyAutoGalaxy` models of three galaxies taken with three different datasets. The top row shows
a double Sersic fit to HST imaging of a galaxy, where `PyAutoGalaxy` has decomposed its structure into two distinct
components; a bulge and disk. Instrumental effects like diffraction from the telescope optics are fully accounted for. 
The middle row shows a `PyAutoGalaxy` fit to ALMA interferometry, where the galaxy's light is fitted directly in the 
complex uv-plane and Fourier transformed to real-space to show model-fits below. The bottom row shows a fit to an
irregular galaxy, where a fit using a symmetric Sersic profile is combined with `PyAutoGalaxy`'s non-parametric models
which successfully separate its smooth bulge component from the irregular spiral-arm structures.
 
# Statement of Need

In the next decade, wide field surveys such as Euclid, the Vera Rubin Observatory and Square Kilometer array are 
poised to observe images of _billions_ of galaxies. Analysing these extremely large galaxy datasets demands 
advanced Bayesian model-fitting techniques which can scale-up in a fully automated manner. Equally, the James Webb 
Space Telescope, thirty-meter class ground telescopes and ?radio? will observe galaxies at an
unprecedented resolution and level of detail. This demands more flexible modeling techniques that can accurately 
represent the complex irregular structures one such high resolution observations reveal. `PyAutoGalaxy` aims to meet 
both these needs, by interfacing galaxy model-fitting with the probabilistic programming language `PyAutoFit` to 
provide Bayesian fitting tools suited to big data analysis alongside image processing tools that represent irregular 
galaxy structures using non-parametric models.

# Software API and Features

At the heart of the `PyAutoGalaxy` API is the `Galaxy` object, which groups together one or more `LightProfile` objects
at an input redshift. Passing these objects a `Grid2D` returns an image of the galaxy(s), which can subsequently
be passed through `Operator` objects to apply a 2D convolution or Fast Fourier Transform and thereby compare 
the `Galaxy`'s image to an imaging or interferometer dataset. The `inversion` package contains a range of non-parametric 
models which fit a galaxy's light using a Bayesian linear matrix inversion. These were originally developed to 
reconstruct the source galaxies of strong gravitational lenses in `PyAutoGalaxy`'s child project `PyAutoLens`. 
`PyAutoGalaxy` includes a comprehensive visualization library for the analysis of both direct imaging and interferometer 
datasets and tools for preprocessing data to formats suited to galaxy model-fitting. The `astropy` cosmology module is 
used to handle unit conversions and calculations are optimized using the packages `NumPy` [@numpy], `numba` [@numba] 
and `PyNUFFT` [@pynufft].

To perform model-fitting, `PyAutoGalaxy` adopts the probabilistic programming  
language `PyAutoFit` (https://github.com/rhayes777/PyAutoFit). `PyAutoFit` allows users to compose a 
model from `LightProfile` and `Galaxy` objects, customize the model parameterization and fit it to data via a 
non-linear search (e.g., `dynesty` [@dynesty], `emcee` [@emcee], `PySwarms` [@pyswarms]). By composing a model with 
`Pixelization` and `Regularization` objects, the galaxy's light is reconstructed using a non-parametric rectangular 
grid or Voronoi mesh that accounts for irregular galaxy morphologies. 

`PyAutoFit`'s graphical modeling framework allows one to simultaneously fit images of thousands of galaxies. Using a 
technique called expectation propagation, this fits each galaxy dataset one-by-one and combines the results of every 
fit into a global model using a self consistent Bayesian framework. Automated fits of complex galaxy models is
possible using `PyAutoFit`'s emprical Bayes framework, which breaks the fitting of a galaxy into a a chained sequence of 
non-linear searches. These fits pass information gained about simpler models fitted by earlier searches to subsequent 
searches, which fit progressively more complex models. By granularizing the model-fitting procedure, automated 
pipelines that fit complex galaxy models without human intervention can be carefully crafted, with example pipelines 
found on the [autogalaxy workspace](https://github.com/Jammy2211/autogalaxy_workspace). To ensure the 
analysis and interpretation of fits to large lens datasets is feasible, `PyAutoFit`'s database tools write lens modeling 
results to a relational database which can be queried from hard-disk to a Python script or Jupyter notebook. This uses 
memory-light `Python` generators, ensuring it is practical fo tens of thousands of galaxies.

# Workspace and HowToLens Tutorials

`PyAutoGalaxy` is distributed with the [autogalaxy workspace](https://github.com/Jammy2211/autogalaxy_workspace>), which 
contains example scripts for modeling and simulating galaxies and tutorials on how to preprocess imaging and 
interferometer datasets before a `PyAutoGalaxy` analysis. Also included are the `HowToGalaxy` tutorials, a five chapter 
lecture series composed of over 30 Jupyter notebooks aimed at non-experts, introducing them to galaxy morphology 
analysis, Bayesian inference and teaching them how to use `PyAutoGalaxy` for scientific study. The lectures 
are available on our [Binder](https://mybinder.org/v2/gh/Jammy2211/autogalaxy_workspace/HEAD) and may therefore be 
taken without a local `PyAutoGalaxy` installation.

# Software Citations

`PyAutoGalaxy` is written in Python 3.6+ [@python] and uses the following software packages:

- `Astropy` [@astropy1] [@astropy2]
- `COLOSSUS` [@colossus]
- `corner.py` [@corner]
- `dynesty` [@dynesty]
- `emcee` [@emcee]
- `Matplotlib` [@matplotlib]
- `numba` [@numba]
- `NumPy` [@numpy]
- `PyAutoFit` [@pyautofit]
- `PyLops` [@PyLops]
- `PyMultiNest` [@pymultinest] [@multinest]
- `PyNUFFT` [@pynufft]
- `pyprojroot` (https://github.com/chendaniely/pyprojroot)
- `pyquad` [@pyquad]
- `PySwarms` [@pyswarms]
- `scikit-image` [@scikit-image]
- `scikit-learn` [@scikit-learn]
- `Scipy` [@scipy]

# Related Software

- `PyAutoLens` [@Nightingale2021] [@Nightingale2021]
- `galfit` http://www.physics.rutgers.edu/~keeton/gravlens/manual.pdf
- `lenstronomy-spinoff` https://github.com/sibirrer/lenstronomy [@Birrer2018a]
- `galpak2d` https://github.com/jspilker/visilens [@spilker16a]
- `megamorph`

# Acknowledgements

JWN and RJM are supported by the UK Space Agency, through grant ST/V001582/1, and by InnovateUK through grant TS/V002856/1. RGH is supported by STFC Opportunities grant ST/T002565/1.
QH, CSF and SMC are supported by ERC Advanced In-vestigator grant, DMIDAS [GA 786910] and also by the STFCConsolidated Grant for Astronomy at Durham [grant numbersST/F001166/1, ST/I00162X/1,ST/P000541/1].
RJM is supported by a Royal Society University Research Fellowship.
DH acknowledges support by the ITP Delta foundation.
AR is supported bythe ERC Horizon2020 project ‘EWC’ (award AMD-776247-6).
MN has received funding from the European Union’s Horizon 2020 research and innovation programme under the Marie Sklodowska-Curie grant agreement no. 707601.
This work used the DiRAC@Durham facility managed by the Institute for Computational Cosmology on behalf of the STFC DiRAC HPC Facility (www.dirac.ac.uk). The equipment was funded by BEIS capital funding via STFC capital grants ST/K00042X/1, ST/P002293/1, ST/R002371/1 and ST/S002502/1, Durham University and STFC operations grant ST/R000832/1. DiRAC is part of the National e-Infrastructure.

# References