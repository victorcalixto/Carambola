#include <carambola/elements/shell3d.hpp>

#include <cmath>
#include <stdexcept>

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

Eigen::Matrix<double, 3, 6>
Shell3D::strain_displacement_matrix() const
{
    /*
     * Express the three nodes in the shell's
     * local XY coordinate system.
     */

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

    const double x1 = 0.0;
    const double y1 = 0.0;

    const double x2 =
        (b_global - origin).dot(x);

    const double y2 =
        (b_global - origin).dot(y);

    const double x3 =
        (c_global - origin).dot(x);

    const double y3 =
        (c_global - origin).dot(y);

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

} // namespace carambola
