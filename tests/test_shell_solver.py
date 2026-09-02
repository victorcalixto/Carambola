import numpy as np
import pytest

import carambola as cb

def test_analysis_result_shell_top_principal_angle():
    model = cb.Model()

    material = cb.Material(
        "Steel",
        200e9,
        0.3,
        7850.0,
    )

    prop = cb.ShellProperty(
        material,
        0.01,
    )

    n0 = model.add_node(0.0, 0.0, 0.0)
    n1 = model.add_node(1.0, 0.0, 0.0)
    n2 = model.add_node(0.0, 1.0, 0.0)

    shell = model.add_shell(
        n0,
        n1,
        n2,
        prop,
    )

    model.add_support(
        n0,
        True, True, True,
        True, True, True,
    )

    model.add_support(
        n1,
        True, True, True,
        True, True, True,
    )

    model.add_support(
        n2,
        True, True, False,
        False, False, True,
    )

    model.add_point_load(
        n2,
        100.0,
        50.0,
        -1000.0,
    )

    result = cb.LinearStaticSolver(
        model
    ).solve()

    xi = 1.0 / 3.0
    eta = 1.0 / 3.0

    top_stress = result.shell_top_stress(
        shell,
        xi,
        eta,
    )

    expected = cb.plane_principal_angle(
        top_stress
    )

    actual = result.shell_top_principal_angle(
        shell,
        xi,
        eta,
    )

    assert np.isclose(
        actual,
        expected,
    )


def test_plane_principal_angle_general_state():
    stress = np.array([
        100.0,
        40.0,
        30.0,
    ])

    angle = cb.plane_principal_angle(
        stress
    )

    expected = 0.5 * np.arctan2(
        60.0,
        60.0,
    )

    assert np.isclose(
        angle,
        expected,
    )




def test_plane_principal_stresses_general_state():
    stress = np.array([
        100.0,
        40.0,
        30.0,
    ])

    principal = cb.plane_principal_stresses(
        stress
    )

    assert np.allclose(
        principal,
        [
            112.42640687119285,
            27.573593128807147,
        ],
    )


def test_analysis_result_shell_surface_principal_stresses():
    model = cb.Model()

    material = cb.Material(
        "Steel",
        200e9,
        0.3,
        7850.0,
    )

    prop = cb.ShellProperty(
        material,
        0.01,
    )

    n0 = model.add_node(0.0, 0.0, 0.0)
    n1 = model.add_node(1.0, 0.0, 0.0)
    n2 = model.add_node(0.0, 1.0, 0.0)

    shell = model.add_shell(
        n0,
        n1,
        n2,
        prop,
    )

    model.add_support(
        n0,
        True, True, True,
        True, True, True,
    )

    model.add_support(
        n1,
        True, True, True,
        True, True, True,
    )

    model.add_support(
        n2,
        True, True, False,
        False, False, True,
    )

    model.add_point_load(
        n2,
        100.0,
        50.0,
        -1000.0,
    )

    result = cb.LinearStaticSolver(
        model
    ).solve()

    xi = 1.0 / 3.0
    eta = 1.0 / 3.0

    top_stress = result.shell_top_stress(
        shell,
        xi,
        eta,
    )

    expected = cb.plane_principal_stresses(
        top_stress
    )

    actual = (
        result.shell_top_principal_stresses(
            shell,
            xi,
            eta,
        )
    )

    assert np.allclose(
        actual,
        expected,
    )

def test_plane_stress_von_mises_uniaxial():
    stress = np.array([
        120.0,
        0.0,
        0.0,
    ])

    vm = cb.plane_stress_von_mises(stress)

    assert np.isclose(
        vm,
        120.0,
    )


def test_plane_stress_von_mises_equal_biaxial():
    stress = np.array([
        120.0,
        120.0,
        0.0,
    ])

    vm = cb.plane_stress_von_mises(stress)

    assert np.isclose(
        vm,
        120.0,
    )


def test_plane_stress_von_mises_pure_shear():
    stress = np.array([
        0.0,
        0.0,
        50.0,
    ])

    vm = cb.plane_stress_von_mises(stress)

    assert np.isclose(
        vm,
        np.sqrt(3.0) * 50.0,
    )

def test_analysis_result_shell_surface_von_mises():
    model = cb.Model()

    material = cb.Material(
        "Steel",
        200e9,
        0.3,
        7850.0,
    )

    prop = cb.ShellProperty(
        material,
        0.01,
    )

    n0 = model.add_node(0.0, 0.0, 0.0)
    n1 = model.add_node(1.0, 0.0, 0.0)
    n2 = model.add_node(0.0, 1.0, 0.0)

    shell = model.add_shell(
        n0,
        n1,
        n2,
        prop,
    )

    model.add_support(
        n0,
        True, True, True,
        True, True, True,
    )

    model.add_support(
        n1,
        True, True, True,
        True, True, True,
    )

    model.add_support(
        n2,
        True, True, False,
        False, False, True,
    )

    model.add_point_load(
        n2,
        100.0,
        50.0,
        -1000.0,
    )

    result = cb.LinearStaticSolver(
        model
    ).solve()

    xi = 1.0 / 3.0
    eta = 1.0 / 3.0

    top = result.shell_top_stress(
        shell,
        xi,
        eta,
    )

    bottom = result.shell_bottom_stress(
        shell,
        xi,
        eta,
    )

    expected_top = np.sqrt(
        top[0] ** 2
        - top[0] * top[1]
        + top[1] ** 2
        + 3.0 * top[2] ** 2
    )

    expected_bottom = np.sqrt(
        bottom[0] ** 2
        - bottom[0] * bottom[1]
        + bottom[1] ** 2
        + 3.0 * bottom[2] ** 2
    )

    assert np.isclose(
        result.shell_top_von_mises(
            shell,
            xi,
            eta,
        ),
        expected_top,
    )

    assert np.isclose(
        result.shell_bottom_von_mises(
            shell,
            xi,
            eta,
        ),
        expected_bottom,
    )




def test_analysis_result_shell_combined_surface_stress():
    model = cb.Model()

    material = cb.Material(
        "Steel",
        200e9,
        0.3,
        7850.0,
    )

    thickness = 0.01

    prop = cb.ShellProperty(
        material,
        thickness,
    )

    n0 = model.add_node(0.0, 0.0, 0.0)
    n1 = model.add_node(1.0, 0.0, 0.0)
    n2 = model.add_node(0.0, 1.0, 0.0)

    shell = model.add_shell(
        n0,
        n1,
        n2,
        prop,
    )

    model.add_support(
        n0,
        True, True, True,
        True, True, True,
    )

    model.add_support(
        n1,
        True, True, True,
        True, True, True,
    )

    model.add_support(
        n2,
        True, True, False,
        False, False, True,
    )

    model.add_point_load(
        n2,
        100.0,
        0.0,
        -1000.0,
    )

    result = cb.LinearStaticSolver(
        model
    ).solve()

    xi = 1.0 / 3.0
    eta = 1.0 / 3.0

    membrane = result.shell_membrane_stress(
        shell
    )

    top_bending = (
        result.shell_top_bending_stress(
            shell,
            xi,
            eta,
        )
    )

    bottom_bending = (
        result.shell_bottom_bending_stress(
            shell,
            xi,
            eta,
        )
    )

    top = result.shell_top_stress(
        shell,
        xi,
        eta,
    )

    bottom = result.shell_bottom_stress(
            shell,
        xi,
        eta,
    )

    assert np.allclose(
        top,
        membrane + top_bending,
    )

    assert np.allclose(
        bottom,
        membrane + bottom_bending,
    )









def test_analysis_result_shell_surface_bending_stresses():
    model = cb.Model()

    material = cb.Material(
        "Steel",
        200e9,
        0.3,
        7850.0,
    )

    thickness = 0.01

    prop = cb.ShellProperty(
        material,
        thickness,
    )

    n0 = model.add_node(0.0, 0.0, 0.0)
    n1 = model.add_node(1.0, 0.0, 0.0)
    n2 = model.add_node(0.0, 1.0, 0.0)

    shell = model.add_shell(
        n0,
        n1,
        n2,
        prop,
    )

    model.add_support(
        n0,
        True, True, True,
        True, True, True,
    )

    model.add_support(
        n1,
        True, True, True,
        True, True, True,
    )

    model.add_support(
        n2,
        True, True, False,
        False, False, True,
    )

    model.add_point_load(
        n2,
        0.0,
        0.0,
        -1000.0,
    )

    result = cb.LinearStaticSolver(
        model
    ).solve()

    top = result.shell_top_bending_stress(
        shell,
        1.0 / 3.0,
        1.0 / 3.0,
    )

    bottom = result.shell_bottom_bending_stress(
        shell,
        1.0 / 3.0,
        1.0 / 3.0,
    )

    assert np.allclose(
        top,
        -bottom,
        rtol=1e-12,
        atol=1e-8,
    )



def test_analysis_result_shell_bending_stress():
    model = cb.Model()

    material = cb.Material(
        "Steel",
        200e9,
        0.3,
        7850.0,
    )

    thickness = 0.01

    prop = cb.ShellProperty(
        material,
        thickness,
    )

    n0 = model.add_node(0.0, 0.0, 0.0)
    n1 = model.add_node(1.0, 0.0, 0.0)
    n2 = model.add_node(0.0, 1.0, 0.0)

    shell = model.add_shell(
        n0,
        n1,
        n2,
        prop,
    )

    model.add_support(
        n0,
        True, True, True,
        True, True, True,
    )

    model.add_support(
        n1,
        True, True, True,
        True, True, True,
    )

    model.add_support(
        n2,
        True, True, False,
        False, False, True,
    )

    model.add_point_load(
        n2,
        0.0,
        0.0,
        -1000.0,
    )

    result = cb.LinearStaticSolver(
        model
    ).solve()

    top = result.shell_bending_stress(
        shell,
        1.0 / 3.0,
        1.0 / 3.0,
        +thickness / 2.0,
    )

    bottom = result.shell_bending_stress(
        shell,
        1.0 / 3.0,
        1.0 / 3.0,
        -thickness / 2.0,
    )

    assert top.shape == (3,)
    assert bottom.shape == (3,)

    assert np.all(
        np.isfinite(top)
    )

    assert np.all(
        np.isfinite(bottom)
    )

    assert np.allclose(
        top,
        -bottom,
        rtol=1e-12,
        atol=1e-8,
    )




def make_membrane_test():
    model = cb.Model()

    # Right triangle in global XY plane.
    n0 = model.add_node(
        0.0,
        0.0,
        0.0,
    )

    n1 = model.add_node(
        1.0,
        0.0,
        0.0,
    )

    n2 = model.add_node(
        0.0,
        1.0,
        0.0,
    )

    E = 200e9
    nu = 0.3
    thickness = 0.01
    P = 1000.0

    steel = cb.Material(
        "Steel",
        E,
        nu,
        7850.0,
    )

    prop = cb.ShellProperty(
        steel,
        thickness,
    )

    shell = model.add_shell(
        n0,
        n1,
        n2,
        prop,
    )

    #
    # Current membrane Shell3D has stiffness only
    # in its local XY plane.
    #
    # Since this shell lies in global XY:
    #
    # active:
    #   UX, UY
    #
    # inactive:
    #   UZ, RX, RY, RZ
    #
    # We deliberately leave only n1.UX free.
    #

    # Node 0: completely fixed.
    model.add_support(
        n0,
        True,
        True,
        True,
        True,
        True,
        True,
    )

    # Node 1:
    # UX free
    # everything else fixed
    model.add_support(
        n1,
        False,
        True,
        True,
        True,
        True,
        True,
    )

    # Node 2: completely fixed.
    model.add_support(
        n2,
        True,
        True,
        True,
        True,
        True,
        True,
    )

    model.add_point_load(
        n1,
        P,
        0.0,
        0.0,
    )

    return (
        model,
        shell,
        n0,
        n1,
        n2,
        E,
        nu,
        thickness,
        P,
    )


def make_bending_test():
    model = cb.Model()

    n0 = model.add_node(
        0.0,
        0.0,
        0.0,
    )

    n1 = model.add_node(
        2.0,
        0.0,
        0.0,
    )

    n2 = model.add_node(
        0.0,
        1.0,
        0.0,
    )

    steel = cb.Material(
        "Steel",
        200e9,
        0.3,
        7850.0,
    )

    prop = cb.ShellProperty(
        steel,
        0.01,
    )

    shell = model.add_shell(
        n0,
        n1,
        n2,
        prop,
    )

    #
    # Bending test:
    #
    # n0 and n1 completely fixed.
    #
    # n2:
    #   UX fixed
    #   UY fixed
    #   UZ free
    #   RX free
    #   RY free
    #   RZ fixed
    #
    # This leaves the DKT bending DOFs
    # [w, rx, ry] active at node 2.
    #

    model.add_support(
        n0,
        True,
        True,
        True,
        True,
        True,
        True,
    )

    model.add_support(
        n1,
        True,
        True,
        True,
        True,
        True,
        True,
    )

    model.add_support(
        n2,
        True,
        True,
        False,
        False,
        False,
        True,
    )

    P = -1000.0

    model.add_point_load(
        n2,
        0.0,
        0.0,
        P,
    )

    return (
        model,
        shell,
        n0,
        n1,
        n2,
        P,
    )

def test_shell_bending_free_dofs():
    (
        model,
        _,
        _,
        _,
        _,
        _,
    ) = make_bending_test()

    free = cb.Assembler(
        model
    ).free_dofs()

    # node 2 starts at global DOF 12:
    #
    # UX = 12
    # UY = 13
    # UZ = 14
    # RX = 15
    # RY = 16
    # RZ = 17
    #
    # UZ, RX, RY are free.
    assert free == [
        14,
        15,
        16,
    ]


def test_shell_membrane_solver_displacement():
    (
        model,
        _,
        _,
        n1,
        _,
        E,
        nu,
        thickness,
        P,
    ) = make_membrane_test()

    result = cb.LinearStaticSolver(
        model
    ).solve()

    displacement = (
        result.node_displacement(n1)
    )

    expected = (
        2.0
        * P
        * (1.0 - nu**2)
        / (E * thickness)
    )

    assert displacement[0] == pytest.approx(
        expected,
        rel=1e-10,
    )

    assert displacement[1] == pytest.approx(
        0.0,
        abs=1e-14,
    )

    assert displacement[2] == pytest.approx(
        0.0,
        abs=1e-14,
    )


def test_shell_bending_solver_displacement():
    (
        model,
        _,
        _,
        _,
        n2,
        _,
    ) = make_bending_test()

    result = cb.LinearStaticSolver(
        model
    ).solve()

    displacement = (
        result.node_displacement(n2)
    )

    assert np.all(
        np.isfinite(displacement)
    )

    assert displacement[0] == pytest.approx(
        0.0,
        abs=1e-14,
    )

    assert displacement[1] == pytest.approx(
        0.0,
        abs=1e-14,
    )

    assert displacement[2] < 0.0

def test_shell_bending_displacement_is_nonzero():
    (
        model,
        _,
        _,
        _,
        n2,
        _,
    ) = make_bending_test()

    result = cb.LinearStaticSolver(
        model
    ).solve()

    displacement = (
        result.node_displacement(n2)
    )

    assert abs(
        displacement[2]
    ) > 1e-12


def test_shell_membrane_constrained_nodes_do_not_move():
    (
        model,
        _,
        n0,
        _,
        n2,
        *_,
    ) = make_membrane_test()

    result = cb.LinearStaticSolver(
        model
    ).solve()

    assert np.allclose(
        result.node_displacement(n0),
        [0.0, 0.0, 0.0],
    )

    assert np.allclose(
        result.node_displacement(n2),
        [0.0, 0.0, 0.0],
    )


def test_shell_membrane_force_equilibrium():
    (
        model,
        _,
        n0,
        _,
        n2,
        _,
        _,
        _,
        P,
    ) = make_membrane_test()

    result = cb.LinearStaticSolver(
        model
    ).solve()

    r0 = result.node_reaction(n0)
    r2 = result.node_reaction(n2)

    total_reaction_x = (
        r0[0] + r2[0]
    )

    assert total_reaction_x == pytest.approx(
        -P,
        rel=1e-10,
    )




def test_shell_bending_rotations_are_finite():
    (
        model,
        _,
        _,
        _,
        n2,
        _,
    ) = make_bending_test()

    result = cb.LinearStaticSolver(
        model
    ).solve()

    rotation = (
        result.node_rotation(n2)
    )

    assert np.all(
        np.isfinite(rotation)
    )

    assert (
        abs(rotation[0]) > 1e-12
        or abs(rotation[1]) > 1e-12
    )

def test_shell_bending_force_equilibrium():
    (
        model,
        _,
        n0,
        n1,
        n2,
        P,
    ) = make_bending_test()

    result = cb.LinearStaticSolver(
        model
    ).solve()

    r0 = result.node_reaction(n0)
    r1 = result.node_reaction(n1)
    r2 = result.node_reaction(n2)

    total_reaction_z = (
        r0[2]
        + r1[2]
        + r2[2]
    )

    assert total_reaction_z == pytest.approx(
        -P,
        rel=1e-9,
        abs=1e-8,
    )

def test_shell_bending_free_uz_has_no_reaction():
    (
        model,
        _,
        _,
        _,
        n2,
        _,
    ) = make_bending_test()

    result = cb.LinearStaticSolver(
        model
    ).solve()

    reaction = result.node_reaction(
        n2
    )

    assert reaction[2] == pytest.approx(
        0.0,
        abs=1e-8,
    )


def test_shell_membrane_free_dof():
    (
        model,
        *_,
    ) = make_membrane_test()

    free = cb.Assembler(
        model
    ).free_dofs()

    # Node 1 UX:
    #
    # node 0 -> DOFs 0-5
    # node 1 -> DOFs 6-11
    #
    # therefore UX(node 1) = 6
    assert free == [6]


def test_shell_membrane_global_stiffness_symmetric():
    (
        model,
        *_,
    ) = make_membrane_test()

    K = cb.Assembler(
        model
    ).stiffness_matrix()

    dense = np.asarray(
        K.todense()
    )

    assert np.allclose(
        dense,
        dense.T,
    )
