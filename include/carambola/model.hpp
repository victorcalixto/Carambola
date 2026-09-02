#pragma once


#include <Eigen/Dense>
#include <cstddef>
#include <deque>

#include <carambola/elements/truss3d.hpp>
#include <carambola/load.hpp>
#include <carambola/node.hpp>
#include <carambola/support.hpp>
#include <carambola/elements/beam3d.hpp>
#include <carambola/beam_load.hpp>
#include <carambola/elements/shell3d.hpp>
#include <carambola/shell_load.hpp>
#include <vector>
#include <carambola/mesh.hpp>


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
  
    Beam3D& add_beam(
      const Node& node_start,
      const Node& node_end,
      const Material& material,
      const Section& section,
      Eigen::Vector3d orientation =
      Eigen::Vector3d(0.0, 0.0, 1.0)

    );

    UniformBeamLoad& add_uniform_beam_load(
    const Beam3D& beam,
    double qx,
    double qy,
    double qz
    
    );

    UniformShellPressure&
    add_uniform_shell_pressure(
        const Shell3D& shell,
        double pressure
    );



    Shell3D& add_shell(
    const Node& node_a,
    const Node& node_b,
    const Node& node_c,
    const ShellProperty& property
    );
   
    void add_shell_mesh(
    const ShellMesh& mesh,
    const ShellProperty& property
    );



    // Counts
    std::size_t node_count() const;
    std::size_t truss_count() const;
    std::size_t support_count() const;
    std::size_t point_load_count() const;
    
    std::size_t beam_count() const;
    std::size_t uniform_beam_load_count() const;
    std::size_t shell_count() const;
    std::size_t uniform_shell_pressure_count() const;

    

    void validate() const;

    std::vector<std::size_t>
    trusses_at_node(std::size_t node_id) const;

    std::vector<std::size_t>
    beams_at_node(std::size_t node_id) const;

    std::vector<std::size_t>
    shells_at_node(std::size_t node_id) const;

    std::vector<std::size_t>
    shell_neighbours(std::size_t shell_id) const;


    
    // Access
    const Node& node(std::size_t id) const;
    const Truss3D& truss(std::size_t id) const;
    const Beam3D& beam(std::size_t id) const;
    const Shell3D& shell(std::size_t id) const;

    const std::deque<Node>& nodes() const;
    const std::deque<Truss3D>& trusses() const;
    const std::deque<Support>& supports() const;
    const std::deque<PointLoad>& point_loads() const;
    const std::deque<Beam3D>& beams() const;

    const std::deque<UniformBeamLoad>&
    uniform_beam_loads() const;

    const std::deque<Shell3D>& shells() const;

    const std::deque<UniformShellPressure>&
    uniform_shell_pressures() const;

    
    std::vector<Eigen::Vector3d>
    node_coordinates() const;

    std::vector<Eigen::Vector2i>
    truss_connectivity() const;

    std::vector<Eigen::Vector2i>
    beam_connectivity() const;

    std::vector<Eigen::Vector3i>
    shell_connectivity() const;


private:
    std::deque<Node> nodes_;
    std::deque<Truss3D> trusses_;
    std::deque<Support> supports_;
    std::deque<PointLoad> point_loads_;
   
    std::deque<Beam3D> beams_;

    std::deque<UniformBeamLoad>
    uniform_beam_loads_;

    std::deque<Shell3D> shells_;

    std::deque<UniformShellPressure>
    uniform_shell_pressures_;

   };

}
