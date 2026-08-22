import math

import numpy as np
import pytest

import carambola as cb


def make_basic_truss():
    model = cb.Model()

    n0 = model.add_node(0.0, 0.0, 0.0)
    n1 = model.add_node(2.0, 0.0, 0.0)

    steel = cb.Material(
        "Steel",
        200e9,
        0.3,
        7850.0,
    )

    section = cb.RectangularSection(
        0.1,
        0.1,
    )

    return cb.Truss3D(
        n0,
        n1,
        steel,
        section,
    )


def test_truss_length():
    truss = make_basic_truss()

    assert truss.length == pytest.approx(2.0)


def test_truss_direction():
    truss = make_basic_truss()

    direction = truss.direction

    assert direction[0] == pytest.approx(1.0)
    assert direction[1] == pytest.approx(0.0)
    assert direction[2] == pytest.approx(0.0)


def test_truss_stiffness_matrix_shape():
    truss = make_basic_truss()

    K = truss.stiffness_matrix()

    assert K.shape == (6, 6)


def test_truss_stiffness_matrix_x_axis():
    truss = make_basic_truss()

    K = truss.stiffness_matrix()

    E = 200e9
    A = 0.1 * 0.1
    L = 2.0

    k = E * A / L

    expected = np.array([
        [ k, 0, 0, -k, 0, 0],
        [ 0, 0, 0,  0, 0, 0],
        [ 0, 0, 0,  0, 0, 0],
        [-k, 0, 0,  k, 0, 0],
        [ 0, 0, 0,  0, 0, 0],
        [ 0, 0, 0,  0, 0, 0],
    ])

    assert np.allclose(K, expected)


def test_truss_stiffness_matrix_is_symmetric():
    truss = make_basic_truss()

    K = truss.stiffness_matrix()

    assert np.allclose(K, K.T)


def test_zero_length_truss_rejected():
    model = cb.Model()

    n0 = model.add_node(0.0, 0.0, 0.0)
    n1 = model.add_node(0.0, 0.0, 0.0)

    steel = cb.Material(
        "Steel",
        200e9,
        0.3,
        7850.0,
    )

    section = cb.RectangularSection(
        0.1,
        0.1,
    )

    with pytest.raises(ValueError):
        cb.Truss3D(
            n0,
            n1,
            steel,
            section,
        )
