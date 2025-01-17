.. _overview_4_simulate:

Simulating Galaxies
===================

**PyAutoGalaxy** provides tool for simulating galaxy data-sets, which can be used to test modeling pipelines
and train neural networks to recognise and analyse images of galaxies.

Simulator
---------

Simulating galaxy images uses a `SimulatorImaging` object, which models the process that an instrument like the
Hubble Space Telescope goes through to observe a galaxy. This includes accounting for the exposure time to
determine the signal-to-noise of the data, blurring the observed light of the galaxy with the telescope optics
and accounting for the background sky in the exposure which adds Poisson noise.

.. code-block:: python

    psf_2d = ag.Kernel2D.from_gaussian(shape_native=(11, 11), sigma=0.1, pixel_scales=0.05)

    simulator = ag.SimulatorImaging(
        exposure_time=300.0, background_sky_level=1.0, psf=psf_2d, add_poisson_noise=True
    )

Once we have a simulator, we can use it to create an imaging dataset which consists of an image, noise-map and
Point Spread Function (PSF) by passing it a plane and grid.

.. code-block:: python

    imaging = simulator.via_plane_from(plane=plane, grid=grid_2d)

Here is what our dataset looks like:

.. image:: https://raw.githubusercontent.com/Jammy2211/PyAutoGalaxy/master/docs/overview/images/simulating/image.png
  :width: 400
  :alt: Alternative text

.. image:: https://raw.githubusercontent.com/Jammy2211/PyAutoGalaxy/master/docs/overview/images/simulating/noise_map.png
  :width: 400
  :alt: Alternative text

.. image:: https://raw.githubusercontent.com/Jammy2211/PyAutoGalaxy/master/docs/overview/images/simulating/psf.png
  :width: 400
  :alt: Alternative text

Examples
--------

The ``autogalaxy_workspace`` includes many example simulators for simulating galaxies with a range of different
physical properties and for creating imaging datasets for a variety of telescopes (e.g. Hubble, Euclid).

Below, we show what a galaxy looks like for different instruments.

.. image:: https://raw.githubusercontent.com/Jammy2211/PyAutoGalaxy/master/docs/overview/images/simulating/vro.png
  :width: 400
  :alt: Alternative text

.. image:: https://raw.githubusercontent.com/Jammy2211/PyAutoGalaxy/master/docs/overview/images/simulating/euclid.png
  :width: 400
  :alt: Alternative text

.. image:: https://raw.githubusercontent.com/Jammy2211/PyAutoGalaxy/master/docs/overview/images/simulating/hst.png
  :width: 400
  :alt: Alternative text

.. image:: https://raw.githubusercontent.com/Jammy2211/PyAutoGalaxy/master/docs/overview/images/simulating/ao.png
  :width: 400
  :alt: Alternative text

Wrap Up
-------

The ``autogalaxy_workspace`` includes many example simulators for simulating strong lenses with a range of different
physical properties, to make imaging datasets for a variety of telescopes (e.g. Hubble, Euclid) as well as
interferometer datasets.