#include <carambola/model.hpp>

namespace carambola {

Node& Model::add_node(double x, double y, double z)
{
    const std::size_t id = nodes_.size();

    nodes_.emplace_back(id, x, y, z);

    return nodes_.back();
}

Truss3D& Model::add_truss(
    const Node& node_start,
    const Node& node_end,
    const Material& material,
    const Section& section
)
{
    trusses_.emplace_back(
        node_start,
        node_end,
        material,
        section
    );

    return trusses_.back();
}

Support& Model::add_support(
    const Node& node,
    bool ux,
    bool uy,
    bool uz,
    bool rx,
    bool ry,
    bool rz
)
{
    supports_.emplace_back(
        node,
        ux,
        uy,
        uz,
        rx,
        ry,
        rz
    );

    return supports_.back();
}

PointLoad& Model::add_point_load(
    const Node& node,
    double fx,
    double fy,
    double fz,
    double mx,
    double my,
    double mz
)
{
    point_loads_.emplace_back(
        node,
        fx,
        fy,
        fz,
        mx,
        my,
        mz
    );

    return point_loads_.back();
}





std::size_t Model::node_count() const
{
    return nodes_.size();
}

std::size_t Model::truss_count() const
{
    return trusses_.size();
}

std::size_t Model::support_count() const
{
    return supports_.size();
}

std::size_t Model::point_load_count() const
{
    return point_loads_.size();
}

const std::deque<Node>& Model::nodes() const
{
    return nodes_;
}

const std::deque<Truss3D>& Model::trusses() const
{
    return trusses_;
}

const std::deque<Support>& Model::supports() const
{
    return supports_;
}

const std::deque<PointLoad>& Model::point_loads() const
{
    return point_loads_;
}

}
