#include <carambola/load.hpp>

namespace carambola {

PointLoad::PointLoad(
    const Node& node,
    double fx,
    double fy,
    double fz,
    double mx,
    double my,
    double mz
)
    : node_(&node),
      fx_(fx),
      fy_(fy),
      fz_(fz),
      mx_(mx),
      my_(my),
      mz_(mz)
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

double PointLoad::mx() const
{
    return mx_;
}

double PointLoad::my() const
{
    return my_;
}

double PointLoad::mz() const
{
    return mz_;
}

} // namespace carambola
