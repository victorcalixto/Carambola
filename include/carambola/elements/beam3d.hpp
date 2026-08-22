#pragma once

#include <Eigen/Dense>

#include <carambola/material.hpp>
#include <carambola/node.hpp>
#include <carambola/section.hpp>

namespace carambola {

class Beam3D {
public:
    Beam3D(
        const Node& node_start,
        const Node& node_end,
        const Material& material,
        const Section& section,
        Eigen::Vector3d orientation =
            Eigen::Vector3d(0.0, 0.0, 1.0)
    );

    const Node& node_start() const;
    const Node& node_end() const;

    const Material& material() const;
    const Section& section() const;

    double length() const;

    Eigen::Vector3d local_x() const;
    Eigen::Vector3d local_y() const;
    Eigen::Vector3d local_z() const;

    Eigen::Matrix3d rotation_matrix() const;

    Eigen::Matrix<double, 12, 12>
    local_stiffness_matrix() const;

    Eigen::Matrix<double, 12, 12>
    transformation_matrix() const;

    Eigen::Matrix<double, 12, 12>
    stiffness_matrix() const;

    Eigen::Matrix<double, 12, 1> element_displacements(
    const Eigen::VectorXd& displacements
    ) const;

    Eigen::Matrix<double, 12, 1> local_displacements(
        const Eigen::VectorXd& displacements
    ) const;

    Eigen::Matrix<double, 12, 1> local_end_forces(
        const Eigen::VectorXd& displacements
    ) const;

private:
    const Node* node_start_;
    const Node* node_end_;
    const Material* material_;
    const Section* section_;

    Eigen::Vector3d orientation_;
};

} // namespace carambola
