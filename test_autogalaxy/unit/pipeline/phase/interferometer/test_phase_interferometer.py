import os
from os import path

from autoconf import conf
import autofit as af
import autogalaxy as ag
import numpy as np
import pytest
from test_autogalaxy import mock

pytestmark = pytest.mark.filterwarnings(
    "ignore:Using a non-tuple sequence for multidimensional indexing is deprecated; use `arr[tuple(seq)]` instead of "
    "`arr[seq]`. In the future this will be interpreted as an arrays index, `arr[np.arrays(seq)]`, which will result "
    "either in an error or a different result."
)

directory = path.dirname(path.realpath(__file__))


def clean_images():
    try:
        os.remove("{}/source_galaxy_phase/source_image_0.fits".format(directory))
        os.remove("{}/source_galaxy_phase/galaxy_image_0.fits".format(directory))
        os.remove("{}/source_galaxy_phase/model_image_0.fits".format(directory))
    except FileNotFoundError:
        pass
    conf.instance.dataset_path = directory


class TestMakeAnalysis:
    def test__masks_visibilities_and_noise_map_correctly(
        self, phase_interferometer_7, interferometer_7, visibilities_mask_7x2
    ):
        analysis = phase_interferometer_7.make_analysis(
            dataset=interferometer_7,
            mask=visibilities_mask_7x2,
            results=mock.MockResults(),
        )

        assert (
            analysis.masked_interferometer.visibilities == interferometer_7.visibilities
        ).all()
        assert (
            analysis.masked_interferometer.noise_map == interferometer_7.noise_map
        ).all()

    def test__phase_info_is_made(
        self, phase_interferometer_7, interferometer_7, visibilities_mask_7x2
    ):
        phase_interferometer_7.make_analysis(
            dataset=interferometer_7,
            mask=visibilities_mask_7x2,
            results=mock.MockResults(),
        )

        file_phase_info = "{}/{}".format(
            phase_interferometer_7.search.paths.output_path, "phase.info"
        )

        phase_info = open(file_phase_info, "r")

        search = phase_info.readline()
        sub_size = phase_info.readline()
        primary_beam_shape_2d = phase_info.readline()
        cosmology = phase_info.readline()

        phase_info.close()

        assert search == "Optimizer = MockSearch \n"
        assert sub_size == "Sub-grid size = 2 \n"
        assert primary_beam_shape_2d == "Primary Beam shape = None \n"
        assert (
            cosmology
            == 'Cosmology = FlatLambdaCDM(name="Planck15", H0=67.7 km / (Mpc s), Om0=0.307, Tcmb0=2.725 K, '
            "Neff=3.05, m_nu=[0.   0.   0.06] eV, Ob0=0.0486) \n"
        )

    def test__phase_can_receive_hyper_image_and_noise_maps(self, mask_7x7):
        phase_interferometer_7 = ag.PhaseInterferometer(
            phase_name="test_phase",
            galaxies=dict(
                galaxy=ag.GalaxyModel(redshift=ag.Redshift),
                galaxy1=ag.GalaxyModel(redshift=ag.Redshift),
            ),
            hyper_background_noise=ag.hyper_data.HyperBackgroundNoise,
            search=mock.MockSearch(),
            real_space_mask=mask_7x7,
        )

        instance = phase_interferometer_7.model.instance_from_vector([0.1, 0.2, 0.3])

        assert instance.galaxies[0].redshift == 0.1
        assert instance.galaxies[1].redshift == 0.2
        assert instance.hyper_background_noise.noise_scale == 0.3


class TestHyperMethods:
    def test__phase_is_extended_with_hyper_phases__sets_up_hyper_images(
        self, interferometer_7, mask_7x7
    ):

        galaxies = af.ModelInstance()
        galaxies.galaxy = ag.Galaxy(redshift=0.5)
        galaxies.source = ag.Galaxy(redshift=1.0)

        instance = af.ModelInstance()
        instance.galaxies = galaxies

        hyper_galaxy_image_path_dict = {
            ("galaxies", "galaxy"): ag.Array.ones(shape_2d=(3, 3), pixel_scales=1.0),
            ("galaxies", "source"): ag.Array.full(
                fill_value=2.0, shape_2d=(3, 3), pixel_scales=1.0
            ),
        }

        hyper_galaxy_visibilities_path_dict = {
            ("galaxies", "galaxy"): ag.Visibilities.full(fill_value=4.0, shape_1d=(7,)),
            ("galaxies", "source"): ag.Visibilities.full(fill_value=5.0, shape_1d=(7,)),
        }

        results = mock.MockResults(
            hyper_galaxy_image_path_dict=hyper_galaxy_image_path_dict,
            hyper_model_image=ag.Array.full(fill_value=3.0, shape_2d=(3, 3)),
            hyper_galaxy_visibilities_path_dict=hyper_galaxy_visibilities_path_dict,
            hyper_model_visibilities=ag.Visibilities.full(
                fill_value=6.0, shape_1d=(7,)
            ),
            mask=mask_7x7,
            use_as_hyper_dataset=True,
        )

        phase_interferometer_7 = ag.PhaseInterferometer(
            phase_name="test_phase",
            galaxies=dict(
                galaxy=ag.GalaxyModel(redshift=0.5, hyper_galaxy=ag.HyperGalaxy)
            ),
            search=mock.MockSearch(),
            real_space_mask=mask_7x7,
        )

        phase_interferometer_7.extend_with_multiple_hyper_phases(
            hyper_combined_search=mock.MockSearch()
        )

        analysis = phase_interferometer_7.make_analysis(
            dataset=interferometer_7, mask=mask_7x7, results=results
        )

        assert (
            analysis.hyper_galaxy_image_path_dict[("galaxies", "galaxy")].in_2d
            == np.ones((3, 3))
        ).all()

        assert (
            analysis.hyper_galaxy_image_path_dict[("galaxies", "source")].in_2d
            == 2.0 * np.ones((3, 3))
        ).all()

        assert (analysis.hyper_model_image.in_2d == 3.0 * np.ones((3, 3))).all()

        assert (
            analysis.hyper_galaxy_visibilities_path_dict[("galaxies", "galaxy")]
            == 4.0 * np.ones((7, 2))
        ).all()

        assert (
            analysis.hyper_galaxy_visibilities_path_dict[("galaxies", "source")]
            == 5.0 * np.ones((7, 2))
        ).all()

        assert (analysis.hyper_model_visibilities == 6.0 * np.ones((7, 2))).all()
