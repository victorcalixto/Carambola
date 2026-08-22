#pragma once

#include <Eigen/Dense>

#include <carambola/model.hpp>

namespace carambola {

class AnalysisResult {
public:
    AnalysisResult(
        Eigen::VectorXd displacements,
        Eigen::VectorXd reactions
    );

    const Eigen::VectorXd& displacements() const;
    const Eigen::VectorXd& reactions() const;

private:
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
