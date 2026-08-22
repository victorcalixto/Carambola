import numpy as np
import pytest

import carambola as cb


def make_beam():
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

    return model, beam


def test_uniform_beam_load_storage():
    model, beam = make_beam()

    model.add_uniform_beam_load(
        beam,
        0.0,
        -1000.0,
        0.0,
    )

    assert (
        model.uniform_beam_load_count
        == 1
    )


def test_uniform_qy_equivalent_load():
    model, beam = make_beam()

    q = -1000.0
    L = 2.0

    load = model.add_uniform_beam_load(
        beam,
        0.0,
        q,
        0.0,
    )

    f = load.local_equivalent_nodal_load()

    assert f[1] == pytest.approx(
        q * L / 2.0
    )

    assert f[7] == pytest.approx(
        q * L / 2.0
    )

    assert f[5] == pytest.approx(
        q * L**2 / 12.0
    )

    assert f[11] == pytest.approx(
        -q * L**2 / 12.0
    )


def test_uniform_load_total_force():
    model, beam = make_beam()

    q = -1000.0
    L = 2.0

    load = model.add_uniform_beam_load(
        beam,
        0.0,
        q,
        0.0,
    )

    f = load.local_equivalent_nodal_load()

    assert (
        f[1] + f[7]
    ) == pytest.approx(
        q * L
    )


def test_uniform_axial_load():
    model, beam = make_beam()

    q = 500.0
    L = 2.0

    load = model.add_uniform_beam_load(
        beam,
        q,
        0.0,
        0.0,
    )

    f = load.local_equivalent_nodal_load()

    assert f[0] == pytest.approx(
        q * L / 2.0
    )

    assert f[6] == pytest.approx(
        q * L / 2.0
    )
