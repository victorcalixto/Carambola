#include <carambola/support.hpp>

namespace carambola {

Support::Support(
    const Node& node,
    bool ux,
    bool uy,
    bool uz
)
    : node_(&node),
      ux_(ux),
      uy_(uy),
      uz_(uz)
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

}
