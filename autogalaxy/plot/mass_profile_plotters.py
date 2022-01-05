from autoarray.structures.grids.two_d import abstract_grid_2d
from autogalaxy.plot import lensing_obj_plotter
from autogalaxy.plot.mat_wrap import lensing_mat_plot, lensing_include, lensing_visuals
from autoarray.plot.mat_wrap import mat_plot
from autogalaxy.profiles.mass_profiles import mass_profiles as mp
from autogalaxy.util import error_util

import math
from typing import List, Optional


class MassProfilePlotter(lensing_obj_plotter.LensingObjPlotter):
    def __init__(
        self,
        mass_profile: mp.MassProfile,
        grid: abstract_grid_2d.AbstractGrid2D,
        mat_plot_1d: lensing_mat_plot.MatPlot1D = lensing_mat_plot.MatPlot1D(),
        visuals_1d: lensing_visuals.Visuals1D = lensing_visuals.Visuals1D(),
        include_1d: lensing_include.Include1D = lensing_include.Include1D(),
        mat_plot_2d: lensing_mat_plot.MatPlot2D = lensing_mat_plot.MatPlot2D(),
        visuals_2d: lensing_visuals.Visuals2D = lensing_visuals.Visuals2D(),
        include_2d: lensing_include.Include2D = lensing_include.Include2D(),
    ):

        super().__init__(
            mat_plot_2d=mat_plot_2d,
            include_2d=include_2d,
            visuals_2d=visuals_2d,
            mat_plot_1d=mat_plot_1d,
            include_1d=include_1d,
            visuals_1d=visuals_1d,
        )

        self.mass_profile = mass_profile
        self.grid = grid

    @property
    def lensing_obj(self):
        return self.mass_profile

    def figures_1d(self, convergence=False, potential=False):

        if self.mat_plot_1d.yx_plot.plot_axis_type is None:
            plot_axis_type_override = "semilogy"
        else:
            plot_axis_type_override = None

        if convergence:

            convergence_1d = self.mass_profile.convergence_1d_from_grid(grid=self.grid)

            self.mat_plot_1d.plot_yx(
                y=convergence_1d,
                x=convergence_1d.grid_radial,
                visuals_1d=self.visuals_with_include_1d,
                auto_labels=mat_plot.AutoLabels(
                    title="Convergence vs Radius",
                    ylabel="Convergence ",
                    xlabel="Radius",
                    legend=self.lensing_obj.__class__.__name__,
                    filename="convergence_1d",
                ),
                plot_axis_type_override=plot_axis_type_override,
            )

        if potential:

            potential_1d = self.mass_profile.potential_1d_from_grid(grid=self.grid)

            self.mat_plot_1d.plot_yx(
                y=potential_1d,
                x=potential_1d.grid_radial,
                visuals_1d=self.visuals_with_include_1d,
                auto_labels=mat_plot.AutoLabels(
                    title="Potential vs Radius",
                    ylabel="Potential ",
                    xlabel="Radius",
                    legend=self.lensing_obj.__class__.__name__,
                    filename="potential_1d",
                ),
                plot_axis_type_override=plot_axis_type_override,
            )


class MassProfilePDFPlotter(MassProfilePlotter):
    def __init__(
        self,
        mass_profile_pdf_list: List[mp.MassProfile],
        grid: abstract_grid_2d.AbstractGrid2D,
        mat_plot_1d: lensing_mat_plot.MatPlot1D = lensing_mat_plot.MatPlot1D(),
        visuals_1d: lensing_visuals.Visuals1D = lensing_visuals.Visuals1D(),
        include_1d: lensing_include.Include1D = lensing_include.Include1D(),
        mat_plot_2d: lensing_mat_plot.MatPlot2D = lensing_mat_plot.MatPlot2D(),
        visuals_2d: lensing_visuals.Visuals2D = lensing_visuals.Visuals2D(),
        include_2d: lensing_include.Include2D = lensing_include.Include2D(),
        sigma: Optional[float] = 3.0,
    ):

        super().__init__(
            mass_profile=None,
            grid=grid,
            mat_plot_1d=mat_plot_1d,
            visuals_1d=visuals_1d,
            include_1d=include_1d,
            mat_plot_2d=mat_plot_2d,
            visuals_2d=visuals_2d,
            include_2d=include_2d,
        )

        self.mass_profile_pdf_list = mass_profile_pdf_list
        self.sigma = sigma
        self.low_limit = (1 - math.erf(sigma / math.sqrt(2))) / 2

    @property
    def visuals_with_include_1d(self) -> lensing_visuals.Visuals1D:
        """
        Extracts from the `MassProfile` attributes that can be plotted and return them in a `Visuals1D` object.

        Only attributes with `True` entries in the `Include` object are extracted for plotting.

        From a `MassProfilePlotter` the following 1D attributes can be extracted for plotting:

        - einstein_radius: the radius containing 50% of the `MassProfile`'s total integrated luminosity.

        Returns
        -------
        vis.Visuals1D
            The collection of attributes that can be plotted by a `Plotter1D` object.
        """

        if self.include_1d.einstein_radius:

            einstein_radius_list = [
                mass_profile.einstein_radius_from_grid(grid=self.grid)
                for mass_profile in self.mass_profile_pdf_list
            ]

            einstein_radius, einstein_radius_errors = error_util.value_median_and_error_region_via_quantile(
                value_list=einstein_radius_list, low_limit=self.low_limit
            )

        else:

            einstein_radius = None
            einstein_radius_errors = None

        return self.visuals_1d + self.visuals_1d.__class__(
            self.extract_1d("einstein_radius", value=einstein_radius),
            self.extract_1d("einstein_radius", value=einstein_radius_errors),
        )

    def figures_1d(self, convergence=False, potential=False):

        if self.mat_plot_1d.yx_plot.plot_axis_type is None:
            plot_axis_type_override = "semilogy"
        else:
            plot_axis_type_override = None

        if convergence:

            grid_radial = (
                self.mass_profile_pdf_list[0]
                .convergence_1d_from_grid(grid=self.grid)
                .grid_radial
            )

            convergence_1d_list = [
                mass_profile.convergence_1d_from_grid(grid=self.grid)
                for mass_profile in self.mass_profile_pdf_list
            ]

            median_convergence_1d, errors_convergence_1d = error_util.profile_1d_median_and_error_region_via_quantile(
                profile_1d_list=convergence_1d_list, low_limit=self.low_limit
            )

            visuals_1d = self.visuals_with_include_1d + self.visuals_1d.__class__(
                shaded_region=errors_convergence_1d
            )

            self.mat_plot_1d.plot_yx(
                y=median_convergence_1d,
                x=grid_radial,
                visuals_1d=visuals_1d,
                auto_labels=mat_plot.AutoLabels(
                    title="Convergence vs Radius",
                    ylabel="Convergence ",
                    xlabel="Radius",
                    legend=self.mass_profile_pdf_list[0].__class__.__name__,
                    filename="convergence_1d",
                ),
                plot_axis_type_override=plot_axis_type_override,
            )

        if potential:

            grid_radial = (
                self.mass_profile_pdf_list[0]
                .potential_1d_from_grid(grid=self.grid)
                .grid_radial
            )

            potential_1d_list = [
                mass_profile.potential_1d_from_grid(grid=self.grid)
                for mass_profile in self.mass_profile_pdf_list
            ]

            median_potential_1d, errors_potential_1d = error_util.profile_1d_median_and_error_region_via_quantile(
                profile_1d_list=potential_1d_list, low_limit=self.low_limit
            )

            visuals_1d = self.visuals_with_include_1d + self.visuals_1d.__class__(
                shaded_region=errors_potential_1d
            )

            self.mat_plot_1d.plot_yx(
                y=median_potential_1d,
                x=grid_radial,
                visuals_1d=visuals_1d,
                auto_labels=mat_plot.AutoLabels(
                    title="Potential vs Radius",
                    ylabel="Potential ",
                    xlabel="Radius",
                    legend=self.mass_profile_pdf_list[0].__class__.__name__,
                    filename="potential_1d",
                ),
                plot_axis_type_override=plot_axis_type_override,
            )