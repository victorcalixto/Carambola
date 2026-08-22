#pragma once

#include <cstddef>

namespace carambola {

constexpr std::size_t DOFS_PER_NODE = 6;

enum class Dof : std::size_t {
    UX = 0,
    UY = 1,
    UZ = 2,
    RX = 3,
    RY = 4,
    RZ = 5
};

inline std::size_t dof_index(
    std::size_t node_id,
    Dof dof
)
{
    return node_id * DOFS_PER_NODE
        + static_cast<std::size_t>(dof);
}

inline std::size_t translational_dof(
    std::size_t node_id,
    std::size_t component
)
{
    return node_id * DOFS_PER_NODE + component;
}

} // namespace carambola
