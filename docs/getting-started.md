# Getting Started with Carambola

This guide covers installing Carambola, verifying the installation, and running a first structural analysis.

Carambola combines a native C++ finite element kernel with a Python interface. The current implementation supports linear-static analysis using 3D truss, beam, and triangular shell elements.

> **Status:** Carambola is under active development and has not yet reached its first stable release.

---

## Platforms

Carambola is designed to be portable across desktop and Unix-like operating systems.

Target platforms include:

- Linux
- macOS
- Windows
- FreeBSD
- OpenBSD

Carambola contains a native C++ extension, so binary wheels are specific to a Python version, ABI, operating system, and architecture.

On platforms for which a pre-built wheel is not available, Carambola can be compiled from source.

### Current platform status

Linux is currently used for primary development and validation.

FreeBSD and OpenBSD are intended targets because the Carambola core relies on portable technologies including:

- standard C++
- CMake
- Eigen
- pybind11
- Python
- scikit-build-core

FreeBSD and OpenBSD support should currently be considered **experimental** until the complete Carambola build and validation suite has been tested on those platforms.

The long-term goal is to validate Carambola across:

```text
Linux      ✓
Windows    planned validation
macOS      planned validation
FreeBSD    planned validation
OpenBSD    planned validation
```

Platform support will be updated as automated and manual testing is introduced.

---

## Requirements

Carambola requires:

- Python 3.10 or newer
- a modern C++ compiler
- CMake
- Eigen
- Python development headers

The Python package automatically installs its Python runtime dependencies, including NumPy.

The native extension is built using:

- C++
- Eigen
- pybind11
- CMake
- scikit-build-core

Ninja is recommended as the build system when available.

---

# Installing from a Wheel

When a compatible Carambola wheel is available, install it with:

```bash
pip install carambola
```

A wheel contains the compiled Carambola C++ extension, so a compiler, CMake, and Eigen are generally not required when installing a compatible pre-built wheel.

Carambola currently uses platform- and Python-specific wheels because the package contains a native extension.

For example:

```text
carambola-0.1.0-cp313-cp313-linux_x86_64.whl
```

identifies a wheel built for CPython 3.13 on 64-bit Linux.

A Linux wheel cannot be used directly on FreeBSD, OpenBSD, Windows, or macOS.

If no compatible wheel exists for your platform, build Carambola from source.

---

# Installing from Source

Clone the repository:

```bash
git clone https://github.com/victorcalixto/Carambola.git
cd Carambola
```

Create a virtual environment:

```bash
python3 -m venv .venv
```

Activate it on Linux, macOS, FreeBSD, or OpenBSD:

```bash
source .venv/bin/activate
```

On Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Then install Carambola:

```bash
pip install .
```

This invokes the Carambola build system, compiles the native C++ extension, and installs the Python package.

---

# Linux

Install the required development tools using your operating system's package manager.

The exact package names depend on the Linux distribution.

The required components are:

```text
Python >= 3.10
Python development headers
C++ compiler
CMake
Eigen
Ninja (recommended)
```

After installing the system dependencies:

```bash
git clone https://github.com/victorcalixto/Carambola.git
cd Carambola

python3 -m venv .venv
source .venv/bin/activate

pip install .
```

For development:

```bash
pip install -e .
```

---

# macOS

Carambola is designed to compile with the Apple Clang toolchain.

The required components are:

```text
Python >= 3.10
CMake
Eigen
C++ compiler
```

A typical development environment can use Homebrew for the required packages.

After installing the dependencies:

```bash
git clone https://github.com/victorcalixto/Carambola.git
cd Carambola

python3 -m venv .venv
source .venv/bin/activate

pip install .
```

macOS support should be considered under validation until included in the project's regular build and test infrastructure.

---

# Windows

Carambola is designed to compile using a modern Windows C++ toolchain.

The required components include:

```text
Python >= 3.10
CMake
Eigen
C++ compiler
```

Microsoft Visual C++ is the expected primary compiler environment.

Create and activate a virtual environment:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

Then install:

```powershell
pip install .
```

Windows support should be considered under validation until included in the project's regular build and test infrastructure.

---

# FreeBSD

FreeBSD is a target platform for Carambola.

Carambola's C++/CMake architecture is intended to allow the native FEM kernel and Python bindings to compile using the FreeBSD LLVM/Clang toolchain.

Install the required system components using FreeBSD's package manager.

Typical requirements include:

```text
Python
CMake
Ninja
Eigen
```

The exact package names may depend on the FreeBSD release and available Python version.

After installing the required packages:

```bash
git clone https://github.com/victorcalixto/Carambola.git
cd Carambola

python3 -m venv .venv
source .venv/bin/activate

pip install .
```

For development:

```bash
pip install -e .
```

Then run:

```bash
python -m pytest
```

FreeBSD support is currently considered **experimental** until the complete build and validation suite has been executed successfully on a clean FreeBSD environment.

---

# OpenBSD

OpenBSD is also a target platform for Carambola.

The core FEM implementation is written in portable C++, and the Python extension uses pybind11 and CMake.

Required components include:

```text
Python
CMake
Ninja
Eigen
C++ compiler
```

Install the corresponding packages using OpenBSD's package system.

Exact package names may vary between OpenBSD releases and should be checked against the package repository for the version being used.

After installing the dependencies:

```bash
git clone https://github.com/victorcalixto/Carambola.git
cd Carambola

python3 -m venv .venv
source .venv/bin/activate

pip install .
```

Then run:

```bash
python -m pytest
```

OpenBSD support is currently considered **experimental** until the complete Carambola build and validation suite has been executed successfully on a clean OpenBSD environment.

---

# Development Installation

For development, use an editable installation.

Clone the repository and create a virtual environment as described above, then run:

```bash
pip install -e .
```

Changes to the Python source become available directly from the working tree.

Changes to the native C++ code may require rebuilding the editable installation:

```bash
pip install -e .
```

If you use `uv`, the equivalent command is:

```bash
uv pip install -e .
```

---

# Verify the Installation

Check that Carambola can be imported:

```bash
python -c "import carambola; print(carambola.__file__)"
```

Check that the native extension loads:

```bash
python -c "import carambola._carambola; print(carambola._carambola.__file__)"
```

Check the command-line interface:

```bash
carambola --help
```

You should see:

```text
usage: carambola [-h] {solve,inspect} ...

Carambola finite element analysis
```

with the commands:

```text
solve
inspect
```

---

# First Analysis

The following example creates a two-metre cantilever beam with a vertical point load at its free end.

## 1. Import Carambola

```python
import carambola
```

---

## 2. Define a Material

Create a steel material:

```python
steel = carambola.Material(
    "Steel",
    210e9,
    0.3,
    7850,
)
```

The parameters are:

```text
name
Young's modulus
Poisson's ratio
density
```

Carambola does not impose a unit system.

All values must therefore use a consistent system of units.

In this example:

- length is in metres
- force is in newtons
- stress is in pascals
- density is in kg/m³

---

## 3. Define a Section

Create a rectangular beam section:

```python
section = carambola.RectangularSection(
    0.1,
    0.2,
)
```

This creates a section with dimensions:

```text
0.1 m × 0.2 m
```

---

## 4. Create the Model

```python
model = carambola.Model()
```

Add two nodes:

```python
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
```

The beam extends two metres along the global X axis.

---

## 5. Add the Beam

```python
model.add_beam(
    n0,
    n1,
    steel,
    section,
    [0.0, 0.0, 1.0],
)
```

The final vector defines the beam orientation used to establish its local coordinate system.

---

## 6. Add the Support

Fix the first node:

```python
model.add_support(
    n0,
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
UX
UY
UZ
RX
RY
RZ
```

where:

- `UX`, `UY`, `UZ` are translations
- `RX`, `RY`, `RZ` are rotations

All six degrees of freedom are restrained at the cantilever support.

---

## 7. Apply a Load

Apply a 1000 N downward force to the free node:

```python
model.add_point_load(
    n1,
    0.0,
    0.0,
    -1000.0,
    0.0,
    0.0,
    0.0,
)
```

The six load components are:

```text
FX
FY
FZ
MX
MY
MZ
```

The load in this example is:

```text
FZ = -1000 N
```

---

## 8. Solve the Model

```python
solver = carambola.LinearStaticSolver(model)

result = solver.solve()
```

---

## 9. Read the Results

Read the displacement at the free node:

```python
displacement = result.node_displacement(n1)

print(displacement)
```

The result is approximately:

```text
[ 0.          0.         -0.00076190 ]
```

The vertical displacement is approximately:

```text
-0.762 mm
```

Read the rotation:

```python
rotation = result.node_rotation(n1)

print(rotation)
```

which gives approximately:

```text
[ 0.          0.00057143  0.        ]
```

---

# Complete Example

```python
import carambola


steel = carambola.Material(
    "Steel",
    210e9,
    0.3,
    7850,
)

section = carambola.RectangularSection(
    0.1,
    0.2,
)

model = carambola.Model()

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

model.add_beam(
    n0,
    n1,
    steel,
    section,
    [0.0, 0.0, 1.0],
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

model.add_point_load(
    n1,
    0.0,
    0.0,
    -1000.0,
    0.0,
    0.0,
    0.0,
)

result = carambola.LinearStaticSolver(model).solve()

print(
    "displacement:",
    result.node_displacement(n1),
)

print(
    "rotation:",
    result.node_rotation(n1),
)
```

Expected output:

```text
displacement: [ 0.          0.         -0.0007619 ]
rotation: [0.         0.00057143 0.        ]
```

---

# Saving a Model

Carambola models can be serialized to the `.carambola` format.

```python
carambola.save_model(
    model,
    "cantilever.carambola",
)
```

The resulting file is JSON-based and can be inspected with a text editor.

Load the model again with:

```python
model = carambola.load_model(
    "cantilever.carambola",
)
```

---

# Using the Command-Line Interface

Inspect the saved model:

```bash
carambola inspect cantilever.carambola
```

Solve it:

```bash
carambola solve cantilever.carambola
```

Carambola writes:

```text
cantilever.carambola-result
```

Inspect the results:

```bash
carambola inspect cantilever.carambola-result
```

---

# Saving Results from Python

Results can also be serialized directly from Python:

```python
carambola.save_result(
    result,
    "cantilever.carambola-result",
    model,
)
```

Load a stored result:

```python
stored_result = carambola.load_result(
    "cantilever.carambola-result",
    model,
)
```

Stored results contain the primary linear-static solution:

- nodal translations
- nodal rotations
- reaction forces
- reaction moments

Element-level result recovery is currently performed from the live analysis result.

---

# Running the Test Suite

For development:

```bash
python -m pytest
```

The test suite contains:

- unit tests
- integration tests
- serialization tests
- CLI tests
- FEM validation benchmarks

Numerical validation is documented in:

- [`validation.md`](validation.md)

---

# Building Distribution Packages

Install the Python build frontend:

```bash
pip install build
```

Build the wheel and source distribution:

```bash
python -m build
```

Artifacts are written to:

```text
dist/
```

A typical build produces:

```text
carambola-<version>.tar.gz
carambola-<version>-<python>-<platform>.whl
```

Because Carambola contains a native extension, binary wheels are platform-specific.

The source distribution can be used to build Carambola on platforms for which a pre-built wheel is unavailable.

---

# Next Steps

Once the first beam analysis is working, see the examples directory for models demonstrating:

- truss analysis
- beam analysis
- shell analysis

Technical file-format documentation:

- [`model-format.md`](model-format.md)
- [`result-format.md`](result-format.md)

Numerical validation:

- [`validation.md`](validation.md)
