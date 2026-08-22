#pragma once

#include <carambola/node.hpp>

namespace carambola {

class PointLoad {
public:
    PointLoad(
        const Node& node,
        double fx,
        double fy,
        double fz
    );

    const Node& node() const;

    double fx() const;
    double fy() const;
    double fz() const;

private:
    const Node* node_;
    double fx_;
    double fy_;
    double fz_;
};

}
