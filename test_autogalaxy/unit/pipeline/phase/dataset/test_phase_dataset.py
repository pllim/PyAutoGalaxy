from os import path
import autofit as af
import autogalaxy as ag
import pytest
from autogalaxy import exc
from test_autogalaxy import mock

pytestmark = pytest.mark.filterwarnings(
    "ignore:Using a non-tuple sequence for multidimensional indexing is deprecated; use `arr[tuple(seq)]` instead of "
    "`arr[seq]`. In the future this will be interpreted as an arrays index, `arr[np.arrays(seq)]`, which will result "
    "either in an error or a different result."
)

directory = path.dirname(path.realpath(__file__))


class TestPhase:
    def test__extend_with_hyper_and_pixelizations(self):

        phase_no_pixelization = ag.PhaseImaging(
            phase_name="test_phase", search=mock.MockSearch()
        )

        phase_extended = phase_no_pixelization.extend_with_multiple_hyper_phases(
            setup=ag.PipelineSetup(hyper_galaxies_search=None, inversion_search=None)
        )
        assert phase_extended == phase_no_pixelization

        # This phase does not have a pixelization, so even though inversion=True it will not be extended

        phase_extended = phase_no_pixelization.extend_with_multiple_hyper_phases(
            setup=ag.PipelineSetup(inversion_search=mock.MockSearch())
        )
        assert phase_extended == phase_no_pixelization

        phase_with_pixelization = ag.PhaseImaging(
            phase_name="test_phase",
            galaxies=dict(
                source=ag.GalaxyModel(
                    redshift=0.5,
                    pixelization=ag.pix.Rectangular,
                    regularization=ag.reg.Constant,
                )
            ),
            search=mock.MockSearch(),
        )

        phase_extended = phase_with_pixelization.extend_with_multiple_hyper_phases(
            setup=ag.PipelineSetup(inversion_search=mock.MockSearch()),
            include_inversion=True,
        )
        assert isinstance(phase_extended.hyper_phases[0], ag.InversionPhase)

        phase_extended = phase_with_pixelization.extend_with_multiple_hyper_phases(
            setup=ag.PipelineSetup(
                hyper_galaxies=True,
                hyper_galaxies_search=mock.MockSearch(),
                inversion_search=None,
            )
        )
        assert isinstance(phase_extended.hyper_phases[0], ag.HyperGalaxyPhase)

        phase_extended = phase_with_pixelization.extend_with_multiple_hyper_phases(
            setup=ag.PipelineSetup(
                hyper_galaxies=True,
                hyper_galaxies_search=mock.MockSearch(),
                inversion_search=mock.MockSearch(),
            ),
            include_inversion=True,
        )
        assert isinstance(phase_extended.hyper_phases[0], ag.InversionPhase)
        assert isinstance(phase_extended.hyper_phases[1], ag.HyperGalaxyPhase)

        phase_extended = phase_with_pixelization.extend_with_multiple_hyper_phases(
            setup=ag.PipelineSetup(
                hyper_galaxies=True,
                hyper_galaxies_search=mock.MockSearch(),
                inversion_search=mock.MockSearch(),
                hyper_galaxy_phase_first=True,
            ),
            include_inversion=True,
        )
        assert isinstance(phase_extended.hyper_phases[0], ag.HyperGalaxyPhase)
        assert isinstance(phase_extended.hyper_phases[1], ag.InversionPhase)


class TestMakeAnalysis:
    def test__mask_input_uses_mask(self, phase_imaging_7x7, imaging_7x7):
        # If an input mask is supplied we use mask input.

        mask_input = ag.Mask.circular(
            shape_2d=imaging_7x7.shape_2d, pixel_scales=1.0, sub_size=1, radius=1.5
        )

        analysis = phase_imaging_7x7.make_analysis(
            dataset=imaging_7x7, mask=mask_input, results=mock.MockResults()
        )

        assert (analysis.masked_imaging.mask == mask_input).all()
        assert analysis.masked_imaging.mask.pixel_scales == mask_input.pixel_scales

    def test__mask_changes_sub_size_depending_on_phase_attribute(
        self, phase_imaging_7x7, imaging_7x7
    ):
        # If an input mask is supplied we use mask input.

        mask_input = ag.Mask.circular(
            shape_2d=imaging_7x7.shape_2d, pixel_scales=1, sub_size=1, radius=1.5
        )

        phase_imaging_7x7.meta_dataset.settings.sub_size = 1
        analysis = phase_imaging_7x7.make_analysis(
            dataset=imaging_7x7, mask=mask_input, results=mock.MockResults()
        )

        assert (analysis.masked_imaging.mask == mask_input).all()
        assert analysis.masked_imaging.mask.sub_size == 1
        assert analysis.masked_imaging.mask.pixel_scales == mask_input.pixel_scales

        phase_imaging_7x7.meta_dataset.settings.sub_size = 2
        analysis = phase_imaging_7x7.make_analysis(
            dataset=imaging_7x7, mask=mask_input, results=mock.MockResults()
        )

        assert (analysis.masked_imaging.mask == mask_input).all()
        assert analysis.masked_imaging.mask.sub_size == 2
        assert analysis.masked_imaging.mask.pixel_scales == mask_input.pixel_scales


class TestPhasePickle:

    # noinspection PyTypeChecker
    def test_assertion_failure(self, imaging_7x7, mask_7x7):

        phase_imaging_7x7 = ag.PhaseImaging(
            phase_name="phase_name",
            galaxies=dict(
                galaxy=ag.Galaxy(light=ag.lp.EllipticalLightProfile, redshift=1)
            ),
            search=mock.MockSearch(),
        )

        result = phase_imaging_7x7.run(dataset=imaging_7x7, mask=mask_7x7, results=None)
        assert result is not None

        phase_imaging_7x7 = ag.PhaseImaging(
            phase_name="phase_name",
            galaxies=dict(
                galaxy=ag.Galaxy(light=ag.lp.EllipticalLightProfile, redshift=1)
            ),
            search=mock.MockSearch(),
        )

        result = phase_imaging_7x7.run(dataset=imaging_7x7, mask=mask_7x7, results=None)
        assert result is not None
