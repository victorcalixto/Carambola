#pragma once

#include <carambola/node.hpp>

namespace carambola {

class Support {
public:
    Support(
        const Node& node,
        bool ux,
        bool uy,
        bool uz
    );

    const Node& node() const;

    bool ux() const;
    bool uy() const;
    bool uz() const;

private:
    const Node* node_;
    bool ux_;
    bool uy_;
    bool uz_;
};

}
