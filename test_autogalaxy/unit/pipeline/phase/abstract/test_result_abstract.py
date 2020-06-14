from os import path

from autoconf import conf
import autogalaxy as ag
import pytest
from test_autogalaxy import mock

pytestmark = pytest.mark.filterwarnings(
    "ignore:Using a non-tuple sequence for multidimensional indexing is deprecated; use `arr[tuple(seq)]` instead of "
    "`arr[seq]`. In the future this will be interpreted as an arrays index, `arr[np.arrays(seq)]`, which will result "
    "either in an error or a different result."
)

directory = path.dirname(path.realpath(__file__))


@pytest.fixture(scope="session", autouse=True)
def do_something():
    print("{}/config/".format(directory))

    conf.instance = conf.Config("{}/config/".format(directory))


class TestGeneric:
    def test__results_of_phase_are_available_as_properties(self, imaging_7x7, mask_7x7):

        phase_dataset_7x7 = ag.PhaseImaging(
            phase_name="test_phase_2",
            galaxies=dict(
                galaxy=ag.Galaxy(
                    redshift=0.5, light=ag.lp.EllipticalSersic(intensity=1.0)
                )
            ),
            search=mock.MockSearch(),
        )

        result = phase_dataset_7x7.run(
            dataset=imaging_7x7, mask=mask_7x7, results=mock.MockResults()
        )

        assert isinstance(result, ag.AbstractPhase.Result)


class TestPlane:
    def test__max_log_likelihood_plane_available_as_result(self, imaging_7x7, mask_7x7):

        galaxy_0 = ag.Galaxy(redshift=0.5, light=ag.lp.EllipticalSersic(intensity=1.0))
        galaxy_1 = ag.Galaxy(
            redshift=0.5, light=ag.lp.EllipticalCoreSersic(intensity=2.0)
        )

        max_log_likelihood_plane = ag.Plane(galaxies=[galaxy_0, galaxy_1])

        phase_dataset_7x7 = ag.PhaseImaging(
            phase_name="test_phase",
            search=mock.MockSearch(
                samples=mock.MockSamples(
                    max_log_likelihood_instance=max_log_likelihood_plane
                )
            ),
        )

        result = phase_dataset_7x7.run(dataset=imaging_7x7, mask=mask_7x7)

        assert isinstance(result.max_log_likelihood_plane, ag.Plane)
        assert result.max_log_likelihood_plane.galaxies[0].light.intensity == 1.0
        assert result.max_log_likelihood_plane.galaxies[1].light.intensity == 2.0
