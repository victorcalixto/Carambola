#include <carambola/support.hpp>

namespace carambola {

Support::Support(
    const Node& node,
    bool ux,
    bool uy,
    bool uz,
    bool rx,
    bool ry,
    bool rz
)
    : node_(&node),
      ux_(ux),
      uy_(uy),
      uz_(uz),
      rx_(rx),
      ry_(ry),
      rz_(rz)
{
}

const Node& Support::node() const
{
    return *node_;
}

bool Support::ux() const
{
    return ux_;
}

bool Support::uy() const
{
    return uy_;
}

bool Support::uz() const
{
    return uz_;
}

bool Support::rx() const
{
    return rx_;
}

bool Support::ry() const
{
    return ry_;
}

bool Support::rz() const
{
    return rz_;
}

} // namespace carambola
