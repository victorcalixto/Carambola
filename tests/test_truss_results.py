import pytest

import carambola as cb


def make_axial_bar(load=1000.0):
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
        load,
        0.0,
        0.0,
    )

    return model


def test_axial_deformation():
    model = make_axial_bar()

    result = cb.LinearStaticSolver(
        model
    ).solve()

    truss = model.trusses[0]

    deformation = truss.axial_deformation(
        result.displacements
    )

    assert deformation == pytest.approx(
        1.0e-6,
        rel=1e-12,
    )


def test_axial_strain():
    model = make_axial_bar()

    result = cb.LinearStaticSolver(
        model
    ).solve()

    truss = model.trusses[0]

    strain = truss.axial_strain(
        result.displacements
    )

    assert strain == pytest.approx(
        5.0e-7,
        rel=1e-12,
    )


def test_axial_stress():
    model = make_axial_bar()

    result = cb.LinearStaticSolver(
        model
    ).solve()

    truss = model.trusses[0]

    stress = truss.axial_stress(
        result.displacements
    )

    assert stress == pytest.approx(
        100000.0,
        rel=1e-12,
    )


def test_axial_force():
    model = make_axial_bar()

    result = cb.LinearStaticSolver(
        model
    ).solve()

    truss = model.trusses[0]

    force = truss.axial_force(
        result.displacements
    )

    assert force == pytest.approx(
        1000.0,
        rel=1e-12,
    )


def test_compression_is_negative():
    model = make_axial_bar(
        load=-1000.0
    )

    result = cb.LinearStaticSolver(
        model
    ).solve()

    truss = model.trusses[0]

    assert truss.axial_force(
        result.displacements
    ) == pytest.approx(
        -1000.0,
        rel=1e-12,
    )
