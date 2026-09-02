import numpy as np

import carambola as cb


def make_material():
    return cb.Material(
        "Steel",
        200e9,
        0.3,
        7850.0,
    )


def make_section():
    return cb.RectangularSection(
        0.02,
        0.01,
    )


def solve_single_bar(
    length=2.0,
    force=10000.0,
):
    model = cb.Model()

    material = make_material()
    section = make_section()

    n0 = model.add_node(
        0.0,
        0.0,
        0.0,
    )

    n1 = model.add_node(
        length,
        0.0,
        0.0,
    )

    truss = model.add_truss(
        n0,
        n1,
        material,
        section,
    )

    # Fully restrain the first node.
    #
    # Truss3D has translational stiffness only,
    # while Carambola uses six DOFs per node.
    # Therefore the rotational DOFs must also
    # be restrained in a pure truss model.
    model.add_support(
        n0,
        True,
        True,
        True,
        True,
        True,
        True,
    )

    # At the loaded node:
    #
    # UX is free.
    # UY and UZ are restrained.
    # RX, RY and RZ are restrained because
    # Truss3D provides no rotational stiffness.
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
        force,
        0.0,
        0.0,
    )

    solver = cb.LinearStaticSolver(
        model
    )

    result = solver.solve()

    return (
        model,
        material,
        section,
        n0,
        n1,
        truss,
        result,
    )


def test_single_bar_axial_displacement():
    length = 2.0
    force = 10000.0

    (
        model,
        material,
        section,
        n0,
        n1,
        truss,
        result,
    ) = solve_single_bar(
        length,
        force,
    )

    E = 200e9
    area = 0.02 * 0.01

    # Analytical solution:
    #
    #     u = F L / (E A)
    #
    expected_displacement = (
        force * length
        / (E * area)
    )

    displacement = (
        result.node_displacement(
            n1
        )
    )

    assert np.isclose(
        displacement[0],
        expected_displacement,
        rtol=1e-10,
        atol=1e-14,
    )

    assert np.isclose(
        displacement[1],
        0.0,
        atol=1e-14,
    )

    assert np.isclose(
        displacement[2],
        0.0,
        atol=1e-14,
    )


def test_single_bar_axial_force():
    force = 10000.0

    (
        model,
        material,
        section,
        n0,
        n1,
        truss,
        result,
    ) = solve_single_bar(
        force=force,
    )

    axial_force = (
        result.truss_force(
            truss
        )
    )

    assert np.isclose(
        axial_force,
        force,
        rtol=1e-10,
        atol=1e-8,
    )


def test_single_bar_stress_and_strain():
    force = 10000.0

    (
        model,
        material,
        section,
        n0,
        n1,
        truss,
        result,
    ) = solve_single_bar(
        force=force,
    )

    E = 200e9
    area = 0.02 * 0.01

    # Analytical solutions:
    #
    #     sigma = F / A
    #
    #     epsilon = sigma / E
    #
    expected_stress = (
        force / area
    )

    expected_strain = (
        expected_stress / E
    )

    stress = (
        result.truss_stress(
            truss
        )
    )

    strain = (
        result.truss_strain(
            truss
        )
    )

    assert np.isclose(
        stress,
        expected_stress,
        rtol=1e-10,
        atol=1e-6,
    )

    assert np.isclose(
        strain,
        expected_strain,
        rtol=1e-10,
        atol=1e-14,
    )


def test_single_bar_support_reaction():
    force = 10000.0

    (
        model,
        material,
        section,
        n0,
        n1,
        truss,
        result,
    ) = solve_single_bar(
        force=force,
    )

    reaction = (
        result.node_reaction(
            n0
        )
    )

    # Global equilibrium:
    #
    #     Rx + F = 0
    #
    # therefore:
    #
    #     Rx = -F
    #
    assert np.isclose(
        reaction[0],
        -force,
        rtol=1e-10,
        atol=1e-8,
    )

    assert np.isclose(
        reaction[1],
        0.0,
        atol=1e-8,
    )

    assert np.isclose(
        reaction[2],
        0.0,
        atol=1e-8,
    )


def test_two_element_bar_matches_analytical_solution():
    model = cb.Model()

    material = make_material()
    section = make_section()

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
        2.0,
        0.0,
        0.0,
    )

    t0 = model.add_truss(
        n0,
        n1,
        material,
        section,
    )

    t1 = model.add_truss(
        n1,
        n2,
        material,
        section,
    )

    # Fixed end.
    model.add_support(
        n0,
        True,
        True,
        True,
        True,
        True,
        True,
    )

    # Interior truss node:
    # only UX remains free.
    model.add_support(
        n1,
        False,
        True,
        True,
        True,
        True,
        True,
    )

    # Loaded end:
    # only UX remains free.
    model.add_support(
        n2,
        False,
        True,
        True,
        True,
        True,
        True,
    )

    force = 10000.0

    model.add_point_load(
        n2,
        force,
        0.0,
        0.0,
    )

    result = (
        cb.LinearStaticSolver(
            model
        )
        .solve()
    )

    E = 200e9
    area = 0.02 * 0.01

    # At x = 1 m:
    #
    #     u = F x / (E A)
    #
    expected_middle_displacement = (
        force * 1.0
        / (E * area)
    )

    # At x = 2 m:
    #
    #     u = F L / (E A)
    #
    expected_tip_displacement = (
        force * 2.0
        / (E * area)
    )

    u1 = (
        result.node_displacement(
            n1
        )
    )

    u2 = (
        result.node_displacement(
            n2
        )
    )

    assert np.isclose(
        u1[0],
        expected_middle_displacement,
        rtol=1e-10,
        atol=1e-14,
    )

    assert np.isclose(
        u2[0],
        expected_tip_displacement,
        rtol=1e-10,
        atol=1e-14,
    )

    # Both elements are in series, therefore
    # both carry the complete applied force.
    assert np.isclose(
        result.truss_force(t0),
        force,
        rtol=1e-10,
        atol=1e-8,
    )

    assert np.isclose(
        result.truss_force(t1),
        force,
        rtol=1e-10,
        atol=1e-8,
    )

    # Check equilibrium at the fixed end too.
    reaction = (
        result.node_reaction(
            n0
        )
    )

    assert np.isclose(
        reaction[0],
        -force,
        rtol=1e-10,
        atol=1e-8,
    )


def test_truss_axis_rotation_invariance():
    model = cb.Model()

    material = make_material()
    section = make_section()

    length = 2.0
    force = 10000.0

    n0 = model.add_node(
        0.0,
        0.0,
        0.0,
    )

    n1 = model.add_node(
        0.0,
        length,
        0.0,
    )

    truss = model.add_truss(
        n0,
        n1,
        material,
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

    # Only global Y translation remains free.
    model.add_support(
        n1,
        True,
        False,
        True,
        True,
        True,
        True,
    )

    model.add_point_load(
        n1,
        0.0,
        force,
        0.0,
    )

    result = (
        cb.LinearStaticSolver(
            model
        )
        .solve()
    )

    E = 200e9
    area = 0.02 * 0.01

    expected_displacement = (
        force * length
        / (E * area)
    )

    displacement = (
        result.node_displacement(
            n1
        )
    )

    assert np.isclose(
        displacement[0],
        0.0,
        atol=1e-14,
    )

    assert np.isclose(
        displacement[1],
        expected_displacement,
        rtol=1e-10,
        atol=1e-14,
    )

    assert np.isclose(
        displacement[2],
        0.0,
        atol=1e-14,
    )

    assert np.isclose(
        result.truss_force(truss),
        force,
        rtol=1e-10,
        atol=1e-8,
    )

    reaction = (
        result.node_reaction(
            n0
        )
    )

    assert np.isclose(
        reaction[0],
        0.0,
        atol=1e-8,
    )

    assert np.isclose(
        reaction[1],
        -force,
        rtol=1e-10,
        atol=1e-8,
    )

    assert np.isclose(
        reaction[2],
        0.0,
        atol=1e-8,
    )
