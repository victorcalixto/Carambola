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

    model.add_point_load(
        n1,
        0.0,
        0.0,
        -P,
    )

    return (
        model,
        beam,
        L,
        P,
    )


def test_beam_local_end_force_shape():
    model, beam, _, _ = make_cantilever()

    result = cb.LinearStaticSolver(
        model
    ).solve()

    forces = result.beam_local_end_forces(
        beam
    )

    assert forces.shape == (12,)


def test_cantilever_beam_shear():
    model, beam, _, P = make_cantilever()

    result = cb.LinearStaticSolver(
        model
    ).solve()

    forces = result.beam_local_end_forces(
        beam
    )

    # Local Y corresponds to global Z
    # in the chosen beam orientation.
    assert abs(forces[1]) == pytest.approx(
        P,
        rel=1e-10,
    )

    assert abs(forces[7]) == pytest.approx(
        P,
        rel=1e-10,
    )


def test_cantilever_beam_moment():
    model, beam, L, P = make_cantilever()

    result = cb.LinearStaticSolver(
        model
    ).solve()

    forces = result.beam_local_end_forces(
        beam
    )

    expected = P * L

    # Fixed-end bending moment.
    assert abs(forces[5]) == pytest.approx(
        expected,
        rel=1e-10,
    )


def test_cantilever_axial_force_zero():
    model, beam, _, _ = make_cantilever()

    result = cb.LinearStaticSolver(
        model
    ).solve()

    forces = result.beam_local_end_forces(
        beam
    )

    assert forces[0] == pytest.approx(
        0.0,
        abs=1e-8,
    )

    assert forces[6] == pytest.approx(
        0.0,
        abs=1e-8,
    )


def test_cantilever_torsion_zero():
    model, beam, _, _ = make_cantilever()

    result = cb.LinearStaticSolver(
        model
    ).solve()

    forces = result.beam_local_end_forces(
        beam
    )

    assert forces[3] == pytest.approx(
        0.0,
        abs=1e-8,
    )

    assert forces[9] == pytest.approx(
        0.0,
        abs=1e-8,
    )


def test_beam_result_convenience_api():
    model, beam, _, _ = make_cantilever()

    result = cb.LinearStaticSolver(
        model
    ).solve()

    assert result.beam_axial_force(
        beam
    ) == pytest.approx(
        0.0,
        abs=1e-8,
    )

    assert result.beam_torsion(
        beam
    ) == pytest.approx(
        0.0,
        abs=1e-8,
    )
