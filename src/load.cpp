#include <carambola/load.hpp>

namespace carambola {

PointLoad::PointLoad(
    const Node& node,
    double fx,
    double fy,
    double fz
)
    : node_(&node),
      fx_(fx),
      fy_(fy),
      fz_(fz)
{
}

const Node& PointLoad::node() const
{
    return *node_;
}

double PointLoad::fx() const
{
    return fx_;
}

double PointLoad::fy() const
{
    return fy_;
}

double PointLoad::fz() const
{
    return fz_;
}

}
