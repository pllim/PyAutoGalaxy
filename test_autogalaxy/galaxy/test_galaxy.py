import numpy as np
import pytest

import autogalaxy as ag

from autogalaxy import exc


def test__cls_list_from(lp_0, lp_linear_0):

    gal = ag.Galaxy(redshift=0.5, light_0=lp_0)

    cls_list = gal.cls_list_from(cls=ag.lp.LightProfile)

    assert cls_list == [lp_0]

    gal = ag.Galaxy(
        redshift=0.5, light_linear_0=lp_linear_0, light_linear_1=lp_linear_0
    )

    cls_list = gal.cls_list_from(
        cls=ag.lp.LightProfile, cls_filtered=ag.lp_linear.LightProfileLinear
    )

    assert cls_list == []

    cls_list = gal.cls_list_from(cls=ag.lp.LightProfile)

    assert cls_list == [lp_linear_0, lp_linear_0]

    cls_list = gal.cls_list_from(cls=ag.lp_linear.LightProfileLinear)

    assert cls_list == [lp_linear_0, lp_linear_0]


def test__image_1d_from(sub_grid_1d_7, lp_0, lp_1, gal_x2_lp):

    grid = ag.Grid2D.manual_native([[[1.05, -0.55]]], pixel_scales=1.0)

    lp_image = lp_0.image_1d_from(grid=grid)
    lp_image += lp_1.image_1d_from(grid=grid)

    gal_image = gal_x2_lp.image_1d_from(grid=grid)

    assert lp_image == gal_image


def test__image_2d_from(sub_grid_2d_7x7, gal_x2_lp):

    lp_0_image = gal_x2_lp.light_profile_0.image_2d_from(grid=sub_grid_2d_7x7)
    lp_1_image = gal_x2_lp.light_profile_1.image_2d_from(grid=sub_grid_2d_7x7)

    lp_image = lp_0_image + lp_1_image

    lp_image_0 = (lp_image[0] + lp_image[1] + lp_image[2] + lp_image[3]) / 4.0

    lp_image_1 = (lp_image[4] + lp_image[5] + lp_image[6] + lp_image[7]) / 4.0

    gal_image = gal_x2_lp.image_2d_from(grid=sub_grid_2d_7x7)

    assert gal_image.binned[0] == lp_image_0
    assert gal_image.binned[1] == lp_image_1


def test__image_2d_from__operated_only_input(sub_grid_2d_7x7, lp_0, lp_operated_0):

    image_2d_not_operated = lp_0.image_2d_from(grid=sub_grid_2d_7x7)
    image_2d_operated = lp_operated_0.image_2d_from(grid=sub_grid_2d_7x7)

    galaxy = ag.Galaxy(redshift=0.5, light=lp_0, light_operated=lp_operated_0)

    image_2d = galaxy.image_2d_from(grid=sub_grid_2d_7x7, operated_only=False)
    assert (image_2d == image_2d_not_operated).all()

    image_2d = galaxy.image_2d_from(grid=sub_grid_2d_7x7, operated_only=True)
    assert (image_2d == image_2d_operated).all()

    image_2d = galaxy.image_2d_from(grid=sub_grid_2d_7x7, operated_only=None)
    assert (image_2d == image_2d_not_operated + image_2d_operated).all()


def test__image_2d_list_from__operated_only_input(sub_grid_2d_7x7, lp_0, lp_operated_0):

    image_2d_not_operated = lp_0.image_2d_from(grid=sub_grid_2d_7x7)
    image_2d_operated = lp_operated_0.image_2d_from(grid=sub_grid_2d_7x7)

    galaxy = ag.Galaxy(redshift=0.5, light=lp_0, light_operated=lp_operated_0)

    image_2d_list = galaxy.image_2d_list_from(grid=sub_grid_2d_7x7, operated_only=False)
    assert (image_2d_list[0] == image_2d_not_operated).all()
    assert (image_2d_list[1] == np.zeros((36))).all()

    image_2d_list = galaxy.image_2d_list_from(grid=sub_grid_2d_7x7, operated_only=True)
    assert (image_2d_list[0] == np.zeros((36))).all()
    assert (image_2d_list[1] == image_2d_operated).all()

    image_2d_list = galaxy.image_2d_list_from(grid=sub_grid_2d_7x7, operated_only=None)
    assert (
        image_2d_list[0] + image_2d_list[1] == image_2d_not_operated + image_2d_operated
    ).all()


def test__luminosity_within_circle(lp_0, lp_1, gal_x2_lp):

    lp_0_luminosity = lp_0.luminosity_within_circle_from(radius=0.5)

    lp_1_luminosity = lp_1.luminosity_within_circle_from(radius=0.5)
    gal_luminosity = gal_x2_lp.luminosity_within_circle_from(radius=0.5)

    assert lp_0_luminosity + lp_1_luminosity == gal_luminosity

    gal_no_lp = ag.Galaxy(redshift=0.5, mass=ag.mp.SphIsothermal())

    assert gal_no_lp.luminosity_within_circle_from(radius=1.0) == None


def test__convergence_1d_from(sub_grid_1d_7, mp_0, gal_x1_mp, mp_1, gal_x2_mp):

    grid = ag.Grid2D.manual_native([[[1.05, -0.55], [2.05, -0.55]]], pixel_scales=1.0)

    mp_convergence = mp_0.convergence_1d_from(grid=grid)
    mp_convergence += mp_1.convergence_1d_from(grid=grid)

    gal_convergence = gal_x2_mp.convergence_1d_from(grid=grid)

    assert (mp_convergence == gal_convergence).all()

    # Test explicitly for a profile with an offset centre and ellipticity, given the 1D to 2D projections are nasty.

    grid = ag.Grid2D.manual_native([[(1.05, -0.55), (2.05, -0.55)]], pixel_scales=1.0)

    elliptical_mp = ag.mp.EllIsothermal(
        centre=(0.5, 1.0), elliptical_comps=(0.2, 0.3), einstein_radius=1.0
    )

    galaxy = ag.Galaxy(redshift=0.5, mass=elliptical_mp)

    mp_convergence = elliptical_mp.convergence_1d_from(grid=grid)
    gal_convergence = galaxy.convergence_1d_from(grid=grid)

    assert (mp_convergence == gal_convergence).all()


def test__convergence_2d_from(sub_grid_2d_7x7, mp_0, gal_x1_mp, mp_1, gal_x2_mp):

    mp_0_convergence = gal_x2_mp.mass_profile_0.convergence_2d_from(
        grid=sub_grid_2d_7x7
    )

    mp_1_convergence = gal_x2_mp.mass_profile_1.convergence_2d_from(
        grid=sub_grid_2d_7x7
    )

    mp_convergence = mp_0_convergence + mp_1_convergence

    mp_convergence_0 = (
        mp_convergence[0] + mp_convergence[1] + mp_convergence[2] + mp_convergence[3]
    ) / 4.0

    mp_convergence_1 = (
        mp_convergence[4] + mp_convergence[5] + mp_convergence[6] + mp_convergence[7]
    ) / 4.0

    gal_convergence = gal_x2_mp.convergence_2d_from(grid=sub_grid_2d_7x7)

    assert gal_convergence.binned[0] == mp_convergence_0
    assert gal_convergence.binned[1] == mp_convergence_1


def test__potential_1d_from(sub_grid_1d_7, mp_0, gal_x1_mp, mp_1, gal_x2_mp):

    grid = ag.Grid2D.manual_native([[[1.05, -0.55]]], pixel_scales=1.0)

    mp_potential = mp_0.potential_1d_from(grid=grid)
    mp_potential += mp_1.potential_1d_from(grid=grid)

    gal_convergence = gal_x2_mp.potential_1d_from(grid=grid)

    assert mp_potential == gal_convergence

    # Test explicitly for a profile with an offset centre and ellipticity, given the 1D to 2D projections are nasty.

    grid = ag.Grid2D.manual_native([[(1.05, -0.55), (2.05, -0.55)]], pixel_scales=1.0)

    elliptical_mp = ag.mp.EllIsothermal(
        centre=(0.5, 1.0), elliptical_comps=(0.2, 0.3), einstein_radius=1.0
    )

    galaxy = ag.Galaxy(redshift=0.5, mass=elliptical_mp)

    mp_potential = elliptical_mp.potential_1d_from(grid=grid)
    gal_mp_potential = galaxy.potential_1d_from(grid=grid)

    assert (mp_potential == gal_mp_potential).all()


def test__potential_2d_from(sub_grid_2d_7x7, gal_x2_mp):

    mp_0_potential = gal_x2_mp.mass_profile_0.potential_2d_from(grid=sub_grid_2d_7x7)

    mp_1_potential = gal_x2_mp.mass_profile_1.potential_2d_from(grid=sub_grid_2d_7x7)

    mp_potential = mp_0_potential + mp_1_potential

    mp_potential_0 = (
        mp_potential[0] + mp_potential[1] + mp_potential[2] + mp_potential[3]
    ) / 4.0

    mp_potential_1 = (
        mp_potential[4] + mp_potential[5] + mp_potential[6] + mp_potential[7]
    ) / 4.0

    gal_potential = gal_x2_mp.potential_2d_from(grid=sub_grid_2d_7x7)

    assert gal_potential.binned[0] == mp_potential_0
    assert gal_potential.binned[1] == mp_potential_1


def test__deflections_yx_2d_from(sub_grid_2d_7x7, gal_x2_mp):
    mp_0_deflections = gal_x2_mp.mass_profile_0.deflections_yx_2d_from(
        grid=sub_grid_2d_7x7
    )

    mp_1_deflections = gal_x2_mp.mass_profile_1.deflections_yx_2d_from(
        grid=sub_grid_2d_7x7
    )

    mp_deflections = mp_0_deflections + mp_1_deflections

    mp_deflections_y_0 = (
        mp_deflections[0, 0]
        + mp_deflections[1, 0]
        + mp_deflections[2, 0]
        + mp_deflections[3, 0]
    ) / 4.0

    mp_deflections_y_1 = (
        mp_deflections[4, 0]
        + mp_deflections[5, 0]
        + mp_deflections[6, 0]
        + mp_deflections[7, 0]
    ) / 4.0

    gal_deflections = gal_x2_mp.deflections_yx_2d_from(grid=sub_grid_2d_7x7)

    assert gal_deflections.binned[0, 0] == mp_deflections_y_0
    assert gal_deflections.binned[1, 0] == mp_deflections_y_1

    mp_deflections_x_0 = (
        mp_deflections[0, 1]
        + mp_deflections[1, 1]
        + mp_deflections[2, 1]
        + mp_deflections[3, 1]
    ) / 4.0

    mp_deflections_x_1 = (
        mp_deflections[4, 1]
        + mp_deflections[5, 1]
        + mp_deflections[6, 1]
        + mp_deflections[7, 1]
    ) / 4.0

    gal_deflections = gal_x2_mp.deflections_yx_2d_from(grid=sub_grid_2d_7x7)

    assert gal_deflections.binned[0, 1] == mp_deflections_x_0
    assert gal_deflections.binned[1, 1] == mp_deflections_x_1


def test__no_mass_profile__quantities_returned_as_0s_of_shape_grid(
    sub_grid_2d_7x7, mp_0, gal_x1_mp, mp_1, gal_x2_mp
):

    grid = ag.Grid2D.manual_native(grid=[[[1.05, -0.55]]], pixel_scales=1.0)

    galaxy = ag.Galaxy(redshift=0.5)

    potential = galaxy.potential_2d_from(grid=sub_grid_2d_7x7)

    assert (potential.slim == np.zeros(shape=sub_grid_2d_7x7.sub_shape_slim)).all()

    deflections = galaxy.deflections_yx_2d_from(grid=sub_grid_2d_7x7)

    assert (
        deflections.slim == np.zeros(shape=(sub_grid_2d_7x7.sub_shape_slim, 2))
    ).all()
    assert (deflections.binned.native == np.zeros(shape=(7, 7, 2))).all()


def test__mass_angular_within_circle_from(mp_0, mp_1, gal_x2_mp):

    mp_0_mass = mp_0.mass_angular_within_circle_from(radius=0.5)

    mp_1_mass = mp_1.mass_angular_within_circle_from(radius=0.5)
    gal_mass = gal_x2_mp.mass_angular_within_circle_from(radius=0.5)

    assert mp_0_mass + mp_1_mass == gal_mass

    gal_no_mp = ag.Galaxy(redshift=0.5, light=ag.lp.SphSersic())

    with pytest.raises(exc.GalaxyException):
        gal_no_mp.mass_angular_within_circle_from(radius=1.0)


def test__light_and_mass_profiles__contained_in_light_and_mass_profile_lists(
    lmp_0, lp_0, lp_1, mp_0
):
    gal_x1_lmp = ag.Galaxy(redshift=0.5, profile=lmp_0)

    assert 1 == len(gal_x1_lmp.cls_list_from(cls=ag.lp.LightProfile))
    assert 1 == len(gal_x1_lmp.cls_list_from(cls=ag.mp.MassProfile))

    assert gal_x1_lmp.cls_list_from(cls=ag.mp.MassProfile)[0] == lmp_0
    assert gal_x1_lmp.cls_list_from(cls=ag.lp.LightProfile)[0] == lmp_0

    gal_multi_profiles = ag.Galaxy(redshift=0.5, profile=lmp_0, light=lp_0, sie=mp_0)

    assert 2 == len(gal_multi_profiles.cls_list_from(cls=ag.lp.LightProfile))
    assert 2 == len(gal_multi_profiles.cls_list_from(cls=ag.mp.MassProfile))


def test__contribution_map_from():

    hyper_image = np.ones((3,))

    hyp = ag.HyperGalaxy(contribution_factor=0.0)
    contribution_map = hyp.contribution_map_from(
        hyper_model_image=hyper_image, hyper_galaxy_image=hyper_image
    )

    assert (contribution_map == np.ones((3,))).all()

    hyper_image = np.ones((3,))

    hyp = ag.HyperGalaxy(contribution_factor=0.0)

    galaxy = ag.Galaxy(
        redshift=0.5,
        hyper_galaxy=hyp,
        hyper_galaxy_image=hyper_image,
        hyper_model_image=hyper_image,
    )

    contribution_map = hyp.contribution_map_from(
        hyper_model_image=hyper_image, hyper_galaxy_image=hyper_image
    )

    assert (contribution_map == galaxy.contribution_map).all()


def test__hyper_noise_map_from():

    noise_map = np.array([1.0, 2.0, 3.0])
    contribution_map = np.array([[0.0, 0.5, 1.0]])

    hyper_galaxy = ag.HyperGalaxy(
        contribution_factor=0.0, noise_factor=2.0, noise_power=2.0
    )

    hyper_noise_map = hyper_galaxy.hyper_noise_map_from(
        noise_map=noise_map, contribution_map=contribution_map
    )

    assert (hyper_noise_map == np.array([0.0, 2.0, 18.0])).all()


def test__extract_attribute():

    galaxy = ag.Galaxy(redshift=0.5)

    values = galaxy.extract_attribute(cls=ag.lp.LightProfile, attr_name="value")

    assert values == None

    galaxy = ag.Galaxy(
        redshift=0.5,
        lp_0=ag.m.MockLightProfile(value=0.9, value1=(0.0, 1.0)),
        lp_1=ag.m.MockLightProfile(value=0.8, value1=(2.0, 3.0)),
        lp_2=ag.m.MockLightProfile(value=0.7, value1=(4.0, 5.0)),
    )

    values = galaxy.extract_attribute(cls=ag.lp.LightProfile, attr_name="value")

    assert values.in_list == [0.9, 0.8, 0.7]

    values = galaxy.extract_attribute(cls=ag.lp.LightProfile, attr_name="value1")

    assert values.in_list == [(0.0, 1.0), (2.0, 3.0), (4.0, 5.0)]

    galaxy = ag.Galaxy(
        redshift=0.5,
        lp_3=ag.lp.LightProfile(),
        lp_0=ag.m.MockLightProfile(value=1.0),
        lp_1=ag.m.MockLightProfile(value=2.0),
        mp_0=ag.m.MockMassProfile(value=5.0),
        lp_2=ag.m.MockLightProfile(value=3.0),
    )

    values = galaxy.extract_attribute(cls=ag.lp.LightProfile, attr_name="value")

    assert values.in_list == [1.0, 2.0, 3.0]


def test__image_2d_from__does_not_include_linear_light_profiles(sub_grid_2d_7x7, lp_0):

    lp_linear = ag.lp_linear.EllSersic(effective_radius=2.0, sersic_index=2.0)

    galaxy = ag.Galaxy(redshift=0.5, light_0=lp_0, light_linear=lp_linear)

    lp_image = lp_0.image_2d_from(grid=sub_grid_2d_7x7)

    image = galaxy.image_2d_from(grid=sub_grid_2d_7x7)

    assert (image == lp_image).all()


def test__light_profile_2d_quantity_from_grid__symmetric_profiles_give_symmetric_results():
    lp_0 = ag.lp.EllSersic(centre=(0.0, 0.0), intensity=1.0)

    lp_1 = ag.lp.EllSersic(centre=(100.0, 0.0), intensity=1.0)

    gal_x2_lp = ag.Galaxy(redshift=0.5, light_profile_0=lp_0, light_profile_1=lp_1)

    assert gal_x2_lp.image_2d_from(grid=np.array([[0.0, 0.0]])) == pytest.approx(
        gal_x2_lp.image_2d_from(grid=np.array([[100.0, 0.0]])), 1.0e-4
    )

    assert gal_x2_lp.image_2d_from(grid=np.array([[49.0, 0.0]])) == pytest.approx(
        gal_x2_lp.image_2d_from(grid=np.array([[51.0, 0.0]])), 1.0e-4
    )

    lp_0 = ag.lp.EllSersic(
        elliptical_comps=(0.0, 0.0),
        intensity=1.0,
        effective_radius=0.6,
        sersic_index=4.0,
    )

    lp_1 = ag.lp.EllSersic(
        elliptical_comps=(0.0, 0.0),
        intensity=1.0,
        effective_radius=0.6,
        sersic_index=4.0,
        centre=(100, 0),
    )

    lp_2 = ag.lp.EllSersic(
        elliptical_comps=(0.0, 0.0),
        intensity=1.0,
        effective_radius=0.6,
        sersic_index=4.0,
        centre=(0, 100),
    )

    lp_3 = ag.lp.EllSersic(
        elliptical_comps=(0.0, 0.0),
        intensity=1.0,
        effective_radius=0.6,
        sersic_index=4.0,
        centre=(100, 100),
    )

    gal_x4_lp = ag.Galaxy(
        redshift=0.5,
        light_profile_0=lp_0,
        light_profile_1=lp_1,
        light_profile_3=lp_2,
        light_profile_4=lp_3,
    )

    assert gal_x4_lp.image_2d_from(grid=np.array([[49.0, 0.0]])) == pytest.approx(
        gal_x4_lp.image_2d_from(grid=np.array([[51.0, 0.0]])), 1e-5
    )

    assert gal_x4_lp.image_2d_from(grid=np.array([[0.0, 49.0]])) == pytest.approx(
        gal_x4_lp.image_2d_from(grid=np.array([[0.0, 51.0]])), 1e-5
    )

    assert gal_x4_lp.image_2d_from(grid=np.array([[100.0, 49.0]])) == pytest.approx(
        gal_x4_lp.image_2d_from(grid=np.array([[100.0, 51.0]])), 1e-5
    )

    assert gal_x4_lp.image_2d_from(grid=np.array([[49.0, 49.0]])) == pytest.approx(
        gal_x4_lp.image_2d_from(grid=np.array([[51.0, 51.0]])), 1e-5
    )


def test__mass_profile_2d_quantity_from_grid__symmetric_profiles_give_symmetric_results():

    mp_0 = ag.mp.EllIsothermal(elliptical_comps=(0.333333, 0.0), einstein_radius=1.0)

    mp_1 = ag.mp.EllIsothermal(
        centre=(100, 0), elliptical_comps=(0.333333, 0.0), einstein_radius=1.0
    )

    gal_x4_mp = ag.Galaxy(redshift=0.5, mass_profile_0=mp_0, mass_profile_1=mp_1)

    assert gal_x4_mp.convergence_2d_from(grid=np.array([[1.0, 0.0]])) == pytest.approx(
        gal_x4_mp.convergence_2d_from(grid=np.array([[99.0, 0.0]])), 1.0e-4
    )

    assert gal_x4_mp.convergence_2d_from(grid=np.array([[49.0, 0.0]])) == pytest.approx(
        gal_x4_mp.convergence_2d_from(grid=np.array([[51.0, 0.0]])), 1.0e-4
    )

    assert gal_x4_mp.potential_2d_from(grid=np.array([[1.0, 0.0]])) == pytest.approx(
        gal_x4_mp.potential_2d_from(grid=np.array([[99.0, 0.0]])), 1e-6
    )

    assert gal_x4_mp.potential_2d_from(grid=np.array([[49.0, 0.0]])) == pytest.approx(
        gal_x4_mp.potential_2d_from(grid=np.array([[51.0, 0.0]])), 1e-6
    )

    assert gal_x4_mp.deflections_yx_2d_from(
        grid=np.array([[1.0, 0.0]])
    ) == pytest.approx(
        gal_x4_mp.deflections_yx_2d_from(grid=np.array([[99.0, 0.0]])), 1e-6
    )

    assert gal_x4_mp.deflections_yx_2d_from(
        grid=np.array([[49.0, 0.0]])
    ) == pytest.approx(
        gal_x4_mp.deflections_yx_2d_from(grid=np.array([[51.0, 0.0]])), 1e-6
    )

    mp_0 = ag.mp.SphIsothermal(einstein_radius=1.0)

    mp_1 = ag.mp.SphIsothermal(centre=(100, 0), einstein_radius=1.0)

    mp_2 = ag.mp.SphIsothermal(centre=(0, 100), einstein_radius=1.0)

    mp_3 = ag.mp.SphIsothermal(centre=(100, 100), einstein_radius=1.0)

    gal_x4_mp = ag.Galaxy(
        redshift=0.5,
        mass_profile_0=mp_0,
        mass_profile_1=mp_1,
        mass_profile_2=mp_2,
        mass_profile_3=mp_3,
    )

    assert gal_x4_mp.convergence_2d_from(grid=np.array([[49.0, 0.0]])) == pytest.approx(
        gal_x4_mp.convergence_2d_from(grid=np.array([[51.0, 0.0]])), 1e-5
    )

    assert gal_x4_mp.convergence_2d_from(grid=np.array([[0.0, 49.0]])) == pytest.approx(
        gal_x4_mp.convergence_2d_from(grid=np.array([[0.0, 51.0]])), 1e-5
    )

    assert gal_x4_mp.convergence_2d_from(
        grid=np.array([[100.0, 49.0]])
    ) == pytest.approx(
        gal_x4_mp.convergence_2d_from(grid=np.array([[100.0, 51.0]])), 1e-5
    )

    assert gal_x4_mp.convergence_2d_from(
        grid=np.array([[49.0, 49.0]])
    ) == pytest.approx(
        gal_x4_mp.convergence_2d_from(grid=np.array([[51.0, 51.0]])), 1e-5
    )

    assert gal_x4_mp.potential_2d_from(grid=np.array([[49.0, 0.0]])) == pytest.approx(
        gal_x4_mp.potential_2d_from(grid=np.array([[51.0, 0.0]])), 1e-5
    )

    assert gal_x4_mp.potential_2d_from(grid=np.array([[0.0, 49.0]])) == pytest.approx(
        gal_x4_mp.potential_2d_from(grid=np.array([[0.0, 51.0]])), 1e-5
    )

    assert gal_x4_mp.potential_2d_from(grid=np.array([[100.0, 49.0]])) == pytest.approx(
        gal_x4_mp.potential_2d_from(grid=np.array([[100.0, 51.0]])), 1e-5
    )

    assert gal_x4_mp.potential_2d_from(grid=np.array([[49.0, 49.0]])) == pytest.approx(
        gal_x4_mp.potential_2d_from(grid=np.array([[51.0, 51.0]])), 1e-5
    )

    assert -1.0 * gal_x4_mp.deflections_yx_2d_from(grid=np.array([[49.0, 0.0]]))[
        0, 0
    ] == pytest.approx(
        gal_x4_mp.deflections_yx_2d_from(grid=np.array([[51.0, 0.0]]))[0, 0], 1e-5
    )

    assert 1.0 * gal_x4_mp.deflections_yx_2d_from(grid=np.array([[0.0, 49.0]]))[
        0, 0
    ] == pytest.approx(
        gal_x4_mp.deflections_yx_2d_from(grid=np.array([[0.0, 51.0]]))[0, 0], 1e-5
    )

    assert 1.0 * gal_x4_mp.deflections_yx_2d_from(grid=np.array([[100.0, 49.0]]))[
        0, 0
    ] == pytest.approx(
        gal_x4_mp.deflections_yx_2d_from(grid=np.array([[100.0, 51.0]]))[0, 0], 1e-5
    )

    assert -1.0 * gal_x4_mp.deflections_yx_2d_from(grid=np.array([[49.0, 49.0]]))[
        0, 0
    ] == pytest.approx(
        gal_x4_mp.deflections_yx_2d_from(grid=np.array([[51.0, 51.0]]))[0, 0], 1e-5
    )

    assert 1.0 * gal_x4_mp.deflections_yx_2d_from(grid=np.array([[49.0, 0.0]]))[
        0, 1
    ] == pytest.approx(
        gal_x4_mp.deflections_yx_2d_from(grid=np.array([[51.0, 0.0]]))[0, 1], 1e-5
    )

    assert -1.0 * gal_x4_mp.deflections_yx_2d_from(grid=np.array([[0.0, 49.0]]))[
        0, 1
    ] == pytest.approx(
        gal_x4_mp.deflections_yx_2d_from(grid=np.array([[0.0, 51.0]]))[0, 1], 1e-5
    )

    assert -1.0 * gal_x4_mp.deflections_yx_2d_from(grid=np.array([[100.0, 49.0]]))[
        0, 1
    ] == pytest.approx(
        gal_x4_mp.deflections_yx_2d_from(grid=np.array([[100.0, 51.0]]))[0, 1], 1e-5
    )

    assert -1.0 * gal_x4_mp.deflections_yx_2d_from(grid=np.array([[49.0, 49.0]]))[
        0, 1
    ] == pytest.approx(
        gal_x4_mp.deflections_yx_2d_from(grid=np.array([[51.0, 51.0]]))[0, 1], 1e-5
    )


def test__centre_of_profile_in_right_place():

    grid = ag.Grid2D.uniform(shape_native=(7, 7), pixel_scales=1.0)

    galaxy = ag.Galaxy(
        redshift=0.5,
        mass=ag.mp.EllIsothermal(centre=(2.0, 1.0), einstein_radius=1.0),
        mass_0=ag.mp.EllIsothermal(centre=(2.0, 1.0), einstein_radius=1.0),
    )

    convergence = galaxy.convergence_2d_from(grid=grid)
    max_indexes = np.unravel_index(
        convergence.native.argmax(), convergence.shape_native
    )
    assert max_indexes == (1, 4)

    potential = galaxy.potential_2d_from(grid=grid)
    max_indexes = np.unravel_index(potential.native.argmin(), potential.shape_native)
    assert max_indexes == (1, 4)

    deflections = galaxy.deflections_yx_2d_from(grid=grid)
    assert deflections.native[1, 4, 0] > 0
    assert deflections.native[2, 4, 0] < 0
    assert deflections.native[1, 4, 1] > 0
    assert deflections.native[1, 3, 1] < 0

    galaxy = ag.Galaxy(
        redshift=0.5,
        mass=ag.mp.SphIsothermal(centre=(2.0, 1.0), einstein_radius=1.0),
        mass_0=ag.mp.SphIsothermal(centre=(2.0, 1.0), einstein_radius=1.0),
    )
    convergence = galaxy.convergence_2d_from(grid=grid)
    max_indexes = np.unravel_index(
        convergence.native.argmax(), convergence.shape_native
    )
    assert max_indexes == (1, 4)

    potential = galaxy.potential_2d_from(grid=grid)
    max_indexes = np.unravel_index(potential.native.argmin(), potential.shape_native)
    assert max_indexes == (1, 4)

    deflections = galaxy.deflections_yx_2d_from(grid=grid)
    assert deflections.native[1, 4, 0] > 0
    assert deflections.native[2, 4, 0] < 0
    assert deflections.native[1, 4, 1] > 0
    assert deflections.native[1, 3, 1] < 0

    grid = ag.Grid2DIterate.uniform(
        shape_native=(7, 7),
        pixel_scales=1.0,
        fractional_accuracy=0.99,
        sub_steps=[2, 4],
    )

    galaxy = ag.Galaxy(
        redshift=0.5,
        mass=ag.mp.EllIsothermal(centre=(2.0, 1.0), einstein_radius=1.0),
        mass_0=ag.mp.EllIsothermal(centre=(2.0, 1.0), einstein_radius=1.0),
    )
    convergence = galaxy.convergence_2d_from(grid=grid)
    max_indexes = np.unravel_index(
        convergence.native.argmax(), convergence.shape_native
    )
    assert max_indexes == (1, 4)

    potential = galaxy.potential_2d_from(grid=grid)
    max_indexes = np.unravel_index(potential.native.argmin(), potential.shape_native)
    assert max_indexes == (1, 4)

    deflections = galaxy.deflections_yx_2d_from(grid=grid)
    assert deflections.native[1, 4, 0] >= 0
    assert deflections.native[2, 4, 0] <= 0
    assert deflections.native[1, 4, 1] >= 0
    assert deflections.native[1, 3, 1] <= 0

    galaxy = ag.Galaxy(
        redshift=0.5, mass=ag.mp.SphIsothermal(centre=(2.0, 1.0), einstein_radius=1.0)
    )
    convergence = galaxy.convergence_2d_from(grid=grid)
    max_indexes = np.unravel_index(
        convergence.native.argmax(), convergence.shape_native
    )
    assert max_indexes == (1, 4)

    potential = galaxy.potential_2d_from(grid=grid)
    max_indexes = np.unravel_index(potential.native.argmin(), potential.shape_native)
    assert max_indexes == (1, 4)

    deflections = galaxy.deflections_yx_2d_from(grid=grid)
    assert deflections.native[1, 4, 0] >= 0
    assert deflections.native[2, 4, 0] <= 0
    assert deflections.native[1, 4, 1] >= 0
    assert deflections.native[1, 3, 1] <= 0


def test__cannot_pass_light_or_mass_list():

    light_list = [ag.lp.EllSersic(), ag.lp.EllSersic()]

    with pytest.raises(exc.GalaxyException):

        ag.Galaxy(redshift=0.5, light=light_list)

    mass_list = [ag.mp.EllSersic(), ag.mp.EllSersic()]

    with pytest.raises(exc.GalaxyException):

        ag.Galaxy(redshift=0.5, mass=mass_list)

    with pytest.raises(exc.GalaxyException):

        ag.Galaxy(redshift=0.5, light=light_list, mass=mass_list)


def test__decorator__grid_iterate_in__iterates_array_result_correctly(gal_x1_lp):

    mask = ag.Mask2D.manual(
        mask=[
            [True, True, True, True, True],
            [True, False, False, False, True],
            [True, False, False, False, True],
            [True, False, False, False, True],
            [True, True, True, True, True],
        ],
        pixel_scales=(1.0, 1.0),
    )

    grid = ag.Grid2DIterate.from_mask(mask=mask, fractional_accuracy=1.0, sub_steps=[2])

    galaxy = ag.Galaxy(redshift=0.5, light=ag.lp.EllSersic(intensity=1.0))

    image = galaxy.image_2d_from(grid=grid)

    mask_sub_2 = mask.mask_new_sub_size_from(mask=mask, sub_size=2)
    grid_sub_2 = ag.Grid2D.from_mask(mask=mask_sub_2)
    image_sub_2 = galaxy.image_2d_from(grid=grid_sub_2).binned

    assert (image == image_sub_2).all()

    grid = ag.Grid2DIterate.from_mask(
        mask=mask, fractional_accuracy=0.95, sub_steps=[2, 4, 8]
    )

    galaxy = ag.Galaxy(
        redshift=0.5, light=ag.lp.EllSersic(centre=(0.08, 0.08), intensity=1.0)
    )

    image = galaxy.image_2d_from(grid=grid)

    mask_sub_4 = mask.mask_new_sub_size_from(mask=mask, sub_size=4)
    grid_sub_4 = ag.Grid2D.from_mask(mask=mask_sub_4)
    image_sub_4 = galaxy.image_2d_from(grid=grid_sub_4).binned

    assert image[0] == image_sub_4[0]

    mask_sub_8 = mask.mask_new_sub_size_from(mask=mask, sub_size=8)
    grid_sub_8 = ag.Grid2D.from_mask(mask=mask_sub_8)
    image_sub_8 = galaxy.image_2d_from(grid=grid_sub_8).binned

    assert image[4] == image_sub_8[4]


def test__decorator__grid_iterate_in__iterates_grid_result_correctly(gal_x1_mp):

    mask = ag.Mask2D.manual(
        mask=[
            [True, True, True, True, True],
            [True, False, False, False, True],
            [True, False, False, False, True],
            [True, False, False, False, True],
            [True, True, True, True, True],
        ],
        pixel_scales=(1.0, 1.0),
    )

    grid = ag.Grid2DIterate.from_mask(mask=mask, fractional_accuracy=1.0, sub_steps=[2])

    galaxy = ag.Galaxy(
        redshift=0.5, mass=ag.mp.EllIsothermal(centre=(0.08, 0.08), einstein_radius=1.0)
    )

    deflections = galaxy.deflections_yx_2d_from(grid=grid)

    mask_sub_2 = mask.mask_new_sub_size_from(mask=mask, sub_size=2)
    grid_sub_2 = ag.Grid2D.from_mask(mask=mask_sub_2)
    deflections_sub_2 = galaxy.deflections_yx_2d_from(grid=grid_sub_2).binned

    assert (deflections == deflections_sub_2).all()

    grid = ag.Grid2DIterate.from_mask(
        mask=mask, fractional_accuracy=0.99, sub_steps=[2, 4, 8]
    )

    galaxy = ag.Galaxy(
        redshift=0.5, mass=ag.mp.EllIsothermal(centre=(0.08, 0.08), einstein_radius=1.0)
    )

    deflections = galaxy.deflections_yx_2d_from(grid=grid)

    mask_sub_4 = mask.mask_new_sub_size_from(mask=mask, sub_size=4)
    grid_sub_4 = ag.Grid2D.from_mask(mask=mask_sub_4)
    deflections_sub_4 = galaxy.deflections_yx_2d_from(grid=grid_sub_4).binned

    assert deflections[0, 0] == deflections_sub_4[0, 0]

    mask_sub_8 = mask.mask_new_sub_size_from(mask=mask, sub_size=8)
    grid_sub_8 = ag.Grid2D.from_mask(mask=mask_sub_8)
    deflections_sub_8 = galaxy.deflections_yx_2d_from(grid=grid_sub_8).binned

    assert deflections[4, 0] == deflections_sub_8[4, 0]
