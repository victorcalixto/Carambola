#include <carambola/model.hpp>

#include <stdexcept>
#include <utility>


namespace carambola {

Node&
Model::add_node(
    double x,
    double y,
    double z
)
{
    const std::size_t id = nodes_.size();

    nodes_.emplace_back(
        id,
        x,
        y,
        z
    );

    return nodes_.back();
}


Truss3D&
Model::add_truss(
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


Support&
Model::add_support(
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


PointLoad&
Model::add_point_load(
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


Beam3D&
Model::add_beam(
    const Node& node_start,
    const Node& node_end,
    const Material& material,
    const Section& section,
    Eigen::Vector3d orientation
)
{
    beams_.emplace_back(
        node_start,
        node_end,
        material,
        section,
        std::move(orientation)
    );

    return beams_.back();
}


UniformBeamLoad&
Model::add_uniform_beam_load(
    const Beam3D& beam,
    double qx,
    double qy,
    double qz
)
{
    uniform_beam_loads_.emplace_back(
        beam,
        qx,
        qy,
        qz
    );

    return uniform_beam_loads_.back();
}


Shell3D&
Model::add_shell(
    const Node& node_a,
    const Node& node_b,
    const Node& node_c,
    const ShellProperty& property
)
{
    shells_.emplace_back(
        node_a,
        node_b,
        node_c,
        property
    );

    return shells_.back();
}


void
Model::add_shell_mesh(
    const ShellMesh& mesh,
    const ShellProperty& property
)
{
    const std::size_t node_offset =
        nodes_.size();

    for (const auto& vertex : mesh.vertices) {
        add_node(
            vertex.x(),
            vertex.y(),
            vertex.z()
        );
    }

    for (const auto& face : mesh.faces) {
        const auto a =
            static_cast<std::size_t>(
                face[0]
            );

        const auto b =
            static_cast<std::size_t>(
                face[1]
            );

        const auto c =
            static_cast<std::size_t>(
                face[2]
            );

        if (
            a >= mesh.vertices.size()
            || b >= mesh.vertices.size()
            || c >= mesh.vertices.size()
        ) {
            throw std::out_of_range(
                "Shell mesh face index "
                "out of range"
            );
        }

        add_shell(
            nodes_[node_offset + a],
            nodes_[node_offset + b],
            nodes_[node_offset + c],
            property
        );
    }
}



UniformShellPressure&
Model::add_uniform_shell_pressure(
    const Shell3D& shell,
    double pressure
)
{
    uniform_shell_pressures_.emplace_back(
        shell,
        pressure
    );

    return uniform_shell_pressures_.back();
}







// Counts

std::size_t
Model::node_count() const
{
    return nodes_.size();
}


std::size_t
Model::truss_count() const
{
    return trusses_.size();
}


std::size_t
Model::support_count() const
{
    return supports_.size();
}


std::size_t
Model::point_load_count() const
{
    return point_loads_.size();
}


std::size_t
Model::beam_count() const
{
    return beams_.size();
}


std::size_t
Model::uniform_beam_load_count() const
{
    return uniform_beam_loads_.size();
}


std::size_t
Model::shell_count() const
{
    return shells_.size();
}


std::size_t
Model::uniform_shell_pressure_count() const
{
    return uniform_shell_pressures_.size();
}


// Lookup

const Node&
Model::node(
    std::size_t id
) const
{
    if (id >= nodes_.size()) {
        throw std::out_of_range(
            "Node id out of range"
        );
    }

    return nodes_[id];
}


const Truss3D&
Model::truss(
    std::size_t id
) const
{
    if (id >= trusses_.size()) {
        throw std::out_of_range(
            "Truss id out of range"
        );
    }

    return trusses_[id];
}


const Beam3D&
Model::beam(
    std::size_t id
) const
{
    if (id >= beams_.size()) {
        throw std::out_of_range(
            "Beam id out of range"
        );
    }

    return beams_[id];
}


const Shell3D&
Model::shell(
    std::size_t id
) const
{
    if (id >= shells_.size()) {
        throw std::out_of_range(
            "Shell id out of range"
        );
    }

    return shells_[id];
}


// Validation

void
Model::validate() const
{
    constexpr double tolerance = 1e-12;

    for (const auto& truss : trusses_) {
        if (truss.length() <= tolerance) {
            throw std::runtime_error(
                "Model validation failed: "
                "zero-length truss"
            );
        }
    }

    for (const auto& beam : beams_) {
        if (beam.length() <= tolerance) {
            throw std::runtime_error(
                "Model validation failed: "
                "zero-length beam"
            );
        }
    }

    for (const auto& shell : shells_) {
        if (shell.area() <= tolerance) {
            throw std::runtime_error(
                "Model validation failed: "
                "zero-area shell"
            );
        }
    }
}


// Collection access

const std::deque<Node>&
Model::nodes() const
{
    return nodes_;
}


const std::deque<Truss3D>&
Model::trusses() const
{
    return trusses_;
}


const std::deque<Support>&
Model::supports() const
{
    return supports_;
}


const std::deque<PointLoad>&
Model::point_loads() const
{
    return point_loads_;
}


const std::deque<Beam3D>&
Model::beams() const
{
    return beams_;
}


const std::deque<UniformBeamLoad>&
Model::uniform_beam_loads() const
{
    return uniform_beam_loads_;
}


const std::deque<Shell3D>&
Model::shells() const
{
    return shells_;
}


const std::deque<UniformShellPressure>&
Model::uniform_shell_pressures() const
{
    return uniform_shell_pressures_;
}


// Connectivity

std::vector<std::size_t>
Model::trusses_at_node(
    std::size_t node_id
) const
{
    const Node& target =
        node(node_id);

    std::vector<std::size_t> result;

    for (
        std::size_t i = 0;
        i < trusses_.size();
        ++i
    ) {
        const Truss3D& truss =
            trusses_[i];

        if (
            truss.node_start().id()
                == target.id()
            || truss.node_end().id()
                == target.id()
        ) {
            result.push_back(i);
        }
    }

    return result;
}


std::vector<std::size_t>
Model::beams_at_node(
    std::size_t node_id
) const
{
    const Node& target =
        node(node_id);

    std::vector<std::size_t> result;

    for (
        std::size_t i = 0;
        i < beams_.size();
        ++i
    ) {
        const Beam3D& beam =
            beams_[i];

        if (
            beam.node_start().id()
                == target.id()
            || beam.node_end().id()
                == target.id()
        ) {
            result.push_back(i);
        }
    }

    return result;
}


std::vector<std::size_t>
Model::shells_at_node(
    std::size_t node_id
) const
{
    const Node& target =
        node(node_id);

    std::vector<std::size_t> result;

    for (
        std::size_t i = 0;
        i < shells_.size();
        ++i
    ) {
        const Shell3D& shell =
            shells_[i];

        if (
            shell.node_a().id()
                == target.id()
            || shell.node_b().id()
                == target.id()
            || shell.node_c().id()
                == target.id()
        ) {
            result.push_back(i);
        }
    }

    return result;
}


std::vector<std::size_t>
Model::shell_neighbours(
    std::size_t shell_id
) const
{
    const Shell3D& target =
        shell(shell_id);

    const std::size_t target_nodes[3] = {
        target.node_a().id(),
        target.node_b().id(),
        target.node_c().id(),
    };

    std::vector<std::size_t> result;

    for (
        std::size_t i = 0;
        i < shells_.size();
        ++i
    ) {
        if (i == shell_id) {
            continue;
        }

        const Shell3D& candidate =
            shells_[i];

        const std::size_t candidate_nodes[3] = {
            candidate.node_a().id(),
            candidate.node_b().id(),
            candidate.node_c().id(),
        };

        int shared = 0;

        for (
            const auto target_node :
            target_nodes
        ) {
            for (
                const auto candidate_node :
                candidate_nodes
            ) {
                if (
                    target_node
                    == candidate_node
                ) {
                    ++shared;
                    break;
                }
            }
        }

        if (shared >= 2) {
            result.push_back(i);
        }
    }

    return result;
}


std::vector<Eigen::Vector3d>
Model::node_coordinates() const
{
    std::vector<Eigen::Vector3d> result;

    result.reserve(nodes_.size());

    for (const auto& node : nodes_) {
        result.emplace_back(
            node.x(),
            node.y(),
            node.z()
        );
    }

    return result;
}


std::vector<Eigen::Vector2i>
Model::truss_connectivity() const
{
    std::vector<Eigen::Vector2i> result;

    result.reserve(trusses_.size());

    for (const auto& truss : trusses_) {
        result.emplace_back(
            static_cast<int>(
                truss.node_start().id()
            ),
            static_cast<int>(
                truss.node_end().id()
            )
        );
    }

    return result;
}


std::vector<Eigen::Vector2i>
Model::beam_connectivity() const
{
    std::vector<Eigen::Vector2i> result;

    result.reserve(beams_.size());

    for (const auto& beam : beams_) {
        result.emplace_back(
            static_cast<int>(
                beam.node_start().id()
            ),
            static_cast<int>(
                beam.node_end().id()
            )
        );
    }

    return result;
}


std::vector<Eigen::Vector3i>
Model::shell_connectivity() const
{
    std::vector<Eigen::Vector3i> result;

    result.reserve(shells_.size());

    for (const auto& shell : shells_) {
        result.emplace_back(
            static_cast<int>(
                shell.node_a().id()
            ),
            static_cast<int>(
                shell.node_b().id()
            ),
            static_cast<int>(
                shell.node_c().id()
            )
        );
    }

    return result;
}




}
