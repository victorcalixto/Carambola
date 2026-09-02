import numpy as np

import carambola as cb




def test_shell_assembler_contains_rotational_stiffness():
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

    model.add_shell(
        n0,
        n1,
        n2,
        prop,
    )
    
    assembler = cb.Assembler(model)
    K = assembler.stiffness_matrix()

    if hasattr(K, "toarray"):
        K = K.toarray()

    rotational_dofs = [
        3, 4,
        9, 10,
        15, 16,
    ]

    rotational_block = K[
        np.ix_(
            rotational_dofs,
            rotational_dofs,
        )
    ]

    assert np.any(
        np.abs(rotational_block) > 1e-12
    )




def test_shell_bending_stiffness_is_assembled():
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

    shell = model.add_shell(
        n0,
        n1,
        n2,
        prop,
    )

    assembler = cb.Assembler(model)
    K = assembler.stiffness_matrix().toarray()
    
    shell_K = shell.stiffness_matrix()

    shell_dofs = [
        0, 1, 2, 3, 4, 5,
        6, 7, 8, 9, 10, 11,
        12, 13, 14, 15, 16, 17,
    ]

    assembled = K[
        np.ix_(
            shell_dofs,
            shell_dofs,
        )
    ]

    assert np.allclose(
        assembled,
        shell_K,
        atol=1e-8,
    )





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
