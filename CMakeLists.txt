cmake_minimum_required(VERSION 3.18)

project(
    carambola
    VERSION 0.1.0
    LANGUAGES CXX
)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

find_package(
    Python
    REQUIRED
    COMPONENTS Interpreter Development.Module
)

find_package(pybind11 CONFIG REQUIRED)
find_package(Eigen3 CONFIG REQUIRED)

add_library(
   carambola_core
    STATIC
    src/version.cpp
    src/node.cpp
    src/material.cpp
    src/section.cpp
    src/model.cpp
    src/support.cpp
    src/load.cpp
    src/beam_load.cpp
    src/assembler.cpp
    src/solver.cpp
    src/elements/truss3d.cpp
    src/elements/beam3d.cpp
    src/shell_property.cpp
    src/elements/shell3d.cpp
)

target_include_directories(
    carambola_core
    PUBLIC
        ${CMAKE_CURRENT_SOURCE_DIR}/include
)

target_link_libraries(
    carambola_core
    PUBLIC
        Eigen3::Eigen
)

set_target_properties(
    carambola_core
    PROPERTIES
        POSITION_INDEPENDENT_CODE ON
)

pybind11_add_module(
    _carambola
    python/bindings.cpp
)

target_link_libraries(
    _carambola
    PRIVATE
        carambola_core
)

install(
    TARGETS _carambola
    LIBRARY DESTINATION carambola
    RUNTIME DESTINATION carambola
)

