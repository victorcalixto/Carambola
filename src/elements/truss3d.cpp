#include <carambola/elements/truss3d.hpp>

#include <cmath>
#include <stdexcept>
#include <carambola/dof.hpp>


namespace carambola {

Truss3D::Truss3D(
    const Node& node_start,
    const Node& node_end,
    const Material& material,
    const Section& section
)
    : node_start_(&node_start),
      node_end_(&node_end),
      material_(&material),
      section_(&section)
{
    if (length() <= 1e-12) {
        throw std::invalid_argument(
            "Truss3D cannot have zero length."
        );
    }
}

const Node& Truss3D::node_start() const
{
    return *node_start_;
}

const Node& Truss3D::node_end() const
{
    return *node_end_;
}

const Material& Truss3D::material() const
{
    return *material_;
}

const Section& Truss3D::section() const
{
    return *section_;
}

double Truss3D::length() const
{
    const double dx = node_end_->x() - node_start_->x();
    const double dy = node_end_->y() - node_start_->y();
    const double dz = node_end_->z() - node_start_->z();

    return std::sqrt(
        dx * dx +
        dy * dy +
        dz * dz
    );
}

Eigen::Vector3d Truss3D::direction() const
{
    const double L = length();

    return Eigen::Vector3d(
        (node_end_->x() - node_start_->x()) / L,
        (node_end_->y() - node_start_->y()) / L,
        (node_end_->z() - node_start_->z()) / L
    );
}

Eigen::Matrix<double, 6, 6> Truss3D::stiffness_matrix() const
{
    const double L = length();
    const double E = material_->youngs_modulus();
    const double A = section_->area();

    const Eigen::Vector3d d = direction();

    const double l = d.x();
    const double m = d.y();
    const double n = d.z();

    const double k = E * A / L;

    Eigen::Matrix<double, 6, 6> K;

    K <<
         l*l,  l*m,  l*n, -l*l, -l*m, -l*n,
         l*m,  m*m,  m*n, -l*m, -m*m, -m*n,
         l*n,  m*n,  n*n, -l*n, -m*n, -n*n,
        -l*l, -l*m, -l*n,  l*l,  l*m,  l*n,
        -l*m, -m*m, -m*n,  l*m,  m*m,  m*n,
        -l*n, -m*n, -n*n,  l*n,  m*n,  n*n;

    return k * K;
}

double Truss3D::axial_deformation(
    const Eigen::VectorXd& displacements
) const
{
    const std::size_t i = node_start_->id();
    const std::size_t j = node_end_->id();

    const Eigen::Vector3d u_start(
        displacements(
            static_cast<Eigen::Index>(
                translational_dof(i, 0)
            )
        ),
        displacements(
            static_cast<Eigen::Index>(
                translational_dof(i, 1)
            )
        ),
        displacements(
            static_cast<Eigen::Index>(
                translational_dof(i, 2)
            )
        )
    );

    const Eigen::Vector3d u_end(
        displacements(
            static_cast<Eigen::Index>(
                translational_dof(j, 0)
            )
        ),
        displacements(
            static_cast<Eigen::Index>(
                translational_dof(j, 1)
            )
        ),
        displacements(
            static_cast<Eigen::Index>(
                translational_dof(j, 2)
            )
        )
    );

    return (u_end - u_start).dot(
        direction()
    );
}

double Truss3D::axial_strain(
    const Eigen::VectorXd& displacements
) const
{
    return axial_deformation(displacements)
        / length();
}

double Truss3D::axial_stress(
    const Eigen::VectorXd& displacements
) const
{
    return material_->youngs_modulus()
        * axial_strain(displacements);
}

double Truss3D::axial_force(
    const Eigen::VectorXd& displacements
) const
{
    return section_->area()
        * axial_stress(displacements);
}



}
