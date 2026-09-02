import numpy as np
import pytest
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
def test_shell_full_block_matches_element():
    model, shell = make_shell_model()

    K = cb.Assembler(
        model
    ).stiffness_matrix()

    dense = np.asarray(
        K.todense()
    )

    shell_dofs = [
        0, 1, 2, 3, 4, 5,
        6, 7, 8, 9, 10, 11,
        12, 13, 14, 15, 16, 17,
    ]

    actual = dense[
        np.ix_(
            shell_dofs,
            shell_dofs,
        )
    ]

    expected = (
        shell.stiffness_matrix()
    )

    assert np.allclose(
        actual,
        expected,
        atol=1e-8,
    )

def test_shell_drilling_rotations_are_stabilized():
    model, shell = make_shell_model()

    K = cb.Assembler(
        model
    ).stiffness_matrix()

    dense = np.asarray(
        K.todense()
    )

    kd = shell._drilling_stiffness()

    # XY-plane shell:
    # node 0 RZ -> 5
    # node 1 RZ -> 11
    # node 2 RZ -> 17

    drilling_dofs = [
        5,
        11,
        17,
    ]

    for dof in drilling_dofs:
        assert dense[
            dof,
            dof
        ] == pytest.approx(
            kd
        )

def test_shell_drilling_stabilization_has_no_cross_coupling():
    model, _ = make_shell_model()

    K = cb.Assembler(
        model
    ).stiffness_matrix()

    dense = np.asarray(
        K.todense()
    )

    drilling_dofs = [
        5,
        11,
        17,
    ]

    for i in drilling_dofs:
        for j in drilling_dofs:
            if i != j:
                assert dense[i, j] == pytest.approx(
                    0.0,
                    abs=1e-12,
                )


def test_shell_has_bending_rotational_stiffness():
    model, _ = make_shell_model()

    K = cb.Assembler(
        model
    ).stiffness_matrix()

    dense = np.asarray(
        K.todense()
    )

    bending_rotations = [
        3, 4,
        9, 10,
        15, 16,
    ]

    block = dense[
        np.ix_(
            bending_rotations,
            bending_rotations,
        )
    ]

    assert np.any(
        np.abs(block) > 1e-12
    )
