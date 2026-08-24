#include <carambola/shell_property.hpp>

#include <stdexcept>

namespace carambola {

ShellProperty::ShellProperty(
    const Material& material,
    double thickness
)
    : material_(&material),
      thickness_(thickness)
{
    if (thickness_ <= 0.0) {
        throw std::invalid_argument(
            "Shell thickness must be positive."
        );
    }
}

const Material& ShellProperty::material() const
{
    return *material_;
}

double ShellProperty::thickness() const
{
    return thickness_;
}

} // namespace carambola

