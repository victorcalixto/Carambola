#include "carambola/loads/uniform_shell_pressure.hpp"

namespace carambola {

UniformShellPressure::UniformShellPressure(
    const Shell3D& shell,
    double pressure
)
    : shell_(&shell),
      pressure_(pressure)
{
}

const Shell3D&
UniformShellPressure::shell() const
{
    return *shell_;
}

double
UniformShellPressure::pressure() const
{
    return pressure_;
}

} // namespace carambola
