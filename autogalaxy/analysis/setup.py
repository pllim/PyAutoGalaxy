from typing import Optional

import autofit as af

from autogalaxy.hyper.hyper_data import HyperImageSky
from autogalaxy.hyper.hyper_data import HyperBackgroundNoise


class SetupHyper:
    def __init__(
        self,
        hyper_galaxies: bool = False,
        hyper_image_sky: Optional[type(HyperImageSky)] = None,
        hyper_background_noise: Optional[type(HyperBackgroundNoise)] = None,
        search_inversion_cls: Optional[af.NonLinearSearch] = None,
        search_noise_cls: Optional[af.NonLinearSearch] = None,
        search_bc_cls: Optional[af.NonLinearSearch] = None,
        search_pixelization_dict: Optional[dict] = None,
        search_noise_dict: Optional[dict] = None,
        search_bc_dict: Optional[dict] = None,
    ):
        """
        The hyper setup of a pipeline, which controls how hyper-features in PyAutoGalaxy template pipelines run,
        for example controlling whether hyper galaxies are used to scale the noise and the non-linear searches used
        in these searchs.

        Users can write their own pipelines which do not use or require the *SetupHyper* class.

        Parameters
        ----------
        hyper_galaxies
            If a hyper-pipeline is being used, this determines if hyper-galaxy functionality is used to scale the
            noise-map of the dataset throughout the fitting.
        hyper_image_sky
            If a hyper-pipeline is being used, this determines if hyper-galaxy functionality is used include the
            image's background sky component in the model.
        hyper_background_noise
            If a hyper-pipeline is being used, this determines if hyper-galaxy functionality is used include the
            noise-map's background component in the model.
        search_inversion_cls
            The non-linear search used by every hyper model-fit search.
        search_pixelization_dict
            The dictionary of search options for the hyper inversion model-fit searches.
        search_noise_dict
            The dictionary of search options for the hyper noise model-fit searches.
        """

        self.hyper_galaxies = hyper_galaxies

        self.hyper_galaxy_names = None

        self.search_inversion_cls = search_inversion_cls or af.DynestyStatic
        self.search_pixelization_dict = search_pixelization_dict or {
            "nlive": 50,
            "sample": "rstagger",
            "dlogz": 10,
        }

        self.search_noise_cls = search_noise_cls or af.DynestyStatic
        self.search_noise_dict = search_noise_dict or {"nlive": 50, "sample": "rwalk"}

        self.search_bc_cls = search_bc_cls or af.DynestyStatic
        self.search_bc_dict = search_bc_dict or {
            "nlive": 50,
            "sample": "rstagger",
            "dlogz": 10,
        }

        self.hyper_image_sky = hyper_image_sky
        self.hyper_background_noise = hyper_background_noise

    @property
    def hypers_all_off(self):
        if not self.hyper_galaxies:
            if self.hyper_image_sky is None and self.hyper_background_noise is None:
                return True
        return False

    @property
    def hypers_all_except_image_sky_off(self):
        if not self.hyper_galaxies:
            if self.hyper_background_noise is None:
                return True
        return False

    def hyper_image_sky_from(self, result: af.Result, as_model=True):

        if self.hyper_image_sky is not None:
            if as_model:
                if hasattr(result, "hyper"):
                    return result.hyper.model.hyper_image_sky
                return result.model.hyper_image_sky
            if hasattr(result, "hyper"):
                return result.hyper.instance.hyper_image_sky
            return result.instance.hyper_image_sky

    def hyper_background_noise_from(self, result: af.Result):

        if self.hyper_background_noise is not None:
            if hasattr(result, "hyper"):
                return result.hyper.instance.hyper_background_noise
            return result.instance.hyper_background_noise
