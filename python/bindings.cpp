#include <pybind11/pybind11.h>

#include <carambola/version.hpp>

namespace py = pybind11;

PYBIND11_MODULE(_carambola, m)
{
    m.doc() = "Carambola structural FEM core";

    m.def(
        "version",
        &carambola::version,
        "Return the Carambola version"
    );
}
