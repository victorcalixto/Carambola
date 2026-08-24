import numpy as np
import pytest

import carambola as cb


def make_membrane_test():
    model = cb.Model()

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
        False,
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
        E,
        nu,
        thickness,
        P,
    )


def test_shell_membrane_strain_shape():
    model, shell, *_ = make_membrane_test()

    result = cb.LinearStaticSolver(
        model
    ).solve()

    strain = result.shell_membrane_strain(
        shell
    )

    assert strain.shape == (3,)


def test_shell_membrane_stress_shape():
    model, shell, *_ = make_membrane_test()

    result = cb.LinearStaticSolver(
        model
    ).solve()

    stress = result.shell_membrane_stress(
        shell
    )

    assert stress.shape == (3,)


def test_shell_membrane_axial_strain():
    (
        model,
        shell,
        E,
        nu,
        thickness,
        P,
    ) = make_membrane_test()

    result = cb.LinearStaticSolver(
        model
    ).solve()

    strain = result.shell_membrane_strain(
        shell
    )

    expected_ux = (
        2.0
        * P
        * (1.0 - nu**2)
        / (E * thickness)
    )

    # For this right triangle and support setup:
    #
    # epsilon_x = u1_x - u0_x
    #           = expected_ux
    #
    # because L = 1.
    assert strain[0] == pytest.approx(
        expected_ux,
        rel=1e-10,
    )


def test_shell_membrane_stress_matches_constitutive_law():
    model, shell, *_ = make_membrane_test()

    result = cb.LinearStaticSolver(
        model
    ).solve()

    strain = result.shell_membrane_strain(
        shell
    )

    stress = result.shell_membrane_stress(
        shell
    )

    expected = (
        shell.constitutive_matrix()
        @ strain
    )

    assert np.allclose(
        stress,
        expected,
    )


def test_shell_membrane_direct_and_result_api_match():
    model, shell, *_ = make_membrane_test()

    result = cb.LinearStaticSolver(
        model
    ).solve()

    direct_strain = shell.membrane_strain(
        result.displacements
    )

    direct_stress = shell.membrane_stress(
        result.displacements
    )

    assert np.allclose(
        result.shell_membrane_strain(shell),
        direct_strain,
    )

    assert np.allclose(
        result.shell_membrane_stress(shell),
        direct_stress,
    )
