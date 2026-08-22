#pragma once

#include <Eigen/Dense>

#include <carambola/material.hpp>
#include <carambola/node.hpp>
#include <carambola/section.hpp>

namespace carambola {

class Truss3D {
public:
    Truss3D(
        const Node& node_start,
        const Node& node_end,
        const Material& material,
        const Section& section
    );

    const Node& node_start() const;
    const Node& node_end() const;

    const Material& material() const;
    const Section& section() const;

    double length() const;

    Eigen::Vector3d direction() const;

    Eigen::Matrix<double, 6, 6> stiffness_matrix() const;

    double axial_deformation(
        const Eigen::VectorXd& displacements
    ) const;

    double axial_strain(
        const Eigen::VectorXd& displacements
    ) const;

    double axial_stress(
        const Eigen::VectorXd& displacements
    ) const;

    double axial_force(
        const Eigen::VectorXd& displacements
    ) const;

private:
    const Node* node_start_;
    const Node* node_end_;
    const Material* material_;
    const Section* section_;
};

} // namespace carambola
