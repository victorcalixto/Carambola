import numpy as np

import carambola as cb


def make_shell_model():
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

    n2 = model.add_node(
        0.0,
        1.0,
        0.0,
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

    return model, shell


def test_shell_global_assembly_shape():
    model, _ = make_shell_model()

    K = cb.Assembler(
        model
    ).stiffness_matrix()

    # 3 nodes × 6 DOFs
    assert K.shape == (18, 18)


def test_shell_global_assembly_symmetric():
    model, _ = make_shell_model()

    K = cb.Assembler(
        model
    ).stiffness_matrix()

    dense = np.asarray(
        K.todense()
    )

    assert np.allclose(
        dense,
        dense.T,
    )


def test_shell_translation_block_matches_element():
    model, shell = make_shell_model()

    K = cb.Assembler(
        model
    ).stiffness_matrix()

    dense = np.asarray(
        K.todense()
    )

    # Global translational DOFs:
    #
    # node 0:
    # UX = 0
    # UY = 1
    # UZ = 2
    #
    # node 1:
    # UX = 6
    # UY = 7
    # UZ = 8
    #
    # node 2:
    # UX = 12
    # UY = 13
    # UZ = 14

    shell_dofs = [
        0,
        1,
        2,
        6,
        7,
        8,
        12,
        13,
        14,
    ]

    actual = dense[
        np.ix_(
            shell_dofs,
            shell_dofs,
        )
    ]

    expected = (
        shell.membrane_stiffness_matrix()
    )

    assert np.allclose(
        actual,
        expected,
    )


def test_shell_has_no_rotational_stiffness_yet():
    model, _ = make_shell_model()

    K = cb.Assembler(
        model
    ).stiffness_matrix()

    dense = np.asarray(
        K.todense()
    )

    # Rotational DOFs:
    #
    # node 0: RX RY RZ -> 3 4 5
    # node 1: RX RY RZ -> 9 10 11
    # node 2: RX RY RZ -> 15 16 17

    rotational_dofs = [
        3,
        4,
        5,
        9,
        10,
        11,
        15,
        16,
        17,
    ]

    block = dense[
        np.ix_(
            rotational_dofs,
            rotational_dofs,
        )
    ]

    assert np.allclose(
        block,
        0.0,
    )
