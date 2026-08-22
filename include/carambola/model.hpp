#pragma once

#include <cstddef>
#include <deque>

#include <carambola/elements/truss3d.hpp>
#include <carambola/load.hpp>
#include <carambola/node.hpp>
#include <carambola/support.hpp>

namespace carambola {

class Model {
public:
    // Nodes
    Node& add_node(double x, double y, double z);

    // Trusses
    Truss3D& add_truss(
        const Node& node_start,
        const Node& node_end,
        const Material& material,
        const Section& section
    );

    // Supports
    Support& add_support(
    const Node& node,
    bool ux,
    bool uy,
    bool uz,
    bool rx = false,
    bool ry = false,
    bool rz = false
    );
    // Loads
    PointLoad& add_point_load(
    const Node& node,
    double fx,
    double fy,
    double fz,
    double mx = 0.0,
    double my = 0.0,
    double mz = 0.0
    );
      
    // Counts
    std::size_t node_count() const;
    std::size_t truss_count() const;
    std::size_t support_count() const;
    std::size_t point_load_count() const;

    // Access
    const std::deque<Node>& nodes() const;
    const std::deque<Truss3D>& trusses() const;
    const std::deque<Support>& supports() const;
    const std::deque<PointLoad>& point_loads() const;

private:
    std::deque<Node> nodes_;
    std::deque<Truss3D> trusses_;
    std::deque<Support> supports_;
    std::deque<PointLoad> point_loads_;
};

}
