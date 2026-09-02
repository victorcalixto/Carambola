import numpy as np
import pytest

import carambola as cb


def triangle_area(vertices, face):
    a = np.asarray(vertices[face[0]])
    b = np.asarray(vertices[face[1]])
    c = np.asarray(vertices[face[2]])

    return 0.5 * np.linalg.norm(
        np.cross(
            b - a,
            c - a,
        )
    )


def triangle_normal(vertices, face):
    a = np.asarray(vertices[face[0]])
    b = np.asarray(vertices[face[1]])
    c = np.asarray(vertices[face[2]])

    return np.cross(
        b - a,
        c - a,
    )


def test_rectangular_shell_mesh_counts():
    mesh = cb.rectangular_shell_mesh(
        2.0,
        1.0,
        2,
        1,
    )

    assert len(mesh.vertices) == 6
    assert len(mesh.faces) == 4


def test_rectangular_shell_mesh_vertex_order():
    mesh = cb.rectangular_shell_mesh(
        2.0,
        1.0,
        2,
        1,
    )

    expected = [
        [0.0, 0.0, 0.0],
        [1.0, 0.0, 0.0],
        [2.0, 0.0, 0.0],
        [0.0, 1.0, 0.0],
        [1.0, 1.0, 0.0],
        [2.0, 1.0, 0.0],
    ]

    assert np.allclose(
        mesh.vertices,
        expected,
    )


def test_rectangular_shell_mesh_connectivity():
    mesh = cb.rectangular_shell_mesh(
        2.0,
        1.0,
        2,
        1,
    )

    expected = [
        [0, 1, 4],
        [0, 4, 3],
        [1, 2, 5],
        [1, 5, 4],
    ]

    assert np.array_equal(
        mesh.faces,
        expected,
    )


def test_rectangular_shell_mesh_positive_normals():
    mesh = cb.rectangular_shell_mesh(
        2.0,
        2.0,
        2,
        2,
    )

    for face in mesh.faces:
        normal = triangle_normal(
            mesh.vertices,
            face,
        )

        assert normal[2] > 0.0


def test_rectangular_shell_mesh_total_area():
    width = 4.0
    height = 3.0

    mesh = cb.rectangular_shell_mesh(
        width,
        height,
        4,
        3,
    )

    total_area = sum(
        triangle_area(
            mesh.vertices,
            face,
        )
        for face in mesh.faces
    )

    assert np.isclose(
        total_area,
        width * height,
    )


def test_rectangular_shell_mesh_general_counts():
    nx = 5
    ny = 4

    mesh = cb.rectangular_shell_mesh(
        10.0,
        8.0,
        nx,
        ny,
    )

    assert len(mesh.vertices) == (
        (nx + 1) * (ny + 1)
    )

    assert len(mesh.faces) == (
        2 * nx * ny
    )


@pytest.mark.parametrize(
    "width,height,nx,ny",
    [
        (0.0, 1.0, 1, 1),
        (-1.0, 1.0, 1, 1),
        (1.0, 0.0, 1, 1),
        (1.0, -1.0, 1, 1),
        (1.0, 1.0, 0, 1),
        (1.0, 1.0, 1, 0),
    ],
)
def test_rectangular_shell_mesh_rejects_invalid_input(
    width,
    height,
    nx,
    ny,
):
    with pytest.raises(ValueError):
        cb.rectangular_shell_mesh(
            width,
            height,
            nx,
            ny,
        )


def make_shell_property():
    material = cb.Material(
        "Steel",
        200e9,
        0.3,
        7850.0,
    )

    return material, cb.ShellProperty(
        material,
        0.01,
    )


def test_add_shell_mesh_to_model():
    material, prop = make_shell_property()

    mesh = cb.rectangular_shell_mesh(
        2.0,
        1.0,
        2,
        1,
    )

    model = cb.Model()

    model.add_shell_mesh(
        mesh,
        prop,
    )

    assert model.node_count == 6
    assert model.shell_count == 4

    model.validate()


def test_add_shell_mesh_preserves_connectivity():
    material, prop = make_shell_property()

    mesh = cb.rectangular_shell_mesh(
        1.0,
        1.0,
        1,
        1,
    )

    model = cb.Model()

    model.add_shell_mesh(
        mesh,
        prop,
    )

    assert model.shell_neighbours(0) == [1]
    assert model.shell_neighbours(1) == [0]


def test_add_shell_mesh_uses_node_offset():
    material, prop = make_shell_property()

    model = cb.Model()

    model.add_node(
        -1.0,
        -1.0,
        0.0,
    )

    mesh = cb.rectangular_shell_mesh(
        1.0,
        1.0,
        1,
        1,
    )

    model.add_shell_mesh(
        mesh,
        prop,
    )

    assert model.node_count == 5
    assert model.shell_count == 2

    assert model.node_count == 5
    assert model.shell_count == 2
