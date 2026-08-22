import numpy as np
import pytest

import carambola as cb


def make_axial_bar():
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

    # Node 0 fully restrained.
    model.add_support(
        n0,
        True,
        True,
        True,
        True,
        True,
        True,
    )

    # Node 1 can move only in X.
    model.add_support(
        n1,
        False,
        True,
        True,
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


def test_axial_bar_displacement():
    model = make_axial_bar()

    solver = cb.LinearStaticSolver(model)

    result = solver.solve()

    E = 200e9
    A = 0.1 * 0.1
    L = 2.0
    P = 1000.0

    expected_displacement = (
        P * L / (A * E)
    )

    # Node 1 UX is global DOF 6.
    assert result.displacements[6] == pytest.approx(
        expected_displacement,
        rel=1e-12,
    )


def test_axial_bar_fixed_node_displacement():
    model = make_axial_bar()

    result = cb.LinearStaticSolver(
        model
    ).solve()

    # All six DOFs at node 0 are fixed.
    assert np.allclose(
        result.displacements[0:6],
        np.zeros(6),
    )


def test_axial_bar_reaction():
    model = make_axial_bar()

    result = cb.LinearStaticSolver(
        model
    ).solve()

    assert result.reactions[0] == pytest.approx(
        -1000.0,
        rel=1e-12,
    )


def test_force_equilibrium():
    model = make_axial_bar()

    result = cb.LinearStaticSolver(
        model
    ).solve()

    assert result.reactions.sum() == pytest.approx(
        -1000.0,
        rel=1e-12,
    )
