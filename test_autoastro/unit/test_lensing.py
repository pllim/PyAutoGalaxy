import autofit as af
import autoarray as aa
import autoastro as aast
from autoastro.profiles import geometry_profiles
import math
from skimage import measure
import numpy as np
import pytest
from pyquad import quad_grid
from astropy import cosmology as cosmo
from autoastro import lensing
from test_autoastro.mock import mock_cosmology
import os

test_path = "{}/test_files/config/lensing".format(
    os.path.dirname(os.path.realpath(__file__))
)
af.conf.instance = af.conf.Config(config_path=test_path)


class MockEllipticalIsothermal(
    geometry_profiles.EllipticalProfile, lensing.LensingObject
):
    @af.map_types
    def __init__(
        self,
        centre: aast.dim.Position = (0.0, 0.0),
        axis_ratio: float = 1.0,
        phi: float = 0.0,
        einstein_radius: aast.dim.Length = 1.0,
    ):
        """
        Abstract class for elliptical mass profiles.

        Parameters
        ----------
        centre: (float, float)
            The (y,x) arc-second coordinates of the profile centre.
        axis_ratio : float
            Ellipse's minor-to-major axis ratio (b/a)
        phi : float
            Rotation angle of profile's ellipse counter-clockwise from positive x-axis
        """
        super(MockEllipticalIsothermal, self).__init__(
            centre=centre, axis_ratio=axis_ratio, phi=phi
        )
        self.axis_ratio = axis_ratio
        self.phi = phi
        self.einstein_radius = einstein_radius

    @property
    def unit_mass(self):
        return "angular"

    @property
    def einstein_radius_rescaled(self):
        """Rescale the einstein radius by slope and axis_ratio, to reduce its degeneracy with other mass-profiles
        parameters"""
        return (1.0 / (1 + self.axis_ratio)) * self.einstein_radius

    def convergence_func(self, radius):
        return self.einstein_radius_rescaled * (radius ** 2) ** (-0.5)

    @geometry_profiles.transform_grid
    @geometry_profiles.move_grid_to_radial_minimum
    def convergence_from_grid(self, grid):
        """ Calculate the projected convergence at a given set of arc-second gridded coordinates.

        The *reshape_returned_array* decorator reshapes the NumPy arrays the convergence is outputted on. See \
        *aa.reshape_returned_array* for a description of the output.

        Parameters
        ----------
        grid : aa.Grid
            The grid of (y,x) arc-second coordinates the convergence is computed on.

        """

        covnergence_grid = np.zeros(grid.sub_shape_1d)

        grid_eta = self.grid_to_elliptical_radii(grid)

        for i in range(grid.sub_shape_1d):
            covnergence_grid[i] = self.convergence_func(grid_eta[i])

        return covnergence_grid

    @staticmethod
    def potential_func(u, y, x, axis_ratio):
        eta_u = np.sqrt((u * ((x ** 2) + (y ** 2 / (1 - (1 - axis_ratio ** 2) * u)))))
        return (
            (eta_u / u)
            * (eta_u) ** -1.0
            * eta_u
            / ((1 - (1 - axis_ratio ** 2) * u) ** 0.5)
        )

    @geometry_profiles.transform_grid
    @geometry_profiles.move_grid_to_radial_minimum
    def potential_from_grid(self, grid):
        """
        Calculate the potential at a given set of arc-second gridded coordinates.

        Parameters
        ----------
        grid : aa.Grid
            The grid of (y,x) arc-second coordinates the deflection angles are computed on.

        """

        potential_grid = quad_grid(
            self.potential_func, 0.0, 1.0, grid, args=(self.axis_ratio)
        )[0]

        return self.einstein_radius_rescaled * self.axis_ratio * potential_grid

    @geometry_profiles.transform_grid
    @geometry_profiles.move_grid_to_radial_minimum
    def deflections_from_grid(self, grid):
        """
        Calculate the deflection angles at a given set of arc-second gridded coordinates.

        For coordinates (0.0, 0.0) the analytic calculation of the deflection angle gives a NaN. Therefore, \
        coordinates at (0.0, 0.0) are shifted slightly to (1.0e-8, 1.0e-8).

        Parameters
        ----------
        grid : aa.Grid
            The grid of (y,x) arc-second coordinates the deflection angles are computed on.

        """
        factor = (
            2.0
            * self.einstein_radius_rescaled
            * self.axis_ratio
            / np.sqrt(1 - self.axis_ratio ** 2)
        )

        psi = np.sqrt(
            np.add(
                np.multiply(self.axis_ratio ** 2, np.square(grid[:, 1])),
                np.square(grid[:, 0]),
            )
        )

        deflection_y = np.arctanh(
            np.divide(np.multiply(np.sqrt(1 - self.axis_ratio ** 2), grid[:, 0]), psi)
        )
        deflection_x = np.arctan(
            np.divide(np.multiply(np.sqrt(1 - self.axis_ratio ** 2), grid[:, 1]), psi)
        )
        return self.rotate_grid_from_profile(
            np.multiply(factor, np.vstack((deflection_y, deflection_x)).T)
        )


class MockSphericalIsothermal(MockEllipticalIsothermal):
    @af.map_types
    def __init__(
        self,
        centre: aast.dim.Position = (0.0, 0.0),
        einstein_radius: aast.dim.Length = 1.0,
    ):
        """
        Abstract class for elliptical mass profiles.

        Parameters
        ----------
        centre: (float, float)
            The (y,x) arc-second coordinates of the profile centre.
        axis_ratio : float
            Ellipse's minor-to-major axis ratio (b/a)
        phi : float
            Rotation angle of profile's ellipse counter-clockwise from positive x-axis
        """
        super(MockSphericalIsothermal, self).__init__(
            centre=centre, axis_ratio=1.0, phi=0.0, einstein_radius=einstein_radius
        )

    @geometry_profiles.transform_grid
    @geometry_profiles.move_grid_to_radial_minimum
    def potential_from_grid(self, grid):
        """
        Calculate the potential at a given set of arc-second gridded coordinates.

        Parameters
        ----------
        grid : aa.Grid
            The grid of (y,x) arc-second coordinates the deflection angles are computed on.

        """
        eta = self.grid_to_elliptical_radii(grid)
        return 2.0 * self.einstein_radius_rescaled * eta

    @geometry_profiles.transform_grid
    @geometry_profiles.move_grid_to_radial_minimum
    def deflections_from_grid(self, grid):
        """
        Calculate the deflection angles at a given set of arc-second gridded coordinates.

        Parameters
        ----------
        grid : aa.Grid
            The grid of (y,x) arc-second coordinates the deflection angles are computed on.

        """
        return self.grid_to_grid_cartesian(
            grid=grid,
            radius=np.full(grid.sub_shape_1d, 2.0 * self.einstein_radius_rescaled),
        )


class TestDeflectionsViaPotential(object):
    def test__compare_sis_deflections_via_potential_and_calculation(self):

        sis = MockSphericalIsothermal(centre=(0.0, 0.0), einstein_radius=2.0)

        grid = aa.grid.uniform(shape_2d=(10, 10), pixel_scales=0.05, sub_size=1)

        deflections_via_calculation = sis.deflections_from_grid(grid=grid)

        deflections_via_potential = sis.deflections_via_potential_from_grid(grid=grid)

        mean_error = np.mean(
            deflections_via_potential.in_1d - deflections_via_calculation.in_1d
        )

        assert mean_error < 1e-4

    def test__compare_sie_at_phi_45__deflections_via_potential_and_calculation(self):

        sie = MockEllipticalIsothermal(
            centre=(0.0, 0.0), phi=45.0, axis_ratio=0.8, einstein_radius=2.0
        )

        grid = aa.grid.uniform(shape_2d=(10, 10), pixel_scales=0.05, sub_size=1)

        deflections_via_calculation = sie.deflections_from_grid(grid=grid)

        deflections_via_potential = sie.deflections_via_potential_from_grid(grid=grid)

        mean_error = np.mean(
            deflections_via_potential.in_1d - deflections_via_calculation.in_1d
        )

        assert mean_error < 1e-4

    def test__compare_sie_at_phi_0__deflections_via_potential_and_calculation(self):

        sie = MockEllipticalIsothermal(
            centre=(0.0, 0.0), phi=0.0, axis_ratio=0.8, einstein_radius=2.0
        )

        grid = aa.grid.uniform(shape_2d=(10, 10), pixel_scales=0.05, sub_size=1)

        deflections_via_calculation = sie.deflections_from_grid(grid=grid)

        deflections_via_potential = sie.deflections_via_potential_from_grid(grid=grid)

        mean_error = np.mean(
            deflections_via_potential.in_1d - deflections_via_calculation.in_1d
        )

        assert mean_error < 1e-4


class TestJacobian(object):
    def test__jacobian_components(self):

        sie = MockEllipticalIsothermal(
            centre=(0.0, 0.0), phi=0.0, axis_ratio=0.8, einstein_radius=2.0
        )

        grid = aa.grid.uniform(shape_2d=(100, 100), pixel_scales=0.05, sub_size=1)

        jacobian = sie.jacobian_from_grid(grid=grid)

        A_12 = jacobian[0][1]
        A_21 = jacobian[1][0]

        mean_error = np.mean(A_12.in_1d - A_21.in_1d)

        assert mean_error < 1e-4

        grid = aa.grid.uniform(shape_2d=(100, 100), pixel_scales=0.05, sub_size=2)

        jacobian = sie.jacobian_from_grid(grid=grid)

        A_12 = jacobian[0][1]
        A_21 = jacobian[1][0]

        mean_error = np.mean(A_12.in_1d - A_21.in_1d)

        assert mean_error < 1e-4


class TestMagnification(object):
    def test__compare_magnification_from_eigen_values_and_from_determinant(self):

        sie = MockEllipticalIsothermal(
            centre=(0.0, 0.0), phi=0.0, axis_ratio=0.8, einstein_radius=2.0
        )

        grid = aa.grid.uniform(shape_2d=(100, 100), pixel_scales=0.05, sub_size=1)

        magnification_via_determinant = sie.magnification_from_grid(grid=grid)

        tangential_eigen_value = sie.tangential_eigen_value_from_grid(grid=grid)

        radal_eigen_value = sie.radial_eigen_value_from_grid(grid=grid)

        magnification_via_eigen_values = 1 / (
            tangential_eigen_value * radal_eigen_value
        )

        mean_error = np.mean(
            magnification_via_determinant.in_1d - magnification_via_eigen_values.in_1d
        )

        assert mean_error < 1e-4

        sie = MockEllipticalIsothermal(
            centre=(0.0, 0.0), phi=0.0, axis_ratio=0.8, einstein_radius=2.0
        )

        grid = aa.grid.uniform(shape_2d=(100, 100), pixel_scales=0.05, sub_size=2)

        magnification_via_determinant = sie.magnification_from_grid(grid=grid)

        tangential_eigen_value = sie.tangential_eigen_value_from_grid(grid=grid)

        radal_eigen_value = sie.radial_eigen_value_from_grid(grid=grid)

        magnification_via_eigen_values = 1 / (
            tangential_eigen_value * radal_eigen_value
        )

        mean_error = np.mean(
            magnification_via_determinant.in_1d - magnification_via_eigen_values.in_1d
        )

        assert mean_error < 1e-4

    def test__compare_magnification_from_determinant_and_from_convergence_and_shear(
        self
    ):

        sie = MockEllipticalIsothermal(
            centre=(0.0, 0.0), phi=0.0, axis_ratio=0.8, einstein_radius=2.0
        )

        grid = aa.grid.uniform(shape_2d=(100, 100), pixel_scales=0.05, sub_size=1)

        magnification_via_determinant = sie.magnification_from_grid(grid=grid)

        convergence = sie.convergence_via_jacobian_from_grid(grid=grid)

        shear = sie.shear_via_jacobian_from_grid(grid=grid)

        magnification_via_convergence_and_shear = 1 / (
            (1 - convergence) ** 2 - shear ** 2
        )

        mean_error = np.mean(
            magnification_via_determinant.in_1d
            - magnification_via_convergence_and_shear.in_1d
        )

        assert mean_error < 1e-4

        grid = aa.grid.uniform(shape_2d=(100, 100), pixel_scales=0.05, sub_size=2)

        magnification_via_determinant = sie.magnification_from_grid(grid=grid)

        convergence = sie.convergence_via_jacobian_from_grid(grid=grid)

        shear = sie.shear_via_jacobian_from_grid(grid=grid)

        magnification_via_convergence_and_shear = 1 / (
            (1 - convergence) ** 2 - shear ** 2
        )

        mean_error = np.mean(
            magnification_via_determinant.in_1d
            - magnification_via_convergence_and_shear.in_1d
        )

        assert mean_error < 1e-4


def critical_curve_via_magnification_from_mass_profile_and_grid(mass_profile, grid):

    magnification = mass_profile.magnification_from_grid(grid=grid)

    inverse_magnification = 1 / magnification

    critical_curves_indices = measure.find_contours(inverse_magnification.in_2d, 0)

    no_critical_curves = len(critical_curves_indices)
    contours = []
    critical_curves = []

    for jj in np.arange(no_critical_curves):

        contours.append(critical_curves_indices[jj])
        contour_x, contour_y = contours[jj].T
        pixel_coord = np.stack((contour_x, contour_y), axis=-1)

        critical_curve = grid.geometry.grid_arcsec_from_grid_pixels_1d_for_marching_squares(
            grid_pixels_1d=pixel_coord, shape_2d=magnification.sub_shape_2d
        )

        critical_curves.append(critical_curve)

    return critical_curves


def caustics_via_magnification_from_mass_profile_and_grid(mass_profile, grid):

    caustics = []

    critical_curves = critical_curve_via_magnification_from_mass_profile_and_grid(
        mass_profile=mass_profile, grid=grid
    )

    for i in range(len(critical_curves)):

        critical_curve = critical_curves[i]

        deflections_1d = mass_profile.deflections_from_grid(grid=critical_curve)

        caustic = critical_curve - deflections_1d

        caustics.append(caustic)

    return caustics


class TestConvergenceViajacobian(object):
    def test__compare_sis_convergence_via_jacobian_and_calculation(self):

        sis = MockSphericalIsothermal(centre=(0.0, 0.0), einstein_radius=2.0)

        grid = aa.grid.uniform(shape_2d=(20, 20), pixel_scales=0.05, sub_size=1)

        convergence_via_calculation = sis.convergence_from_grid(grid=grid)

        convergence_via_jacobian = sis.convergence_via_jacobian_from_grid(grid=grid)

        mean_error = np.mean(
            convergence_via_jacobian.in_1d - convergence_via_calculation.in_1d
        )

        assert convergence_via_jacobian.in_2d_binned.shape == (20, 20)
        assert mean_error < 1e-1

        mean_error = np.mean(
            convergence_via_jacobian.in_1d - convergence_via_calculation.in_1d
        )

        assert mean_error < 1e-1

    def test__compare_sie_at_phi_45__convergence_via_jacobian_and_calculation(self):

        sie = MockEllipticalIsothermal(
            centre=(0.0, 0.0), phi=45.0, axis_ratio=0.8, einstein_radius=2.0
        )

        grid = aa.grid.uniform(shape_2d=(20, 20), pixel_scales=0.05, sub_size=1)

        convergence_via_calculation = sie.convergence_from_grid(grid=grid)

        convergence_via_jacobian = sie.convergence_via_jacobian_from_grid(grid=grid)

        mean_error = np.mean(
            convergence_via_jacobian.in_1d - convergence_via_calculation.in_1d
        )

        assert mean_error < 1e-1


class TestCriticalCurvesAndCaustics(object):
    def test_compare_magnification_from_determinant_and_from_convergence_and_shear(
        self
    ):

        sie = MockEllipticalIsothermal(
            centre=(0.0, 0.0), phi=0.0, axis_ratio=0.8, einstein_radius=2.0
        )

        grid = aa.grid.uniform(shape_2d=(100, 100), pixel_scales=0.05, sub_size=2)

        magnification_via_determinant = sie.magnification_from_grid(grid=grid)

        convergence = sie.convergence_via_jacobian_from_grid(grid=grid)

        shear = sie.shear_via_jacobian_from_grid(grid=grid)

        magnification_via_convergence_and_shear = 1 / (
            (1 - convergence) ** 2 - shear ** 2
        )

        mean_error = np.mean(
            magnification_via_determinant - magnification_via_convergence_and_shear
        )

        assert mean_error < 1e-2

    def test__tangential_critical_curve_radii__spherical_isothermal(self):

        sis = MockSphericalIsothermal(centre=(0.0, 0.0), einstein_radius=2.0)

        grid = aa.grid.uniform(shape_2d=(20, 20), pixel_scales=0.25, sub_size=2)

        critical_curves = sis.critical_curves_from_grid(grid=grid)

        tangential_critical_curve = critical_curves[0]

        x_critical_tangential, y_critical_tangential = (
            tangential_critical_curve[:, 1],
            tangential_critical_curve[:, 0],
        )

        assert np.mean(
            x_critical_tangential ** 2 + y_critical_tangential ** 2
        ) == pytest.approx(sis.einstein_radius ** 2, 5e-1)

        sis = MockSphericalIsothermal(centre=(0.0, 0.0), einstein_radius=2.0)

        grid = aa.grid.uniform(shape_2d=(10, 10), pixel_scales=0.5, sub_size=4)

        critical_curves = sis.critical_curves_from_grid(grid=grid)

        tangential_critical_curve = critical_curves[0]

        x_critical_tangential, y_critical_tangential = (
            tangential_critical_curve[:, 1],
            tangential_critical_curve[:, 0],
        )

        assert np.mean(
            x_critical_tangential ** 2 + y_critical_tangential ** 2
        ) == pytest.approx(sis.einstein_radius ** 2, 5e-1)

    def test__tangential_critical_curve_centres__spherical_isothermal(self):

        sis = MockSphericalIsothermal(centre=(0.0, 0.0), einstein_radius=2.0)

        grid = aa.grid.uniform(shape_2d=(20, 20), pixel_scales=0.25, sub_size=1)

        critical_curves = sis.critical_curves_from_grid(grid=grid)

        tangential_critical_curve = critical_curves[0]

        y_centre = np.mean(tangential_critical_curve[:, 0])
        x_centre = np.mean(tangential_critical_curve[:, 1])

        assert -0.03 < y_centre < 0.03
        assert -0.03 < x_centre < 0.03

        grid = aa.grid.uniform(shape_2d=(20, 20), pixel_scales=0.25, sub_size=4)

        critical_curves = sis.critical_curves_from_grid(grid=grid)

        tangential_critical_curve = critical_curves[0]

        y_centre = np.mean(tangential_critical_curve[:, 0])
        x_centre = np.mean(tangential_critical_curve[:, 1])

        assert -0.01 < y_centre < 0.01
        assert -0.01 < x_centre < 0.01

        sis = MockSphericalIsothermal(centre=(0.5, 1.0), einstein_radius=2.0)

        grid = aa.grid.uniform(shape_2d=(60, 60), pixel_scales=0.25, sub_size=1)

        critical_curves = sis.critical_curves_from_grid(grid=grid)

        tangential_critical_curve = critical_curves[0]

        y_centre = np.mean(tangential_critical_curve[:, 0])
        x_centre = np.mean(tangential_critical_curve[:, 1])

        assert 0.47 < y_centre < 0.53
        assert 0.97 < x_centre < 1.03

    def test__radial_critical_curve_centres__spherical_isothermal(self):

        sis = MockSphericalIsothermal(centre=(0.0, 0.0), einstein_radius=2.0)

        grid = aa.grid.uniform(shape_2d=(20, 20), pixel_scales=0.25, sub_size=1)

        critical_curves = sis.critical_curves_from_grid(grid=grid)

        radial_critical_curve = critical_curves[1]

        y_centre = np.mean(radial_critical_curve[:, 0])
        x_centre = np.mean(radial_critical_curve[:, 1])

        assert -0.05 < y_centre < 0.05
        assert -0.05 < x_centre < 0.05

        grid = aa.grid.uniform(shape_2d=(20, 20), pixel_scales=0.25, sub_size=4)

        critical_curves = sis.critical_curves_from_grid(grid=grid)

        radial_critical_curve = critical_curves[1]

        y_centre = np.mean(radial_critical_curve[:, 0])
        x_centre = np.mean(radial_critical_curve[:, 1])

        assert -0.01 < y_centre < 0.01
        assert -0.01 < x_centre < 0.01

        sis = MockSphericalIsothermal(centre=(0.5, 1.0), einstein_radius=2.0)

        grid = aa.grid.uniform(shape_2d=(60, 60), pixel_scales=0.25, sub_size=1)

        critical_curves = sis.critical_curves_from_grid(grid=grid)

        radial_critical_curve = critical_curves[1]

        y_centre = np.mean(radial_critical_curve[:, 0])
        x_centre = np.mean(radial_critical_curve[:, 1])

        assert 0.45 < y_centre < 0.55
        assert 0.95 < x_centre < 1.05

    def test__tangential_caustic_centres__spherical_isothermal(self):

        sis = MockSphericalIsothermal(centre=(0.0, 0.0), einstein_radius=2.0)

        grid = aa.grid.uniform(shape_2d=(20, 20), pixel_scales=0.25, sub_size=1)

        caustics = sis.caustics_from_grid(grid=grid)

        tangential_caustic = caustics[0]

        y_centre = np.mean(tangential_caustic[:, 0])
        x_centre = np.mean(tangential_caustic[:, 1])

        assert -0.03 < y_centre < 0.03
        assert -0.03 < x_centre < 0.03

        grid = aa.grid.uniform(shape_2d=(20, 20), pixel_scales=0.25, sub_size=4)

        caustics = sis.caustics_from_grid(grid=grid)

        tangential_caustic = caustics[0]

        y_centre = np.mean(tangential_caustic[:, 0])
        x_centre = np.mean(tangential_caustic[:, 1])

        assert -0.01 < y_centre < 0.01
        assert -0.01 < x_centre < 0.01

        sis = MockSphericalIsothermal(centre=(0.5, 1.0), einstein_radius=2.0)

        grid = aa.grid.uniform(shape_2d=(60, 60), pixel_scales=0.25, sub_size=1)

        caustics = sis.caustics_from_grid(grid=grid)

        tangential_caustic = caustics[0]

        y_centre = np.mean(tangential_caustic[:, 0])
        x_centre = np.mean(tangential_caustic[:, 1])

        assert 0.47 < y_centre < 0.53
        assert 0.97 < x_centre < 1.03

    def test__radial_caustics_radii__spherical_isothermal(self):

        sis = MockSphericalIsothermal(centre=(0.0, 0.0), einstein_radius=2.0)

        grid = aa.grid.uniform(shape_2d=(10, 10), pixel_scales=0.5, sub_size=4)

        caustics = sis.caustics_from_grid(grid=grid)

        caustic_radial = caustics[1]

        x_caustic_radial, y_caustic_radial = (
            caustic_radial[:, 1],
            caustic_radial[:, 0],
        )

        assert np.mean(x_caustic_radial ** 2 + y_caustic_radial ** 2) == pytest.approx(
            sis.einstein_radius ** 2, 5e-1
        )

    def test__radial_caustic_centres__spherical_isothermal(self):

        sis = MockSphericalIsothermal(centre=(0.0, 0.0), einstein_radius=2.0)

        grid = aa.grid.uniform(shape_2d=(20, 20), pixel_scales=0.25, sub_size=1)

        caustics = sis.caustics_from_grid(grid=grid)

        radial_caustic = caustics[1]

        y_centre = np.mean(radial_caustic[:, 0])
        x_centre = np.mean(radial_caustic[:, 1])

        assert -0.2 < y_centre < 0.2
        assert -0.2 < x_centre < 0.2

        grid = aa.grid.uniform(shape_2d=(20, 20), pixel_scales=0.25, sub_size=4)

        caustics = sis.caustics_from_grid(grid=grid)

        radial_caustic = caustics[1]

        y_centre = np.mean(radial_caustic[:, 0])
        x_centre = np.mean(radial_caustic[:, 1])

        assert -0.09 < y_centre < 0.09
        assert -0.09 < x_centre < 0.09

        sis = MockSphericalIsothermal(centre=(0.5, 1.0), einstein_radius=2.0)

        grid = aa.grid.uniform(shape_2d=(60, 60), pixel_scales=0.25, sub_size=1)

        caustics = sis.caustics_from_grid(grid=grid)

        radial_caustic = caustics[1]

        y_centre = np.mean(radial_caustic[:, 0])
        x_centre = np.mean(radial_caustic[:, 1])

        assert 0.3 < y_centre < 0.7
        assert 0.8 < x_centre < 1.2

    def test__compare_tangential_critical_curves_from_magnification_and_eigen_values(
        self
    ):

        sie = MockEllipticalIsothermal(
            centre=(0.0, 0.0), einstein_radius=2, axis_ratio=0.8, phi=40
        )

        grid = aa.grid.uniform(shape_2d=(20, 20), pixel_scales=0.25, sub_size=1)

        tangential_critical_curve_from_magnification = critical_curve_via_magnification_from_mass_profile_and_grid(
            mass_profile=sie, grid=grid
        )[
            0
        ]

        tangential_critical_curve_from_eigen_values = sie.tangential_critical_curve_from_grid(
            grid=grid
        )

        assert tangential_critical_curve_from_eigen_values == pytest.approx(
            tangential_critical_curve_from_magnification, 5e-1
        )

        grid = aa.grid.uniform(shape_2d=(10, 10), pixel_scales=0.5, sub_size=2)

        tangential_critical_curve_from_magnification = critical_curve_via_magnification_from_mass_profile_and_grid(
            mass_profile=sie, grid=grid
        )[
            0
        ]

        tangential_critical_curve_from_eigen_values = sie.tangential_critical_curve_from_grid(
            grid=grid
        )

        assert tangential_critical_curve_from_eigen_values == pytest.approx(
            tangential_critical_curve_from_magnification, 5e-1
        )

    def test__compare_radial_critical_curves_from_magnification_and_eigen_values(self):

        sie = MockEllipticalIsothermal(
            centre=(0.0, 0.0), einstein_radius=2, axis_ratio=0.8, phi=40
        )

        grid = aa.grid.uniform(shape_2d=(100, 100), pixel_scales=0.05, sub_size=2)

        critical_curve_radial_from_magnification = critical_curve_via_magnification_from_mass_profile_and_grid(
            mass_profile=sie, grid=grid
        )[
            1
        ]

        critical_curve_radial_from_eigen_values = sie.radial_critical_curve_from_grid(
            grid=grid
        )

        assert sum(critical_curve_radial_from_magnification) == pytest.approx(
            sum(critical_curve_radial_from_eigen_values), 5e-1
        )

    def test__compare_tangential_caustic_from_magnification_and_eigen_values(self):

        sie = MockEllipticalIsothermal(
            centre=(0.0, 0.0), einstein_radius=2, axis_ratio=0.8, phi=40
        )

        grid = aa.grid.uniform(shape_2d=(20, 20), pixel_scales=0.25, sub_size=1)

        tangential_caustic_from_magnification = caustics_via_magnification_from_mass_profile_and_grid(
            mass_profile=sie, grid=grid
        )[
            0
        ]

        tangential_caustic_from_eigen_values = sie.tangential_caustic_from_grid(
            grid=grid
        )

        assert sum(tangential_caustic_from_eigen_values) == pytest.approx(
            sum(tangential_caustic_from_magnification), 5e-1
        )

        grid = aa.grid.uniform(shape_2d=(10, 10), pixel_scales=0.5, sub_size=2)

        tangential_caustic_from_magnification = caustics_via_magnification_from_mass_profile_and_grid(
            mass_profile=sie, grid=grid
        )[
            0
        ]

        tangential_caustic_from_eigen_values = sie.tangential_caustic_from_grid(
            grid=grid
        )

        assert sum(tangential_caustic_from_eigen_values) == pytest.approx(
            sum(tangential_caustic_from_magnification), 5e-1
        )

    def test__compare_radial_caustic_from_magnification_and_eigen_values__grid(self):

        sie = MockEllipticalIsothermal(
            centre=(0.0, 0.0), einstein_radius=2, axis_ratio=0.8, phi=40
        )

        grid = aa.grid.uniform(shape_2d=(100, 100), pixel_scales=0.05, sub_size=1)

        caustic_radial_from_magnification = caustics_via_magnification_from_mass_profile_and_grid(
            mass_profile=sie, grid=grid
        )[
            1
        ]

        caustic_radial_from_eigen_values = sie.caustics_from_grid(grid=grid)[1]

        assert sum(caustic_radial_from_eigen_values) == pytest.approx(
            sum(caustic_radial_from_magnification), 7e-1
        )

        grid = aa.grid.uniform(shape_2d=(100, 100), pixel_scales=0.05, sub_size=2)

        caustic_radial_from_magnification = caustics_via_magnification_from_mass_profile_and_grid(
            mass_profile=sie, grid=grid
        )[
            1
        ]

        caustic_radial_from_eigen_values = sie.caustics_from_grid(grid=grid)[1]

        assert sum(caustic_radial_from_eigen_values) == pytest.approx(
            sum(caustic_radial_from_magnification), 5e-1
        )


class TestEinsteinRadiusMassfrom(object):
    def test__tangential_critical_curve_area_from_critical_curve_and_calculation__spherical_isothermal(
        self
    ):

        sis = MockSphericalIsothermal(centre=(0.0, 0.0), einstein_radius=2.0)

        grid = aa.grid.uniform(shape_2d=(20, 20), pixel_scales=0.25, sub_size=2)

        area_crit = sis.area_within_tangential_critical_curve(grid=grid)

        area_calc = np.pi * sis.einstein_radius ** 2

        assert area_crit == pytest.approx(area_calc, 1e-3)

        grid = aa.grid.uniform(shape_2d=(20, 20), pixel_scales=0.25, sub_size=4)

        area_crit = sis.area_within_tangential_critical_curve(grid=grid)

        area_calc = np.pi * sis.einstein_radius ** 2

        assert area_crit == pytest.approx(area_calc, 1e-3)

    def test__einstein_radius_from_tangential_critical_curve__spherical_isothermal(
        self
    ):

        sis = MockSphericalIsothermal(centre=(0.0, 0.0), einstein_radius=2.0)

        grid = aa.grid.uniform(shape_2d=(20, 20), pixel_scales=0.25, sub_size=2)

        radius_from_critical_curve = sis.einstein_radius_in_units(grid=grid)

        assert radius_from_critical_curve == pytest.approx(2.0, 1e-3)

        cosmology = mock_cosmology.MockCosmology(arcsec_per_kpc=2.0, kpc_per_arcsec=0.5)

        radius_from_critical_curve = sis.einstein_radius_in_units(
            grid=grid, unit_length="kpc", redshift_object=2.0, cosmology=cosmology
        )

        assert radius_from_critical_curve == pytest.approx(1.0, 1e-3)

    def test__compare_einstein_radius_from_tangential_critical_curve_and_rescaled__sie(
        self
    ):

        sie = MockEllipticalIsothermal(
            centre=(0.0, 0.0), einstein_radius=2.0, axis_ratio=0.6
        )

        grid = aa.grid.uniform(shape_2d=(50, 50), pixel_scales=0.25, sub_size=2)

        radius_from_critical_curve = sie.einstein_radius_in_units(grid=grid)

        assert radius_from_critical_curve == pytest.approx(1.9360, 1e-3)

        cosmology = mock_cosmology.MockCosmology(arcsec_per_kpc=2.0, kpc_per_arcsec=0.5)

        radius_from_critical_curve = sie.einstein_radius_in_units(
            grid=grid, unit_length="kpc", redshift_object=2.0, cosmology=cosmology
        )

        assert radius_from_critical_curve == pytest.approx(0.5 * 1.9360, 1e-3)

    def test__einstein_mass_from_tangential_critical_curve_and_kappa__spherical_isothermal(
        self
    ):

        sis = MockSphericalIsothermal(centre=(0.0, 0.0), einstein_radius=2.0)

        grid = aa.grid.uniform(shape_2d=(20, 20), pixel_scales=0.25, sub_size=2)

        mass_from_critical_curve = sis.einstein_mass_in_units(
            grid=grid, redshift_object=1, redshift_source=2, unit_mass="angular"
        )

        assert mass_from_critical_curve == pytest.approx(np.pi * 2.0 ** 2.0, 1e-3)

        cosmology = mock_cosmology.MockCosmology(kpc_per_arcsec=1.0, arcsec_per_kpc=1.0, critical_surface_density=0.5)

        mass_from_critical_curve = sis.einstein_mass_in_units(
            grid=grid, redshift_object=1, redshift_source=2, unit_mass="solMass", cosmology=cosmology
        )

        assert mass_from_critical_curve == pytest.approx(2.0 * np.pi * 2.0**2.0, 1e-3)

    def test__einstein_mass_from_tangential_critical_curve_and_radius_rescaled_calc__sie(
        self
    ):

        sie = MockEllipticalIsothermal(
            centre=(0.0, 0.0), einstein_radius=2.0, axis_ratio=0.6
        )

        grid = aa.grid.uniform(shape_2d=(50, 50), pixel_scales=0.25, sub_size=2)

        mass_from_critical_curve = sie.einstein_mass_in_units(
            grid=grid,
            redshift_object=1,
            redshift_source=2,
            unit_mass="solMass",
            cosmology=cosmo.Planck15,
        )

        radius_rescaled = sie.einstein_radius_in_units(grid=grid, unit_length="arcsec")

        sigma_crit = aast.util.cosmology.critical_surface_density_between_redshifts_from_redshifts_and_cosmology(
            redshift_0=1,
            redshift_1=2,
            unit_length="arcsec",
            unit_mass="solMass",
            cosmology=cosmo.Planck15,
        )

        mass_from_einstein_radius = np.pi * radius_rescaled ** 2 * sigma_crit

        assert mass_from_critical_curve == pytest.approx(mass_from_einstein_radius, 1e-3)