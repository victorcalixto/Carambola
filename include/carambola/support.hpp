#pragma once

#include <carambola/node.hpp>

namespace carambola {

class Support {
public:
    Support(
        const Node& node,
        bool ux,
        bool uy,
        bool uz,
        bool rx = false,
        bool ry = false,
        bool rz = false
    );

    const Node& node() const;

    bool ux() const;
    bool uy() const;
    bool uz() const;

    bool rx() const;
    bool ry() const;
    bool rz() const;

private:
    const Node* node_;

    bool ux_;
    bool uy_;
    bool uz_;

    bool rx_;
    bool ry_;
    bool rz_;
};

} // namespace carambola
