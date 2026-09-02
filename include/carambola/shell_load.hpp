#pragma once


#include "carambola/elements/shell3d.hpp"


namespace carambola {

class UniformShellPressure
{
public:
    UniformShellPressure(
        const Shell3D& shell,
        double pressure
    );

    const Shell3D& shell() const;

    double pressure() const;

private:
    const Shell3D* shell_;
    double pressure_;
};

} // namespace carambola
