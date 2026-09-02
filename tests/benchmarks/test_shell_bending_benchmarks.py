import numpy as np

import carambola as cb


E = 200e9
NU = 0.3
THICKNESS = 0.01
PRESSURE = -1000.0
SIZE = 1.0


def make_square_plate(
    divisions=4,
    pressure=PRESSURE,
    size=SIZE,
    thickness=THICKNESS,
):
    model = cb.Model()

    material = cb.Material(
        "Steel",
        E,
        NU,
        7850.0,
    )

    prop = cb.ShellProperty(
        material,
        thickness,
    )

    spacing = size / divisions

    nodes = []

    for j in range(divisions + 1):
        row = []

        for i in range(divisions + 1):
            row.append(
                model.add_node(
                    i * spacing,
                    j * spacing,
                    0.0,
                )
            )

        nodes.append(row)

    shells = []

    for j in range(divisions):
        for i in range(divisions):
            n00 = nodes[j][i]
            n10 = nodes[j][i + 1]
            n11 = nodes[j + 1][i + 1]
            n01 = nodes[j + 1][i]

            shells.append(
                model.add_shell(
                    n00,
                    n10,
                    n11,
                    prop,
                )
            )

            shells.append(
                model.add_shell(
                    n00,
                    n11,
                    n01,
                    prop,
                )
            )

    for shell in shells:
        model.add_uniform_shell_pressure(
            shell,
            pressure,
        )

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
                    True,
                    True,
                    True,
                    True,
                    True,
                    True,
                )

    return (
        model,
        nodes,
        shells,
    )


def center_shells(
    shells,
    divisions,
):
    """
    Return the two triangles belonging to
    the cell immediately below-left of the
    plate centre.

    For an even number of divisions, the
    plate centre is one corner of this cell.
    """
    i = divisions // 2 - 1
    j = divisions // 2 - 1

    cell_index = (
        j * divisions + i
    )

    first_shell = (
        2 * cell_index
    )

    return (
        shells[first_shell],
        shells[first_shell + 1],
    )


def test_shell_bending_moments_are_finite_and_nonzero():
    divisions = 4

    (
        model,
        nodes,
        shells,
    ) = make_square_plate(
        divisions=divisions,
    )

    result = (
        cb.LinearStaticSolver(model)
        .solve()
    )

    shell_a, shell_b = center_shells(
        shells,
        divisions,
    )

    # DKT recovery uses triangle natural
    # coordinates (xi, eta).
    #
    # The centroid is:
    #
    # xi = 1/3
    # eta = 1/3
    #
    xi = 1.0 / 3.0
    eta = 1.0 / 3.0

    moments_a = (
        result.shell_bending_moments(
            shell_a,
            xi,
            eta,
        )
    )

    moments_b = (
        result.shell_bending_moments(
            shell_b,
            xi,
            eta,
        )
    )

    assert np.isfinite(
        moments_a
    ).all()

    assert np.isfinite(
        moments_b
    ).all()

    assert np.linalg.norm(
        moments_a
    ) > 0.0

    assert np.linalg.norm(
        moments_b
    ) > 0.0


def test_shell_top_and_bottom_bending_stress_are_opposite():
    divisions = 4

    (
        model,
        nodes,
        shells,
    ) = make_square_plate(
        divisions=divisions,
    )

    result = (
        cb.LinearStaticSolver(model)
        .solve()
    )

    shell, _ = center_shells(
        shells,
        divisions,
    )

    xi = 1.0 / 3.0
    eta = 1.0 / 3.0

    top = (
        result.shell_top_bending_stress(
            shell,
            xi,
            eta,
        )
    )

    bottom = (
        result.shell_bottom_bending_stress(
            shell,
            xi,
            eta,
        )
    )

    assert np.isfinite(
        top
    ).all()

    assert np.isfinite(
        bottom
    ).all()

    assert np.linalg.norm(
        top
    ) > 0.0

    assert np.linalg.norm(
        bottom
    ) > 0.0

    # Pure bending stress is antisymmetric
    # through the midsurface.
    assert np.allclose(
        top,
        -bottom,
        rtol=1e-10,
        atol=1e-8,
    )


def test_shell_surface_stress_equals_bending_stress_for_pure_plate_bending():
    divisions = 4

    (
        model,
        nodes,
        shells,
    ) = make_square_plate(
        divisions=divisions,
    )

    result = (
        cb.LinearStaticSolver(model)
        .solve()
    )

    shell, _ = center_shells(
        shells,
        divisions,
    )

    xi = 1.0 / 3.0
    eta = 1.0 / 3.0

    bending_top = (
        result.shell_top_bending_stress(
            shell,
            xi,
            eta,
        )
    )

    surface_top = (
        result.shell_top_stress(
            shell,
            xi,
            eta,
        )
    )

    bending_bottom = (
        result.shell_bottom_bending_stress(
            shell,
            xi,
            eta,
        )
    )

    surface_bottom = (
        result.shell_bottom_stress(
            shell,
            xi,
            eta,
        )
    )

    # This plate is loaded only normal to its
    # midsurface. There is no imposed in-plane
    # loading, so membrane stress should be
    # zero apart from numerical roundoff.
    assert np.allclose(
        surface_top,
        bending_top,
        rtol=1e-10,
        atol=1e-6,
    )

    assert np.allclose(
        surface_bottom,
        bending_bottom,
        rtol=1e-10,
        atol=1e-6,
    )


def test_shell_surface_von_mises_is_finite_and_positive():
    divisions = 4

    (
        model,
        nodes,
        shells,
    ) = make_square_plate(
        divisions=divisions,
    )

    result = (
        cb.LinearStaticSolver(model)
        .solve()
    )

    shell, _ = center_shells(
        shells,
        divisions,
    )

    xi = 1.0 / 3.0
    eta = 1.0 / 3.0

    top_vm = (
        result.shell_top_von_mises(
            shell,
            xi,
            eta,
        )
    )

    bottom_vm = (
        result.shell_bottom_von_mises(
            shell,
            xi,
            eta,
        )
    )

    assert np.isfinite(
        top_vm
    )

    assert np.isfinite(
        bottom_vm
    )

    assert top_vm > 0.0
    assert bottom_vm > 0.0

    # With zero membrane stress, top and
    # bottom bending stresses differ only
    # by sign. Von Mises is therefore equal.
    assert np.isclose(
        top_vm,
        bottom_vm,
        rtol=1e-10,
        atol=1e-6,
    )
