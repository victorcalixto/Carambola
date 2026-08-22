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

    truss = model.add_truss(
        n0,
        n1,
        steel,
        section,
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

    return model, n0, n1, truss


def test_node_displacement_api():
    model, _, n1, _ = make_axial_bar()

    result = cb.LinearStaticSolver(
        model
    ).solve()

    displacement = result.node_displacement(
        n1
    )

    assert np.allclose(
        displacement,
        [
            1.0e-6,
            0.0,
            0.0,
        ],
    )


def test_node_reaction_api():
    model, n0, _, _ = make_axial_bar()

    result = cb.LinearStaticSolver(
        model
    ).solve()

    reaction = result.node_reaction(
        n0
    )

    assert np.allclose(
        reaction,
        [
            -1000.0,
            0.0,
            0.0,
        ],
    )


def test_truss_force_api():
    model, _, _, truss = make_axial_bar()

    result = cb.LinearStaticSolver(
        model
    ).solve()

    assert result.truss_force(
        truss
    ) == pytest.approx(
        1000.0,
        rel=1e-12,
    )


def test_truss_stress_api():
    model, _, _, truss = make_axial_bar()

    result = cb.LinearStaticSolver(
        model
    ).solve()

    assert result.truss_stress(
        truss
    ) == pytest.approx(
        100000.0,
        rel=1e-12,
    )


def test_truss_strain_api():
    model, _, _, truss = make_axial_bar()

    result = cb.LinearStaticSolver(
        model
    ).solve()

    assert result.truss_strain(
        truss
    ) == pytest.approx(
        5.0e-7,
        rel=1e-12,
    )


def test_truss_deformation_api():
    model, _, _, truss = make_axial_bar()

    result = cb.LinearStaticSolver(
        model
    ).solve()

    assert result.truss_deformation(
        truss
    ) == pytest.approx(
        1.0e-6,
        rel=1e-12,
    )
