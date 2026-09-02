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

    Eigen::Matrix<double, 3, 2>
    local_coordinates() const;

    Eigen::Matrix<double, 3, 3>
bending_edge_geometry() const;

Eigen::Matrix<double, 3, 5>
bending_edge_coefficients() const;

Eigen::Vector3d bending_curvature(
    double xi,
    double eta,
    const Eigen::VectorXd& displacements
) const;


Eigen::Vector3d bending_moments(
    double xi,
    double eta,
    const Eigen::VectorXd& displacements
) const;


Eigen::Vector3d bending_stress(
    double xi,
    double eta,
    double z,
    const Eigen::VectorXd& displacements
) const;


Eigen::Matrix<double, 3, 5>
dkt_rotation_coefficients() const;




Eigen::Matrix<double, 6, 1>
bending_shape_functions(
    double L1,
    double L2,
    double L3
) const;

Eigen::Matrix<double, 2, 9>
dkt_rotation_interpolation(
    double L1,
    double L2,
    double L3
) const;




Eigen::Matrix<double, 6, 2>
bending_shape_function_derivatives(
    double xi,
    double eta
) const;

Eigen::Matrix<double, 4, 9>
dkt_rotation_derivatives(
    double xi,
    double eta
) const;

Eigen::Matrix<double, 3, 9>
dkt_bending_strain_displacement_matrix(
    double xi,
    double eta
) const;


Eigen::Matrix<double, 9, 9>
local_bending_stiffness_matrix() const;



double drilling_stiffness() const;


Eigen::Matrix<double, 18, 18>
local_stiffness_matrix() const;

Eigen::Matrix<double, 18, 18>
stiffness_matrix() const;

Eigen::Matrix<double, 18, 1>
pressure_load_vector(double pressure) const;


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

    Eigen::Matrix<double, 6, 1>
    local_membrane_displacements(
        const Eigen::VectorXd& displacements
    ) const;

    Eigen::Vector3d membrane_strain(
        const Eigen::VectorXd& displacements
    ) const;

    Eigen::Vector3d membrane_stress(
        const Eigen::VectorXd& displacements
    ) const;
Eigen::Matrix<double, 18, 18>
full_transformation_matrix() const;

Eigen::Matrix<double, 9, 1>
local_bending_displacements(
    const Eigen::VectorXd& displacements
) const;

Eigen::Matrix3d
bending_constitutive_matrix() const;




private:
    const Node* node_a_;
    const Node* node_b_;
    const Node* node_c_;

    const ShellProperty* property_;
};

} // namespace carambola
