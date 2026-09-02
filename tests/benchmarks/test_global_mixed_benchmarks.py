import numpy as np

import carambola as cb


E = 200e9
NU = 0.3
RHO = 7850.0


def make_material():
    return cb.Material(
        "Steel",
        E,
        NU,
        RHO,
    )


def make_beam_section():
    return cb.RectangularSection(
        0.02,
        0.04,
    )


def make_truss_section():
    return cb.RectangularSection(
        0.02,
        0.01,
    )


def make_shell_property(material):
    return cb.ShellProperty(
        material,
        0.01,
    )


def test_global_force_equilibrium_with_point_loads():
    model = cb.Model()

    material = make_material()
    section = make_beam_section()

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

    model.add_beam(
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

    fx = 1200.0
    fy = -800.0
    fz = -1500.0

    model.add_point_load(
        n1,
        fx,
        fy,
        fz,
    )

    result = (
        cb.LinearStaticSolver(model)
        .solve()
    )

    reaction = (
        result.node_reaction(n0)
    )

    applied = np.array(
        [
            fx,
            fy,
            fz,
        ]
    )

    assert np.allclose(
        reaction + applied,
        np.zeros(3),
        rtol=1e-10,
        atol=1e-8,
    )


def test_global_moment_equilibrium():
    model = cb.Model()

    material = make_material()
    section = make_beam_section()

    length = 2.0

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

    model.add_beam(
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

    force = -1000.0
    applied_torque = 250.0

    model.add_point_load(
        n1,
        0.0,
        0.0,
        force,
        applied_torque,
        0.0,
        0.0,
    )

    result = (
        cb.LinearStaticSolver(model)
        .solve()
    )

    moment_reaction = (
        result.node_moment_reaction(n0)
    )

    # External point force at:
    #
    # r = [L, 0, 0]
    #
    # F = [0, 0, force]
    #
    # r x F =
    #
    # [0, -L*force, 0]
    #
    force_moment = np.array(
        [
            0.0,
            -length * force,
            0.0,
        ]
    )

    applied_moment = np.array(
        [
            applied_torque,
            0.0,
            0.0,
        ]
    )

    total_external_moment = (
        force_moment
        + applied_moment
    )

    assert np.allclose(
        moment_reaction
        + total_external_moment,
        np.zeros(3),
        rtol=1e-10,
        atol=1e-8,
    )


def test_mixed_truss_and_beam_model():
    model = cb.Model()

    material = make_material()

    beam_section = (
        make_beam_section()
    )

    truss_section = (
        make_truss_section()
    )

    # Beam:
    #
    # n0 -------- n1
    #              |
    #              |
    #              n2
    #
    # Truss connects n1 to n2.
    #
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
        2.0,
        1.0,
        0.0,
    )

    beam = model.add_beam(
        n0,
        n1,
        material,
        beam_section,
    )

    truss = model.add_truss(
        n1,
        n2,
        material,
        truss_section,
    )

    # Fully fixed beam root.
    model.add_support(
        n0,
        True,
        True,
        True,
        True,
        True,
        True,
    )

    # Truss end:
    #
    # translations fixed,
    # rotations fixed because truss has no
    # rotational stiffness.
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
        0.0,
        -1000.0,
        0.0,
    )

    result = (
        cb.LinearStaticSolver(model)
        .solve()
    )

    displacement = (
        result.node_displacement(n1)
    )

    beam_forces = (
        result.beam_local_end_forces(
            beam
        )
    )

    truss_force = (
        result.truss_force(
            truss
        )
    )

    assert np.isfinite(
        displacement
    ).all()

    assert np.isfinite(
        beam_forces
    ).all()

    assert np.isfinite(
        truss_force
    )

    assert np.linalg.norm(
        displacement
    ) > 0.0


def test_mixed_beam_and_shell_model():
    model = cb.Model()

    material = make_material()

    beam_section = (
        make_beam_section()
    )

    shell_property = (
        make_shell_property(
            material
        )
    )

    # Small triangular shell attached
    # to a beam at n1.
    #
    # n2
    # |\
    # | \
    # n1--n3
    #
    # n0 ---- n1 = beam
    #
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
        1.0,
        1.0,
        0.0,
    )

    n3 = model.add_node(
        2.0,
        0.0,
        0.0,
    )

    beam = model.add_beam(
        n0,
        n1,
        material,
        beam_section,
    )

    shell = model.add_shell(
        n1,
        n3,
        n2,
        shell_property,
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

    # Stabilize the remaining shell edge.
    model.add_support(
        n2,
        True,
        True,
        True,
        True,
        True,
        True,
    )

    model.add_support(
        n3,
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
        -500.0,
    )

    result = (
        cb.LinearStaticSolver(model)
        .solve()
    )

    displacement = (
        result.node_displacement(n1)
    )

    beam_forces = (
        result.beam_local_end_forces(
            beam
        )
    )

    shell_stress = (
        result.shell_top_stress(
            shell,
            1.0 / 3.0,
            1.0 / 3.0,
        )
    )

    assert np.isfinite(
        displacement
    ).all()

    assert np.isfinite(
        beam_forces
    ).all()

    assert np.isfinite(
        shell_stress
    ).all()


def build_order_invariance_model(
    reverse=False,
):
    model = cb.Model()

    material = make_material()
    section = make_beam_section()

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

    if reverse:
        model.add_beam(
            n1,
            n2,
            material,
            section,
        )

        model.add_beam(
            n0,
            n1,
            material,
            section,
        )

    else:
        model.add_beam(
            n0,
            n1,
            material,
            section,
        )

        model.add_beam(
            n1,
            n2,
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

    model.add_point_load(
        n2,
        0.0,
        0.0,
        -1000.0,
    )

    return (
        model,
        n2,
    )


def test_element_insertion_order_does_not_change_solution():
    (
        model_a,
        tip_a,
    ) = build_order_invariance_model(
        reverse=False,
    )

    (
        model_b,
        tip_b,
    ) = build_order_invariance_model(
        reverse=True,
    )

    result_a = (
        cb.LinearStaticSolver(model_a)
        .solve()
    )

    result_b = (
        cb.LinearStaticSolver(model_b)
        .solve()
    )

    displacement_a = (
        result_a.node_displacement(
            tip_a
        )
    )

    displacement_b = (
        result_b.node_displacement(
            tip_b
        )
    )

    assert np.allclose(
        displacement_a,
        displacement_b,
        rtol=1e-10,
        atol=1e-12,
    )
