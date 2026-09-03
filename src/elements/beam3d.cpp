#include <carambola/elements/beam3d.hpp>

#include <cmath>
#include <stdexcept>
#include <utility>
#include <carambola/dof.hpp>

namespace carambola {

Beam3D::Beam3D(
    const Node& node_start,
    const Node& node_end,
    const Material& material,
    const Section& section,
    Eigen::Vector3d orientation
)
    : node_start_(&node_start),
      node_end_(&node_end),
      material_(&material),
      section_(&section),
      orientation_(std::move(orientation))
{
    if (length() <= 1e-12) {
        throw std::invalid_argument(
            "Beam3D cannot have zero length."
        );
    }

    if (orientation_.norm() <= 1e-12) {
        throw std::invalid_argument(
            "Beam3D orientation vector cannot be zero."
        );
    }

    const double alignment =
        std::abs(
            local_x().dot(
                orientation_.normalized()
            )
        );

    if (alignment > 1.0 - 1e-10) {
        throw std::invalid_argument(
            "Beam3D orientation vector cannot be "
            "parallel to the beam axis."
        );
    }
}


const Eigen::Vector3d& Beam3D::orientation() const {
    return orientation_;
}


const Node& Beam3D::node_start() const
{
    return *node_start_;
}

const Node& Beam3D::node_end() const
{
    return *node_end_;
}

const Material& Beam3D::material() const
{
    return *material_;
}

const Section& Beam3D::section() const
{
    return *section_;
}

double Beam3D::length() const
{
    const double dx =
        node_end_->x() - node_start_->x();

    const double dy =
        node_end_->y() - node_start_->y();

    const double dz =
        node_end_->z() - node_start_->z();

    return std::sqrt(
        dx * dx +
        dy * dy +
        dz * dz
    );
}

Eigen::Vector3d Beam3D::local_x() const
{
    Eigen::Vector3d x(
        node_end_->x() - node_start_->x(),
        node_end_->y() - node_start_->y(),
        node_end_->z() - node_start_->z()
    );

    return x.normalized();
}

Eigen::Vector3d Beam3D::local_z() const
{
    const Eigen::Vector3d x =
        local_x();

    Eigen::Vector3d z =
        x.cross(
            orientation_.normalized()
        );

    return z.normalized();
}

Eigen::Vector3d Beam3D::local_y() const
{
    const Eigen::Vector3d z =
        local_z();

    const Eigen::Vector3d x =
        local_x();

    return z.cross(x).normalized();
}

Eigen::Matrix3d Beam3D::rotation_matrix() const
{
    Eigen::Matrix3d R;

    R.row(0) = local_x().transpose();
    R.row(1) = local_y().transpose();
    R.row(2) = local_z().transpose();

    return R;
}

Eigen::Matrix<double, 12, 12>
Beam3D::local_stiffness_matrix() const
{
    const double L = length();

    const double E =
        material_->youngs_modulus();

    const double G =
        material_->shear_modulus();

    const double A =
        section_->area();

    const double Iy =
        section_->iy();

    const double Iz =
        section_->iz();

    const double J =
        section_->torsional_constant();

    const double EA_L =
        E * A / L;

    const double GJ_L =
        G * J / L;

    const double EIy =
        E * Iy;

    const double EIz =
        E * Iz;

    const double L2 =
        L * L;

    const double L3 =
        L2 * L;

    Eigen::Matrix<double, 12, 12> K =
        Eigen::Matrix<double, 12, 12>::Zero();

    /*
     * DOF order per node:
     *
     * UX UY UZ RX RY RZ
     *
     * Element:
     *
     * 0  1  2  3  4  5
     * 6  7  8  9 10 11
     */

    // Axial
    K(0, 0) = EA_L;
    K(0, 6) = -EA_L;
    K(6, 0) = -EA_L;
    K(6, 6) = EA_L;

    // Torsion
    K(3, 3) = GJ_L;
    K(3, 9) = -GJ_L;
    K(9, 3) = -GJ_L;
    K(9, 9) = GJ_L;

    /*
     * Bending about local Z:
     * transverse displacement UY
     * rotation RZ
     */
    const double kz1 =
        12.0 * EIz / L3;

    const double kz2 =
        6.0 * EIz / L2;

    const double kz3 =
        4.0 * EIz / L;

    const double kz4 =
        2.0 * EIz / L;

    K(1, 1) = kz1;
    K(1, 5) = kz2;
    K(1, 7) = -kz1;
    K(1, 11) = kz2;

    K(5, 1) = kz2;
    K(5, 5) = kz3;
    K(5, 7) = -kz2;
    K(5, 11) = kz4;

    K(7, 1) = -kz1;
    K(7, 5) = -kz2;
    K(7, 7) = kz1;
    K(7, 11) = -kz2;

    K(11, 1) = kz2;
    K(11, 5) = kz4;
    K(11, 7) = -kz2;
    K(11, 11) = kz3;

    /*
     * Bending about local Y:
     * transverse displacement UZ
     * rotation RY
     */
    const double ky1 =
        12.0 * EIy / L3;

    const double ky2 =
        6.0 * EIy / L2;

    const double ky3 =
        4.0 * EIy / L;

    const double ky4 =
        2.0 * EIy / L;

    K(2, 2) = ky1;
    K(2, 4) = -ky2;
    K(2, 8) = -ky1;
    K(2, 10) = -ky2;

    K(4, 2) = -ky2;
    K(4, 4) = ky3;
    K(4, 8) = ky2;
    K(4, 10) = ky4;

    K(8, 2) = -ky1;
    K(8, 4) = ky2;
    K(8, 8) = ky1;
    K(8, 10) = ky2;

    K(10, 2) = -ky2;
    K(10, 4) = ky4;
    K(10, 8) = ky2;
    K(10, 10) = ky3;

    return K;
}

Eigen::Matrix<double, 12, 12>
Beam3D::transformation_matrix() const
{
    const Eigen::Matrix3d R =
        rotation_matrix();

    Eigen::Matrix<double, 12, 12> T =
        Eigen::Matrix<double, 12, 12>::Zero();

    T.block<3, 3>(0, 0) = R;
    T.block<3, 3>(3, 3) = R;
    T.block<3, 3>(6, 6) = R;
    T.block<3, 3>(9, 9) = R;

    return T;
}

Eigen::Matrix<double, 12, 12>
Beam3D::stiffness_matrix() const
{
    const auto T =
        transformation_matrix();

    const auto K_local =
        local_stiffness_matrix();

    return T.transpose()
        * K_local
        * T;
}


Eigen::Matrix<double, 12, 1>
Beam3D::element_displacements(
    const Eigen::VectorXd& displacements
) const
{
    const std::size_t i =
        node_start_->id();

    const std::size_t j =
        node_end_->id();

    Eigen::Matrix<double, 12, 1> u;

    u <<
        displacements(
            static_cast<Eigen::Index>(
                dof_index(i, Dof::UX)
            )
        ),
        displacements(
            static_cast<Eigen::Index>(
                dof_index(i, Dof::UY)
            )
        ),
        displacements(
            static_cast<Eigen::Index>(
                dof_index(i, Dof::UZ)
            )
        ),
        displacements(
            static_cast<Eigen::Index>(
                dof_index(i, Dof::RX)
            )
        ),
        displacements(
            static_cast<Eigen::Index>(
                dof_index(i, Dof::RY)
            )
        ),
        displacements(
            static_cast<Eigen::Index>(
                dof_index(i, Dof::RZ)
            )
        ),

        displacements(
            static_cast<Eigen::Index>(
                dof_index(j, Dof::UX)
            )
        ),
        displacements(
            static_cast<Eigen::Index>(
                dof_index(j, Dof::UY)
            )
        ),
        displacements(
            static_cast<Eigen::Index>(
                dof_index(j, Dof::UZ)
            )
        ),
        displacements(
            static_cast<Eigen::Index>(
                dof_index(j, Dof::RX)
            )
        ),
        displacements(
            static_cast<Eigen::Index>(
                dof_index(j, Dof::RY)
            )
        ),
        displacements(
            static_cast<Eigen::Index>(
                dof_index(j, Dof::RZ)
            )
        );

    return u;
}

Eigen::Matrix<double, 12, 1>
Beam3D::local_displacements(
    const Eigen::VectorXd& displacements
) const
{
    return transformation_matrix()
        * element_displacements(
            displacements
        );
}

Eigen::Matrix<double, 12, 1>
Beam3D::local_end_forces(
    const Eigen::VectorXd& displacements
) const
{
    return local_stiffness_matrix()
        * local_displacements(
            displacements
        );
}


} // namespace carambola
