#pragma once

#include <Eigen/Dense>

#include <carambola/elements/truss3d.hpp>
#include <carambola/model.hpp>
#include <carambola/node.hpp>
#include <carambola/elements/beam3d.hpp>

namespace carambola {

class AnalysisResult {
public:
    AnalysisResult(
        const Model& model,
        Eigen::VectorXd displacements,
        Eigen::VectorXd reactions
    );

    const Eigen::VectorXd& displacements() const;
    const Eigen::VectorXd& reactions() const;

    Eigen::Vector3d node_displacement(
        const Node& node
    ) const;

    Eigen::Vector3d node_reaction(
        const Node& node
    ) const;

    double truss_deformation(
        const Truss3D& truss
    ) const;

    double truss_strain(
        const Truss3D& truss
    ) const;

    double truss_stress(
        const Truss3D& truss
    ) const;

    double truss_force(
        const Truss3D& truss
    ) const;

    Eigen::Vector3d node_rotation(
        const Node& node
    ) const;

    Eigen::Vector3d node_moment_reaction(
        const Node& node
    ) const;

    Eigen::Matrix<double, 12, 1>
      beam_local_end_forces(
          const Beam3D& beam
      ) const;

      double beam_axial_force(
          const Beam3D& beam
      ) const;

      double beam_torsion(
          const Beam3D& beam
      ) const;

      double beam_shear_y(
          const Beam3D& beam
      ) const;

      double beam_shear_z(
          const Beam3D& beam
      ) const;

      double beam_moment_y(
          const Beam3D& beam
      ) const;

      double beam_moment_z(
          const Beam3D& beam
      ) const;


private:
    const Model* model_;
    Eigen::VectorXd displacements_;
    Eigen::VectorXd reactions_;
};

class LinearStaticSolver {
public:
    explicit LinearStaticSolver(const Model& model);

    AnalysisResult solve() const;

private:
    const Model* model_;
};

} // namespace carambola
