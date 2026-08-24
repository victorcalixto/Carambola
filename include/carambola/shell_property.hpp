#pragma once

#include <carambola/material.hpp>

namespace carambola {

class ShellProperty {
public:
    ShellProperty(
        const Material& material,
        double thickness
    );

    const Material& material() const;

    double thickness() const;

private:
    const Material* material_;
    double thickness_;
};

} // namespace carambola
