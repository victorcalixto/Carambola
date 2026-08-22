#pragma once

#include <cstddef>

namespace carambola {

inline std::size_t translational_dof(
    std::size_t node_id,
    std::size_t component
)
{
    return node_id * 3 + component;
}

}
