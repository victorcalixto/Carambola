#pragma once

#include <cstddef>
#include <deque>

#include <carambola/node.hpp>

namespace carambola {

class Model {
public:
    Node& add_node(double x, double y, double z);

    std::size_t node_count() const;

    const std::deque<Node>& nodes() const;

private:
    std::deque<Node> nodes_;
};

}
