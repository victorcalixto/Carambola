#pragma once

#include <cstddef>
#include <deque>

#include <carambola/elements/truss3d.hpp>
#include <carambola/node.hpp>

namespace carambola {

class Model {
public:
    Node& add_node(double x, double y, double z);

    Truss3D& add_truss(
        const Node& node_start,
        const Node& node_end,
        const Material& material,
        const Section& section
    );

    std::size_t node_count() const;
    std::size_t truss_count() const;

    const std::deque<Node>& nodes() const;
    const std::deque<Truss3D>& trusses() const;

private:
    std::deque<Node> nodes_;
    std::deque<Truss3D> trusses_;
};

}
