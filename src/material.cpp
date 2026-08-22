#include <carambola/material.hpp>

#include <stdexcept>
#include <utility>

namespace carambola {

Material::Material(
    std::string name,
    double youngs_modulus,
    double poisson_ratio,
    double density
)
    : name_(std::move(name)),
      youngs_modulus_(youngs_modulus),
      poisson_ratio_(poisson_ratio),
      density_(density)
{
    if (youngs_modulus_ <= 0.0) {
        throw std::invalid_argument("Young's modulus must be positive.");
    }

    if (poisson_ratio_ <= -1.0 || poisson_ratio_ >= 0.5) {
        throw std::invalid_argument(
            "Poisson ratio must be greater than -1 and less than 0.5."
        );
    }

    if (density_ < 0.0) {
        throw std::invalid_argument("Density cannot be negative.");
    }
}

const std::string& Material::name() const
{
    return name_;
}

double Material::youngs_modulus() const
{
    return youngs_modulus_;
}

double Material::poisson_ratio() const
{
    return poisson_ratio_;
}

double Material::density() const
{
    return density_;
}

double Material::shear_modulus() const
{
    return youngs_modulus_ / (2.0 * (1.0 + poisson_ratio_));
}

}
