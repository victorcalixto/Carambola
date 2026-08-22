#include <carambola/assembler.hpp>
#include <carambola/dof.hpp>

#include <algorithm>
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

Eigen::VectorXd Assembler::force_vector() const
{
    const std::size_t dof_count =
        model_->node_count() * 3;

    Eigen::VectorXd F =
        Eigen::VectorXd::Zero(
            static_cast<Eigen::Index>(dof_count)
        );

    for (const auto& load : model_->point_loads()) {
        const std::size_t node_id =
            load.node().id();

        F(
            static_cast<Eigen::Index>(
                translational_dof(node_id, 0)
            )
        ) += load.fx();

        F(
            static_cast<Eigen::Index>(
                translational_dof(node_id, 1)
            )
        ) += load.fy();

        F(
            static_cast<Eigen::Index>(
                translational_dof(node_id, 2)
            )
        ) += load.fz();
    }

    return F;
}

std::vector<std::size_t> Assembler::constrained_dofs() const
{
    std::vector<std::size_t> dofs;

    for (const auto& support : model_->supports()) {
        const std::size_t node_id =
            support.node().id();

        if (support.ux()) {
            dofs.push_back(
                translational_dof(node_id, 0)
            );
        }

        if (support.uy()) {
            dofs.push_back(
                translational_dof(node_id, 1)
            );
        }

        if (support.uz()) {
            dofs.push_back(
                translational_dof(node_id, 2)
            );
        }
    }

    std::sort(
        dofs.begin(),
        dofs.end()
    );

    dofs.erase(
        std::unique(
            dofs.begin(),
            dofs.end()
        ),
        dofs.end()
    );

    return dofs;
}

std::vector<std::size_t> Assembler::free_dofs() const
{
    const std::size_t dof_count =
        model_->node_count() * 3;

    const auto constrained =
        constrained_dofs();

    std::vector<std::size_t> free;

    free.reserve(
        dof_count - constrained.size()
    );

    for (std::size_t dof = 0; dof < dof_count; ++dof) {
        if (!std::binary_search(
                constrained.begin(),
                constrained.end(),
                dof
            )) {
            free.push_back(dof);
        }
    }

    return free;
}

}
