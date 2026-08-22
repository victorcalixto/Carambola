# Carambola

Carambola is an open-source structural finite-element analysis toolkit
for computational design, with native integration planned for Python,
Blender and Sverchok.

## Status

Early development.

Current goal:

- native C++ FEM core
- Python bindings
- 3D truss analysis
- 3D frame analysis
- Sverchok integration

## Architecture

Carambola is separated into:

- **Carambola Core** — C++ FEM and structural analysis
- **Carambola Python** — Python interface via pybind11
- **Carambola Sverchok** — Blender/Sverchok integration
