import numpy as np

import carambola as cb


def test_six_dof_force_vector():
    model = cb.Model()

    n0 = model.add_node(
        0.0,
        0.0,
        0.0,
    )

    model.add_point_load(
        n0,
        10.0,
        20.0,
        30.0,
        40.0,
        50.0,
        60.0,
    )

    assembler = cb.Assembler(model)

    F = assembler.force_vector()

    assert F.shape == (6,)

    assert np.allclose(
        F,
        [
            10.0,
            20.0,
            30.0,
            40.0,
            50.0,
            60.0,
        ],
    )


def test_six_dof_support():
    model = cb.Model()

    n0 = model.add_node(
        0.0,
        0.0,
        0.0,
    )

    model.add_support(
        n0,
        True,
        False,
        True,
        False,
        True,
        False,
    )

    assembler = cb.Assembler(model)

    assert assembler.constrained_dofs() == [
        0,
        2,
        4,
    ]

    assert assembler.free_dofs() == [
        1,
        3,
        5,
    ]


def test_six_dof_global_stiffness_shape():
    model = cb.Model()

    n0 = model.add_node(0.0, 0.0, 0.0)
    n1 = model.add_node(1.0, 0.0, 0.0)

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

    K = cb.Assembler(
        model
    ).stiffness_matrix()

    assert K.shape == (12, 12)
