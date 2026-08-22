#include <carambola/node.hpp>

namespace carambola {

Node::Node(std::size_t id, double x, double y, double z)
    : id_(id), x_(x), y_(y), z_(z)
{
}

std::size_t Node::id() const
{
    return id_;
}

double Node::x() const
{
    return x_;
}

double Node::y() const
{
    return y_;
}

double Node::z() const
{
    return z_;
}

}
