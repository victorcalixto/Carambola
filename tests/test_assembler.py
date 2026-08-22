import numpy as np

import carambola as cb


def make_two_element_bar():
    model = cb.Model()

    n0 = model.add_node(0.0, 0.0, 0.0)
    n1 = model.add_node(1.0, 0.0, 0.0)
    n2 = model.add_node(2.0, 0.0, 0.0)

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

    model.add_truss(
        n1,
        n2,
        steel,
        section,
    )

    return model


def test_model_owns_trusses():
    model = make_two_element_bar()

    assert model.node_count == 3
    assert model.truss_count == 2


def test_global_stiffness_shape():
    model = make_two_element_bar()

    assembler = cb.Assembler(model)

    K = assembler.stiffness_matrix()

    # 3 nodes × 6 DOFs
    assert K.shape == (18, 18)


def test_two_element_bar_global_stiffness():
    model = make_two_element_bar()

    assembler = cb.Assembler(model)

    K = assembler.stiffness_matrix()

    E = 200e9
    A = 0.1 * 0.1
    L = 1.0

    k = E * A / L

    dense = np.asarray(K.todense())

    expected_x = np.array([
        [k, -k, 0],
        [-k, 2 * k, -k],
        [0, -k, k],
    ])

    # UX DOFs:
    #
    # node 0 -> 0
    # node 1 -> 6
    # node 2 -> 12
    actual_x = dense[
        np.ix_(
            [0, 6, 12],
            [0, 6, 12],
        )
    ]

    assert np.allclose(
        actual_x,
        expected_x,
    )


def test_global_stiffness_is_symmetric():
    model = make_two_element_bar()

    assembler = cb.Assembler(model)

    K = assembler.stiffness_matrix()

    dense = np.asarray(K.todense())

    assert np.allclose(
        dense,
        dense.T,
    )
