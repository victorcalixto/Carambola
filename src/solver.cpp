#include <carambola/solver.hpp>

#include <carambola/assembler.hpp>
#include <carambola/dof.hpp>
#include <carambola/elements/beam3d.hpp>

#include <Eigen/SparseCholesky>

#include <stdexcept>
#include <utility>
#include <vector>
#include <cmath>


#include "carambola/results.hpp"


namespace carambola {

AnalysisResult::AnalysisResult(
    const Model& model,
    Eigen::VectorXd displacements,
    Eigen::VectorXd reactions
)
    : model_(&model),
      displacements_(std::move(displacements)),
      reactions_(std::move(reactions))
{
}

const Eigen::VectorXd& AnalysisResult::displacements() const
{
    return displacements_;
}

const Eigen::VectorXd& AnalysisResult::reactions() const
{
    return reactions_;
}

Eigen::Vector3d AnalysisResult::node_displacement(
    const Node& node
) const
{
    const std::size_t id = node.id();

    return Eigen::Vector3d(
        displacements_(
            static_cast<Eigen::Index>(
                translational_dof(id, 0)
            )
        ),
        displacements_(
            static_cast<Eigen::Index>(
                translational_dof(id, 1)
            )
        ),
        displacements_(
            static_cast<Eigen::Index>(
                translational_dof(id, 2)
            )
        )
    );
}

Eigen::Vector3d AnalysisResult::node_reaction(
    const Node& node
) const
{
    const std::size_t id = node.id();

    return Eigen::Vector3d(
        reactions_(
            static_cast<Eigen::Index>(
                translational_dof(id, 0)
            )
        ),
        reactions_(
            static_cast<Eigen::Index>(
                translational_dof(id, 1)
            )
        ),
        reactions_(
            static_cast<Eigen::Index>(
                translational_dof(id, 2)
            )
        )
    );
}

Eigen::Vector3d AnalysisResult::node_rotation(
    const Node& node
) const
{
    const std::size_t id = node.id();

    return Eigen::Vector3d(
        displacements_(
            static_cast<Eigen::Index>(
                dof_index(id, Dof::RX)
            )
        ),
        displacements_(
            static_cast<Eigen::Index>(
                dof_index(id, Dof::RY)
            )
        ),
        displacements_(
            static_cast<Eigen::Index>(
                dof_index(id, Dof::RZ)
            )
        )
    );
}

Eigen::Vector3d AnalysisResult::node_moment_reaction(
    const Node& node
) const
{
    const std::size_t id = node.id();

    return Eigen::Vector3d(
        reactions_(
            static_cast<Eigen::Index>(
                dof_index(id, Dof::RX)
            )
        ),
        reactions_(
            static_cast<Eigen::Index>(
                dof_index(id, Dof::RY)
            )
        ),
        reactions_(
            static_cast<Eigen::Index>(
                dof_index(id, Dof::RZ)
            )
        )
    );
}

double AnalysisResult::truss_deformation(
    const Truss3D& truss
) const
{
    return truss.axial_deformation(
        displacements_
    );
}

double AnalysisResult::truss_strain(
    const Truss3D& truss
) const
{
    return truss.axial_strain(
        displacements_
    );
}

double AnalysisResult::truss_stress(
    const Truss3D& truss
) const
{
    return truss.axial_stress(
        displacements_
    );
}

double AnalysisResult::truss_force(
    const Truss3D& truss
) const
{
    return truss.axial_force(
        displacements_
    );
}

Eigen::Vector3d
AnalysisResult::shell_membrane_strain(
    const Shell3D& shell
) const
{
    return shell.membrane_strain(
        displacements_
    );
}

Eigen::Vector3d
AnalysisResult::shell_membrane_stress(
    const Shell3D& shell
) const
{
    return shell.membrane_stress(
        displacements_
    );
}

Eigen::Vector3d
AnalysisResult::shell_bending_curvature(
    const Shell3D& shell,
    double xi,
    double eta
) const
{
    return shell.bending_curvature(
        xi,
        eta,
        displacements_
    );
}

Eigen::Vector3d
AnalysisResult::shell_bending_moments(
    const Shell3D& shell,
    double xi,
    double eta
) const
{
    return shell.bending_moments(
        xi,
        eta,
        displacements_
    );
}




Eigen::Matrix<double, 12, 1>
AnalysisResult::beam_local_end_forces(
    const Beam3D& beam
) const
{
    Eigen::Matrix<double, 12, 1> f =
        beam.local_end_forces(
            displacements_
        );

    for (
        const auto& load :
        model_->uniform_beam_loads()
    ) {
        if (&load.beam() == &beam) {
            f -=
                load.local_equivalent_nodal_load();
        }
    }

    return f;
}

double AnalysisResult::beam_axial_force(
    const Beam3D& beam
) const
{
    const auto f =
        beam_local_end_forces(beam);

    return f(6);
}

double AnalysisResult::beam_torsion(
    const Beam3D& beam
) const
{
    const auto f =
        beam_local_end_forces(beam);

    return f(9);
}

double AnalysisResult::beam_shear_y(
    const Beam3D& beam
) const
{
    const auto f =
        beam_local_end_forces(beam);

    return f(7);
}

double AnalysisResult::beam_shear_z(
    const Beam3D& beam
) const
{
    const auto f =
        beam_local_end_forces(beam);

    return f(8);
}

double AnalysisResult::beam_moment_y(
    const Beam3D& beam
) const
{
    const auto f =
        beam_local_end_forces(beam);

    return f(10);
}

double AnalysisResult::beam_moment_z(
    const Beam3D& beam
) const
{
    const auto f =
        beam_local_end_forces(beam);

    return f(11);
}

LinearStaticSolver::LinearStaticSolver(
    const Model& model
)
    : model_(&model)
{
}

AnalysisResult LinearStaticSolver::solve() const
{
    Assembler assembler(*model_);

    const Eigen::SparseMatrix<double> K =
        assembler.stiffness_matrix();

    const Eigen::VectorXd F =
        assembler.force_vector();

    const auto free_dofs =
        assembler.free_dofs();

    const std::size_t total_dofs =
        model_->node_count() * DOFS_PER_NODE;

    if (free_dofs.empty()) {
        throw std::runtime_error(
            "No free degrees of freedom available."
        );
    }

    const Eigen::Index n_free =
        static_cast<Eigen::Index>(
            free_dofs.size()
        );

    /*
     * Map global DOFs to reduced free-DOF indices.
     *
     * -1 means constrained.
     */
    std::vector<Eigen::Index> global_to_free(
        total_dofs,
        -1
    );

    for (
        Eigen::Index i = 0;
        i < n_free;
        ++i
    ) {
        const std::size_t global_dof =
            free_dofs[
                static_cast<std::size_t>(i)
            ];

        global_to_free[global_dof] = i;
    }

    /*
     * Construct reduced stiffness matrix.
     */
    Eigen::SparseMatrix<double> Kff(
        n_free,
        n_free
    );

    std::vector<Eigen::Triplet<double>>
        triplets;

    triplets.reserve(
        static_cast<std::size_t>(
            K.nonZeros()
        )
    );

    for (
        Eigen::Index outer = 0;
        outer < K.outerSize();
        ++outer
    ) {
        for (
            Eigen::SparseMatrix<double>::InnerIterator
                it(K, outer);
            it;
            ++it
        ) {
            const Eigen::Index global_row =
                it.row();

            const Eigen::Index global_col =
                it.col();

            const Eigen::Index local_row =
                global_to_free[
                    static_cast<std::size_t>(
                        global_row
                    )
                ];

            const Eigen::Index local_col =
                global_to_free[
                    static_cast<std::size_t>(
                        global_col
                    )
                ];

            if (
                local_row >= 0 &&
                local_col >= 0
            ) {
                triplets.emplace_back(
                    local_row,
                    local_col,
                    it.value()
                );
            }
        }
    }

    Kff.setFromTriplets(
        triplets.begin(),
        triplets.end()
    );

    Kff.makeCompressed();

    /*
     * Reduced force vector.
     */
    Eigen::VectorXd Ff(n_free);

    for (
        Eigen::Index i = 0;
        i < n_free;
        ++i
    ) {
        const std::size_t global_dof =
            free_dofs[
                static_cast<std::size_t>(i)
            ];

        Ff(i) =
            F(
                static_cast<Eigen::Index>(
                    global_dof
                )
            );
    }

    /*
     * Solve:
     *
     * Kff * uf = Ff
     */
    Eigen::SimplicialLDLT<
        Eigen::SparseMatrix<double>
    > solver;

    solver.compute(Kff);

    if (solver.info() != Eigen::Success) {
        throw std::runtime_error(
            "Failed to factorize stiffness matrix. "
            "The structure may be unstable or singular."
        );
    }

    const Eigen::VectorXd uf =
        solver.solve(Ff);

    if (solver.info() != Eigen::Success) {
        throw std::runtime_error(
            "Failed to solve structural system."
        );
    }

    /*
     * Reconstruct full displacement vector.
     */
    Eigen::VectorXd u =
        Eigen::VectorXd::Zero(
            static_cast<Eigen::Index>(
                total_dofs
            )
        );

    for (
        Eigen::Index i = 0;
        i < n_free;
        ++i
    ) {
        const std::size_t global_dof =
            free_dofs[
                static_cast<std::size_t>(i)
            ];

        u(
            static_cast<Eigen::Index>(
                global_dof
            )
        ) = uf(i);
    }

    /*
     * Recover support reactions:
     *
     * R = K*u - F
     */
    const Eigen::VectorXd reactions =
        K * u - F;

    return AnalysisResult(
        *model_,
        std::move(u),
        std::move(reactions)
    );
}


Eigen::Vector3d
AnalysisResult::shell_bending_stress(
    const Shell3D& shell,
    double xi,
    double eta,
    double z
) const
{
    return shell.bending_stress(
        xi,
        eta,
        z,
        displacements_
    );
}


Eigen::Vector3d
AnalysisResult::shell_top_bending_stress(
    const Shell3D& shell,
    double xi,
    double eta
) const
{
    const double z =
        shell.property().thickness()
        / 2.0;

    return shell.bending_stress(
        xi,
        eta,
        z,
        displacements_
    );
}

Eigen::Vector3d
AnalysisResult::shell_bottom_bending_stress(
    const Shell3D& shell,
    double xi,
    double eta
) const
{
    const double z =
        -shell.property().thickness()
        / 2.0;

    return shell.bending_stress(
        xi,
        eta,
        z,
        displacements_
    );
}



Eigen::Vector3d
AnalysisResult::shell_top_stress(
    const Shell3D& shell,
    double xi,
    double eta
) const
{
    const Eigen::Vector3d membrane =
        shell.membrane_stress(displacements_);

    const Eigen::Vector3d bending =
        shell_top_bending_stress(
            shell,
            xi,
            eta
        );

    return membrane + bending;
}

Eigen::Vector3d
AnalysisResult::shell_bottom_stress(
    const Shell3D& shell,
    double xi,
    double eta
) const
{
    const Eigen::Vector3d membrane =
        shell.membrane_stress(displacements_);

    const Eigen::Vector3d bending =
        shell_bottom_bending_stress(
            shell,
            xi,
            eta
        );

    return membrane + bending;
}



double
AnalysisResult::shell_top_von_mises(
    const Shell3D& shell,
    double xi,
    double eta
) const
{
    return plane_stress_von_mises(
        shell_top_stress(
            shell,
            xi,
            eta
        )
    );
}

double
AnalysisResult::shell_bottom_von_mises(
    const Shell3D& shell,
    double xi,
    double eta
) const
{
    return plane_stress_von_mises(
        shell_bottom_stress(
            shell,
            xi,
            eta
        )
    );
}

Eigen::Vector2d
AnalysisResult::shell_top_principal_stresses(
    const Shell3D& shell,
    double xi,
    double eta
) const
{
    return plane_principal_stresses(
        shell_top_stress(
            shell,
            xi,
            eta
        )
    );
}

Eigen::Vector2d
AnalysisResult::shell_bottom_principal_stresses(
    const Shell3D& shell,
    double xi,
    double eta
) const
{
    return plane_principal_stresses(
        shell_bottom_stress(
            shell,
            xi,
            eta
        )
    );
}


double
AnalysisResult::shell_top_principal_angle(
    const Shell3D& shell,
    double xi,
    double eta
) const
{
    return plane_principal_angle(
        shell_top_stress(
            shell,
            xi,
            eta
        )
    );
}

double
AnalysisResult::shell_bottom_principal_angle(
    const Shell3D& shell,
    double xi,
    double eta
) const
{
    return plane_principal_angle(
        shell_bottom_stress(
            shell,
            xi,
            eta
        )
    );
}




} // namespace carambola
