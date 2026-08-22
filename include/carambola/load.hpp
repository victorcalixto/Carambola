#pragma once

#include <carambola/node.hpp>

namespace carambola {

class PointLoad {
public:
    PointLoad(
        const Node& node,
        double fx,
        double fy,
        double fz,
        double mx = 0.0,
        double my = 0.0,
        double mz = 0.0
    );

    const Node& node() const;

    double fx() const;
    double fy() const;
    double fz() const;

    double mx() const;
    double my() const;
    double mz() const;

private:
    const Node* node_;

    double fx_;
    double fy_;
    double fz_;

    double mx_;
    double my_;
    double mz_;
};

} // namespace carambola
