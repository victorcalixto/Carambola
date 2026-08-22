import math

import carambola as cb


def test_node_creation():
    model = cb.Model()

    n0 = model.add_node(0.0, 0.0, 0.0)
    n1 = model.add_node(3.0, 2.0, 1.0)

    assert n0.id == 0
    assert n1.id == 1

    assert model.node_count == 2


def test_material():
    steel = cb.Material(
        "Steel",
        210e9,
        0.3,
        7850.0,
    )

    assert steel.name == "Steel"
    assert steel.E == 210e9
    assert steel.nu == 0.3
    assert steel.density == 7850.0

    expected_g = 210e9 / (2.0 * (1.0 + 0.3))

    assert math.isclose(
        steel.G,
        expected_g,
        rel_tol=1e-12,
    )


def test_rectangular_section():
    section = cb.RectangularSection(
        width=0.2,
        height=0.3,
    )

    assert math.isclose(
        section.A,
        0.06,
        rel_tol=1e-12,
    )

    assert section.Iy > 0.0
    assert section.Iz > 0.0
    assert section.J > 0.0


def test_circular_section():
    section = cb.CircularSection(
        radius=0.1,
    )

    assert math.isclose(
        section.A,
        math.pi * 0.1**2,
        rel_tol=1e-12,
    )
