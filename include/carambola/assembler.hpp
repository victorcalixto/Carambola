#pragma once

#include <cstddef>
#include <vector>

#include <Eigen/Dense>
#include <Eigen/Sparse>

#include <carambola/model.hpp>

namespace carambola {

class Assembler {
public:
    explicit Assembler(const Model& model);

    Eigen::SparseMatrix<double> stiffness_matrix() const;

    Eigen::VectorXd force_vector() const;

    std::vector<std::size_t> constrained_dofs() const;

    std::vector<std::size_t> free_dofs() const;

private:
    const Model* model_;
};

}
