import numpy as np
from typing import List, Optional

import autoarray as aa

from autogalaxy.profiles.light_profiles import light_profiles as lp
from autogalaxy.profiles.light_profiles import light_profiles_linear as lp_linear


class Basis(lp.LightProfile):
    def __init__(
        self,
        light_profile_list: List[lp.LightProfile],
        regularization: Optional[aa.AbstractRegularization] = None,
    ):

        super().__init__(
            centre=light_profile_list[0].centre,
            elliptical_comps=light_profile_list[0].elliptical_comps,
        )

        self.light_profile_list = light_profile_list
        self.regularization = regularization

    def image_2d_from(
        self, grid: aa.type.Grid2DLike, operated_only: Optional[bool] = None
    ) -> aa.Array2D:

        return sum(self.image_2d_list_from(grid=grid, operated_only=operated_only))

    def image_2d_list_from(
        self, grid: aa.type.Grid2DLike, operated_only: Optional[bool] = None
    ) -> List[aa.Array2D]:
        return [
            light_profile.image_2d_from(grid=grid, operated_only=operated_only)
            if not isinstance(light_profile, lp_linear.LightProfileLinear)
            else np.zeros((grid.shape[0],))
            for light_profile in self.light_profile_list
        ]
