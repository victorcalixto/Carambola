import carambola as cb


def main():
    model = cb.Model()

    material = cb.Material(
        "Steel",
        210.0e9,
        0.3,
        7850.0,
    )

    section = cb.RectangularSection(
        0.1,
        0.2,
    )

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

    beam = model.add_beam(
        n0,
        n1,
        material,
        section,
        [0.0, 0.0, 1.0],
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
        -1000.0,
        0.0,
        0.0,
        0.0,
    )

    # -----------------------------------------------------------------------
    # Solve
    # -----------------------------------------------------------------------

    result = cb.LinearStaticSolver(
        model
    ).solve()

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

    print(
        "Carambola — cantilever beam example"
    )
    print()

    print(
        "Free-node displacement:"
    )
    print(displacement)
    print()

    print(
        "Free-node rotation:"
    )
    print(rotation)
    print()

    print(
        "Support reaction:"
    )
    print(reaction)
    print()

    print(
        "Support moment reaction:"
    )
    print(moment_reaction)
    print()

    # -----------------------------------------------------------------------
    # Beam result recovery
    # -----------------------------------------------------------------------

    print(
        "Beam axial force:"
    )
    print(
        result.beam_axial_force(beam)
    )
    print()

    print(
        "Beam shear Y:"
    )
    print(
        result.beam_shear_y(beam)
    )
    print()

    print(
        "Beam shear Z:"
    )
    print(
        result.beam_shear_z(beam)
    )
    print()

    print(
        "Beam moment Y:"
    )
    print(
        result.beam_moment_y(beam)
    )
    print()

    print(
        "Beam moment Z:"
    )
    print(
        result.beam_moment_z(beam)
    )
    print()

    print(
        "Beam torsion:"
    )
    print(
        result.beam_torsion(beam)
    )
    print()
    
    # -----------------------------------------------------------------------
    # Analytical comparison
    # -----------------------------------------------------------------------

    load = 1000.0
    length = 2.0
    youngs_modulus = 210.0e9

    width = 0.1
    height = 0.2

    # The beam runs along global X.
    #
    # With the orientation vector [0, 0, 1], Carambola establishes:
    #
    #     local x = +X
    #     local y = +Z
    #     local z = -Y
    #
    # The global -Z load therefore acts along local -Y,
    # producing bending about the local Z axis.
    #
    # For a rectangular section:
    #
    #     Iz = h b^3 / 12

    second_moment_z = (
        height
        * width**3
        / 12.0
    )

    expected_displacement = (
        load
        * length**3
        / (
            3.0
            * youngs_modulus
            * second_moment_z
        )
    )

    expected_rotation = (
        load
        * length**2
        / (
            2.0
            * youngs_modulus
            * second_moment_z
        )
    )

    print(
        "Analytical tip displacement:"
    )
    print(
        expected_displacement
    )
    print()

    print(
        "Analytical tip rotation:"
    )
    print(
        expected_rotation
    )
    print()

    print(
        "Displacement error:",
        abs(
            abs(displacement[2])
            - expected_displacement
        ),
    )

    print(
        "Rotation error:",
        abs(
            abs(rotation[1])
            - expected_rotation
        ),
    )



    # -----------------------------------------------------------------------
    # Save model
    # -----------------------------------------------------------------------

    output = (
        "examples/"
        "cantilever_beam.carambola"
    )

    cb.save_model(
        model,
        output,
    )

    print()
    print(
        f"Model written to {output}"
    )


if __name__ == "__main__":
    main()
