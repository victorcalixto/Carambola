#include "carambola/results.hpp"

#include <cmath>

namespace carambola {

double plane_stress_von_mises(
    const Eigen::Vector3d& stress
)
{
    const double sx = stress(0);
    const double sy = stress(1);
    const double txy = stress(2);

    return std::sqrt(
        sx * sx
        - sx * sy
        + sy * sy
        + 3.0 * txy * txy
    );
}

Eigen::Vector2d plane_principal_stresses(
    const Eigen::Vector3d& stress
)
{
    const double sx = stress(0);
    const double sy = stress(1);
    const double txy = stress(2);

    const double mean =
        0.5 * (sx + sy);

    const double radius =
        std::sqrt(
            0.25 * (sx - sy) * (sx - sy)
            + txy * txy
        );

    return Eigen::Vector2d(
        mean + radius,
        mean - radius
    );
}

double plane_principal_angle(
    const Eigen::Vector3d& stress
)
{
    const double sx = stress(0);
    const double sy = stress(1);
    const double txy = stress(2);

    return 0.5 * std::atan2(
        2.0 * txy,
        sx - sy
    );
}






}
