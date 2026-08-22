import numpy as np
import pytest

import carambola as cb


def make_beam():
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

    steel = cb.Material(
        "Steel",
        200e9,
        0.3,
        7850.0,
    )

    section = cb.RectangularSection(
        0.2,
        0.3,
    )

    beam = cb.Beam3D(
        n0,
        n1,
        steel,
        section,
        np.array(
            [0.0, 0.0, 1.0]
        ),
    )

    return beam


def test_beam_length():
    beam = make_beam()

    assert beam.length == pytest.approx(
        2.0
    )


def test_beam_local_axes():
    beam = make_beam()

    assert np.allclose(
        beam.local_x,
        [1.0, 0.0, 0.0],
    )

    assert np.allclose(
        beam.local_y,
        [0.0, 0.0, 1.0],
    )

    assert np.allclose(
        beam.local_z,
        [0.0, -1.0, 0.0],
    )


def test_beam_axes_are_orthonormal():
    beam = make_beam()

    x = beam.local_x
    y = beam.local_y
    z = beam.local_z

    assert np.dot(x, y) == pytest.approx(0.0)
    assert np.dot(x, z) == pytest.approx(0.0)
    assert np.dot(y, z) == pytest.approx(0.0)

    assert np.linalg.norm(x) == pytest.approx(1.0)
    assert np.linalg.norm(y) == pytest.approx(1.0)
    assert np.linalg.norm(z) == pytest.approx(1.0)


def test_rotation_matrix_is_orthogonal():
    beam = make_beam()

    R = beam.rotation_matrix()

    identity = np.eye(3)

    assert np.allclose(
        R @ R.T,
        identity,
    )


def test_local_stiffness_shape():
    beam = make_beam()

    K = beam.local_stiffness_matrix()

    assert K.shape == (12, 12)


def test_local_stiffness_is_symmetric():
    beam = make_beam()

    K = beam.local_stiffness_matrix()

    assert np.allclose(
        K,
        K.T,
    )


def test_global_stiffness_shape():
    beam = make_beam()

    K = beam.stiffness_matrix()

    assert K.shape == (12, 12)


def test_global_stiffness_is_symmetric():
    beam = make_beam()

    K = beam.stiffness_matrix()

    assert np.allclose(
        K,
        K.T,
    )


def test_axial_stiffness():
    beam = make_beam()

    K = beam.local_stiffness_matrix()

    E = 200e9
    A = 0.2 * 0.3
    L = 2.0

    expected = E * A / L

    assert K[0, 0] == pytest.approx(
        expected
    )

    assert K[0, 6] == pytest.approx(
        -expected
    )

    assert K[6, 6] == pytest.approx(
        expected
    )


def test_zero_length_beam_rejected():
    model = cb.Model()

    n0 = model.add_node(
        0.0,
        0.0,
        0.0,
    )

    n1 = model.add_node(
        0.0,
        0.0,
        0.0,
    )

    steel = cb.Material(
        "Steel",
        200e9,
        0.3,
        7850.0,
    )

    section = cb.RectangularSection(
        0.2,
        0.3,
    )

    with pytest.raises(ValueError):
        cb.Beam3D(
            n0,
            n1,
            steel,
            section,
        )


def test_parallel_orientation_rejected():
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

    steel = cb.Material(
        "Steel",
        200e9,
        0.3,
        7850.0,
    )

    section = cb.RectangularSection(
        0.2,
        0.3,
    )

    with pytest.raises(ValueError):
        cb.Beam3D(
            n0,
            n1,
            steel,
            section,
            np.array(
                [1.0, 0.0, 0.0]
            ),
        )
