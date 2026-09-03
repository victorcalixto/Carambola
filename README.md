# Carambola

**Carambola is an open-source finite element analysis toolkit for computational design.**

It provides a compact C++ FEM kernel with Python bindings for structural modelling, linear static analysis, result recovery, model serialization, and computational design workflows.

Carambola is being developed toward integration with **Blender** and **Sverchok**, providing an open structural-analysis environment that can be embedded directly into computational design workflows.

> **Status:** Carambola is under active development. Version 0.1.0 provides the first public release of the linear-static FEM kernel and Python interface.

---

## Features

### FEM kernel

Carambola currently supports:

- 3D truss elements
- 3D beam elements
- triangular shell elements
- 6 degrees of freedom per node
- linear elastic materials
- rectangular and circular sections
- shell properties
- nodal supports
- point forces and moments
- uniform beam loads
- uniform shell pressure
- sparse global stiffness assembly
- linear static analysis

### Result recovery

#### Truss3D

- deformation
- axial strain
- axial stress
- axial force

#### Beam3D

- axial force
- shear forces
- bending moments
- torsion
- element end forces

#### Shell3D

- membrane strain
- membrane stress
- bending curvature
- bending moments
- top and bottom surface stresses
- von Mises stress
- principal stresses
- principal stress angle

### Computational workflows

Carambola also provides:

- Python bindings through pybind11
- structured shell mesh generation
- model lookup and connectivity utilities
- JSON-based model serialization
- JSON-based result serialization
- command-line analysis
- command-line model and result inspection
- reusable model files
- reusable analysis-result files

---

## Architecture

Carambola separates the finite element kernel from higher-level computational design environments.

```text
                 Computational Design
                         │
            ┌────────────┴────────────┐
            │                         │
         Python                 Blender / Sverchok
            │                    planned integration
            │                         │
            └────────────┬────────────┘
                         │
                         ▼
                  Carambola Model
                         │
                         ▼
                  FEM Core (C++)
                         │
              ┌──────────┴──────────┐
              │                     │
              ▼                     ▼
          Assembly              Result Recovery
              │                     │
              └──────────┬──────────┘
                         │
                         ▼
                Linear Static Solver
                         │
                         ▼
                  AnalysisResult
```

The FEM kernel is implemented in C++, while pybind11 exposes the core model, solver, elements, loads, and result APIs to Python.

This architecture is intended to keep the numerical core independent from any particular modelling environment.

---

## Installation

Carambola currently builds from source using:

- C++
- CMake
- Eigen
- pybind11
- scikit-build-core

Python 3.10 or newer is required.

For development, clone the repository and create a virtual environment:

```bash
git clone https://github.com/victorcalixto/Carambola.git
cd Carambola

python -m venv .venv
source .venv/bin/activate
```

Install Carambola in editable mode:

```bash
python -m pip install -e .
```

If using `uv`:

```bash
uv pip install -e .
```

Verify the installation:

```bash
python - <<'PY'
import carambola

print(carambola.version())
PY
```

For Carambola 0.1.0 this should report:

```text
0.1.0
```

More detailed build and platform instructions are available in:

```text
docs/getting-started.md
```

---

## Quick Start

The following example creates a simple axial truss.

```python
import carambola as cb


model = cb.Model()

steel = cb.Material(
    "Steel",
    210e9,
    0.3,
    7850.0,
)

section = cb.RectangularSection(
    0.1,
    0.1,
)

n0 = model.add_node(
    0.0,
    0.0,
    0.0,
)

n1 = model.add_node(
    2.0,
    0.0,
    0.0,
)

truss = model.add_truss(
    n0,
    n1,
    steel,
    section,
)

model.add_support(
    n0,
    True,
    True,
    True,
    True,
    True,
    True,
)

model.add_support(
    n1,
    False,
    True,
    True,
    True,
    True,
    True,
)

model.add_point_load(
    n1,
    10000.0,
    0.0,
    0.0,
)

result = cb.LinearStaticSolver(
    model
).solve()

print(
    result.node_displacement(n1)
)

print(
    result.truss_force(truss)
)
```

For this model, the axial displacement is approximately:

```text
9.52380952e-06 m
```

and the truss axial force is:

```text
10000 N
```

---

## Elements

### Truss3D

`Truss3D` represents a two-node spatial axial element.

It supports:

- arbitrary 3D orientation
- linear elastic material behaviour
- axial stiffness
- axial deformation
- strain
- stress
- axial-force recovery

Example:

```python
truss = model.add_truss(
    node_a,
    node_b,
    material,
    section,
)
```

---

### Beam3D

`Beam3D` is a spatial beam element with six degrees of freedom per node:

```text
UX
UY
UZ
RX
RY
RZ
```

It supports:

- axial deformation
- bending about both local axes
- torsion
- local-axis orientation
- point loading through the global model
- uniform distributed loading
- beam-force and moment recovery

Example:

```python
beam = model.add_beam(
    node_a,
    node_b,
    material,
    section,
    [0.0, 0.0, 1.0],
)
```

The orientation vector establishes the beam's local coordinate system.

---

### Shell3D

`Shell3D` is a three-node triangular shell element combining:

- constant-strain triangular membrane behaviour
- triangular plate-bending behaviour

A shell property associates the element with a material and thickness:

```python
shell_property = cb.ShellProperty(
    material,
    0.01,
)
```

A shell can then be created with:

```python
shell = model.add_shell(
    node_a,
    node_b,
    node_c,
    shell_property,
)
```

Shell result recovery includes membrane, bending, and surface stress quantities.

---

## Loads and Supports

### Supports

Supports constrain translational and rotational degrees of freedom.

```python
model.add_support(
    node,
    True,
    True,
    True,
    True,
    True,
    True,
)
```

The six Boolean values correspond to:

```text
UX UY UZ RX RY RZ
```

---

### Point Loads

Point loads support forces and moments.

```python
model.add_point_load(
    node,
    fx,
    fy,
    fz,
    mx,
    my,
    mz,
)
```

Moment components may be omitted when not required.

---

### Uniform Beam Loads

Uniform distributed loads can be applied to beam elements.

```python
model.add_uniform_beam_load(
    beam,
    qx,
    qy,
    qz,
)
```

---

### Uniform Shell Pressure

Uniform pressure can be applied to shell elements.

```python
model.add_uniform_shell_pressure(
    shell,
    pressure,
)
```

---

## Shell Meshes

Carambola provides a structured rectangular shell mesh generator.

```python
mesh = cb.rectangular_shell_mesh(
    1.0,
    1.0,
    16,
    16,
)
```

The mesh can be inserted into a model with a shell property:

```python
model.add_shell_mesh(
    mesh,
    shell_property,
)
```

This is useful for plate and surface analysis and provides a foundation for future integration with computational geometry systems.

---

## Solving

Linear static analysis is performed using:

```python
result = cb.LinearStaticSolver(
    model
).solve()
```

Nodal translations can be obtained with:

```python
result.node_displacement(node)
```

Nodal rotations:

```python
result.node_rotation(node)
```

Support reactions:

```python
result.node_reaction(node)
```

and reaction moments:

```python
result.node_moment_reaction(node)
```

Element-level result recovery is available through the same `AnalysisResult`.

---

## Serialization

Carambola provides a JSON-based model format using the extension:

```text
.carambola
```

Save a model:

```python
cb.save_model(
    model,
    "model.carambola",
)
```

Load it again:

```python
model = cb.load_model(
    "model.carambola"
)
```

The format can be inspected directly because it is JSON-based.

The complete specification is documented in:

```text
docs/model-format.md
```

---

## Result Serialization

Analysis results can be stored using:

```text
.carambola-result
```

For example:

```python
cb.save_result(
    result,
    "analysis.carambola-result",
    model,
)
```

Load the stored result with:

```python
stored_result = cb.load_result(
    "analysis.carambola-result",
    model,
)
```

Stored results contain the primary nodal solution, including:

- translations
- rotations
- reaction forces
- reaction moments

The result format is documented in:

```text
docs/result-format.md
```

---

## Command-Line Interface

Installing Carambola provides the `carambola` command.

Inspect a model:

```bash
carambola inspect model.carambola
```

Solve a model:

```bash
carambola solve model.carambola
```

Specify an output result:

```bash
carambola solve \
    model.carambola \
    -o analysis.carambola-result
```

Inspect a result:

```bash
carambola inspect \
    analysis.carambola-result
```

More information is available in:

```text
docs/cli-and-serialization.md
```

---

## Examples

Canonical examples are provided in:

```text
examples/
├── truss.py
├── cantilever_beam.py
└── shell_plate.py
```

Run the truss example:

```bash
python examples/truss.py
```

Run the cantilever beam example:

```bash
python examples/cantilever_beam.py
```

Run the shell plate example:

```bash
python examples/shell_plate.py
```

The examples demonstrate both FEM analysis and analytical comparisons.

---

## Validation

Carambola is developed using analytical benchmarks and automated regression tests.

The current test suite contains:

```text
365 automated tests
27 dedicated FEM benchmark tests
```

Benchmark coverage includes:

### Truss

- single-bar axial displacement
- axial force
- stress and strain
- support reactions
- multi-element axial response
- axis-rotation invariance

### Beam

- cantilever tip loading
- cantilever distributed loading
- simply supported distributed loading
- pure torsion
- local-axis rotation invariance
- multi-element cantilever behaviour

### Shell membrane

- constant strain in X
- constant strain in Y
- pure shear
- plane-stress constitutive response
- rotated-element invariance
- two-triangle patch behaviour

### Shell bending

- bending moment recovery
- top/bottom stress symmetry
- surface stress recovery
- von Mises stress recovery

### Global behaviour

- force equilibrium
- moment equilibrium
- mixed truss/beam models
- mixed beam/shell models
- element insertion-order invariance

Run the complete test suite with:

```bash
python -m pytest
```

Run only the FEM benchmark suite with:

```bash
python -m pytest tests/benchmarks -v
```

Additional validation information is available in:

```text
docs/validation.md
```

---

## Project Structure

The repository is organised around a small native FEM kernel and its Python interface.

```text
Carambola/
├── carambola/
│   ├── __init__.py
│   ├── __main__.py
│   ├── cli.py
│   ├── serialization.py
│   └── result_serialization.py
│
├── include/
│   └── carambola/
│
├── src/
│
├── python/
│   └── bindings.cpp
│
├── tests/
│   └── benchmarks/
│
├── examples/
│   ├── truss.py
│   ├── cantilever_beam.py
│   └── shell_plate.py
│
├── docs/
│   ├── getting-started.md
│   ├── cli-and-serialization.md
│   ├── model-format.md
│   ├── result-format.md
│   └── validation.md
│
├── CMakeLists.txt
├── pyproject.toml
├── CHANGELOG.md
├── LICENSE
└── README.md
```

---

## Platform Support

The primary validated development platform for Carambola 0.1.0 is **Linux**.

The architecture is intended to remain portable across:

| Platform | Status |
|---|---|
| Linux | Validated |
| Windows | Planned validation |
| macOS | Planned validation |
| FreeBSD | Planned validation |
| OpenBSD | Planned validation |

FreeBSD and OpenBSD support should currently be considered experimental until complete build and test validation has been performed on those systems.

Binary Python wheels are platform-specific. Platforms for which pre-built wheels are not provided can build Carambola from source.

---

## Roadmap

Carambola 0.1.0 establishes the first standalone FEM kernel.

The next major development areas include:

### Blender and Sverchok

- Blender integration
- Sverchok FEM nodes
- geometry-to-FEM workflows
- result visualisation
- interactive computational design workflows

### Structural optimisation

- BESO topology optimisation
- design-variable infrastructure
- optimisation/result feedback loops
- integration with computational design geometry

### FEM development

Longer-term FEM capabilities may include:

- modal analysis
- buckling analysis
- nonlinear analysis
- additional element formulations
- additional material models
- richer load cases
- analysis combinations

### Portability

- Windows build validation
- macOS build validation
- FreeBSD build validation
- OpenBSD build validation
- expanded CI coverage

---

## Design Philosophy

Carambola is intended to be more than a structural-analysis library.

The project explores how structural computation can become part of an open computational-design environment rather than remain isolated inside proprietary analysis applications.

Several principles guide its development.

### Open source

The complete FEM kernel and computational-design interface should be inspectable, modifiable, and distributable.

### Small core

The numerical kernel should remain relatively compact and independent from large modelling environments.

### Interoperability

Models and results should be exchangeable through transparent formats and accessible from different computational systems.

### Computational design

Structural analysis should be usable as part of generative, parametric, optimisation, and design-exploration workflows.

### Toolmaking

Carambola treats software development itself as a design and research activity.

The long-term objective is therefore not only to reproduce conventional structural-analysis functionality, but to create an open foundation for experimenting with new relationships between geometry, structural behaviour, optimisation, and computational design.

---

## Development

For a development installation:

```bash
git clone https://github.com/victorcalixto/Carambola.git
cd Carambola

python -m venv .venv
source .venv/bin/activate

python -m pip install -e .
```

Run the test suite:

```bash
python -m pytest
```

Build distribution packages:

```bash
python -m build
```

Validate package metadata:

```bash
python -m twine check dist/*
```

---

## License

Carambola is free and open-source software distributed under the **GNU General Public License v3.0 or later (GPL-3.0-or-later)**.

See:

```text
LICENSE
```

for the complete license text.

---

## Author

**Victor Calixto**

Architect, urban designer, researcher, educator, and computational designer.

Carambola is developed as part of an ongoing exploration of open-source computational design, structural analysis, digital toolmaking, and interoperable design systems.
