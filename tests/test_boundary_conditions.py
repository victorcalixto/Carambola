import numpy as np

import carambola as cb


def make_model():
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

    model.add_truss(
        n0,
        n1,
        steel,
        section,
    )

    model.add_support(
        n0,
        True,
        True,
        True,
    )

    model.add_point_load(
        n1,
        1000.0,
        0.0,
        0.0,
    )

    return model


def test_supports_and_loads_are_stored():
    model = make_model()

    assert model.support_count == 1
    assert model.point_load_count == 1


def test_force_vector():
    model = make_model()

    assembler = cb.Assembler(model)

    F = assembler.force_vector()

    expected = np.array([
        0.0,
        0.0,
        0.0,
        1000.0,
        0.0,
        0.0,
    ])

    assert np.allclose(F, expected)


def test_constrained_dofs():
    model = make_model()

    assembler = cb.Assembler(model)

    assert assembler.constrained_dofs() == [
        0,
        1,
        2,
    ]


def test_free_dofs():
    model = make_model()

    assembler = cb.Assembler(model)

    assert assembler.free_dofs() == [
        3,
        4,
        5,
    ]
