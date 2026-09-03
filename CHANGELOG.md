# Changelog

All notable changes to Carambola are documented in this file.


## [0.1.2] - 2026-09-03

### Fixed

- Improved cross-platform C++ portability by replacing non-portable `M_PI` usage.
- Fixed Linux wheel builds by installing Eigen inside the manylinux build container.
- Added validated wheel builds for:
  - Linux x86_64
  - Windows x86_64
  - macOS x86_64
  - macOS arm64

### Changed

- Prepared Carambola for cross-platform PyPI distribution.



## [0.1.1] - 2026-09-03

### Fixed

- Declare SciPy as a runtime dependency for sparse matrix interoperability.
- Add CI validation for Python 3.10 through 3.14.



## [0.1.0] - 2026-09-03

### Added

- Initial public release of the Carambola finite element analysis kernel.
- 3D truss elements with axial deformation, strain, stress, and force recovery.
- 3D beam elements with six degrees of freedom per node.
- Beam axial, shear, bending, torsion, and end-force result recovery.
- Uniform distributed beam loads.
- Triangular shell elements combining membrane and plate-bending behaviour.
- Uniform shell pressure loading.
- Shell membrane strain and stress recovery.
- Shell bending curvature and bending moment recovery.
- Top and bottom surface stress recovery.
- Von Mises and principal stress utilities for shells.
- Linear static finite element solver.
- Global stiffness assembly, force-vector assembly, supports, and point loads.
- Structured rectangular shell mesh generation.
- Model lookup and connectivity utilities.
- JSON-based `.carambola` model serialization.
- JSON-based `.carambola-result` result serialization.
- Command-line interface with `solve` and `inspect` commands.
- Python bindings implemented with pybind11.
- CMake and scikit-build-core packaging.
- Example analyses for truss, beam, and shell models.
- FEM benchmark and regression test suite.
- Documentation for installation, serialization, validation, CLI workflows, and examples.

### Validation

Carambola 0.1.0 includes analytical and numerical validation covering:

- axial truss response,
- cantilever and simply supported beam response,
- distributed beam loading,
- beam torsion,
- axis-rotation invariance,
- shell constant-strain membrane behaviour,
- shell bending behaviour,
- mixed element models,
- global force and moment equilibrium,
- element insertion-order invariance.

The release contains 365 automated tests, including 27 benchmark tests.

### Platforms

The primary validated development platform for 0.1.0 is Linux.

The codebase is designed to support:

- Linux
- macOS
- Windows
- FreeBSD
- OpenBSD

The non-Linux platforms remain pending full build and test validation.

### Notes

Carambola 0.1.0 focuses on the standalone FEM kernel and Python interface.

Blender and Sverchok integration, topology optimisation, nonlinear analysis, modal analysis, buckling analysis, and other advanced FEM capabilities are planned for later releases.
