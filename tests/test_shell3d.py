import numpy as np
import pytest

import carambola as cb


def make_shell():
    model = cb.Model()

    n0 = model.add_node(
        0.0, 0.0, 0.0
    )

    n1 = model.add_node(
        2.0, 0.0, 0.0
    )

    n2 = model.add_node(
        0.0, 1.0, 0.0
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

    shell = cb.Shell3D(
        n0,
        n1,
        n2,
        prop,
    )

    return shell


def test_shell_area():
    shell = make_shell()

    assert shell.area == pytest.approx(
        1.0
    )


def test_shell_local_axes():
    shell = make_shell()

    assert np.allclose(
        shell.local_x,
        [1.0, 0.0, 0.0],
    )

    assert np.allclose(
        shell.local_y,
        [0.0, 1.0, 0.0],
    )

    assert np.allclose(
        shell.local_z,
        [0.0, 0.0, 1.0],
    )


def test_shell_axes_are_orthonormal():
    shell = make_shell()

    x = shell.local_x
    y = shell.local_y
    z = shell.local_z

    assert np.dot(x, y) == pytest.approx(
        0.0
    )

    assert np.dot(x, z) == pytest.approx(
        0.0
    )

    assert np.dot(y, z) == pytest.approx(
        0.0
    )

    assert np.linalg.norm(x) == pytest.approx(
        1.0
    )

    assert np.linalg.norm(y) == pytest.approx(
        1.0
    )

    assert np.linalg.norm(z) == pytest.approx(
        1.0
    )


def test_shell_B_matrix_shape():
    shell = make_shell()

    B = shell.strain_displacement_matrix()

    assert B.shape == (3, 6)


def test_shell_constitutive_matrix_shape():
    shell = make_shell()

    D = shell.constitutive_matrix()

    assert D.shape == (3, 3)


def test_shell_local_stiffness_shape():
    shell = make_shell()

    K = (
        shell.local_membrane_stiffness_matrix()
    )

    assert K.shape == (6, 6)


def test_shell_global_stiffness_shape():
    shell = make_shell()

    K = shell.membrane_stiffness_matrix()

    assert K.shape == (9, 9)


def test_shell_stiffness_is_symmetric():
    shell = make_shell()

    K = shell.membrane_stiffness_matrix()

    assert np.allclose(
        K,
        K.T,
    )


def test_zero_area_shell_rejected():
    model = cb.Model()

    n0 = model.add_node(
        0.0, 0.0, 0.0
    )

    n1 = model.add_node(
        1.0, 0.0, 0.0
    )

    n2 = model.add_node(
        2.0, 0.0, 0.0
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

    with pytest.raises(ValueError):
        cb.Shell3D(
            n0,
            n1,
            n2,
            prop,
        )
