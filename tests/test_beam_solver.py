import numpy as np
import pytest

import carambola as cb


def make_cantilever():
    model = cb.Model()

    L = 2.0
    P = 1000.0

    n0 = model.add_node(
        0.0,
        0.0,
        0.0,
    )

    n1 = model.add_node(
        L,
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
        0.2,
        0.3,
    )

    beam = model.add_beam(
        n0,
        n1,
        steel,
        section,
        np.array(
            [0.0, 0.0, 1.0]
        ),
    )

    model.add_support(
        n0,
        True,
        True,
        True,
        True,
        True,
        True,
    )

    # Downward load in global Z.
    model.add_point_load(
        n1,
        0.0,
        0.0,
        -P,
    )

    return (
        model,
        n0,
        n1,
        beam,
        steel,
        section,
        L,
        P,
    )


def test_model_owns_beam():
    model, *_ = make_cantilever()

    assert model.beam_count == 1


def test_cantilever_tip_displacement():
    (
        model,
        _,
        n1,
        _,
        steel,
        section,
        L,
        P,
    ) = make_cantilever()

    result = cb.LinearStaticSolver(
        model
    ).solve()

    displacement = result.node_displacement(n1)

    E = steel.E

    # Beam local Y is global Z for the chosen
    # orientation, therefore bending is about
    # local Z and uses Iz.
    I = section.Iz

    expected = (
        P * L**3
        / (3.0 * E * I)
    )

    assert displacement[2] == pytest.approx(
        -expected,
        rel=1e-10,
    )


def test_cantilever_tip_rotation():
    (
        model,
        _,
        n1,
        _,
        steel,
        section,
        L,
        P,
    ) = make_cantilever()

    result = cb.LinearStaticSolver(
        model
    ).solve()

    rotation = result.node_rotation(n1)

    E = steel.E
    I = section.Iz

    expected = (
        P * L**2
        / (2.0 * E * I)
    )

    # For this axis convention the rotation
    # occurs about global Y.
    assert abs(rotation[1]) == pytest.approx(
        expected,
        rel=1e-10,
    )


def test_cantilever_vertical_reaction():
    (
        model,
        n0,
        _,
        _,
        _,
        _,
        _,
        P,
    ) = make_cantilever()

    result = cb.LinearStaticSolver(
        model
    ).solve()

    reaction = result.node_reaction(n0)

    assert reaction[2] == pytest.approx(
        P,
        rel=1e-10,
    )


def test_cantilever_fixed_end_moment():
    (
        model,
        n0,
        _,
        _,
        _,
        _,
        L,
        P,
    ) = make_cantilever()

    result = cb.LinearStaticSolver(
        model
    ).solve()

    moment = result.node_moment_reaction(n0)

    expected = P * L

    assert abs(moment[1]) == pytest.approx(
        expected,
        rel=1e-10,
    )


def test_beam_global_stiffness_is_symmetric():
    (
        model,
        *_,
    ) = make_cantilever()

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
