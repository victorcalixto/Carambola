import numpy as np
import pytest

import carambola as cb


def make_membrane_test():
    model = cb.Model()

    # Right triangle in global XY plane.
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
        0.0,
        1.0,
        0.0,
    )

    E = 200e9
    nu = 0.3
    thickness = 0.01
    P = 1000.0

    steel = cb.Material(
        "Steel",
        E,
        nu,
        7850.0,
    )

    prop = cb.ShellProperty(
        steel,
        thickness,
    )

    shell = model.add_shell(
        n0,
        n1,
        n2,
        prop,
    )

    #
    # Current membrane Shell3D has stiffness only
    # in its local XY plane.
    #
    # Since this shell lies in global XY:
    #
    # active:
    #   UX, UY
    #
    # inactive:
    #   UZ, RX, RY, RZ
    #
    # We deliberately leave only n1.UX free.
    #

    # Node 0: completely fixed.
    model.add_support(
        n0,
        True,
        True,
        True,
        True,
        True,
        True,
    )

    # Node 1:
    # UX free
    # everything else fixed
    model.add_support(
        n1,
        False,
        True,
        True,
        True,
        True,
        True,
    )

    # Node 2: completely fixed.
    model.add_support(
        n2,
        True,
        True,
        True,
        True,
        True,
        True,
    )

    model.add_point_load(
        n1,
        P,
        0.0,
        0.0,
    )

    return (
        model,
        shell,
        n0,
        n1,
        n2,
        E,
        nu,
        thickness,
        P,
    )


def test_shell_membrane_solver_displacement():
    (
        model,
        _,
        _,
        n1,
        _,
        E,
        nu,
        thickness,
        P,
    ) = make_membrane_test()

    result = cb.LinearStaticSolver(
        model
    ).solve()

    displacement = (
        result.node_displacement(n1)
    )

    expected = (
        2.0
        * P
        * (1.0 - nu**2)
        / (E * thickness)
    )

    assert displacement[0] == pytest.approx(
        expected,
        rel=1e-10,
    )

    assert displacement[1] == pytest.approx(
        0.0,
        abs=1e-14,
    )

    assert displacement[2] == pytest.approx(
        0.0,
        abs=1e-14,
    )


def test_shell_membrane_constrained_nodes_do_not_move():
    (
        model,
        _,
        n0,
        _,
        n2,
        *_,
    ) = make_membrane_test()

    result = cb.LinearStaticSolver(
        model
    ).solve()

    assert np.allclose(
        result.node_displacement(n0),
        [0.0, 0.0, 0.0],
    )

    assert np.allclose(
        result.node_displacement(n2),
        [0.0, 0.0, 0.0],
    )


def test_shell_membrane_force_equilibrium():
    (
        model,
        _,
        n0,
        _,
        n2,
        _,
        _,
        _,
        P,
    ) = make_membrane_test()

    result = cb.LinearStaticSolver(
        model
    ).solve()

    r0 = result.node_reaction(n0)
    r2 = result.node_reaction(n2)

    total_reaction_x = (
        r0[0] + r2[0]
    )

    assert total_reaction_x == pytest.approx(
        -P,
        rel=1e-10,
    )


def test_shell_membrane_free_dof():
    (
        model,
        *_,
    ) = make_membrane_test()

    free = cb.Assembler(
        model
    ).free_dofs()

    # Node 1 UX:
    #
    # node 0 -> DOFs 0-5
    # node 1 -> DOFs 6-11
    #
    # therefore UX(node 1) = 6
    assert free == [6]


def test_shell_membrane_global_stiffness_symmetric():
    (
        model,
        *_,
    ) = make_membrane_test()

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
