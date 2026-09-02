#pragma once

#include <Eigen/Core>

namespace carambola {

double plane_stress_von_mises(
    const Eigen::Vector3d& stress
);


Eigen::Vector2d plane_principal_stresses(
    const Eigen::Vector3d& stress
);

double plane_principal_angle(
    const Eigen::Vector3d& stress
);

}
