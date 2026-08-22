#pragma once

#include <Eigen/Sparse>

#include <carambola/model.hpp>

namespace carambola {

class Assembler {
public:
    explicit Assembler(const Model& model);

    Eigen::SparseMatrix<double> stiffness_matrix() const;

private:
    const Model* model_;
};

}
