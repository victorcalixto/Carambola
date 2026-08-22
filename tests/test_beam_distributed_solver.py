import numpy as np
import pytest

import carambola as cb


def make_udl_cantilever():
    model = cb.Model()

    L = 2.0
    q = 1000.0

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

    # Local Y points global Z.
    #
    # Negative local Y therefore means
    # downward global Z.
    model.add_uniform_beam_load(
        beam,
        0.0,
        -q,
        0.0,
    )

    return (
        model,
        n0,
        n1,
        steel,
        section,
        L,
        q,
    )


def test_udl_cantilever_tip_displacement():
    (
        model,
        _,
        n1,
        steel,
        section,
        L,
        q,
    ) = make_udl_cantilever()

    result = cb.LinearStaticSolver(
        model
    ).solve()

    displacement = (
        result.node_displacement(n1)
    )

    expected = (
        q * L**4
        / (
            8.0
            * steel.E
            * section.Iz
        )
    )

    assert displacement[2] == pytest.approx(
        -expected,
        rel=1e-10,
    )


def test_udl_cantilever_reaction():
    (
        model,
        n0,
        _,
        _,
        _,
        L,
        q,
    ) = make_udl_cantilever()

    result = cb.LinearStaticSolver(
        model
    ).solve()

    reaction = (
        result.node_reaction(n0)
    )

    assert reaction[2] == pytest.approx(
        q * L,
        rel=1e-10,
    )


def test_udl_cantilever_fixed_end_moment():
    (
        model,
        n0,
        _,
        _,
        _,
        L,
        q,
    ) = make_udl_cantilever()

    result = cb.LinearStaticSolver(
        model
    ).solve()

    moment = (
        result.node_moment_reaction(n0)
    )

    expected = (
        q * L**2 / 2.0
    )

    assert abs(moment[1]) == pytest.approx(
        expected,
        rel=1e-10,
    )
