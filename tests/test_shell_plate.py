import numpy as np
import pytest

import carambola as cb


def analytical_clamped_square_center_deflection(
    pressure,
    size,
    thickness,
    youngs_modulus,
    poisson_ratio,
):
    bending_rigidity = (
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

    coefficient = 0.001265

    return (
        coefficient
        * pressure
        * size**4
        / bending_rigidity
    )


def test_clamped_square_plate_matches_analytical_solution():
    pressure = -1000.0
    size = 1.0
    thickness = 0.01
    youngs_modulus = 200e9
    poisson_ratio = 0.3

    numerical = solve_center_displacement(
        divisions=16,
        pressure=pressure,
        size=size,
        thickness=thickness,
    )

    analytical = (
        analytical_clamped_square_center_deflection(
            pressure=pressure,
            size=size,
            thickness=thickness,
            youngs_modulus=youngs_modulus,
            poisson_ratio=poisson_ratio,
        )
    )

    relative_error = abs(
        (
            numerical
            - analytical
        )
        / analytical
    )

    print()
    print(
        "Numerical:",
        numerical,
    )

    print(
        "Analytical:",
        analytical,
    )

    print(
        "Relative error:",
        relative_error,
    )

    assert relative_error < 0.02



def solve_center_displacement(
    divisions,
    pressure=-1000.0,
    size=1.0,
    thickness=0.01,
):
    (
        model,
        nodes,
        _,
        _,
        _,
    ) = make_square_plate(
        divisions=divisions,
        size=size,
        thickness=thickness,
        pressure=pressure,
    )

    result = cb.LinearStaticSolver(
        model
    ).solve()

    center_index = divisions // 2

    center = nodes[
        center_index
    ][
        center_index
    ]

    return result.node_displacement(
        center
    )[2]


@pytest.mark.parametrize(
    "divisions",
    [
        2,
        4,
        8,
        16,
    ],
)
def test_square_plate_center_deflection_is_finite(
    divisions,
):
    uz = solve_center_displacement(
        divisions
    )

    assert np.isfinite(uz)

    assert uz < 0.0


def test_square_plate_center_deflection_converges():
    divisions = [
        2,
        4,
        8,
        16,
    ]

    displacements = [
        solve_center_displacement(n)
        for n in divisions
    ]

    magnitudes = np.abs(
        displacements
    )

    print()
    print("Square plate convergence")
    print("------------------------")

    for n, uz in zip(
        divisions,
        displacements,
    ):
        print(
            f"{n:2d} x {n:2d}: "
            f"uz = {uz:.12e}"
        )

    differences = np.abs(
        np.diff(
            magnitudes
        )
    )

    print()
    print("Successive differences:")

    for i, difference in enumerate(
        differences
    ):
        print(
            f"{divisions[i]} -> "
            f"{divisions[i + 1]}: "
            f"{difference:.12e}"
        )

    # The refinement increment should decrease.
    #
    # We deliberately do not compare against
    # an analytical value yet. First we want
    # evidence that the numerical formulation
    # converges internally.
    assert differences[2] < differences[1]

    assert differences[1] < differences[0]



def make_square_plate(
    divisions=2,
    size=1.0,
    thickness=0.01,
    pressure=-1000.0,
):
    model = cb.Model()

    material = cb.Material(
        "Steel",
        200e9,
        0.3,
        7850.0,
    )

    prop = cb.ShellProperty(
        material,
        thickness,
    )

    spacing = size / divisions

    nodes = []

    # Create structured grid.
    for j in range(divisions + 1):
        row = []

        for i in range(divisions + 1):
            node = model.add_node(
                i * spacing,
                j * spacing,
                0.0,
            )

            row.append(node)

        nodes.append(row)

    shells = []

    # Split every square cell into two
    # counter-clockwise triangles.
    #
    # n01 ----- n11
    #  |       / |
    #  |     /   |
    #  |   /     |
    #  | /       |
    # n00 ----- n10
    #
    for j in range(divisions):
        for i in range(divisions):
            n00 = nodes[j][i]
            n10 = nodes[j][i + 1]
            n11 = nodes[j + 1][i + 1]
            n01 = nodes[j + 1][i]

            shell_a = model.add_shell(
                n00,
                n10,
                n11,
                prop,
            )

            shell_b = model.add_shell(
                n00,
                n11,
                n01,
                prop,
            )

            shells.append(shell_a)
            shells.append(shell_b)

    # Apply the same uniform pressure
    # to every triangle.
    for shell in shells:
        model.add_uniform_shell_pressure(
            shell,
            pressure,
        )

    # Clamp all nodes on the plate boundary.
    for j in range(divisions + 1):
        for i in range(divisions + 1):
            is_boundary = (
                i == 0
                or i == divisions
                or j == 0
                or j == divisions
            )

            if is_boundary:
                model.add_support(
                    nodes[j][i],
                    True,  # UX
                    True,  # UY
                    True,  # UZ
                    True,  # RX
                    True,  # RY
                    True,  # RZ
                )

    return (
        model,
        nodes,
        shells,
        pressure,
        size,
    )


def test_square_plate_mesh_counts():
    model, nodes, shells, _, _ = (
        make_square_plate(
            divisions=2,
        )
    )

    # 3 x 3 grid.
    assert model.node_count == 9

    # 2 x 2 cells, two triangles each.
    assert model.shell_count == 8

    assert len(shells) == 8


def test_square_plate_total_applied_pressure():
    (
        model,
        nodes,
        shells,
        pressure,
        size,
    ) = make_square_plate(
        divisions=2,
    )

    f = cb.Assembler(
        model
    ).force_vector()

    total_fz = np.sum(
        f[2::6]
    )

    expected = (
        pressure
        * size
        * size
    )

    assert total_fz == pytest.approx(
        expected,
    )


def test_square_plate_pressure_has_no_direct_moments():
    model, *_ = make_square_plate(
        divisions=2,
    )

    f = cb.Assembler(
        model
    ).force_vector()

    moments = []

    for node_id in range(
        model.node_count
    ):
        offset = node_id * 6

        moments.extend(
            [
                f[offset + 3],
                f[offset + 4],
                f[offset + 5],
            ]
        )

    assert np.allclose(
        moments,
        0.0,
    )


def test_clamped_square_plate_center_moves_down():
    (
        model,
        nodes,
        _,
        _,
        _,
    ) = make_square_plate(
        divisions=2,
    )

    result = cb.LinearStaticSolver(
        model
    ).solve()

    center = nodes[1][1]

    displacement = (
        result.node_displacement(
            center
        )
    )

    assert np.isfinite(
        displacement
    ).all()

    assert displacement[2] < 0.0


def test_clamped_square_plate_global_equilibrium():
    (
        model,
        nodes,
        _,
        pressure,
        size,
    ) = make_square_plate(
        divisions=2,
    )

    result = cb.LinearStaticSolver(
        model
    ).solve()

    total_reaction_z = 0.0

    divisions = 2

    for j in range(divisions + 1):
        for i in range(divisions + 1):
            is_boundary = (
                i == 0
                or i == divisions
                or j == 0
                or j == divisions
            )

            if not is_boundary:
                continue

            reaction = (
                result.node_reaction(
                    nodes[j][i]
                )
            )

            total_reaction_z += (
                reaction[2]
            )

    applied_force_z = (
        pressure
        * size
        * size
    )

    assert total_reaction_z == pytest.approx(
        -applied_force_z,
        rel=1e-9,
        abs=1e-8,
    )


def test_center_displacement_scales_with_pressure():
    (
        model_a,
        nodes_a,
        *_,
    ) = make_square_plate(
        divisions=2,
        pressure=-1000.0,
    )

    (
        model_b,
        nodes_b,
        *_,
    ) = make_square_plate(
        divisions=2,
        pressure=-2000.0,
    )

    result_a = cb.LinearStaticSolver(
        model_a
    ).solve()

    result_b = cb.LinearStaticSolver(
        model_b
    ).solve()

    uz_a = result_a.node_displacement(
        nodes_a[1][1]
    )[2]

    uz_b = result_b.node_displacement(
        nodes_b[1][1]
    )[2]

    # Linear-static response:
    # doubling the pressure should double
    # the displacement.
    assert uz_b == pytest.approx(
        2.0 * uz_a,
        rel=1e-9,
    )
