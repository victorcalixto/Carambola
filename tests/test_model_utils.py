import pytest
import carambola as cb
import numpy as np


def test_shell_neighbours_share_edge():
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
    n2 = model.add_node(1.0, 1.0, 0.0)
    n3 = model.add_node(0.0, 1.0, 0.0)

    s0 = model.add_shell(
        n0,
        n1,
        n2,
        prop,
    )

    s1 = model.add_shell(
        n0,
        n2,
        n3,
        prop,
    )

    neighbours = model.shell_neighbours(0)

    assert neighbours == [1]
    
def test_shells_at_node():
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
    n3 = model.add_node(-1.0, 0.0, 0.0)

    model.add_shell(
        n0,
        n1,
        n2,
        prop,
    )

    model.add_shell(
        n0,
        n2,
        n3,
        prop,
    )

    connected = model.shells_at_node(
        n0.id
    )

    assert len(connected) == 2


def test_line_elements_at_node():
    model = cb.Model()

    material = cb.Material(
        "Steel",
        200e9,
        0.3,
        7850.0,
    )

    section = cb.RectangularSection(
        0.1,
        0.1,
    )

    n0 = model.add_node(0.0, 0.0, 0.0)
    n1 = model.add_node(1.0, 0.0, 0.0)
    n2 = model.add_node(0.0, 1.0, 0.0)

    model.add_truss(
        n0,
        n1,
        material,
        section,
    )

    model.add_beam(
        n0,
        n2,
        material,
        section,
    )

    assert len(
        model.trusses_at_node(n0.id)
    ) == 1

    assert len(
        model.beams_at_node(n0.id)
    ) == 1





def test_model_validate_valid_model():
    model = cb.Model()

    material = cb.Material(
        "Steel",
        200e9,
        0.3,
        7850.0,
    )

    section = cb.RectangularSection(
        0.1,
        0.1,
    )

    n0 = model.add_node(0.0, 0.0, 0.0)
    n1 = model.add_node(1.0, 0.0, 0.0)
    n2 = model.add_node(0.0, 1.0, 0.0)

    model.add_truss(
        n0,
        n1,
        material,
        section,
    )

    model.add_beam(
        n0,
        n2,
        material,
        section,
    )

    prop = cb.ShellProperty(
        material,
        0.01,
    )

    model.add_shell(
        n0,
        n1,
        n2,
        prop,
    )

    model.validate()


def test_model_rejects_zero_length_truss():
    model = cb.Model()

    material = cb.Material(
        "Steel",
        200e9,
        0.3,
        7850.0,
    )

    section = cb.RectangularSection(
        0.1,
        0.1,
    )

    n0 = model.add_node(0.0, 0.0, 0.0)
    n1 = model.add_node(0.0, 0.0, 0.0)

    with pytest.raises(
        ValueError,
        match="zero length",
    ):
        model.add_truss(
            n0,
            n1,
            material,
            section,
        )



def test_model_rejects_zero_length_beam():
    model = cb.Model()

    material = cb.Material(
        "Steel",
        200e9,
        0.3,
        7850.0,
    )

    section = cb.RectangularSection(
        0.1,
        0.1,
    )

    n0 = model.add_node(0.0, 0.0, 0.0)
    n1 = model.add_node(0.0, 0.0, 0.0)

    with pytest.raises(
        ValueError,
        match="zero length",
    ):
        model.add_beam(
            n0,
            n1,
            material,
            section,
        )



def test_model_rejects_zero_area_shell():
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
    n2 = model.add_node(2.0, 0.0, 0.0)

    with pytest.raises(
        ValueError,
        match="zero or near-zero area",
    ):
        model.add_shell(
            n0,
            n1,
            n2,
            prop,
        )




def test_model_node_lookup():
    model = cb.Model()

    n0 = model.add_node(
        1.0,
        2.0,
        3.0,
    )

    retrieved = model.node(0)

    assert retrieved.id == n0.id


def test_model_invalid_node_lookup():
    model = cb.Model()

    with pytest.raises(IndexError):
        model.node(0)


def test_model_truss_lookup():
    model = cb.Model()

    material = cb.Material(
        "Steel",
        200e9,
        0.3,
        7850.0,
    )

    section = cb.RectangularSection(
        0.1,
        0.1,
    )

    n0 = model.add_node(0.0, 0.0, 0.0)
    n1 = model.add_node(1.0, 0.0, 0.0)

    truss = model.add_truss(
        n0,
        n1,
        material,
        section,
    )

    retrieved = model.truss(0)

    assert retrieved.length == truss.length


def test_model_beam_lookup():
    model = cb.Model()

    material = cb.Material(
        "Steel",
        200e9,
        0.3,
        7850.0,
    )

    section = cb.RectangularSection(
        0.1,
        0.1,
    )

    n0 = model.add_node(0.0, 0.0, 0.0)
    n1 = model.add_node(1.0, 0.0, 0.0)

    beam = model.add_beam(
        n0,
        n1,
        material,
        section,
    )

    retrieved = model.beam(0)

    assert retrieved.length == beam.length


def test_model_shell_lookup():
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

    retrieved = model.shell(0)

    assert np.isclose(
        retrieved.area,
        shell.area,
    )

def test_model_invalid_element_lookups():
    model = cb.Model()

    with pytest.raises(IndexError):
        model.truss(0)

    with pytest.raises(IndexError):
        model.beam(0)

    with pytest.raises(IndexError):
        model.shell(0)


def test_node_coordinates():
    model = cb.Model()

    model.add_node(
        0.0,
        0.0,
        0.0,
    )

    model.add_node(
        1.0,
        2.0,
        3.0,
    )

    coordinates = model.node_coordinates()

    assert np.allclose(
        coordinates,
        [
            [0.0, 0.0, 0.0],
            [1.0, 2.0, 3.0],
        ],
    )


def test_truss_connectivity():
    model = cb.Model()

    material = cb.Material(
        "Steel",
        200e9,
        0.3,
        7850.0,
    )

    section = cb.RectangularSection(
        0.1,
        0.1,
    )

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
        2.0,
        0.0,
        0.0,
    )

    model.add_truss(
        n0,
        n1,
        material,
        section,
    )

    model.add_truss(
        n1,
        n2,
        material,
        section,
    )

    connectivity = model.truss_connectivity()

    assert np.array_equal(
        connectivity,
        [
            [0, 1],
            [1, 2],
        ],
    )


def test_beam_connectivity():
    model = cb.Model()

    material = cb.Material(
        "Steel",
        200e9,
        0.3,
        7850.0,
    )

    section = cb.RectangularSection(
        0.1,
        0.1,
    )

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

    model.add_beam(
        n0,
        n1,
        material,
        section,
        [0.0, 0.0, 1.0],
    )

    connectivity = model.beam_connectivity()

    assert np.array_equal(
        connectivity,
        [
            [0, 1],
        ],
    )


def test_shell_connectivity():
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

    connectivity = model.shell_connectivity()

    assert np.array_equal(
        connectivity,
        [
            [0, 1, 3],
            [0, 3, 2],
        ],
    )

def test_model_exposes_owned_collections():
    model = cb.Model()

    assert len(model.trusses) == model.truss_count
    assert len(model.beams) == model.beam_count
    assert len(model.shells) == model.shell_count

    assert len(model.supports) == model.support_count
    assert len(model.point_loads) == model.point_load_count

    assert (
        len(model.uniform_beam_loads)
        == model.uniform_beam_load_count
    )

    assert (
        len(model.uniform_shell_pressures)
        == model.uniform_shell_pressure_count
    )
