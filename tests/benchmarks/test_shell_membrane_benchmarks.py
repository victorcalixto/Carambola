import numpy as np

import carambola as cb


E = 200e9
NU = 0.3
THICKNESS = 0.01


def make_material():
    return cb.Material(
        "Steel",
        E,
        NU,
        7850.0,
    )


def make_property(material):
    return cb.ShellProperty(
        material,
        THICKNESS,
    )


def make_single_triangle():
    model = cb.Model()

    material = make_material()
    property = make_property(material)

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
        0.0,
        1.0,
        0.0,
    )

    shell = model.add_shell(
        n0,
        n1,
        n2,
        property,
    )

    return (
        model,
        material,
        property,
        n0,
        n1,
        n2,
        shell,
    )


def plane_stress_matrix():
    factor = (
        E
        / (1.0 - NU**2)
    )

    return factor * np.array(
        [
            [1.0, NU, 0.0],
            [NU, 1.0, 0.0],
            [0.0, 0.0, (1.0 - NU) / 2.0],
        ]
    )


def test_constant_strain_uniaxial_x():
    (
        model,
        material,
        property,
        n0,
        n1,
        n2,
        shell,
    ) = make_single_triangle()

    epsilon_x = 1.0e-4

    # Prescribed displacement field:
    #
    # u = epsilon_x * x
    # v = 0
    #
    # gives:
    #
    # epsilon_x = constant
    # epsilon_y = 0
    # gamma_xy = 0
    #
    displacement = np.zeros(18)

    displacement[0] = 0.0
    displacement[6] = epsilon_x * 2.0
    displacement[12] = 0.0

    strain = shell.membrane_strain(
        displacement
    )

    expected = np.array(
        [
            epsilon_x,
            0.0,
            0.0,
        ]
    )

    assert np.allclose(
        strain,
        expected,
        rtol=1e-12,
        atol=1e-14,
    )


def test_constant_strain_uniaxial_y():
    (
        model,
        material,
        property,
        n0,
        n1,
        n2,
        shell,
    ) = make_single_triangle()

    epsilon_y = 2.0e-4

    # Prescribed field:
    #
    # u = 0
    # v = epsilon_y * y
    #
    displacement = np.zeros(18)

    displacement[1] = 0.0
    displacement[7] = 0.0
    displacement[13] = epsilon_y

    strain = shell.membrane_strain(
        displacement
    )

    expected = np.array(
        [
            0.0,
            epsilon_y,
            0.0,
        ]
    )

    assert np.allclose(
        strain,
        expected,
        rtol=1e-12,
        atol=1e-14,
    )


def test_constant_strain_pure_shear():
    (
        model,
        material,
        property,
        n0,
        n1,
        n2,
        shell,
    ) = make_single_triangle()

    gamma_xy = 3.0e-4

    # Use:
    #
    # u = gamma_xy / 2 * y
    # v = gamma_xy / 2 * x
    #
    # Therefore:
    #
    # du/dy + dv/dx = gamma_xy
    #
    displacement = np.zeros(18)

    # node 0: (0, 0)
    displacement[0] = 0.0
    displacement[1] = 0.0

    # node 1: (2, 0)
    displacement[6] = 0.0
    displacement[7] = (
        gamma_xy
        / 2.0
        * 2.0
    )

    # node 2: (0, 1)
    displacement[12] = (
        gamma_xy
        / 2.0
    )

    displacement[13] = 0.0

    strain = shell.membrane_strain(
        displacement
    )

    expected = np.array(
        [
            0.0,
            0.0,
            gamma_xy,
        ]
    )

    assert np.allclose(
        strain,
        expected,
        rtol=1e-12,
        atol=1e-14,
    )


def test_membrane_stress_matches_plane_stress_constitutive_law():
    (
        model,
        material,
        property,
        n0,
        n1,
        n2,
        shell,
    ) = make_single_triangle()

    epsilon_x = 1.0e-4
    epsilon_y = -2.0e-5
    gamma_xy = 5.0e-5

    # Linear displacement field:
    #
    # u = epsilon_x*x + gamma_xy/2*y
    #
    # v = epsilon_y*y + gamma_xy/2*x
    #
    displacement = np.zeros(18)

    coordinates = [
        (0.0, 0.0),
        (2.0, 0.0),
        (0.0, 1.0),
    ]

    for i, (x, y) in enumerate(
        coordinates
    ):
        u = (
            epsilon_x * x
            + gamma_xy
            / 2.0
            * y
        )

        v = (
            epsilon_y * y
            + gamma_xy
            / 2.0
            * x
        )

        base = 6 * i

        displacement[base] = u
        displacement[base + 1] = v

    strain = shell.membrane_strain(
        displacement
    )

    stress = shell.membrane_stress(
        displacement
    )

    expected_strain = np.array(
        [
            epsilon_x,
            epsilon_y,
            gamma_xy,
        ]
    )

    expected_stress = (
        plane_stress_matrix()
        @ expected_strain
    )

    assert np.allclose(
        strain,
        expected_strain,
        rtol=1e-12,
        atol=1e-14,
    )

    assert np.allclose(
        stress,
        expected_stress,
        rtol=1e-10,
        atol=1e-4,
    )


def test_rotated_shell_constant_strain_invariance():
    model = cb.Model()

    material = make_material()
    property = make_property(material)

    angle = np.deg2rad(37.0)

    ex = np.array(
        [
            np.cos(angle),
            np.sin(angle),
            0.0,
        ]
    )

    ey = np.array(
        [
            -np.sin(angle),
            np.cos(angle),
            0.0,
        ]
    )

    p0 = np.zeros(3)

    p1 = (
        2.0 * ex
    )

    p2 = ey

    n0 = model.add_node(
        *p0
    )

    n1 = model.add_node(
        *p1
    )

    n2 = model.add_node(
        *p2
    )

    shell = model.add_shell(
        n0,
        n1,
        n2,
        property,
    )

    epsilon_x = 1.5e-4

    # Apply displacement in the shell's
    # local x direction:
    #
    # u_local = epsilon_x * x_local
    #
    displacement = np.zeros(18)

    local_coordinates = [
        (0.0, 0.0),
        (2.0, 0.0),
        (0.0, 1.0),
    ]

    for i, (x, y) in enumerate(
        local_coordinates
    ):
        local_u = np.array(
            [
                epsilon_x * x,
                0.0,
                0.0,
            ]
        )

        # ex and ey define the shell's
        # global orientation.
        global_u = (
            ex * local_u[0]
            + ey * local_u[1]
        )

        base = 6 * i

        displacement[
            base:base + 3
        ] = global_u

    strain = shell.membrane_strain(
        displacement
    )

    expected = np.array(
        [
            epsilon_x,
            0.0,
            0.0,
        ]
    )

    assert np.allclose(
        strain,
        expected,
        rtol=1e-10,
        atol=1e-13,
    )


def test_two_triangle_patch_reproduces_constant_strain():
    model = cb.Model()

    material = make_material()
    property = make_property(material)

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
        0.0,
        1.0,
        0.0,
    )

    s0 = model.add_shell(
        n0,
        n1,
        n2,
        property,
    )

    s1 = model.add_shell(
        n0,
        n2,
        n3,
        property,
    )

    epsilon_x = 1.0e-4
    epsilon_y = 5.0e-5
    gamma_xy = 2.0e-5

    coordinates = [
        (0.0, 0.0),
        (1.0, 0.0),
        (1.0, 1.0),
        (0.0, 1.0),
    ]

    # Global small-strain tensor.
    #
    # Engineering shear:
    #
    # gamma_xy = 2 * epsilon_xy
    #
    global_strain_tensor = np.array(
        [
            [
                epsilon_x,
                gamma_xy / 2.0,
                0.0,
            ],
            [
                gamma_xy / 2.0,
                epsilon_y,
                0.0,
            ],
            [
                0.0,
                0.0,
                0.0,
            ],
        ]
    )

    # Global displacement vector:
    #
    # u = epsilon_x*x + gamma_xy/2*y
    # v = epsilon_y*y + gamma_xy/2*x
    #
    displacement = np.zeros(
        4 * 6
    )

    for node_id, (x, y) in enumerate(
        coordinates
    ):
        u = (
            epsilon_x * x
            + gamma_xy
            / 2.0
            * y
        )

        v = (
            epsilon_y * y
            + gamma_xy
            / 2.0
            * x
        )

        base = 6 * node_id

        displacement[base] = u
        displacement[base + 1] = v

    def expected_local_strain(shell):
        local_x = np.asarray(
            shell.local_x
        )

        local_y = np.asarray(
            shell.local_y
        )

        # Q maps global vector components
        # into the shell local system.
        Q = np.vstack(
            [
                local_x,
                local_y,
                np.asarray(
                    shell.local_z
                ),
            ]
        )

        local_tensor = (
            Q
            @ global_strain_tensor
            @ Q.T
        )

        return np.array(
            [
                local_tensor[0, 0],
                local_tensor[1, 1],
                2.0 * local_tensor[0, 1],
            ]
        )

    strain_0 = s0.membrane_strain(
        displacement
    )

    strain_1 = s1.membrane_strain(
        displacement
    )

    expected_0 = (
        expected_local_strain(s0)
    )

    expected_1 = (
        expected_local_strain(s1)
    )

    assert np.allclose(
        strain_0,
        expected_0,
        rtol=1e-12,
        atol=1e-14,
    )

    assert np.allclose(
        strain_1,
        expected_1,
        rtol=1e-12,
        atol=1e-14,
    )
