#include <carambola/elements/shell3d.hpp>

#include <cmath>
#include <stdexcept>
#include <carambola/dof.hpp>
#include <algorithm>


namespace carambola {

Shell3D::Shell3D(
    const Node& node_a,
    const Node& node_b,
    const Node& node_c,
    const ShellProperty& property
)
    : node_a_(&node_a),
      node_b_(&node_b),
      node_c_(&node_c),
      property_(&property)
{
    if (area() <= 1e-12) {
        throw std::invalid_argument(
            "Shell3D cannot have zero or near-zero area."
        );
    }
}

const Node& Shell3D::node_a() const
{
    return *node_a_;
}

const Node& Shell3D::node_b() const
{
    return *node_b_;
}

const Node& Shell3D::node_c() const
{
    return *node_c_;
}

const ShellProperty& Shell3D::property() const
{
    return *property_;
}

double Shell3D::area() const
{
    const Eigen::Vector3d a(
        node_a_->x(),
        node_a_->y(),
        node_a_->z()
    );

    const Eigen::Vector3d b(
        node_b_->x(),
        node_b_->y(),
        node_b_->z()
    );

    const Eigen::Vector3d c(
        node_c_->x(),
        node_c_->y(),
        node_c_->z()
    );

    return 0.5
        * (
            (b - a).cross(c - a)
        ).norm();
}

Eigen::Vector3d Shell3D::local_x() const
{
    Eigen::Vector3d x(
        node_b_->x() - node_a_->x(),
        node_b_->y() - node_a_->y(),
        node_b_->z() - node_a_->z()
    );

    return x.normalized();
}

Eigen::Vector3d Shell3D::local_z() const
{
    const Eigen::Vector3d a(
        node_a_->x(),
        node_a_->y(),
        node_a_->z()
    );

    const Eigen::Vector3d b(
        node_b_->x(),
        node_b_->y(),
        node_b_->z()
    );

    const Eigen::Vector3d c(
        node_c_->x(),
        node_c_->y(),
        node_c_->z()
    );

    return (
        (b - a).cross(c - a)
    ).normalized();
}

Eigen::Vector3d Shell3D::local_y() const
{
    return local_z()
        .cross(local_x())
        .normalized();
}

Eigen::Matrix3d Shell3D::rotation_matrix() const
{
    Eigen::Matrix3d R;

    R.row(0) =
        local_x().transpose();

    R.row(1) =
        local_y().transpose();

    R.row(2) =
        local_z().transpose();

    return R;
}


Eigen::Matrix<double, 3, 2>
Shell3D::local_coordinates() const
{
    const Eigen::Vector3d origin(
        node_a_->x(),
        node_a_->y(),
        node_a_->z()
    );

    const Eigen::Vector3d b_global(
        node_b_->x(),
        node_b_->y(),
        node_b_->z()
    );

    const Eigen::Vector3d c_global(
        node_c_->x(),
        node_c_->y(),
        node_c_->z()
    );

    const Eigen::Vector3d x =
        local_x();

    const Eigen::Vector3d y =
        local_y();

    Eigen::Matrix<double, 3, 2> coordinates;

    coordinates <<
        0.0, 0.0,
        (b_global - origin).dot(x),
        (b_global - origin).dot(y),
        (c_global - origin).dot(x),
        (c_global - origin).dot(y);

    return coordinates;
}

Eigen::Matrix<double, 3, 3>
Shell3D::bending_edge_geometry() const
{
    const auto coordinates =
        local_coordinates();

    const double x1 =
        coordinates(0, 0);

    const double y1 =
        coordinates(0, 1);

    const double x2 =
        coordinates(1, 0);

    const double y2 =
        coordinates(1, 1);

    const double x3 =
        coordinates(2, 0);

    const double y3 =
        coordinates(2, 1);

    /*
     * DKT cyclic edge convention:
     *
     * edge 23
     * edge 31
     * edge 12
     */

    const double x23 =
        x2 - x3;

    const double y23 =
        y2 - y3;

    const double x31 =
        x3 - x1;

    const double y31 =
        y3 - y1;

    const double x12 =
        x1 - x2;

    const double y12 =
        y1 - y2;

    const double l23_squared =
        x23 * x23
        + y23 * y23;

    const double l31_squared =
        x31 * x31
        + y31 * y31;

    const double l12_squared =
        x12 * x12
        + y12 * y12;

    Eigen::Matrix<double, 3, 3> geometry;

    geometry <<
        x23, y23, l23_squared,
        x31, y31, l31_squared,
        x12, y12, l12_squared;

    return geometry;
}


Eigen::Matrix<double, 3, 6>
Shell3D::strain_displacement_matrix() const
{
    /*
     * Express the three nodes in the shell's
     * local XY coordinate system.
     */
const auto coordinates =
    local_coordinates();

const double x1 =
    coordinates(0, 0);

const double y1 =
    coordinates(0, 1);

const double x2 =
    coordinates(1, 0);

const double y2 =
    coordinates(1, 1);

const double x3 =
    coordinates(2, 0);

const double y3 =
    coordinates(2, 1);






      const double twoA =
        (x2 - x1) * (y3 - y1)
        - (x3 - x1) * (y2 - y1);

    if (std::abs(twoA) <= 1e-12) {
        throw std::runtime_error(
            "Degenerate Shell3D element."
        );
    }

    const double b1 =
        y2 - y3;

    const double b2 =
        y3 - y1;

    const double b3 =
        y1 - y2;

    const double c1 =
        x3 - x2;

    const double c2 =
        x1 - x3;

    const double c3 =
        x2 - x1;

    Eigen::Matrix<double, 3, 6> B;

    B <<
        b1, 0.0, b2, 0.0, b3, 0.0,
        0.0, c1, 0.0, c2, 0.0, c3,
        c1, b1, c2, b2, c3, b3;

    B /= twoA;

    return B;
}

Eigen::Matrix3d
Shell3D::constitutive_matrix() const
{
    const double E =
        property_->material()
            .youngs_modulus();

    const double nu =
        property_->material()
            .poisson_ratio();

    const double factor =
        E / (1.0 - nu * nu);

    Eigen::Matrix3d D;

    D <<
        1.0, nu, 0.0,
        nu, 1.0, 0.0,
        0.0, 0.0, (1.0 - nu) / 2.0;

    return factor * D;
}

Eigen::Matrix<double, 6, 6>
Shell3D::local_membrane_stiffness_matrix() const
{
    const auto B =
        strain_displacement_matrix();

    const auto D =
        constitutive_matrix();

    return property_->thickness()
        * area()
        * B.transpose()
        * D
        * B;
}




Eigen::Matrix<double, 9, 9>
Shell3D::transformation_matrix() const
{
    /*
     * Each shell node currently contributes only
     * three translational membrane DOFs here.
     */

    const Eigen::Matrix3d R =
        rotation_matrix();

    Eigen::Matrix<double, 9, 9> T =
        Eigen::Matrix<double, 9, 9>::Zero();

    T.block<3, 3>(0, 0) = R;
    T.block<3, 3>(3, 3) = R;
    T.block<3, 3>(6, 6) = R;

    return T;
}

Eigen::Matrix<double, 18, 18>
Shell3D::full_transformation_matrix() const
{
    /*
     * Full shell DOF ordering:
     *
     * [u v w rx ry rz] per node.
     *
     * Both translational and rotational vectors
     * transform from global to local coordinates
     * using the same shell rotation matrix R.
     */

    const Eigen::Matrix3d R =
        rotation_matrix();

    Eigen::Matrix<double, 18, 18> T =
        Eigen::Matrix<double, 18, 18>::Zero();

    for (int node = 0; node < 3; ++node) {
        const int offset =
            node * 6;

        // Translation
        T.block<3, 3>(
            offset,
            offset
        ) = R;

        // Rotation
        T.block<3, 3>(
            offset + 3,
            offset + 3
        ) = R;
    }

    return T;
}








Eigen::Matrix<double, 9, 9>
Shell3D::membrane_stiffness_matrix() const
{
    /*
     * Local membrane matrix has:
     *
     * [u1 v1 u2 v2 u3 v3]
     *
     * but the 3D translational representation has:
     *
     * [ux1 uy1 uz1 ux2 uy2 uz2 ux3 uy3 uz3]
     *
     * Embed the 6x6 membrane stiffness into a
     * 9x9 local translational matrix.
     */

    const auto Km =
        local_membrane_stiffness_matrix();

    Eigen::Matrix<double, 9, 9> Klocal =
        Eigen::Matrix<double, 9, 9>::Zero();

    const int map[6] = {
        0, 1,
        3, 4,
        6, 7
    };

    for (int r = 0; r < 6; ++r) {
        for (int c = 0; c < 6; ++c) {
            Klocal(
                map[r],
                map[c]
            ) = Km(r, c);
        }
    }

    const auto T =
        transformation_matrix();

    return T.transpose()
        * Klocal
        * T;
}


Eigen::Matrix<double, 6, 1>
Shell3D::local_membrane_displacements(
    const Eigen::VectorXd& displacements
) const
{
    const std::size_t a =
        node_a_->id();

    const std::size_t b =
        node_b_->id();

    const std::size_t c =
        node_c_->id();

    const Eigen::Matrix3d R =
        rotation_matrix();

    const Eigen::Vector3d ua_global(
        displacements(
            static_cast<Eigen::Index>(
                dof_index(a, Dof::UX)
            )
        ),
        displacements(
            static_cast<Eigen::Index>(
                dof_index(a, Dof::UY)
            )
        ),
        displacements(
            static_cast<Eigen::Index>(
                dof_index(a, Dof::UZ)
            )
        )
    );

    const Eigen::Vector3d ub_global(
        displacements(
            static_cast<Eigen::Index>(
                dof_index(b, Dof::UX)
            )
        ),
        displacements(
            static_cast<Eigen::Index>(
                dof_index(b, Dof::UY)
            )
        ),
        displacements(
            static_cast<Eigen::Index>(
                dof_index(b, Dof::UZ)
            )
        )
    );

    const Eigen::Vector3d uc_global(
        displacements(
            static_cast<Eigen::Index>(
                dof_index(c, Dof::UX)
            )
        ),
        displacements(
            static_cast<Eigen::Index>(
                dof_index(c, Dof::UY)
            )
        ),
        displacements(
            static_cast<Eigen::Index>(
                dof_index(c, Dof::UZ)
            )
        )
    );

    const Eigen::Vector3d ua_local =
        R * ua_global;

    const Eigen::Vector3d ub_local =
        R * ub_global;

    const Eigen::Vector3d uc_local =
        R * uc_global;

    Eigen::Matrix<double, 6, 1> u;

    u <<
        ua_local.x(),
        ua_local.y(),

        ub_local.x(),
        ub_local.y(),

        uc_local.x(),
        uc_local.y();

    return u;
}

Eigen::Matrix<double, 9, 1>
Shell3D::local_bending_displacements(
    const Eigen::VectorXd& displacements
) const
{
    const std::size_t node_ids[3] = {
        node_a_->id(),
        node_b_->id(),
        node_c_->id()
    };

    const Eigen::Matrix3d R =
        rotation_matrix();

    Eigen::Matrix<double, 9, 1> u =
        Eigen::Matrix<double, 9, 1>::Zero();

    for (int node = 0; node < 3; ++node) {
        const std::size_t id =
            node_ids[node];

        const Eigen::Vector3d translation_global(
            displacements(
                static_cast<Eigen::Index>(
                    dof_index(id, Dof::UX)
                )
            ),
            displacements(
                static_cast<Eigen::Index>(
                    dof_index(id, Dof::UY)
                )
            ),
            displacements(
                static_cast<Eigen::Index>(
                    dof_index(id, Dof::UZ)
                )
            )
        );

        const Eigen::Vector3d rotation_global(
            displacements(
                static_cast<Eigen::Index>(
                    dof_index(id, Dof::RX)
                )
            ),
            displacements(
                static_cast<Eigen::Index>(
                    dof_index(id, Dof::RY)
                )
            ),
            displacements(
                static_cast<Eigen::Index>(
                    dof_index(id, Dof::RZ)
                )
            )
        );

        const Eigen::Vector3d translation_local =
            R * translation_global;

        const Eigen::Vector3d rotation_local =
            R * rotation_global;

        const int offset =
            node * 3;

        u(offset + 0) =
            translation_local.z();

        u(offset + 1) =
            rotation_local.x();

        u(offset + 2) =
            rotation_local.y();
    }

    return u;
}


Eigen::Vector3d
Shell3D::membrane_strain(
    const Eigen::VectorXd& displacements
) const
{
    return strain_displacement_matrix()
        * local_membrane_displacements(
            displacements
        );
}

Eigen::Vector3d
Shell3D::membrane_stress(
    const Eigen::VectorXd& displacements
) const
{
    return constitutive_matrix()
        * membrane_strain(
            displacements
        );
}



Eigen::Matrix3d
Shell3D::bending_constitutive_matrix() const
{
    const double E =
        property_->material().youngs_modulus();

    const double nu =
        property_->material().poisson_ratio();

    const double t =
        property_->thickness();

    const double factor =
        E * t * t * t
        / (
            12.0
            * (1.0 - nu * nu)
        );

    Eigen::Matrix3d D;

    D <<
        1.0, nu,  0.0,
        nu,  1.0, 0.0,
        0.0, 0.0, (1.0 - nu) / 2.0;

    return factor * D;
}

Eigen::Matrix<double, 3, 5>
Shell3D::bending_edge_coefficients() const
{
    const auto geometry =
        bending_edge_geometry();

    Eigen::Matrix<double, 3, 5> coefficients;

    for (int edge = 0; edge < 3; ++edge) {
        const double x =
            geometry(edge, 0);

        const double y =
            geometry(edge, 1);

        const double l2 =
            geometry(edge, 2);

        if (l2 <= 1e-24) {
            throw std::runtime_error(
                "Degenerate Shell3D bending edge."
            );
        }

        const double p =
            -6.0 * x / l2;

        const double q =
            3.0 * x * y / l2;

        const double r =
            3.0 * y * y / l2;

        const double t =
            -6.0 * y / l2;

        const double s =
            3.0 * x * x / l2;

        coefficients.row(edge) <<
            p, q, r, t, s;
    }

    return coefficients;
}

Eigen::Matrix<double, 3, 5>
Shell3D::dkt_rotation_coefficients() const
{
    const auto geometry =
        bending_edge_geometry();

    Eigen::Matrix<double, 3, 5> coefficients;

    for (int edge = 0; edge < 3; ++edge) {
        const double x =
            geometry(edge, 0);

        const double y =
            geometry(edge, 1);

        const double l2 =
            geometry(edge, 2);

        if (l2 <= 1e-24) {
            throw std::runtime_error(
                "Degenerate Shell3D DKT edge."
            );
        }

        const double a =
            -x / l2;

        const double b =
            3.0 * x * y
            / (4.0 * l2);

        const double c =
            (
                x * x
                - 2.0 * y * y
            )
            / (4.0 * l2);

        const double d =
            -y / l2;

        const double e =
            (
                y * y
                - 2.0 * x * x
            )
            / (4.0 * l2);

        coefficients.row(edge) <<
            a, b, c, d, e;
    }

    return coefficients;
}








Eigen::Matrix<double, 6, 1>
Shell3D::bending_shape_functions(
    double L1,
    double L2,
    double L3
) const
{
    Eigen::Matrix<double, 6, 1> N;

    N(0) =
        L1 * (2.0 * L1 - 1.0);

    N(1) =
        L2 * (2.0 * L2 - 1.0);
  /*
   * DKT midside convention:
   *
   * N4 -> edge 23
   * N5 -> edge 31
   * N6 -> edge 12
   */

  N(3) =
      4.0 * L2 * L3;

  N(4) =
      4.0 * L3 * L1;

  N(5) =
      4.0 * L1 * L2;


      N(2) =
          L3 * (2.0 * L3 - 1.0);

      
    return N;
}

Eigen::Matrix<double, 6, 2>
Shell3D::bending_shape_function_derivatives(
    double xi,
    double eta
) const
{
    /*
     * Natural coordinates:
     *
     * L1 = 1 - xi - eta
     * L2 = xi
     * L3 = eta
     *
     * DKT midside convention:
     *
     * N4 -> edge 23
     * N5 -> edge 31
     * N6 -> edge 12
     */

    const double L1 =
        1.0 - xi - eta;

    const double L2 =
        xi;

    const double L3 =
        eta;

    Eigen::Matrix<double, 6, 2> dN;

    /*
     * N1 = L1 (2 L1 - 1)
     */
    dN(0, 0) =
        1.0 - 4.0 * L1;

    dN(0, 1) =
        1.0 - 4.0 * L1;

    /*
     * N2 = L2 (2 L2 - 1)
     */
    dN(1, 0) =
        4.0 * L2 - 1.0;

    dN(1, 1) =
        0.0;

    /*
     * N3 = L3 (2 L3 - 1)
     */
    dN(2, 0) =
        0.0;

    dN(2, 1) =
        4.0 * L3 - 1.0;

    /*
     * N4 = 4 L2 L3
     */
    dN(3, 0) =
        4.0 * L3;

    dN(3, 1) =
        4.0 * L2;

    /*
     * N5 = 4 L3 L1
     */
    dN(4, 0) =
        -4.0 * L3;

    dN(4, 1) =
        4.0 * (L1 - L3);

    /*
     * N6 = 4 L1 L2
     */
    dN(5, 0) =
        4.0 * (L1 - L2);

    dN(5, 1) =
        -4.0 * L2;

    return dN;
}






Eigen::Matrix<double, 2, 9>
Shell3D::dkt_rotation_interpolation(
    double L1,
    double L2,
    double L3
) const
{
    const auto N =
        bending_shape_functions(
            L1,
            L2,
            L3
        );

    const auto coefficients =
        dkt_rotation_coefficients();

    /*
     * Edge coefficient rows:
     *
     * row 0 -> k4 -> edge 23
     * row 1 -> k5 -> edge 31
     * row 2 -> k6 -> edge 12
     */

    const double a4 = coefficients(0, 0);
    const double b4 = coefficients(0, 1);
    const double c4 = coefficients(0, 2);
    const double d4 = coefficients(0, 3);
    const double e4 = coefficients(0, 4);

    const double a5 = coefficients(1, 0);
    const double b5 = coefficients(1, 1);
    const double c5 = coefficients(1, 2);
    const double d5 = coefficients(1, 3);
    const double e5 = coefficients(1, 4);

    const double a6 = coefficients(2, 0);
    const double b6 = coefficients(2, 1);
    const double c6 = coefficients(2, 2);
    const double d6 = coefficients(2, 3);
    const double e6 = coefficients(2, 4);

    /*
     * Quadratic triangle shape functions.
     */

    const double N1 = N(0);
    const double N2 = N(1);
    const double N3 = N(2);
    const double N4 = N(3);
    const double N5 = N(4);
    const double N6 = N(5);

    Eigen::Matrix<double, 1, 9> Hx;
    Eigen::Matrix<double, 1, 9> Hy;

    /*
     * Node 1.
     */

    Hx(0) =
        1.5 * (
            a6 * N6
            - a5 * N5
        );

    Hx(1) =
        b5 * N5
        + b6 * N6;

    Hx(2) =
        N1
        - c5 * N5
        - c6 * N6;

    Hy(0) =
        1.5 * (
            d6 * N6
            - d5 * N5
        );

    Hy(1) =
        -N1
        + e5 * N5
        + e6 * N6;

    Hy(2) =
        -Hx(1);

    /*
     * Node 2.
     */

    Hx(3) =
        1.5 * (
            a4 * N4
            - a6 * N6
        );

    Hx(4) =
        b6 * N6
        + b4 * N4;

    Hx(5) =
        N2
        - c6 * N6
        - c4 * N4;

    Hy(3) =
        1.5 * (
            d4 * N4
            - d6 * N6
        );

    Hy(4) =
        -N2
        + e6 * N6
        + e4 * N4;

    Hy(5) =
        -Hx(4);

    /*
     * Node 3.
     */
   Hx(6) =
    1.5 * (
        a5 * N5
        - a4 * N4
    );
    
    Hx(7) =
        b5 * N5
        + b4 * N4;

    Hx(8) =
        N3
        - c5 * N5
        - c4 * N4;
   
    Hy(6) =
    1.5 * (
        d5 * N5
        - d4 * N4
    );


    Hy(7) =
        -N3
        + e5 * N5
        + e4 * N4;

    Hy(8) =
        -Hx(7);

    Eigen::Matrix<double, 2, 9> H;

    H.row(0) = Hx;
    H.row(1) = Hy;

    return H;
}


Eigen::Matrix<double, 4, 9>
Shell3D::dkt_rotation_derivatives(
    double xi,
    double eta
) const
{
    const auto dN =
        bending_shape_function_derivatives(
            xi,
            eta
        );

    const auto coefficients =
        dkt_rotation_coefficients();

    /*
     * DKT coefficient rows:
     *
     * row 0 -> k4 -> edge 23
     * row 1 -> k5 -> edge 31
     * row 2 -> k6 -> edge 12
     */

    const double a4 = coefficients(0, 0);
    const double b4 = coefficients(0, 1);
    const double c4 = coefficients(0, 2);
    const double d4 = coefficients(0, 3);
    const double e4 = coefficients(0, 4);

    const double a5 = coefficients(1, 0);
    const double b5 = coefficients(1, 1);
    const double c5 = coefficients(1, 2);
    const double d5 = coefficients(1, 3);
    const double e5 = coefficients(1, 4);

    const double a6 = coefficients(2, 0);
    const double b6 = coefficients(2, 1);
    const double c6 = coefficients(2, 2);
    const double d6 = coefficients(2, 3);
    const double e6 = coefficients(2, 4);

    /*
     * Given derivatives of N1...N6,
     * construct derivatives of Hx and Hy.
     */

    auto build_derivative =
        [&](
            const Eigen::Matrix<double, 6, 1>& d
        )
        {
            const double dN1 = d(0);
            const double dN2 = d(1);
            const double dN3 = d(2);
            const double dN4 = d(3);
            const double dN5 = d(4);
            const double dN6 = d(5);

            Eigen::Matrix<double, 2, 9> result;

            Eigen::Matrix<double, 1, 9> Hx;
            Eigen::Matrix<double, 1, 9> Hy;

            /*
             * Node 1.
             */

            Hx(0) =
                1.5 * (
                    a6 * dN6
                    - a5 * dN5
                );

            Hx(1) =
                b5 * dN5
                + b6 * dN6;

            Hx(2) =
                dN1
                - c5 * dN5
                - c6 * dN6;

            Hy(0) =
                1.5 * (
                    d6 * dN6
                    - d5 * dN5
                );

            Hy(1) =
                -dN1
                + e5 * dN5
                + e6 * dN6;

            Hy(2) =
                -Hx(1);

            /*
             * Node 2.
             */

            Hx(3) =
                1.5 * (
                    a4 * dN4
                    - a6 * dN6
                );

            Hx(4) =
                b6 * dN6
                + b4 * dN4;

            Hx(5) =
                dN2
                - c6 * dN6
                - c4 * dN4;

            Hy(3) =
                1.5 * (
                    d4 * dN4
                    - d6 * dN6
                );

            Hy(4) =
                -dN2
                + e6 * dN6
                + e4 * dN4;

            Hy(5) =
                -Hx(4);

            /*
             * Node 3.
             */

            Hx(6) =
                1.5 * (
                    a5 * dN5
                    - a4 * dN4
                );

            Hx(7) =
                b5 * dN5
                + b4 * dN4;

            Hx(8) =
                dN3
                - c5 * dN5
                - c4 * dN4;

            Hy(6) =
                1.5 * (
                    d5 * dN5
                    - d4 * dN4
                );

            Hy(7) =
                -dN3
                + e5 * dN5
                + e4 * dN4;

            Hy(8) =
                -Hx(7);

            result.row(0) = Hx;
            result.row(1) = Hy;

            return result;
        };

    const Eigen::Matrix<double, 6, 1> dN_dxi =
        dN.col(0);

    const Eigen::Matrix<double, 6, 1> dN_deta =
        dN.col(1);

    const auto derivative_xi =
        build_derivative(dN_dxi);

    const auto derivative_eta =
        build_derivative(dN_deta);

    Eigen::Matrix<double, 4, 9> derivatives;

    derivatives.row(0) =
        derivative_xi.row(0);

    derivatives.row(1) =
        derivative_eta.row(0);

    derivatives.row(2) =
        derivative_xi.row(1);

    derivatives.row(3) =
        derivative_eta.row(1);

    return derivatives;
}



Eigen::Matrix<double, 3, 9>
Shell3D::dkt_bending_strain_displacement_matrix(
    double xi,
    double eta
) const
{
    const auto derivatives =
        dkt_rotation_derivatives(
            xi,
            eta
        );

    /*
     * rows:
     *
     * 0 -> Hx,xi
     * 1 -> Hx,eta
     * 2 -> Hy,xi
     * 3 -> Hy,eta
     */

    const auto Hx_xi =
        derivatives.row(0);

    const auto Hx_eta =
        derivatives.row(1);

    const auto Hy_xi =
        derivatives.row(2);

    const auto Hy_eta =
        derivatives.row(3);

    const auto coordinates =
        local_coordinates();

    const double x1 = coordinates(0, 0);
    const double y1 = coordinates(0, 1);

    const double x2 = coordinates(1, 0);
    const double y2 = coordinates(1, 1);

    const double x3 = coordinates(2, 0);
    const double y3 = coordinates(2, 1);

    const double x31 =
        x3 - x1;

    const double y31 =
        y3 - y1;

    const double x12 =
        x1 - x2;

    const double y12 =
        y1 - y2;

    const double twoA =
        (x2 - x1) * (y3 - y1)
        - (x3 - x1) * (y2 - y1);

    if (std::abs(twoA) <= 1e-12) {
        throw std::runtime_error(
            "Degenerate Shell3D DKT element."
        );
    }

    Eigen::Matrix<double, 3, 9> B;

    /*
     * DKT curvature-displacement matrix.
     */

    B.row(0) =
        (
            y31 * Hx_xi
            + y12 * Hx_eta
        )
        / twoA;

    B.row(1) =
        -(
            x31 * Hy_xi
            + x12 * Hy_eta
        )
        / twoA;

    B.row(2) =
        (
            -x31 * Hx_xi
            -x12 * Hx_eta
            +y31 * Hy_xi
            +y12 * Hy_eta
        )
        / twoA;

    return B;
}


Eigen::Matrix<double, 9, 9>
Shell3D::local_bending_stiffness_matrix() const
{
    const Eigen::Matrix3d D =
        bending_constitutive_matrix();

    Eigen::Matrix<double, 9, 9> K =
        Eigen::Matrix<double, 9, 9>::Zero();

    /*
     * Three-point Gaussian quadrature
     * for a triangle.
     */

    const double points[3][2] = {
        {
            1.0 / 6.0,
            1.0 / 6.0
        },
        {
            2.0 / 3.0,
            1.0 / 6.0
        },
        {
            1.0 / 6.0,
            2.0 / 3.0
        }
    };

    for (const auto& point : points) {
        const double xi =
            point[0];

        const double eta =
            point[1];

        const auto B =
            dkt_bending_strain_displacement_matrix(
                xi,
                eta
            );

        K +=
            B.transpose()
            * D
            * B;
    }

    K *= area() / 3.0;

    return K;
}


Eigen::Matrix<double, 18, 18>
Shell3D::local_stiffness_matrix() const
{
    Eigen::Matrix<double, 18, 18> K =
        Eigen::Matrix<double, 18, 18>::Zero();

    const auto Km =
        local_membrane_stiffness_matrix();

    const auto Kb =
        local_bending_stiffness_matrix();

    /*
     * Full local shell DOF ordering:
     *
     * node 1: u v w rx ry rz
     * node 2: u v w rx ry rz
     * node 3: u v w rx ry rz
     *
     * Membrane ordering:
     *
     * [u1 v1 u2 v2 u3 v3]
     *
     * Bending ordering:
     *
     * [w1 rx1 ry1
     *  w2 rx2 ry2
     *  w3 rx3 ry3]
     */

    const int membrane_map[6] = {
        0, 1,
        6, 7,
        12, 13
    };

    const int bending_map[9] = {
        2, 3, 4,
        8, 9, 10,
        14, 15, 16
    };

    for (int i = 0; i < 6; ++i) {
        for (int j = 0; j < 6; ++j) {
            K(
                membrane_map[i],
                membrane_map[j]
            ) += Km(i, j);
        }
    }
    for (int i = 0; i < 9; ++i) {
    for (int j = 0; j < 9; ++j) {
        K(
            bending_map[i],
            bending_map[j]
        ) += Kb(i, j);
    }
}

    /*
     * Artificial drilling stabilization.
     *
     * The CST + DKT shell has no physical stiffness
     * associated with the local rz rotation.
     *
     * A small membrane-scaled diagonal penalty removes
     * the zero-energy drilling modes while keeping their
     * contribution negligible relative to the physical
     * membrane response.
     */

    const double kd =
        drilling_stiffness();

    const int drilling_map[3] = {
        5,
        11,
        17
    };

    for (const int dof : drilling_map) {
        K(dof, dof) += kd;
    }

    return K;
       }


double
Shell3D::drilling_stiffness() const
{
    const auto Km =
        local_membrane_stiffness_matrix();

    double max_diagonal = 0.0;

    for (int i = 0; i < 6; ++i) {
        max_diagonal =
            std::max(
                max_diagonal,
                std::abs(Km(i, i))
            );
    }

    constexpr double alpha =
        1.0e-6;

    return alpha * max_diagonal;
}










Eigen::Matrix<double, 18, 18>
Shell3D::stiffness_matrix() const
{
    const auto Klocal =
        local_stiffness_matrix();

    const auto T =
        full_transformation_matrix();

    return
        T.transpose()
        * Klocal
        * T;
}



Eigen::Matrix<double, 18, 1>
Shell3D::pressure_load_vector(
    double pressure
) const
{
    Eigen::Matrix<double, 18, 1> f =
        Eigen::Matrix<double, 18, 1>::Zero();

    /*
     * Positive pressure acts along the shell's
     * positive local z direction.
     *
     * For a constant pressure over a linear
     * three-node triangle:
     *
     *     total force = pressure * area
     *
     * and each node receives one third.
     */

    const Eigen::Vector3d nodal_force =
        pressure
        * area()
        / 3.0
        * local_z();

    /*
     * Full shell ordering:
     *
     * node 1: UX UY UZ RX RY RZ
     * node 2: UX UY UZ RX RY RZ
     * node 3: UX UY UZ RX RY RZ
     *
     * Pressure contributes translational
     * nodal forces only.
     */

    for (int node = 0; node < 3; ++node) {
        const int offset = node * 6;

        f(offset + 0) = nodal_force.x();
        f(offset + 1) = nodal_force.y();
        f(offset + 2) = nodal_force.z();
    }

    return f;
}

Eigen::Vector3d
Shell3D::bending_curvature(
    double xi,
    double eta,
    const Eigen::VectorXd& displacements
) const
{
    const auto B =
        dkt_bending_strain_displacement_matrix(
            xi,
            eta
        );

    const auto u =
        local_bending_displacements(
            displacements
        );

    return B * u;
}


Eigen::Vector3d
Shell3D::bending_moments(
    double xi,
    double eta,
    const Eigen::VectorXd& displacements
) const
{
    return bending_constitutive_matrix()
        * bending_curvature(
            xi,
            eta,
            displacements
        );
}


Eigen::Vector3d
Shell3D::bending_stress(
    double xi,
    double eta,
    double z,
    const Eigen::VectorXd& displacements
) const
{
    const double t =
        property_->thickness();

    const Eigen::Vector3d moments =
        bending_moments(
            xi,
            eta,
            displacements
        );

    return (
        12.0
        * z
        / (t * t * t)
    ) * moments;
}

} // namespace carambola
