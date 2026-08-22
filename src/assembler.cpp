#include <carambola/assembler.hpp>
#include <carambola/dof.hpp>

#include <array>
#include <vector>

namespace carambola {

Assembler::Assembler(const Model& model)
    : model_(&model)
{
}

Eigen::SparseMatrix<double> Assembler::stiffness_matrix() const
{
    const std::size_t dof_count =
        model_->node_count() * 3;

    Eigen::SparseMatrix<double> K(
        static_cast<Eigen::Index>(dof_count),
        static_cast<Eigen::Index>(dof_count)
    );

    std::vector<Eigen::Triplet<double>> triplets;

    triplets.reserve(
        model_->truss_count() * 36
    );

    for (const auto& truss : model_->trusses()) {
        const auto Ke = truss.stiffness_matrix();

        const std::size_t i =
            truss.node_start().id();

        const std::size_t j =
            truss.node_end().id();

        const std::array<std::size_t, 6> dofs = {
            translational_dof(i, 0),
            translational_dof(i, 1),
            translational_dof(i, 2),
            translational_dof(j, 0),
            translational_dof(j, 1),
            translational_dof(j, 2),
        };

        for (std::size_t row = 0; row < 6; ++row) {
            for (std::size_t col = 0; col < 6; ++col) {
                const double value = Ke(
                    static_cast<Eigen::Index>(row),
                    static_cast<Eigen::Index>(col)
                );

                if (value != 0.0) {
                    triplets.emplace_back(
                        static_cast<Eigen::Index>(dofs[row]),
                        static_cast<Eigen::Index>(dofs[col]),
                        value
                    );
                }
            }
        }
    }

    K.setFromTriplets(
        triplets.begin(),
        triplets.end()
    );

    K.makeCompressed();

    return K;
}

}
