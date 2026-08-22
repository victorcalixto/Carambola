#pragma once

#include <cstddef>

namespace carambola {

class Node {
public:
    Node(std::size_t id, double x, double y, double z);

    std::size_t id() const;

    double x() const;
    double y() const;
    double z() const;

private:
    std::size_t id_;
    double x_;
    double y_;
    double z_;
};

}
