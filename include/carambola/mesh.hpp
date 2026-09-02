#pragma once

#include <Eigen/Dense>

#include <cstddef>
#include <vector>


namespace carambola {

struct ShellMesh {
    std::vector<Eigen::Vector3d> vertices;
    std::vector<Eigen::Vector3i> faces;
};


ShellMesh rectangular_shell_mesh(
    double width,
    double height,
    std::size_t nx,
    std::size_t ny
);

}
