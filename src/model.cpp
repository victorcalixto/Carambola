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

std::size_t Model::node_count() const
{
    return nodes_.size();
}

std::size_t Model::truss_count() const
{
    return trusses_.size();
}

const std::deque<Node>& Model::nodes() const
{
    return nodes_;
}

const std::deque<Truss3D>& Model::trusses() const
{
    return trusses_;
}

}
