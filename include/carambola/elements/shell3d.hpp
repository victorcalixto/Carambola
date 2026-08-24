#pragma once

#include <Eigen/Dense>

#include <carambola/node.hpp>
#include <carambola/shell_property.hpp>

namespace carambola {

class Shell3D {
public:
    Shell3D(
        const Node& node_a,
        const Node& node_b,
        const Node& node_c,
        const ShellProperty& property
    );

    const Node& node_a() const;
    const Node& node_b() const;
    const Node& node_c() const;

    const ShellProperty& property() const;

    double area() const;

    Eigen::Vector3d local_x() const;
    Eigen::Vector3d local_y() const;
    Eigen::Vector3d local_z() const;

    Eigen::Matrix3d rotation_matrix() const;

    Eigen::Matrix<double, 3, 6>
    strain_displacement_matrix() const;

    Eigen::Matrix3d
    constitutive_matrix() const;

    Eigen::Matrix<double, 6, 6>
    local_membrane_stiffness_matrix() const;

    Eigen::Matrix<double, 9, 9>
    transformation_matrix() const;

    Eigen::Matrix<double, 9, 9>
    membrane_stiffness_matrix() const;

private:
    const Node* node_a_;
    const Node* node_b_;
    const Node* node_c_;

    const ShellProperty* property_;
};

} // namespace carambola
