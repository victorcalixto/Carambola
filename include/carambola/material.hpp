#pragma once

#include <string>

namespace carambola {

class Material {
public:
    Material(
        std::string name,
        double youngs_modulus,
        double poisson_ratio,
        double density
    );

    const std::string& name() const;

    double youngs_modulus() const;
    double poisson_ratio() const;
    double density() const;
    double shear_modulus() const;

private:
    std::string name_;
    double youngs_modulus_;
    double poisson_ratio_;
    double density_;
};

}
