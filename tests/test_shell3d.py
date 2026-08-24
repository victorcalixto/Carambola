import numpy as np
import pytest

import carambola as cb

def test_shell_reference_remains_valid():
    model = cb.Model()

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

    n0 = model.add_node(0.0, 0.0, 0.0)
    n1 = model.add_node(1.0, 0.0, 0.0)
    n2 = model.add_node(0.0, 1.0, 0.0)

    shell = model.add_shell(
        n0,
        n1,
        n2,
        prop,
    )

    for i in range(100):
        a = model.add_node(
            float(i + 10),
            0.0,
            0.0,
        )

        b = model.add_node(
            float(i + 10),
            1.0,
            0.0,
        )

        c = model.add_node(
            float(i + 11),
            0.0,
            0.0,
        )

        model.add_shell(
            a,
            b,
            c,
            prop,
        )

    assert shell.area == pytest.approx(
        0.5
    )

def test_model_owns_shell():
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

    shell = model.add_shell(
        n0,
        n1,
        n2,
        prop,
    )

    assert model.shell_count == 1

    assert len(model.shells) == 1

    assert model.shells[0].area == pytest.approx(
        1.0
    )

    assert shell.area == pytest.approx(
        1.0
    )




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
