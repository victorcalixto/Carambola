#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include <carambola/material.hpp>
#include <carambola/model.hpp>
#include <carambola/node.hpp>
#include <carambola/section.hpp>
#include <carambola/version.hpp>

#include <pybind11/eigen.h>
#include <carambola/elements/truss3d.hpp>
#include <carambola/assembler.hpp>


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
        .def_property_readonly("id", &carambola::Node::id)
        .def_property_readonly("x", &carambola::Node::x)
        .def_property_readonly("y", &carambola::Node::y)
        .def_property_readonly("z", &carambola::Node::z);

    py::class_<carambola::Material>(m, "Material")
        .def(
            py::init<std::string, double, double, double>(),
            py::arg("name"),
            py::arg("E"),
            py::arg("nu"),
            py::arg("density")
        )
        .def_property_readonly("name", &carambola::Material::name)
        .def_property_readonly("E", &carambola::Material::youngs_modulus)
        .def_property_readonly("nu", &carambola::Material::poisson_ratio)
        .def_property_readonly("density", &carambola::Material::density)
        .def_property_readonly("G", &carambola::Material::shear_modulus);

    py::class_<carambola::Section>(m, "Section")
        .def_property_readonly("A", &carambola::Section::area)
        .def_property_readonly("Iy", &carambola::Section::iy)
        .def_property_readonly("Iz", &carambola::Section::iz)
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
      .def_property_readonly(
          "node_count",
          &carambola::Model::node_count
      )
      .def_property_readonly(
          "truss_count",
          &carambola::Model::truss_count
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
    );


}
