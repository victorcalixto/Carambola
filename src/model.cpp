#include <carambola/model.hpp>

namespace carambola {

Node& Model::add_node(double x, double y, double z)
{
    const std::size_t id = nodes_.size();

    nodes_.emplace_back(id, x, y, z);

    return nodes_.back();
}

std::size_t Model::node_count() const
{
    return nodes_.size();
}

const std::deque<Node>& Model::nodes() const
{
    return nodes_;
}

}
