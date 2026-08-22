#include <pybind11/eigen.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include <carambola/assembler.hpp>
#include <carambola/elements/truss3d.hpp>
#include <carambola/load.hpp>
#include <carambola/material.hpp>
#include <carambola/model.hpp>
#include <carambola/node.hpp>
#include <carambola/section.hpp>
#include <carambola/support.hpp>
#include <carambola/version.hpp>
#include <carambola/solver.hpp>



namespace py = pybind11;

PYBIND11_MODULE(_carambola, m)
{
    m.doc() = "Carambola structural FEM core";

    m.def(
        "version",
        &carambola::version,
        "Return the Carambola version"
    );

    py::class_<carambola::Node>(m, "Node")
        .def_property_readonly(
            "id",
            &carambola::Node::id
        )
        .def_property_readonly(
            "x",
            &carambola::Node::x
        )
        .def_property_readonly(
            "y",
            &carambola::Node::y
        )
        .def_property_readonly(
            "z",
            &carambola::Node::z
        );

    py::class_<carambola::Material>(m, "Material")
        .def(
            py::init<std::string, double, double, double>(),
            py::arg("name"),
            py::arg("E"),
            py::arg("nu"),
            py::arg("density")
        )
        .def_property_readonly(
            "name",
            &carambola::Material::name
        )
        .def_property_readonly(
            "E",
            &carambola::Material::youngs_modulus
        )
        .def_property_readonly(
            "nu",
            &carambola::Material::poisson_ratio
        )
        .def_property_readonly(
            "density",
            &carambola::Material::density
        )
        .def_property_readonly(
            "G",
            &carambola::Material::shear_modulus
        );

    py::class_<carambola::Section>(m, "Section")
        .def_property_readonly(
            "A",
            &carambola::Section::area
        )
        .def_property_readonly(
            "Iy",
            &carambola::Section::iy
        )
        .def_property_readonly(
            "Iz",
            &carambola::Section::iz
        )
        .def_property_readonly(
            "J",
            &carambola::Section::torsional_constant
        );

    py::class_<
        carambola::RectangularSection,
        carambola::Section
    >(m, "RectangularSection")
        .def(
            py::init<double, double>(),
            py::arg("width"),
            py::arg("height")
        )
        .def_property_readonly(
            "width",
            &carambola::RectangularSection::width
        )
        .def_property_readonly(
            "height",
            &carambola::RectangularSection::height
        );

    py::class_<
        carambola::CircularSection,
        carambola::Section
    >(m, "CircularSection")
        .def(
            py::init<double>(),
            py::arg("radius")
        )
        .def_property_readonly(
            "radius",
            &carambola::CircularSection::radius
        );

    py::class_<carambola::Truss3D>(m, "Truss3D")
        .def(
            py::init<
                const carambola::Node&,
                const carambola::Node&,
                const carambola::Material&,
                const carambola::Section&
            >(),
            py::arg("node_start"),
            py::arg("node_end"),
            py::arg("material"),
            py::arg("section"),
            py::keep_alive<1, 2>(),
            py::keep_alive<1, 3>(),
            py::keep_alive<1, 4>(),
            py::keep_alive<1, 5>()
        )
        .def_property_readonly(
            "length",
            &carambola::Truss3D::length
        )
        .def_property_readonly(
            "direction",
            &carambola::Truss3D::direction
        )
        .def(
            "stiffness_matrix",
            &carambola::Truss3D::stiffness_matrix
        )
        .def(
          "axial_deformation",
          &carambola::Truss3D::axial_deformation,
          py::arg("displacements")
        )
        .def(
            "axial_strain",
            &carambola::Truss3D::axial_strain,
            py::arg("displacements")
        )
        .def(
            "axial_stress",
            &carambola::Truss3D::axial_stress,
            py::arg("displacements")
        )
        .def(
            "axial_force",
            &carambola::Truss3D::axial_force,
            py::arg("displacements")
        );

      py::class_<carambola::Support>(m, "Support")
        .def_property_readonly(
            "ux",
            &carambola::Support::ux
        )
        .def_property_readonly(
            "uy",
            &carambola::Support::uy
        )
        .def_property_readonly(
            "uz",
            &carambola::Support::uz
        )
        .def_property_readonly(
            "rx",
            &carambola::Support::rx
        )
        .def_property_readonly(
            "ry",
            &carambola::Support::ry
        )
        .def_property_readonly(
            "rz",
            &carambola::Support::rz
        );
      py::class_<carambola::PointLoad>(m, "PointLoad")
          .def_property_readonly(
              "fx",
              &carambola::PointLoad::fx
          )
          .def_property_readonly(
              "fy",
              &carambola::PointLoad::fy
          )
          .def_property_readonly(
              "fz",
              &carambola::PointLoad::fz
          )
          .def_property_readonly(
              "mx",
              &carambola::PointLoad::mx
          )
          .def_property_readonly(
              "my",
              &carambola::PointLoad::my
          )
          .def_property_readonly(
              "mz",
              &carambola::PointLoad::mz
          );
              
    py::class_<carambola::Model>(m, "Model")
        .def(py::init<>())
        .def(
            "add_node",
            &carambola::Model::add_node,
            py::arg("x"),
            py::arg("y"),
            py::arg("z"),
            py::return_value_policy::reference_internal
        )
        .def(
            "add_truss",
            &carambola::Model::add_truss,
            py::arg("node_start"),
            py::arg("node_end"),
            py::arg("material"),
            py::arg("section"),
            py::return_value_policy::reference_internal,
            py::keep_alive<1, 4>(),
            py::keep_alive<1, 5>()
        )
      .def(
          "add_support",
          &carambola::Model::add_support,
          py::arg("node"),
          py::arg("ux"),
          py::arg("uy"),
          py::arg("uz"),
          py::arg("rx") = false,
          py::arg("ry") = false,
          py::arg("rz") = false,
          py::return_value_policy::reference_internal
      )
    .def(
          "add_point_load",
          &carambola::Model::add_point_load,
          py::arg("node"),
          py::arg("fx"),
          py::arg("fy"),
          py::arg("fz"),
          py::arg("mx") = 0.0,
          py::arg("my") = 0.0,
          py::arg("mz") = 0.0,
          py::return_value_policy::reference_internal
      )


      .def_property_readonly(
            "node_count",
            &carambola::Model::node_count
        )
        .def_property_readonly(
            "truss_count",
            &carambola::Model::truss_count
        )
        .def_property_readonly(
            "support_count",
            &carambola::Model::support_count
        )
        .def_property_readonly(
            "point_load_count",
            &carambola::Model::point_load_count
        )
        .def_property_readonly(
            "trusses",
            &carambola::Model::trusses,
            py::return_value_policy::reference_internal
        );

    py::class_<carambola::Assembler>(m, "Assembler")
        .def(
            py::init<const carambola::Model&>(),
            py::arg("model"),
            py::keep_alive<1, 2>()
        )
        .def(
            "stiffness_matrix",
            &carambola::Assembler::stiffness_matrix
        )
        .def(
            "force_vector",
            &carambola::Assembler::force_vector
        )
        .def(
            "constrained_dofs",
            &carambola::Assembler::constrained_dofs
        )
        .def(
            "free_dofs",
            &carambola::Assembler::free_dofs
        );
    py::class_<carambola::AnalysisResult>(
        m,
        "AnalysisResult"
    )
        .def_property_readonly(
            "displacements",
            &carambola::AnalysisResult::displacements
        )
        .def_property_readonly(
            "reactions",
            &carambola::AnalysisResult::reactions
        )
        .def(
            "node_displacement",
            &carambola::AnalysisResult::node_displacement,
            py::arg("node")
        )
        .def(
            "node_reaction",
            &carambola::AnalysisResult::node_reaction,
            py::arg("node")
        )
        .def(
            "truss_deformation",
            &carambola::AnalysisResult::truss_deformation,
            py::arg("truss")
        )
        .def(
            "truss_strain",
            &carambola::AnalysisResult::truss_strain,
            py::arg("truss")
        )
        .def(
            "truss_stress",
            &carambola::AnalysisResult::truss_stress,
            py::arg("truss")
        )
        .def(
            "truss_force",
            &carambola::AnalysisResult::truss_force,
            py::arg("truss")
        );

    py::class_<carambola::LinearStaticSolver>(
      m,
      "LinearStaticSolver"
  )
      .def(
          py::init<const carambola::Model&>(),
          py::arg("model"),
          py::keep_alive<1, 2>()
      )
      .def(
          "solve",
          &carambola::LinearStaticSolver::solve
      );
}
