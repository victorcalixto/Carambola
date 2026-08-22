#pragma once

#include <Eigen/Dense>

#include <carambola/elements/beam3d.hpp>

namespace carambola {

class UniformBeamLoad {
public:
    UniformBeamLoad(
        const Beam3D& beam,
        double qx,
        double qy,
        double qz
    );

    const Beam3D& beam() const;

    double qx() const;
    double qy() const;
    double qz() const;

    Eigen::Matrix<double, 12, 1>
    local_equivalent_nodal_load() const;

    Eigen::Matrix<double, 12, 1>
    global_equivalent_nodal_load() const;

private:
    const Beam3D* beam_;

    double qx_;
    double qy_;
    double qz_;
};

} // namespace carambola
