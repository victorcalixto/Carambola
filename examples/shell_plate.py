"""Clamped square shell plate example for Carambola.

A 1 m x 1 m steel plate is subjected to uniform transverse pressure.

The plate is discretised using triangular Shell3D elements and all
degrees of freedom along its boundary are restrained.

The example demonstrates:

- structured shell mesh generation
- ShellProperty
- model mesh insertion
- uniform shell pressure
- linear-static analysis
- centre displacement
- analytical plate comparison
- model serialization
"""

import carambola as cb


def main():
    # -----------------------------------------------------------------------
    # Plate properties
    # -----------------------------------------------------------------------

    width = 1.0
    height = 1.0

    nx = 16
    ny = 16

    thickness = 0.01

    youngs_modulus = 210.0e9
    poisson_ratio = 0.3

    pressure = -10_000.0

    material = cb.Material(
        "Steel",
        youngs_modulus,
        poisson_ratio,
        7850.0,
    )

    shell_property = cb.ShellProperty(
        material,
        thickness,
    )

    # -----------------------------------------------------------------------
    # Mesh
    # -----------------------------------------------------------------------

    mesh = cb.rectangular_shell_mesh(
        width,
        height,
        nx,
        ny,
    )

    print("Carambola — clamped square plate example")
    print()

    print("Mesh vertices:")
    print(len(mesh.vertices))

    print("Mesh triangles:")
    print(len(mesh.faces))
    print()

    # -----------------------------------------------------------------------
    # Model
    # -----------------------------------------------------------------------

    model = cb.Model()

    model.add_shell_mesh(
        mesh,
        shell_property,
    )

    print("Model nodes:")
    print(model.node_count)

    print("Model shells:")
    print(model.shell_count)
    print()

    # -----------------------------------------------------------------------
    # Boundary conditions
    # -----------------------------------------------------------------------

    tolerance = 1.0e-9

    boundary_nodes = []

    for node_id in range(model.node_count):
        node = model.node(node_id)

        x = node.x
        y = node.y

        on_boundary = (
            abs(x) < tolerance
            or abs(x - width) < tolerance
            or abs(y) < tolerance
            or abs(y - height) < tolerance
        )

        if on_boundary:
            model.add_support(
                node,
                True,
                True,
                True,
                True,
                True,
                True,
            )

            boundary_nodes.append(node)



    print("Boundary supports:")
    print(len(boundary_nodes))
    print()

    # -----------------------------------------------------------------------
    # Uniform pressure
    # -----------------------------------------------------------------------
    
    for shell_id in range(model.shell_count):
        shell = model.shell(shell_id)

        model.add_uniform_shell_pressure(
            shell,
            pressure,
        )


    
    print("Uniform shell pressures:")
    print(model.uniform_shell_pressure_count)
    print()

    # -----------------------------------------------------------------------
    # Solve
    # -----------------------------------------------------------------------

    result = cb.LinearStaticSolver(
        model
    ).solve()

    # -----------------------------------------------------------------------
    # Centre displacement
    # -----------------------------------------------------------------------

    centre_x = width / 2.0
    centre_y = height / 2.0

    centre_node = min(
        (
            model.node(node_id)
            for node_id in range(
                model.node_count
            )
        ),
        key=lambda node: (
            (node.x - centre_x) ** 2
            + (node.y - centre_y) ** 2
        ),
    )




    displacement = (
        result.node_displacement(
            centre_node
        )
    )

    print("Centre node:")
    print(
        centre_node.x,
        centre_node.y,
        centre_node.z,
    )
    print()

    print("Centre displacement:")
    print(displacement)
    print()

    print("Centre Z displacement:")
    print(displacement[2])
    print()

    # -----------------------------------------------------------------------
    # Analytical comparison
    # -----------------------------------------------------------------------
    #
    # Flexural rigidity:
    #
    #           E t^3
    #     D = -----------
    #         12(1-v^2)
    #
    # For a uniformly loaded clamped square plate:
    #
    #     w_max = alpha q a^4 / D
    #
    # with alpha approximately 0.00126.
    #
    # This provides a classical thin-plate reference for comparison with
    # the numerical Shell3D solution.
    # -----------------------------------------------------------------------

    flexural_rigidity = (
        youngs_modulus
        * thickness**3
        / (
            12.0
            * (
                1.0
                - poisson_ratio**2
            )
        )
    )

    alpha = 0.00126

    expected_displacement = (
        alpha
        * abs(pressure)
        * width**4
        / flexural_rigidity
    )

    numerical_displacement = abs(
        displacement[2]
    )

    relative_error = (
        abs(
            numerical_displacement
            - expected_displacement
        )
        / expected_displacement
    )

    print(
        "Analytical centre displacement:"
    )
    print(
        expected_displacement
    )
    print()

    print(
        "Numerical centre displacement:"
    )
    print(
        numerical_displacement
    )
    print()

    print(
        "Relative error:"
    )
    print(
        relative_error
    )
    print()

    print(
        "Relative error [%]:"
    )
    print(
        relative_error * 100.0
    )
    
     # -----------------------------------------------------------------------
    # Shell result recovery
    # -----------------------------------------------------------------------

    centre_shell = min(
        (
            model.shell(shell_id)
            for shell_id in range(
                model.shell_count
            )
        ),
        key=lambda shell: (
            (
                (
                    shell.node_a.x
                    + shell.node_b.x
                    + shell.node_c.x
                )
                / 3.0
                - centre_x
            ) ** 2
            +
            (
                (
                    shell.node_a.y
                    + shell.node_b.y
                    + shell.node_c.y
                )
                / 3.0
                - centre_y
            ) ** 2
        ),
    )

    # Evaluate close to the centre of the triangular element.
    xi = 1.0 / 3.0
    eta = 1.0 / 3.0

    membrane_strain = (
        result.shell_membrane_strain(
            centre_shell
        )
    )

    membrane_stress = (
        result.shell_membrane_stress(
            centre_shell
        )
    )

    bending_curvature = (
        result.shell_bending_curvature(
            centre_shell,
            xi,
            eta,
        )
    )

    bending_moments = (
        result.shell_bending_moments(
            centre_shell,
            xi,
            eta,
        )
    )

    top_stress = (
        result.shell_top_stress(
            centre_shell,
            xi,
            eta,
        )
    )

    bottom_stress = (
        result.shell_bottom_stress(
            centre_shell,
            xi,
            eta,
        )
    )

    top_von_mises = (
        result.shell_top_von_mises(
            centre_shell,
            xi,
            eta,
        )
    )

    bottom_von_mises = (
        result.shell_bottom_von_mises(
            centre_shell,
            xi,
            eta,
        )
    )

    top_principal = (
        result.shell_top_principal_stresses(
            centre_shell,
            xi,
            eta,
        )
    )

    bottom_principal = (
        result.shell_bottom_principal_stresses(
            centre_shell,
            xi,
            eta,
        )
    )

    print()
    print("Centre shell membrane strain:")
    print(membrane_strain)

    print()
    print("Centre shell membrane stress:")
    print(membrane_stress)

    print()
    print("Centre shell bending curvature:")
    print(bending_curvature)

    print()
    print("Centre shell bending moments:")
    print(bending_moments)

    print()
    print("Centre shell top stress:")
    print(top_stress)

    print()
    print("Centre shell bottom stress:")
    print(bottom_stress)

    print()
    print("Centre shell top von Mises:")
    print(top_von_mises)

    print()
    print("Centre shell bottom von Mises:")
    print(bottom_von_mises)

    print()
    print("Centre shell top principal stresses:")
    print(top_principal)

    print()
    print("Centre shell bottom principal stresses:")
    print(bottom_principal)




    # -----------------------------------------------------------------------
    # Serialization
    # -----------------------------------------------------------------------

    output = (
        "examples/"
        "shell_plate.carambola"
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
