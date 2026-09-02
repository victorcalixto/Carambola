import numpy as np
import pytest

import carambola as cb





def test_bending_stress_zero_at_mid_surface():
    shell = make_shell()

    u = np.zeros(18)

    stress = shell.bending_stress(
        1.0 / 3.0,
        1.0 / 3.0,
        0.0,
        u,
    )

    assert np.allclose(
        stress,
        np.zeros(3),
        atol=1e-12,
    )

def test_bending_stress_matches_moment_resultant():
    shell = make_shell()

    kappa_x = 0.02

    coordinates = shell._local_coordinates()

    u = np.zeros(18)

    for node in range(3):
        x = coordinates[node, 0]

        offset = node * 6

        u[offset + 2] = (
            0.5
            * kappa_x
            * x**2
        )

        u[offset + 4] = (
            -kappa_x
            * x
        )

    thickness = 0.01
    z = thickness / 2.0

    moments = shell.bending_moments(
        1.0 / 3.0,
        1.0 / 3.0,
        u,
    )

    expected = (
        12.0
        * z
        / thickness**3
    ) * moments

    stress = shell.bending_stress(
        1.0 / 3.0,
        1.0 / 3.0,
        z,
        u,
    )

    assert np.allclose(
        stress,
        expected,
        rtol=1e-12,
        atol=1e-8,
    )


def test_bending_stress_top_bottom_are_opposite():
    shell = make_shell()

    kappa_x = 0.02

    coordinates = shell._local_coordinates()

    u = np.zeros(18)

    for node in range(3):
        x = coordinates[node, 0]

        offset = node * 6

        u[offset + 2] = (
            0.5
            * kappa_x
            * x**2
        )

        u[offset + 3] = 0.0
        u[offset + 4] = (
            -kappa_x
            * x
        )

    thickness = 0.01

    top = shell.bending_stress(
        1.0 / 3.0,
        1.0 / 3.0,
        +thickness / 2.0,
        u,
    )

    bottom = shell.bending_stress(
        1.0 / 3.0,
        1.0 / 3.0,
        -thickness / 2.0,
        u,
    )

    assert np.allclose(
        top,
        -bottom,
        rtol=1e-12,
        atol=1e-10,
    )

def test_bending_moment_recovery_x():
    shell = make_shell()

    kappa_x = 0.02

    coordinates = shell._local_coordinates()

    u = np.zeros(18)

    for node in range(3):
        x = coordinates[node, 0]

        offset = node * 6

        u[offset + 2] = 0.5 * kappa_x * x**2
        u[offset + 3] = 0.0
        u[offset + 4] = -kappa_x * x

    curvature = np.array([
        -kappa_x,
        0.0,
        0.0,
    ])

    D = shell._bending_constitutive_matrix()

    expected = D @ curvature

    moment = shell.bending_moments(
        1.0 / 3.0,
        1.0 / 3.0,
        u,
    )

    assert np.allclose(
        moment,
        expected,
        atol=1e-10,
    )



def test_bending_curvature_recovery_x():
    shell = make_shell()

    kappa_x = 0.02

    coordinates = shell._local_coordinates()

    u = np.zeros(18)

    for node in range(3):
        x = coordinates[node, 0]
        y = coordinates[node, 1]

        w = 0.5 * kappa_x * x**2
        rx = 0.0
        ry = -kappa_x * x

        offset = node * 6

        u[offset + 2] = w
        u[offset + 3] = rx
        u[offset + 4] = ry

    expected = np.array(
        [
            -kappa_x,
            0.0,
            0.0,
        ]
    )

    integration_points = [
        (1.0 / 6.0, 1.0 / 6.0),
        (2.0 / 3.0, 1.0 / 6.0),
        (1.0 / 6.0, 2.0 / 3.0),
        (1.0 / 3.0, 1.0 / 3.0),
    ]

    for xi, eta in integration_points:
        curvature = shell.bending_curvature(
            xi,
            eta,
            u,
        )

        assert np.allclose(
            curvature,
            expected,
            atol=1e-12,
        )


def test_bending_curvature_recovery_y():
    shell = make_shell()

    kappa_y = 0.03

    coordinates = shell._local_coordinates()

    u = np.zeros(18)

    for node in range(3):
        x = coordinates[node, 0]
        y = coordinates[node, 1]

        w = 0.5 * kappa_y * y**2
        rx = kappa_y * y
        ry = 0.0

        offset = node * 6

        u[offset + 2] = w
        u[offset + 3] = rx
        u[offset + 4] = ry

    expected = np.array(
        [
            0.0,
            -kappa_y,
            0.0,
        ]
    )

    integration_points = [
        (1.0 / 6.0, 1.0 / 6.0),
        (2.0 / 3.0, 1.0 / 6.0),
        (1.0 / 6.0, 2.0 / 3.0),
        (1.0 / 3.0, 1.0 / 3.0),
    ]

    for xi, eta in integration_points:
        curvature = shell.bending_curvature(
            xi,
            eta,
            u,
        )

        assert np.allclose(
            curvature,
            expected,
            atol=1e-12,
        )


def test_bending_curvature_recovery_twisting():
    shell = make_shell()

    gamma = 0.015

    coordinates = shell._local_coordinates()

    u = np.zeros(18)

    for node in range(3):
        x = coordinates[node, 0]
        y = coordinates[node, 1]

        w = gamma * x * y
        rx = gamma * x
        ry = -gamma * y

        offset = node * 6

        u[offset + 2] = w
        u[offset + 3] = rx
        u[offset + 4] = ry

    expected = np.array(
        [
            0.0,
            0.0,
            -2.0 * gamma,
        ]
    )

    integration_points = [
        (1.0 / 6.0, 1.0 / 6.0),
        (2.0 / 3.0, 1.0 / 6.0),
        (1.0 / 6.0, 2.0 / 3.0),
        (1.0 / 3.0, 1.0 / 3.0),
    ]

    for xi, eta in integration_points:
        curvature = shell.bending_curvature(
            xi,
            eta,
            u,
        )

        assert np.allclose(
            curvature,
            expected,
            atol=1e-12,
        )






def test_shell_pressure_load_vector_shape():
    shell = make_shell()

    f = shell.pressure_load_vector(
        1000.0
    )

    assert f.shape == (18,)

def test_shell_pressure_load_vector_xy():
    shell = make_shell()

    pressure = 900.0

    f = shell.pressure_load_vector(
        pressure
    )

    expected = np.zeros(18)

    expected[2] = 300.0
    expected[8] = 300.0
    expected[14] = 300.0

    assert np.allclose(
        f,
        expected,
    )

def test_shell_pressure_total_force_equals_pressure_times_area():
    shell = make_shell()

    pressure = 1200.0

    f = shell.pressure_load_vector(
        pressure
    )

    nodal_forces = np.array([
        f[0:3],
        f[6:9],
        f[12:15],
    ])

    resultant = np.sum(
        nodal_forces,
        axis=0,
    )

    expected = (
        pressure
        * shell.area
        * np.array(
            shell.local_z
        )
    )

    assert np.allclose(
        resultant,
        expected,
    )

def test_shell_negative_pressure_acts_downward():
    shell = make_shell()

    f = shell.pressure_load_vector(
        -600.0
    )

    assert f[2] < 0.0
    assert f[8] < 0.0
    assert f[14] < 0.0

    assert (
        f[2]
        + f[8]
        + f[14]
    ) == pytest.approx(
        -600.0 * shell.area
    )

def test_shell_pressure_follows_shell_normal():
    model = cb.Model()

    n0 = model.add_node(
        0.0, 0.0, 0.0
    )

    n1 = model.add_node(
        0.0, 1.0, 0.0
    )

    n2 = model.add_node(
        0.0, 0.0, 1.0
    )

    material = cb.Material(
        "Steel",
        200e9,
        0.3,
        7850.0,
    )

    prop = cb.ShellProperty(
        material,
        0.01,
    )

    shell = model.add_shell(
        n0,
        n1,
        n2,
        prop,
    )

    pressure = 600.0

    f = shell.pressure_load_vector(
        pressure
    )

    resultant = (
        f[0:3]
        + f[6:9]
        + f[12:15]
    )

    expected = (
        pressure
        * shell.area
        * np.array(
            shell.local_z
        )
    )

    assert np.allclose(
        resultant,
        expected,
    )


def test_shell_pressure_has_no_direct_nodal_moments():
    shell = make_shell()

    f = shell.pressure_load_vector(
        1000.0
    )

    rotational_dofs = [
        3, 4, 5,
        9, 10, 11,
        15, 16, 17,
    ]

    assert np.allclose(
        f[rotational_dofs],
        0.0,
    )








def test_dkt_constant_curvature_x_patch():
    shell = make_shell()

    kappa_x = 0.002

    coordinates = shell._local_coordinates()

    #
    # Prescribed quadratic field:
    #
    #   w(x, y) = 0.5 * kappa_x * x^2
    #
    # DKT nodal rotations:
    #
    #   rx = theta_x = dw/dy = 0
    #   ry = theta_y = -dw/dx = -kappa_x * x
    #
    # Bending DOF ordering:
    #
    #   [w1, rx1, ry1,
    #    w2, rx2, ry2,
    #    w3, rx3, ry3]
    #

    q = np.zeros(9)

    for node in range(3):
        x = coordinates[node, 0]

        w = (
            0.5
            * kappa_x
            * x**2
        )

        rx = 0.0

        ry = (
            -kappa_x
            * x
        )

        offset = 3 * node

        q[offset + 0] = w
        q[offset + 1] = rx
        q[offset + 2] = ry

    expected = np.array([
        -kappa_x,
        0.0,
        0.0,
    ])

    points = [
        (1.0 / 6.0, 1.0 / 6.0),
        (2.0 / 3.0, 1.0 / 6.0),
        (1.0 / 6.0, 2.0 / 3.0),
        (1.0 / 3.0, 1.0 / 3.0),
    ]

    for xi, eta in points:
        B = (
            shell
            ._dkt_bending_strain_displacement_matrix(
                xi,
                eta,
            )
        )

        curvature = B @ q

        assert np.allclose(
            curvature,
            expected,
            rtol=1e-10,
            atol=1e-12,
        )

def test_dkt_constant_curvature_y_patch():
    shell = make_shell()

    kappa_y = 0.003

    coordinates = shell._local_coordinates()

    q = np.zeros(9)

    for node in range(3):
        y = coordinates[node, 1]

        w = (
            0.5
            * kappa_y
            * y**2
        )

        rx = (
            kappa_y
            * y
        )

        ry = 0.0

        offset = 3 * node

        q[offset + 0] = w
        q[offset + 1] = rx
        q[offset + 2] = ry

    expected = np.array([
        0.0,
        -kappa_y,
        0.0,
    ])

    points = [
        (1.0 / 6.0, 1.0 / 6.0),
        (2.0 / 3.0, 1.0 / 6.0),
        (1.0 / 6.0, 2.0 / 3.0),
        (1.0 / 3.0, 1.0 / 3.0),
    ]

    for xi, eta in points:
        B = (
            shell
            ._dkt_bending_strain_displacement_matrix(
                xi,
                eta,
            )
        )

        curvature = B @ q

        assert np.allclose(
            curvature,
            expected,
            rtol=1e-10,
            atol=1e-12,
        )
def test_dkt_constant_twisting_curvature_patch():
    shell = make_shell()

    gamma = 0.0025

    coordinates = shell._local_coordinates()

    q = np.zeros(9)

    for node in range(3):
        x = coordinates[node, 0]
        y = coordinates[node, 1]

        w = gamma * x * y

        rx = gamma * x
        ry = -gamma * y

        offset = 3 * node

        q[offset + 0] = w
        q[offset + 1] = rx
        q[offset + 2] = ry

    expected = np.array([
        0.0,
        0.0,
        -2.0 * gamma,
    ])

    points = [
        (1.0 / 6.0, 1.0 / 6.0),
        (2.0 / 3.0, 1.0 / 6.0),
        (1.0 / 6.0, 2.0 / 3.0),
        (1.0 / 3.0, 1.0 / 3.0),
    ]

    for xi, eta in points:
        B = (
            shell
            ._dkt_bending_strain_displacement_matrix(
                xi,
                eta,
            )
        )

        curvature = B @ q

        assert np.allclose(
            curvature,
            expected,
            rtol=1e-10,
            atol=1e-12,
        )



def test_shell_local_stiffness_matrix_shape():
    shell = make_shell()

    K = shell._local_stiffness_matrix()

    assert K.shape == (18, 18)


def test_shell_local_stiffness_matrix_symmetric():
    shell = make_shell()

    K = shell._local_stiffness_matrix()

    assert np.allclose(
        K,
        K.T,
        atol=1e-8,
    )

def test_shell_local_stiffness_contains_drilling_stabilization():
    shell = make_shell()

    K = shell._local_stiffness_matrix()
    kd = shell._drilling_stiffness()

    drilling = [5, 11, 17]

    for dof in drilling:
        assert K[dof, dof] == pytest.approx(kd)


def test_shell_drilling_stabilization_is_diagonal():
    shell = make_shell()

    K = shell._local_stiffness_matrix()

    drilling = [5, 11, 17]

    for i in drilling:
        for j in drilling:
            if i != j:
                assert K[i, j] == pytest.approx(
                    0.0,
                    abs=1e-12,
                )



def test_shell_local_stiffness_contains_membrane_block():
    shell = make_shell()

    K = shell._local_stiffness_matrix()
    Km = shell._local_membrane_stiffness_matrix()

    membrane_map = [
        0, 1,
        6, 7,
        12, 13,
    ]

    extracted = K[
        np.ix_(
            membrane_map,
            membrane_map,
        )
    ]

    assert np.allclose(
        extracted,
        Km,
        atol=1e-8,
    )


def test_shell_local_stiffness_contains_bending_block():
    shell = make_shell()

    K = shell._local_stiffness_matrix()
    Kb = shell._local_bending_stiffness_matrix()

    bending_map = [
        2, 3, 4,
        8, 9, 10,
        14, 15, 16,
    ]

    extracted = K[
        np.ix_(
            bending_map,
            bending_map,
        )
    ]

    assert np.allclose(
        extracted,
        Kb,
        atol=1e-8,
    )



def test_shell_stiffness_matrix_shape():
    shell = make_shell()

    K = shell.stiffness_matrix()

    assert K.shape == (18, 18)


def test_shell_stiffness_matrix_symmetric():
    shell = make_shell()

    K = shell.stiffness_matrix()

    assert np.allclose(
        K,
        K.T,
        atol=1e-8,
    )


def test_shell_stiffness_xy_matches_local():
    shell = make_shell()

    Klocal = shell._local_stiffness_matrix()
    Kglobal = shell.stiffness_matrix()

    assert np.allclose(
        Kglobal,
        Klocal,
        atol=1e-8,
    )






def test_local_bending_stiffness_matrix_shape():
    shell = make_shell()

    K = shell._local_bending_stiffness_matrix()

    assert K.shape == (9, 9)


def test_local_bending_stiffness_matrix_symmetric():
    shell = make_shell()

    K = shell._local_bending_stiffness_matrix()

    assert np.allclose(
        K,
        K.T,
        atol=1e-8,
    )


def test_local_bending_stiffness_matrix_finite():
    shell = make_shell()

    K = shell._local_bending_stiffness_matrix()

    assert np.all(
        np.isfinite(K)
    )


def test_local_bending_stiffness_rigid_translation_zero_energy():
    shell = make_shell()

    K = shell._local_bending_stiffness_matrix()

    rigid_w = np.array([
        1.0, 0.0, 0.0,
        1.0, 0.0, 0.0,
        1.0, 0.0, 0.0,
    ])

    energy = (
        rigid_w
        @ K
        @ rigid_w
    )

    assert energy == pytest.approx(
        0.0,
        abs=1e-6,
    )

def test_local_bending_stiffness_positive_semidefinite():
    shell = make_shell()

    K = shell._local_bending_stiffness_matrix()

    eigenvalues = np.linalg.eigvalsh(K)

    assert np.min(eigenvalues) >= -1e-6


def test_dkt_bending_strain_displacement_matrix_shape():
    shell = make_shell()

    B = shell._dkt_bending_strain_displacement_matrix(
        1.0 / 3.0,
        1.0 / 3.0,
    )

    assert B.shape == (3, 9)

    assert np.all(
        np.isfinite(B)
    )

def test_dkt_bending_strain_displacement_matrix_finite():
    shell = make_shell()

    points = [
        (1.0 / 6.0, 1.0 / 6.0),
        (2.0 / 3.0, 1.0 / 6.0),
        (1.0 / 6.0, 2.0 / 3.0),
    ]

    for xi, eta in points:
        B = shell._dkt_bending_strain_displacement_matrix(
            xi,
            eta,
        )

        assert np.all(
            np.isfinite(B)
        )



def test_dkt_bending_rigid_translation_zero_curvature():
    shell = make_shell()

    B = shell._dkt_bending_strain_displacement_matrix(
        0.23,
        0.31,
    )

    # Same transverse displacement w at all nodes,
    # no rotations.
    rigid_w = np.array([
        1.0, 0.0, 0.0,
        1.0, 0.0, 0.0,
        1.0, 0.0, 0.0,
    ])

    curvature = B @ rigid_w

    assert np.allclose(
        curvature,
        np.zeros(3),
        atol=1e-12,
    )



def test_bending_shape_function_derivatives_centroid():
    shell = make_shell()

    dN = shell._bending_shape_function_derivatives(
        1.0 / 3.0,
        1.0 / 3.0,
    )

    expected = np.array([
        [-1.0 / 3.0, -1.0 / 3.0],
        [ 1.0 / 3.0,  0.0],
        [ 0.0,        1.0 / 3.0],
        [ 4.0 / 3.0,  4.0 / 3.0],
        [-4.0 / 3.0,  0.0],
        [ 0.0,       -4.0 / 3.0],
    ])

    assert dN.shape == (6, 2)

    assert np.allclose(
        dN,
        expected,
        atol=1e-12,
    )

def test_bending_shape_function_derivative_sum():
    shell = make_shell()

    dN = shell._bending_shape_function_derivatives(
        0.23,
        0.31,
    )

    assert np.sum(dN[:, 0]) == pytest.approx(
        0.0,
        abs=1e-12,
    )

    assert np.sum(dN[:, 1]) == pytest.approx(
        0.0,
        abs=1e-12,
    )


def test_dkt_rotation_derivatives_finite_difference():
    shell = make_shell()

    xi = 0.23
    eta = 0.31

    h = 1e-7

    derivatives = shell._dkt_rotation_derivatives(
        xi,
        eta,
    )

    H_xi_plus = shell._dkt_rotation_interpolation(
        1.0 - (xi + h) - eta,
        xi + h,
        eta,
    )

    H_xi_minus = shell._dkt_rotation_interpolation(
        1.0 - (xi - h) - eta,
        xi - h,
        eta,
    )

    numeric_xi = (
        H_xi_plus - H_xi_minus
    ) / (2.0 * h)

    H_eta_plus = shell._dkt_rotation_interpolation(
        1.0 - xi - (eta + h),
        xi,
        eta + h,
    )

    H_eta_minus = shell._dkt_rotation_interpolation(
        1.0 - xi - (eta - h),
        xi,
        eta - h,
    )

    numeric_eta = (
        H_eta_plus - H_eta_minus
    ) / (2.0 * h)

    assert np.allclose(
        derivatives[0],
        numeric_xi[0],
        atol=1e-8,
    )

    assert np.allclose(
        derivatives[1],
        numeric_eta[0],
        atol=1e-8,
    )

    assert np.allclose(
        derivatives[2],
        numeric_xi[1],
        atol=1e-8,
    )

    assert np.allclose(
        derivatives[3],
        numeric_eta[1],
        atol=1e-8,
    )

def test_dkt_rotation_interpolation_centroid():
    shell = make_shell()

    H = shell._dkt_rotation_interpolation(
        1.0 / 3.0,
        1.0 / 3.0,
        1.0 / 3.0,
    )

    expected = np.array([
        [
             1.0 / 3.0,
             0.0,
             0.0,
            -3.0 / 5.0,
            -2.0 / 15.0,
            -4.0 / 15.0,
             4.0 / 15.0,
            -2.0 / 15.0,
             1.0 / 15.0,
        ],
        [
             2.0 / 3.0,
             0.0,
             0.0,
             2.0 / 15.0,
            -4.0 / 15.0,
             2.0 / 15.0,
            -4.0 / 5.0,
             1.0 / 15.0,
             2.0 / 15.0,
        ],
    ])

    assert np.allclose(
        H,
        expected,
        atol=1e-12,
    )




def test_dkt_rotation_interpolation_node_1():
    shell = make_shell()

    H = shell._dkt_rotation_interpolation(
        1.0, 0.0, 0.0
    )

    expected = np.zeros((2, 9))

    # beta_x = ry
    expected[0, 2] = 1.0

    # beta_y = -rx
    expected[1, 1] = -1.0

    assert H.shape == (2, 9)

    assert np.allclose(
        H,
        expected,
        atol=1e-12,
    )



def test_dkt_rotation_interpolation_node_2():
    shell = make_shell()

    H = shell._dkt_rotation_interpolation(
        0.0, 1.0, 0.0
    )

    expected = np.zeros((2, 9))

    expected[0, 5] = 1.0
    expected[1, 4] = -1.0

    assert np.allclose(
        H,
        expected,
        atol=1e-12,
    )



def test_dkt_rotation_interpolation_node_3():
    shell = make_shell()

    H = shell._dkt_rotation_interpolation(
        0.0, 0.0, 1.0
    )

    expected = np.zeros((2, 9))

    expected[0, 8] = 1.0
    expected[1, 7] = -1.0

    assert np.allclose(
        H,
        expected,
        atol=1e-12,
    )

def test_dkt_rotation_interpolation_is_finite():
    shell = make_shell()

    H = shell._dkt_rotation_interpolation(
        1.0 / 3.0,
        1.0 / 3.0,
        1.0 / 3.0,
    )

    assert H.shape == (2, 9)

    assert np.all(
        np.isfinite(H)
    )



def test_dkt_rotation_coefficients():
    shell = make_shell()

    coefficients = shell._dkt_rotation_coefficients()

    expected = np.array([
        [
            -0.4,
            -0.3,
             0.1,
             0.2,
            -0.35,
        ],
        [
             0.0,
             0.0,
            -0.5,
            -1.0,
             0.25,
        ],
        [
             0.5,
             0.0,
             0.25,
             0.0,
            -0.5,
        ],
    ])

    assert coefficients.shape == (3, 5)

    assert np.allclose(
        coefficients,
        expected,
        atol=1e-12,
    )



def test_bending_shape_functions_vertices():
    shell = make_shell()

    n1 = shell._bending_shape_functions(
        1.0, 0.0, 0.0
    )

    n2 = shell._bending_shape_functions(
        0.0, 1.0, 0.0
    )

    n3 = shell._bending_shape_functions(
        0.0, 0.0, 1.0
    )

    assert np.allclose(
        n1,
        [1.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        atol=1e-12,
    )

    assert np.allclose(
        n2,
        [0.0, 1.0, 0.0, 0.0, 0.0, 0.0],
        atol=1e-12,
    )

    assert np.allclose(
        n3,
        [0.0, 0.0, 1.0, 0.0, 0.0, 0.0],
        atol=1e-12,
    )

def test_bending_shape_functions_midpoints():
    shell = make_shell()

    # edge 12 -> N6
    n12 = shell._bending_shape_functions(
        0.5, 0.5, 0.0
    )

    # edge 23 -> N4
    n23 = shell._bending_shape_functions(
        0.0, 0.5, 0.5
    )

    # edge 31 -> N5
    n31 = shell._bending_shape_functions(
        0.5, 0.0, 0.5
    )

    assert np.allclose(
        n12,
        [0.0, 0.0, 0.0, 0.0, 0.0, 1.0],
        atol=1e-12,
    )

    assert np.allclose(
        n23,
        [0.0, 0.0, 0.0, 1.0, 0.0, 0.0],
        atol=1e-12,
    )

    assert np.allclose(
        n31,
        [0.0, 0.0, 0.0, 0.0, 1.0, 0.0],
        atol=1e-12,
    )






def test_bending_shape_functions_partition_of_unity():
    shell = make_shell()

    N = shell._bending_shape_functions(
        0.2,
        0.3,
        0.5,
    )

    assert np.sum(N) == pytest.approx(
        1.0,
        rel=1e-12,
        abs=1e-12,
    )
def test_bending_edge_coefficients():
    shell = make_shell()

    coefficients = shell._bending_edge_coefficients()

    expected = np.array([
        [
            -12.0 / 5.0,
            -6.0 / 5.0,
             3.0 / 5.0,
             6.0 / 5.0,
            12.0 / 5.0,
        ],
        [
             0.0,
             0.0,
             3.0,
            -6.0,
             0.0,
        ],
        [
             3.0,
             0.0,
             0.0,
             0.0,
             3.0,
        ],
    ])

    assert coefficients.shape == (3, 5)

    assert np.allclose(
        coefficients,
        expected,
        atol=1e-12,
    )




def test_bending_edge_geometry():
    shell = make_shell()

    geometry = shell._bending_edge_geometry()

    expected = np.array([
        [2.0, -1.0, 5.0],
        [0.0,  1.0, 1.0],
        [-2.0, 0.0, 4.0],
    ])

    assert geometry.shape == (3, 3)

    assert np.allclose(
        geometry,
        expected,
        atol=1e-12,
    )

def test_bending_edge_geometry_lengths():
    shell = make_shell()

    geometry = shell._bending_edge_geometry()

    for edge in geometry:
        dx = edge[0]
        dy = edge[1]
        length_squared = edge[2]

        assert length_squared == pytest.approx(
            dx * dx + dy * dy,
            rel=1e-12,
        )

def test_local_coordinates_xy_shell():
    shell = make_shell()

    coordinates = shell._local_coordinates()

    expected = np.array([
        [0.0, 0.0],
        [2.0, 0.0],
        [0.0, 1.0],
    ])

    assert coordinates.shape == (3, 2)

    assert np.allclose(
        coordinates,
        expected,
        atol=1e-12,
    )

def test_local_coordinates_rotated_shell():
    model = cb.Model()

    n0 = model.add_node(
        0.0,
        0.0,
        0.0,
    )

    n1 = model.add_node(
        0.0,
        1.0,
        0.0,
    )

    n2 = model.add_node(
        0.0,
        0.0,
        1.0,
    )

    material = cb.Material(
        "Steel",
        200e9,
        0.3,
        7850.0,
    )

    prop = cb.ShellProperty(
        material,
        0.01,
    )

    shell = model.add_shell(
        n0,
        n1,
        n2,
        prop,
    )

    coordinates = shell._local_coordinates()

    expected = np.array([
        [0.0, 0.0],
        [1.0, 0.0],
        [0.0, 1.0],
    ])

    assert np.allclose(
        coordinates,
        expected,
        atol=1e-12,
    )


def test_local_coordinates_preserve_edge_lengths():
    model = cb.Model()

    n0 = model.add_node(
        1.0,
        2.0,
        3.0,
    )

    n1 = model.add_node(
        3.0,
        3.0,
        4.0,
    )

    n2 = model.add_node(
        2.0,
        5.0,
        6.0,
    )

    material = cb.Material(
        "Steel",
        200e9,
        0.3,
        7850.0,
    )

    prop = cb.ShellProperty(
        material,
        0.01,
    )

    shell = model.add_shell(
        n0,
        n1,
        n2,
        prop,
    )

    xy = shell._local_coordinates()

    local_ab = np.linalg.norm(
        xy[1] - xy[0]
    )

    local_bc = np.linalg.norm(
        xy[2] - xy[1]
    )

    local_ca = np.linalg.norm(
        xy[0] - xy[2]
    )

    global_a = np.array([1.0, 2.0, 3.0])
    global_b = np.array([3.0, 3.0, 4.0])
    global_c = np.array([2.0, 5.0, 6.0])

    global_ab = np.linalg.norm(
        global_b - global_a
    )

    global_bc = np.linalg.norm(
        global_c - global_b
    )

    global_ca = np.linalg.norm(
        global_a - global_c
    )

    assert local_ab == pytest.approx(
        global_ab,
        rel=1e-12,
    )

    assert local_bc == pytest.approx(
        global_bc,
        rel=1e-12,
    )

    assert local_ca == pytest.approx(
        global_ca,
        rel=1e-12,
    )



def test_local_bending_displacements_rotated_shell():
    model = cb.Model()

    n0 = model.add_node(
        0.0,
        0.0,
        0.0,
    )

    n1 = model.add_node(
        0.0,
        1.0,
        0.0,
    )

    n2 = model.add_node(
        0.0,
        0.0,
        1.0,
    )

    material = cb.Material(
        "Steel",
        200e9,
        0.3,
        7850.0,
    )

    prop = cb.ShellProperty(
        material,
        0.01,
    )

    shell = model.add_shell(
        n0,
        n1,
        n2,
        prop,
    )

    displacements = np.zeros(18)

    # For this shell:
    #
    # local x = global Y
    # local y = global Z
    # local z = global X
    #
    # Therefore:
    #
    # w  <- global UX
    # rx <- global RY
    # ry <- global RZ

    # Node A
    displacements[0] = 1.0   # UX -> local w
    displacements[4] = 2.0   # RY -> local rx
    displacements[5] = 3.0   # RZ -> local ry

    # Node B
    displacements[6] = 4.0
    displacements[10] = 5.0
    displacements[11] = 6.0

    # Node C
    displacements[12] = 7.0
    displacements[16] = 8.0
    displacements[17] = 9.0

    u = shell._local_bending_displacements(
        displacements
    )

    expected = np.array([
        1.0, 2.0, 3.0,
        4.0, 5.0, 6.0,
        7.0, 8.0, 9.0,
    ])

    assert np.allclose(
        u,
        expected,
        atol=1e-12,
    )


def test_full_transformation_matrix_shape():
    shell = make_shell()

    T = shell._full_transformation_matrix()

    assert T.shape == (18, 18)


def test_full_transformation_matrix_is_orthogonal():
    shell = make_shell()

    T = shell._full_transformation_matrix()

    identity = np.eye(18)

    assert np.allclose(
        T @ T.T,
        identity,
        atol=1e-12,
    )


def test_local_bending_displacements_shape():
    shell = make_shell()

    displacements = np.zeros(18)

    u = shell._local_bending_displacements(
        displacements
    )

    assert u.shape == (9,)


def test_local_bending_displacements_xy_shell():
    shell = make_shell()

    displacements = np.zeros(18)

    # Node A
    displacements[2] = 1.0   # UZ
    displacements[3] = 2.0   # RX
    displacements[4] = 3.0   # RY
    displacements[5] = 99.0  # RZ - should be ignored

    # Node B
    displacements[8] = 4.0
    displacements[9] = 5.0
    displacements[10] = 6.0
    displacements[11] = 99.0

    # Node C
    displacements[14] = 7.0
    displacements[15] = 8.0
    displacements[16] = 9.0
    displacements[17] = 99.0

    u = shell._local_bending_displacements(
        displacements
    )

    expected = np.array([
        1.0, 2.0, 3.0,
        4.0, 5.0, 6.0,
        7.0, 8.0, 9.0,
    ])

    assert np.allclose(
        u,
        expected,
    )






def test_bending_constitutive_matrix_shape():
    shell = make_shell()

    D = shell._bending_constitutive_matrix()

    assert D.shape == (3, 3)


def test_bending_constitutive_matrix_symmetric():
    shell = make_shell()

    D = shell._bending_constitutive_matrix()

    assert np.allclose(
        D,
        D.T,
    )






def test_shell_reference_remains_valid():
    model = cb.Model()

    steel = cb.Material(
        "Steel",
        200e9,
        0.3,
        7850.0,
    )

    prop = cb.ShellProperty(
        steel,
        0.01,
    )

    n0 = model.add_node(0.0, 0.0, 0.0)
    n1 = model.add_node(1.0, 0.0, 0.0)
    n2 = model.add_node(0.0, 1.0, 0.0)

    shell = model.add_shell(
        n0,
        n1,
        n2,
        prop,
    )

    for i in range(100):
        a = model.add_node(
            float(i + 10),
            0.0,
            0.0,
        )

        b = model.add_node(
            float(i + 10),
            1.0,
            0.0,
        )

        c = model.add_node(
            float(i + 11),
            0.0,
            0.0,
        )

        model.add_shell(
            a,
            b,
            c,
            prop,
        )

    assert shell.area == pytest.approx(
        0.5
    )

def test_model_owns_shell():
    model = cb.Model()

    n0 = model.add_node(
        0.0, 0.0, 0.0
    )

    n1 = model.add_node(
        2.0, 0.0, 0.0
    )

    n2 = model.add_node(
        0.0, 1.0, 0.0
    )

    steel = cb.Material(
        "Steel",
        200e9,
        0.3,
        7850.0,
    )

    prop = cb.ShellProperty(
        steel,
        0.01,
    )

    shell = model.add_shell(
        n0,
        n1,
        n2,
        prop,
    )

    assert model.shell_count == 1

    assert len(model.shells) == 1

    assert model.shells[0].area == pytest.approx(
        1.0
    )

    assert shell.area == pytest.approx(
        1.0
    )




def make_shell():
    model = cb.Model()

    n0 = model.add_node(
        0.0, 0.0, 0.0
    )

    n1 = model.add_node(
        2.0, 0.0, 0.0
    )

    n2 = model.add_node(
        0.0, 1.0, 0.0
    )

    steel = cb.Material(
        "Steel",
        200e9,
        0.3,
        7850.0,
    )

    prop = cb.ShellProperty(
        steel,
        0.01,
    )

    shell = cb.Shell3D(
        n0,
        n1,
        n2,
        prop,
    )

    return shell


def test_shell_area():
    shell = make_shell()

    assert shell.area == pytest.approx(
        1.0
    )


def test_shell_local_axes():
    shell = make_shell()

    assert np.allclose(
        shell.local_x,
        [1.0, 0.0, 0.0],
    )

    assert np.allclose(
        shell.local_y,
        [0.0, 1.0, 0.0],
    )

    assert np.allclose(
        shell.local_z,
        [0.0, 0.0, 1.0],
    )


def test_shell_axes_are_orthonormal():
    shell = make_shell()

    x = shell.local_x
    y = shell.local_y
    z = shell.local_z

    assert np.dot(x, y) == pytest.approx(
        0.0
    )

    assert np.dot(x, z) == pytest.approx(
        0.0
    )

    assert np.dot(y, z) == pytest.approx(
        0.0
    )

    assert np.linalg.norm(x) == pytest.approx(
        1.0
    )

    assert np.linalg.norm(y) == pytest.approx(
        1.0
    )

    assert np.linalg.norm(z) == pytest.approx(
        1.0
    )


def test_shell_B_matrix_shape():
    shell = make_shell()

    B = shell._strain_displacement_matrix()

    assert B.shape == (3, 6)


def test_shell_constitutive_matrix_shape():
    shell = make_shell()

    D = shell._constitutive_matrix()

    assert D.shape == (3, 3)


def test_shell_local_stiffness_shape():
    shell = make_shell()

    K = (
        shell._local_membrane_stiffness_matrix()
    )

    assert K.shape == (6, 6)


def test_shell_global_stiffness_shape():
    shell = make_shell()

    K = shell._membrane_stiffness_matrix()

    assert K.shape == (9, 9)


def test_shell_stiffness_is_symmetric():
    shell = make_shell()

    K = shell._membrane_stiffness_matrix()

    assert np.allclose(
        K,
        K.T,
    )


def test_zero_area_shell_rejected():
    model = cb.Model()

    n0 = model.add_node(
        0.0, 0.0, 0.0
    )

    n1 = model.add_node(
        1.0, 0.0, 0.0
    )

    n2 = model.add_node(
        2.0, 0.0, 0.0
    )

    steel = cb.Material(
        "Steel",
        200e9,
        0.3,
        7850.0,
    )

    prop = cb.ShellProperty(
        steel,
        0.01,
    )

    with pytest.raises(ValueError):
        cb.Shell3D(
            n0,
            n1,
            n2,
            prop,
        )
