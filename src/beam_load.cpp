#include <carambola/beam_load.hpp>

namespace carambola {

UniformBeamLoad::UniformBeamLoad(
    const Beam3D& beam,
    double qx,
    double qy,
    double qz
)
    : beam_(&beam),
      qx_(qx),
      qy_(qy),
      qz_(qz)
{
}

const Beam3D& UniformBeamLoad::beam() const
{
    return *beam_;
}

double UniformBeamLoad::qx() const
{
    return qx_;
}

double UniformBeamLoad::qy() const
{
    return qy_;
}

double UniformBeamLoad::qz() const
{
    return qz_;
}

Eigen::Matrix<double, 12, 1>
UniformBeamLoad::local_equivalent_nodal_load() const
{
    const double L =
        beam_->length();

    const double L2 =
        L * L;

    Eigen::Matrix<double, 12, 1> f =
        Eigen::Matrix<double, 12, 1>::Zero();

    /*
     * Local beam DOF ordering:
     *
     * node i:
     * UX UY UZ RX RY RZ
     *
     * node j:
     * UX UY UZ RX RY RZ
     */

    // Uniform axial load qx
    f(0) += qx_ * L / 2.0;
    f(6) += qx_ * L / 2.0;

    /*
     * Uniform load qy.
     *
     * Bending about local Z.
     */
    f(1) += qy_ * L / 2.0;
    f(5) += qy_ * L2 / 12.0;

    f(7) += qy_ * L / 2.0;
    f(11) -= qy_ * L2 / 12.0;

    /*
     * Uniform load qz.
     *
     * Bending about local Y.
     */
    f(2) += qz_ * L / 2.0;
    f(4) -= qz_ * L2 / 12.0;

    f(8) += qz_ * L / 2.0;
    f(10) += qz_ * L2 / 12.0;

    return f;
}

Eigen::Matrix<double, 12, 1>
UniformBeamLoad::global_equivalent_nodal_load() const
{
    /*
     * u_local = T * u_global
     *
     * Therefore:
     *
     * f_global = T^T * f_local
     */

    return beam_->transformation_matrix().transpose()
        * local_equivalent_nodal_load();
}

} // namespace carambola
