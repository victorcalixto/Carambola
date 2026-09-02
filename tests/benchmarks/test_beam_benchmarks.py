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
        0.04,
    )


def test_cantilever_tip_load():
    model = cb.Model()

    material = make_material()
    section = make_section()

    length = 2.0
    force = 1000.0

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

    beam = model.add_beam(
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

    # Global -Z point load.
    model.add_point_load(
        n1,
        0.0,
        0.0,
        -force,
    )

    result = (
        cb.LinearStaticSolver(model)
        .solve()
    )

    E = 200e9

    # For a beam along global X:
    #
    # local y = global +Z
    # local z = global -Y
    #
    # A global -Z load therefore causes
    # bending about local z.
    I = section.Iz

    # Euler-Bernoulli cantilever:
    #
    # delta = P L^3 / (3 E I)
    # theta = P L^2 / (2 E I)
    #
    expected_tip_deflection = (
        force * length**3
        / (3.0 * E * I)
    )

    expected_tip_rotation = (
        force * length**2
        / (2.0 * E * I)
    )

    displacement = (
        result.node_displacement(n1)
    )

    rotation = (
        result.node_rotation(n1)
    )

    reaction = (
        result.node_reaction(n0)
    )

    moment_reaction = (
        result.node_moment_reaction(n0)
    )

    assert np.isclose(
        displacement[0],
        0.0,
        atol=1e-12,
    )

    assert np.isclose(
        displacement[1],
        0.0,
        atol=1e-12,
    )

    assert np.isclose(
        displacement[2],
        -expected_tip_deflection,
        rtol=1e-8,
        atol=1e-12,
    )

    assert np.isclose(
        abs(rotation[1]),
        expected_tip_rotation,
        rtol=1e-8,
        atol=1e-12,
    )

    assert np.isclose(
        reaction[2],
        force,
        rtol=1e-10,
        atol=1e-8,
    )

    assert np.isclose(
        abs(moment_reaction[1]),
        force * length,
        rtol=1e-10,
        atol=1e-8,
    )


def test_cantilever_uniform_distributed_load():
    model = cb.Model()

    material = make_material()
    section = make_section()

    length = 3.0
    load = 500.0

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

    beam = model.add_beam(
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

    # UniformBeamLoad uses beam-local coordinates.
    #
    # For this beam:
    #
    # local y = global +Z
    #
    # Therefore qy = -load corresponds to
    # a global -Z distributed load.
    model.add_uniform_beam_load(
        beam,
        0.0,
        -load,
        0.0,
    )

    result = (
        cb.LinearStaticSolver(model)
        .solve()
    )

    E = 200e9
    I = section.Iz

    # Euler-Bernoulli cantilever under UDL:
    #
    # delta = q L^4 / (8 E I)
    #
    # theta = q L^3 / (6 E I)
    #
    expected_tip_deflection = (
        load * length**4
        / (8.0 * E * I)
    )

    expected_tip_rotation = (
        load * length**3
        / (6.0 * E * I)
    )

    expected_reaction = (
        load * length
    )

    expected_fixed_moment = (
        load * length**2
        / 2.0
    )

    displacement = (
        result.node_displacement(n1)
    )

    rotation = (
        result.node_rotation(n1)
    )

    reaction = (
        result.node_reaction(n0)
    )

    moment_reaction = (
        result.node_moment_reaction(n0)
    )

    assert np.isclose(
        displacement[2],
        -expected_tip_deflection,
        rtol=1e-8,
        atol=1e-12,
    )

    assert np.isclose(
        abs(rotation[1]),
        expected_tip_rotation,
        rtol=1e-8,
        atol=1e-12,
    )

    assert np.isclose(
        reaction[2],
        expected_reaction,
        rtol=1e-10,
        atol=1e-8,
    )

    assert np.isclose(
        abs(moment_reaction[1]),
        expected_fixed_moment,
        rtol=1e-10,
        atol=1e-8,
    )


def test_simply_supported_beam_uniform_load():
    model = cb.Model()

    material = make_material()
    section = make_section()

    length = 4.0
    load = 1000.0

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

    beam = model.add_beam(
        n0,
        n1,
        material,
        section,
    )

    # Pinned support.
    #
    # Translations restrained.
    #
    # RX is restrained to remove the rigid
    # torsional mode of the whole beam.
    #
    # RY and RZ remain free so the beam
    # behaves as simply supported in bending.
    model.add_support(
        n0,
        True,
        True,
        True,
        True,
        False,
        False,
    )

    # Roller support.
    #
    # UX free.
    # UY and UZ restrained.
    # All rotations free.
    model.add_support(
        n1,
        False,
        True,
        True,
        False,
        False,
        False,
    )

    # Global -Z UDL =
    # negative local-y load.
    model.add_uniform_beam_load(
        beam,
        0.0,
        -load,
        0.0,
    )

    result = (
        cb.LinearStaticSolver(model)
        .solve()
    )

    E = 200e9
    I = section.Iz

    expected_reaction = (
        load * length / 2.0
    )

    # End slope for simply supported beam
    # under full-span UDL:
    #
    # theta = q L^3 / (24 E I)
    #
    expected_end_rotation = (
        load * length**3
        / (24.0 * E * I)
    )

    reaction_0 = (
        result.node_reaction(n0)
    )

    reaction_1 = (
        result.node_reaction(n1)
    )

    rotation_0 = (
        result.node_rotation(n0)
    )

    rotation_1 = (
        result.node_rotation(n1)
    )

    assert np.isclose(
        reaction_0[2],
        expected_reaction,
        rtol=1e-10,
        atol=1e-8,
    )

    assert np.isclose(
        reaction_1[2],
        expected_reaction,
        rtol=1e-10,
        atol=1e-8,
    )

    assert np.isclose(
        reaction_0[2] + reaction_1[2],
        load * length,
        rtol=1e-10,
        atol=1e-8,
    )

    assert np.isclose(
        abs(rotation_0[1]),
        expected_end_rotation,
        rtol=1e-8,
        atol=1e-12,
    )

    assert np.isclose(
        abs(rotation_1[1]),
        expected_end_rotation,
        rtol=1e-8,
        atol=1e-12,
    )

    # Slopes must have opposite signs.
    assert (
        rotation_0[1]
        * rotation_1[1]
        < 0.0
    )


def test_beam_pure_torsion():
    model = cb.Model()

    material = make_material()
    section = make_section()

    length = 2.0
    torque = 500.0

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

    beam = model.add_beam(
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

    model.add_point_load(
        n1,
        0.0,
        0.0,
        0.0,
        torque,
        0.0,
        0.0,
    )

    result = (
        cb.LinearStaticSolver(model)
        .solve()
    )

    E = 200e9
    nu = 0.3

    G = (
        E
        / (2.0 * (1.0 + nu))
    )

    J = section.J

    expected_rotation = (
        torque * length
        / (G * J)
    )

    rotation = (
        result.node_rotation(n1)
    )

    moment_reaction = (
        result.node_moment_reaction(n0)
    )

    assert np.isclose(
        rotation[0],
        expected_rotation,
        rtol=1e-8,
        atol=1e-12,
    )

    assert np.isclose(
        moment_reaction[0],
        -torque,
        rtol=1e-10,
        atol=1e-8,
    )

    assert np.isclose(
        result.beam_torsion(beam),
        torque,
        rtol=1e-10,
        atol=1e-8,
    )


def test_beam_axis_rotation_invariance():
    model = cb.Model()

    material = make_material()
    section = make_section()

    length = 2.0
    force = 1000.0

    # Rotate the beam axis from global X
    # to global Y.
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

    beam = model.add_beam(
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

    model.add_point_load(
        n1,
        0.0,
        0.0,
        -force,
    )

    result = (
        cb.LinearStaticSolver(model)
        .solve()
    )

    displacement = (
        result.node_displacement(n1)
    )

    reaction = (
        result.node_reaction(n0)
    )

    assert np.isfinite(
        displacement
    ).all()

    assert np.isclose(
        reaction[2],
        force,
        rtol=1e-10,
        atol=1e-8,
    )

    assert np.isclose(
        np.linalg.norm(reaction),
        force,
        rtol=1e-10,
        atol=1e-8,
    )

def test_multi_element_cantilever_matches_analytical_solution():
    model = cb.Model()

    material = make_material()
    section = make_section()

    length = 4.0
    force = 1000.0
    element_count = 4

    nodes = []

    for i in range(element_count + 1):
        x = (
            length
            * i
            / element_count
        )

        nodes.append(
            model.add_node(
                x,
                0.0,
                0.0,
            )
        )

    beams = []

    for i in range(element_count):
        beams.append(
            model.add_beam(
                nodes[i],
                nodes[i + 1],
                material,
                section,
            )
        )

    model.add_support(
        nodes[0],
        True,
        True,
        True,
        True,
        True,
        True,
    )

    model.add_point_load(
        nodes[-1],
        0.0,
        0.0,
        -force,
    )

    result = (
        cb.LinearStaticSolver(model)
        .solve()
    )

    E = 200e9
    I = section.Iz

    expected_tip_deflection = (
        force * length**3
        / (3.0 * E * I)
    )

    expected_tip_rotation = (
        force * length**2
        / (2.0 * E * I)
    )

    displacement = (
        result.node_displacement(
            nodes[-1]
        )
    )

    rotation = (
        result.node_rotation(
            nodes[-1]
        )
    )

    reaction = (
        result.node_reaction(
            nodes[0]
        )
    )

    moment_reaction = (
        result.node_moment_reaction(
            nodes[0]
        )
    )

    assert np.isclose(
        displacement[2],
        -expected_tip_deflection,
        rtol=1e-8,
        atol=1e-12,
    )

    assert np.isclose(
        abs(rotation[1]),
        expected_tip_rotation,
        rtol=1e-8,
        atol=1e-12,
    )

    assert np.isclose(
        reaction[2],
        force,
        rtol=1e-10,
        atol=1e-8,
    )

    assert np.isclose(
        abs(moment_reaction[1]),
        force * length,
        rtol=1e-10,
        atol=1e-8,
    )

