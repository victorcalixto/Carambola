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
        model_->node_count() * DOFS_PER_NODE;

    Eigen::SparseMatrix<double> K(
        static_cast<Eigen::Index>(dof_count),
        static_cast<Eigen::Index>(dof_count)
    );

    std::vector<Eigen::Triplet<double>> triplets;
    
    triplets.reserve(
    model_->truss_count() * 36
    + model_->beam_count() * 144
    + model_->shell_count() * 324
    );

    for (const auto& truss : model_->trusses()) {
        const auto Ke = truss.stiffness_matrix();

        const std::size_t i =
            truss.node_start().id();

        const std::size_t j =
            truss.node_end().id();

        // Truss3D uses only translational DOFs.
        const std::array<std::size_t, 6> dofs = {
            dof_index(i, Dof::UX),
            dof_index(i, Dof::UY),
            dof_index(i, Dof::UZ),

            dof_index(j, Dof::UX),
            dof_index(j, Dof::UY),
            dof_index(j, Dof::UZ),
        };

        for (std::size_t row = 0; row < 6; ++row) {
            for (std::size_t col = 0; col < 6; ++col) {
                const double value = Ke(
                    static_cast<Eigen::Index>(row),
                    static_cast<Eigen::Index>(col)
                );

                if (value != 0.0) {
                    triplets.emplace_back(
                        static_cast<Eigen::Index>(
                            dofs[row]
                        ),
                        static_cast<Eigen::Index>(
                            dofs[col]
                        ),
                        value
                    );
                }
            }
        }
    }
    
    for (const auto& beam : model_->beams()) {
    const auto Ke =
        beam.stiffness_matrix();

    const std::size_t i =
        beam.node_start().id();

    const std::size_t j =
        beam.node_end().id();

    const std::array<std::size_t, 12> dofs = {
        dof_index(i, Dof::UX),
        dof_index(i, Dof::UY),
        dof_index(i, Dof::UZ),
        dof_index(i, Dof::RX),
        dof_index(i, Dof::RY),
        dof_index(i, Dof::RZ),

        dof_index(j, Dof::UX),
        dof_index(j, Dof::UY),
        dof_index(j, Dof::UZ),
        dof_index(j, Dof::RX),
        dof_index(j, Dof::RY),
        dof_index(j, Dof::RZ),
    };

    for (std::size_t row = 0;
         row < 12;
         ++row) {

        for (std::size_t col = 0;
             col < 12;
             ++col) {

            const double value = Ke(
                static_cast<Eigen::Index>(row),
                static_cast<Eigen::Index>(col)
            );

            if (value != 0.0) {
                triplets.emplace_back(
                    static_cast<Eigen::Index>(
                        dofs[row]
                    ),
                    static_cast<Eigen::Index>(
                        dofs[col]
                    ),
                    value
                );
            }
        }
    }
}   
    

for (const auto& shell : model_->shells()) {
    const auto Ke =
        shell.stiffness_matrix();

    const std::size_t node_ids[3] = {
        shell.node_a().id(),
        shell.node_b().id(),
        shell.node_c().id()
    };

    Eigen::Index global_dofs[18];

    for (int node = 0; node < 3; ++node) {
        const std::size_t id =
            node_ids[node];

        const int offset =
            node * 6;

        global_dofs[offset + 0] =
            static_cast<Eigen::Index>(
                dof_index(id, Dof::UX)
            );

        global_dofs[offset + 1] =
            static_cast<Eigen::Index>(
                dof_index(id, Dof::UY)
            );

        global_dofs[offset + 2] =
            static_cast<Eigen::Index>(
                dof_index(id, Dof::UZ)
            );

        global_dofs[offset + 3] =
            static_cast<Eigen::Index>(
                dof_index(id, Dof::RX)
            );

        global_dofs[offset + 4] =
            static_cast<Eigen::Index>(
                dof_index(id, Dof::RY)
            );

        global_dofs[offset + 5] =
            static_cast<Eigen::Index>(
                dof_index(id, Dof::RZ)
            );
    }

    for (int i = 0; i < 18; ++i) {
        for (int j = 0; j < 18; ++j) {
            const double value =
                Ke(i, j);

            if (value != 0.0) {
                triplets.emplace_back(
                    global_dofs[i],
                    global_dofs[j],
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
        model_->node_count() * DOFS_PER_NODE;

    Eigen::VectorXd F =
        Eigen::VectorXd::Zero(
            static_cast<Eigen::Index>(
                dof_count
            )
        );

    for (const auto& load : model_->point_loads()) {
        const std::size_t node_id =
            load.node().id();

        F(
            static_cast<Eigen::Index>(
                dof_index(node_id, Dof::UX)
            )
        ) += load.fx();

        F(
            static_cast<Eigen::Index>(
                dof_index(node_id, Dof::UY)
            )
        ) += load.fy();

        F(
            static_cast<Eigen::Index>(
                dof_index(node_id, Dof::UZ)
            )
        ) += load.fz();

        F(
            static_cast<Eigen::Index>(
                dof_index(node_id, Dof::RX)
            )
        ) += load.mx();

        F(
            static_cast<Eigen::Index>(
                dof_index(node_id, Dof::RY)
            )
        ) += load.my();

        F(
            static_cast<Eigen::Index>(
                dof_index(node_id, Dof::RZ)
            )
        ) += load.mz();
    }

   for (
    const auto& load :
    model_->uniform_beam_loads()
) {
    const Beam3D& beam =
        load.beam();

    const auto f =
        load.global_equivalent_nodal_load();

    const std::size_t i =
        beam.node_start().id();

    const std::size_t j =
        beam.node_end().id();

    const std::array<std::size_t, 12> dofs = {
        dof_index(i, Dof::UX),
        dof_index(i, Dof::UY),
        dof_index(i, Dof::UZ),
        dof_index(i, Dof::RX),
        dof_index(i, Dof::RY),
        dof_index(i, Dof::RZ),

        dof_index(j, Dof::UX),
        dof_index(j, Dof::UY),
        dof_index(j, Dof::UZ),
        dof_index(j, Dof::RX),
        dof_index(j, Dof::RY),
        dof_index(j, Dof::RZ),
    };

    for (std::size_t k = 0;
         k < 12;
         ++k) {

        F(
            static_cast<Eigen::Index>(
                dofs[k]
            )
        ) += f(
            static_cast<Eigen::Index>(k)
        );
    }
}


    for (
    const auto& load :
    model_->uniform_shell_pressures()
) {
    const Shell3D& shell =
        load.shell();

    const auto f =
        shell.pressure_load_vector(
            load.pressure()
        );

    const std::size_t node_ids[3] = {
        shell.node_a().id(),
        shell.node_b().id(),
        shell.node_c().id()
    };

    std::array<std::size_t, 18> dofs;

    for (int node = 0; node < 3; ++node) {
        const std::size_t id =
            node_ids[node];

        const int offset =
            node * 6;

        dofs[offset + 0] =
            dof_index(id, Dof::UX);

        dofs[offset + 1] =
            dof_index(id, Dof::UY);

        dofs[offset + 2] =
            dof_index(id, Dof::UZ);

        dofs[offset + 3] =
            dof_index(id, Dof::RX);

        dofs[offset + 4] =
            dof_index(id, Dof::RY);

        dofs[offset + 5] =
            dof_index(id, Dof::RZ);
    }

    for (std::size_t k = 0;
         k < 18;
         ++k) {

        F(
            static_cast<Eigen::Index>(
                dofs[k]
            )
        ) += f(
            static_cast<Eigen::Index>(k)
        );
    }
}
    

    return F;
}


std::vector<std::size_t>
Assembler::constrained_dofs() const
{
    std::vector<std::size_t> dofs;

    for (const auto& support : model_->supports()) {
        const std::size_t node_id =
            support.node().id();

        if (support.ux()) {
            dofs.push_back(
                dof_index(node_id, Dof::UX)
            );
        }

        if (support.uy()) {
            dofs.push_back(
                dof_index(node_id, Dof::UY)
            );
        }

        if (support.uz()) {
            dofs.push_back(
                dof_index(node_id, Dof::UZ)
            );
        }

        if (support.rx()) {
            dofs.push_back(
                dof_index(node_id, Dof::RX)
            );
        }

        if (support.ry()) {
            dofs.push_back(
                dof_index(node_id, Dof::RY)
            );
        }

        if (support.rz()) {
            dofs.push_back(
                dof_index(node_id, Dof::RZ)
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

std::vector<std::size_t>
Assembler::free_dofs() const
{
    const std::size_t dof_count =
        model_->node_count() * DOFS_PER_NODE;

    const auto constrained =
        constrained_dofs();

    std::vector<std::size_t> free;

    free.reserve(
        dof_count - constrained.size()
    );

    for (std::size_t dof = 0;
         dof < dof_count;
         ++dof) {

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

} // namespace carambola
