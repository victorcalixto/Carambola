# Carambola FEM Validation

Carambola includes an automated verification and validation suite for its
finite element formulations, assembly procedures, linear static solver, and
result-recovery functions.

The purpose of this suite is not only to detect software regressions, but also
to compare the numerical behaviour of the implementation against analytical
solutions, fundamental mechanics relationships, equilibrium conditions, patch
tests, coordinate transformations, and mesh-convergence behaviour.

At the current v1 development baseline, the complete automated test suite
contains **256 passing tests**.

The dedicated FEM benchmark suite includes analytical and numerical benchmarks
for truss, beam, shell membrane, shell bending, and mixed-element models.

---

## 1. Scope

The current validation covers the linear-static finite element capabilities of
Carambola:

- 3D truss elements
- 3D beam elements
- triangular shell membrane behaviour
- triangular shell plate-bending behaviour
- combined membrane and bending shell behaviour
- nodal point loads
- beam distributed loads
- shell pressure loads
- translational and rotational supports
- global stiffness assembly
- linear static solution
- element result recovery
- nodal reaction recovery
- global force and moment equilibrium
- mixed-element models

The validation suite combines:

1. analytical benchmark solutions;
2. element-level formulation tests;
3. patch tests;
4. coordinate-invariance tests;
5. global equilibrium tests;
6. mesh-convergence studies;
7. mixed-element integration tests; and
8. API and regression tests.

---

## 2. Current Solver and Element Formulations

### Degrees of freedom

Carambola uses six degrees of freedom per node:

\[
[u_x,\;u_y,\;u_z,\;r_x,\;r_y,\;r_z]
\]

This common representation allows truss, beam, and shell elements to coexist
within the same global system.

### Linear static analysis

The current solver addresses the linear system

\[
K u = f
\]

subject to prescribed support conditions, where:

- \(K\) is the assembled global stiffness matrix;
- \(u\) is the global displacement vector; and
- \(f\) is the assembled global load vector.

The current v1 validation therefore concerns **small-displacement,
linear-elastic static analysis**.

---

## 3. Truss3D Validation

The `Truss3D` implementation is validated against classical axial-bar
solutions.

For a prismatic bar subjected to an axial force \(P\), the expected axial
displacement is

\[
\delta = \frac{PL}{EA}
\]

where:

- \(P\) is axial force;
- \(L\) is element length;
- \(E\) is Young's modulus; and
- \(A\) is cross-sectional area.

The corresponding strain and stress are

\[
\varepsilon = \frac{\delta}{L}
\]

and

\[
\sigma = E\varepsilon = \frac{P}{A}.
\]

### Verified behaviour

The automated benchmark suite verifies:

- single-bar axial displacement;
- axial force recovery;
- axial strain recovery;
- axial stress recovery;
- support reaction;
- tension and compression sign conventions;
- multi-element axial-bar behaviour; and
- coordinate-axis rotation invariance.

The multi-element benchmark verifies that subdividing an axial member into
multiple finite elements reproduces the same analytical structural response.

Coordinate-invariance testing verifies that equivalent structures do not
change their physical response simply because their orientation in the global
coordinate system changes.

---

## 4. Beam3D Validation

`Beam3D` includes axial, bending, shear-related nodal actions, and torsional
behaviour within a 12-DOF three-dimensional beam formulation.

Validation includes several classical structural mechanics problems.

### Cantilever with tip load

For a cantilever beam of length \(L\) subjected to a transverse point load
\(P\), the analytical tip displacement is

\[
\delta = \frac{PL^3}{3EI}.
\]

The tip rotation is

\[
\theta = \frac{PL^2}{2EI}.
\]

The fixed-end bending moment is

\[
M = PL.
\]

Carambola verifies the numerical displacement, rotation, reaction force, and
reaction moment against these relationships.

### Cantilever with uniformly distributed load

For a cantilever subjected to a uniformly distributed transverse load \(w\),

\[
\delta = \frac{wL^4}{8EI}.
\]

The fixed-end reaction and bending moment are also checked against their
analytical values.

### Simply supported beam

A simply supported beam subjected to a uniformly distributed load is included
as an additional benchmark, providing a structural configuration different
from the cantilever tests.

### Torsion

Pure beam torsion is tested independently to verify the torsional stiffness and
result-recovery implementation.

### Multi-element behaviour

A cantilever represented using multiple beam elements is compared with the
analytical solution to verify that assembly and element subdivision preserve
the expected structural response.

### Verified behaviour

The beam benchmark suite therefore covers:

- cantilever point loading;
- cantilever distributed loading;
- simply supported distributed loading;
- displacement;
- rotation;
- shear-force recovery;
- bending-moment recovery;
- axial-force recovery;
- torsional response;
- reaction forces;
- reaction moments;
- multi-element assembly; and
- coordinate-axis rotation invariance.

---

## 5. Shell3D Membrane Validation

The membrane component of `Shell3D` uses a three-node constant-strain triangle
(CST) formulation under plane-stress conditions.

The membrane strain vector is represented as

\[
\varepsilon =
\begin{bmatrix}
\varepsilon_x \\
\varepsilon_y \\
\gamma_{xy}
\end{bmatrix}.
\]

The corresponding plane-stress vector is

\[
\sigma =
\begin{bmatrix}
\sigma_x \\
\sigma_y \\
\tau_{xy}
\end{bmatrix}.
\]

Stress recovery follows

\[
\sigma = D\varepsilon
\]

where \(D\) is the plane-stress constitutive matrix.

### Constant-strain patch tests

The benchmark suite includes constant-strain states for:

- uniaxial strain in the local \(x\) direction;
- uniaxial strain in the local \(y\) direction; and
- pure in-plane shear.

These tests verify the membrane strain-displacement matrix and constitutive
response independently of a larger structural problem.

### Constitutive-law verification

Recovered membrane stresses are explicitly compared with

\[
D\varepsilon
\]

to verify consistency between strain recovery and the material constitutive
law.

### Coordinate invariance

A rotated shell benchmark verifies that membrane behaviour remains physically
consistent when the element is transformed in three-dimensional space.

Because shell stresses and strains are reported in the element's local
coordinate frame, local components may differ between differently oriented
elements even when they represent the same global physical strain state.

### Multi-element patch

A two-triangle patch is tested under a constant strain field.

This verifies that adjacent shell elements can reproduce a compatible
constant-strain state and provides an important test of shell connectivity,
coordinate transformations, and global assembly.

---

## 6. Shell3D Bending Validation

The plate-bending component of `Shell3D` uses a three-node
Discrete Kirchhoff Triangle (DKT) formulation.

The implementation follows the classical DKT formulation associated with the
three-node triangular plate-bending element.

The bending degrees of freedom are derived from the shell nodal quantities

\[
[w,\;r_x,\;r_y].
\]

The curvature vector is

\[
\kappa =
\begin{bmatrix}
\kappa_x \\
\kappa_y \\
\kappa_{xy}
\end{bmatrix}.
\]

Bending moments are recovered using

\[
M = D_b \kappa
\]

where \(D_b\) is the plate-bending constitutive matrix.

### Constant-curvature tests

The DKT implementation includes patch-style tests for:

- constant curvature about the local \(x\) direction;
- constant curvature about the local \(y\) direction; and
- constant twisting curvature.

These tests directly exercise the DKT strain-displacement formulation.

### Rigid-body behaviour

Rigid transverse translation is tested to verify that it does not generate
artificial bending curvature or bending energy.

### Stiffness properties

The shell bending stiffness is checked for:

- correct dimensions;
- symmetry;
- finite values; and
- positive-semidefinite behaviour within numerical tolerance.

### Drilling stabilization

The combined shell formulation includes a small drilling-rotation
stabilization term.

Tests verify that:

- drilling rotations receive stabilization stiffness;
- stabilization is applied to the intended degrees of freedom; and
- the stabilization does not introduce unintended cross-coupling.

---

## 7. Combined Shell Behaviour and Stress Recovery

`Shell3D` combines membrane and plate-bending behaviour within an 18-DOF
element representation.

The local nodal ordering is

\[
[u,\;v,\;w,\;r_x,\;r_y,\;r_z].
\]

The combined shell stiffness includes:

- membrane stiffness;
- DKT bending stiffness; and
- drilling-rotation stabilization.

### Through-thickness bending stress

Bending stress at a distance \(z\) from the shell midsurface is recovered from
the bending moment resultants.

For shell thickness \(t\),

\[
\sigma_b(z) = \frac{12z}{t^3}M.
\]

Consequently:

- bending stress is zero at the midsurface;
- top and bottom bending stresses have opposite signs in pure bending.

Both behaviours are explicitly tested.

### Combined surface stress

Carambola exposes top and bottom shell surface stresses obtained by combining
membrane and bending contributions.

The result API also provides:

- plane-stress von Mises stress;
- principal stresses; and
- principal-stress angle.

These result transformations are independently tested using known stress
states.

---

## 8. Shell Pressure Loading

Uniform pressure loading is supported for triangular shell elements.

Pressure acts along the shell local normal.

For a shell of area \(A\) subjected to uniform pressure \(p\), the total
equivalent nodal force must satisfy

\[
\sum F = pA.
\]

The validation suite verifies:

- equivalent load-vector dimensions;
- total applied force;
- pressure sign;
- shell-normal orientation;
- absence of artificial direct nodal moments;
- accumulation of multiple pressure loads; and
- global equilibrium after solution.

---

## 9. Clamped Square Plate Convergence

A multi-element clamped square plate under uniform pressure is used as the main
shell bending convergence benchmark.

Structured triangular meshes are generated at increasing resolutions,
including:

- \(2 \times 2\);
- \(4 \times 4\);
- \(8 \times 8\); and
- \(16 \times 16\) subdivisions.

The centre displacement is compared across successive mesh refinements.

The validation checks that:

- centre displacement is finite;
- displacement occurs in the expected direction;
- the solution converges with mesh refinement;
- the applied pressure resultant is correct;
- the model satisfies global equilibrium; and
- displacement scales linearly with pressure.

At the current benchmark configuration, the \(16 \times 16\) solution differs
from the analytical reference by approximately **0.8%**.

This convergence study provides a substantially stronger validation of shell
bending behaviour than a single-element stiffness test because it exercises
mesh generation, shell orientation, distributed loading, assembly, boundary
conditions, solution, and result extraction together.

---

## 10. Global Equilibrium and Mixed-Element Models

Element-level correctness does not guarantee correct system-level behaviour.

Carambola therefore includes global benchmarks testing the assembled model and
solver.

### Force equilibrium

Models are checked against

\[
\sum F_{\mathrm{applied}}
+
\sum F_{\mathrm{reaction}}
= 0.
\]

### Moment equilibrium

Reaction and applied moments are also checked to verify global moment
equilibrium.

### Mixed-element models

The benchmark suite contains models combining different finite element types,
including:

- truss and beam elements; and
- beam and shell elements.

These tests verify that different element formulations can coexist correctly
within the common six-DOF global system.

### Element insertion order

A benchmark verifies that changing the order in which elements are inserted
into a model does not change the resulting structural solution.

This provides an additional check against unintended dependence on internal
container ordering.

---

## 11. Verification Summary

| Area | Verification | Status |
|---|---|---:|
| Truss3D | Axial displacement | ✓ |
| Truss3D | Force, stress, and strain recovery | ✓ |
| Truss3D | Support reaction | ✓ |
| Truss3D | Multi-element analytical solution | ✓ |
| Truss3D | Coordinate invariance | ✓ |
| Beam3D | Cantilever point load | ✓ |
| Beam3D | Cantilever distributed load | ✓ |
| Beam3D | Simply supported distributed load | ✓ |
| Beam3D | Beam torsion | ✓ |
| Beam3D | Multi-element analytical behaviour | ✓ |
| Beam3D | Coordinate invariance | ✓ |
| Shell3D membrane | Constant-strain patch tests | ✓ |
| Shell3D membrane | Plane-stress constitutive law | ✓ |
| Shell3D membrane | Rotated-element invariance | ✓ |
| Shell3D membrane | Two-element patch | ✓ |
| Shell3D bending | Constant-curvature tests | ✓ |
| Shell3D bending | Twisting curvature | ✓ |
| Shell3D bending | Rigid-body translation | ✓ |
| Shell3D bending | Surface bending stresses | ✓ |
| Shell3D | Drilling stabilization | ✓ |
| Shell3D | Combined membrane/bending stress | ✓ |
| Shell3D | von Mises stress | ✓ |
| Shell3D | Principal stresses and angle | ✓ |
| Shell pressure | Resultant load | ✓ |
| Shell pressure | Orientation/sign | ✓ |
| Shell pressure | Global equilibrium | ✓ |
| Plate | Clamped square analytical comparison | ✓ |
| Plate | Mesh convergence | ✓ |
| Global system | Force equilibrium | ✓ |
| Global system | Moment equilibrium | ✓ |
| Global system | Mixed truss/beam model | ✓ |
| Global system | Mixed beam/shell model | ✓ |
| Global system | Element insertion-order independence | ✓ |

---

## 12. Automated Verification

The complete test suite can be executed with:

```bash
python -m pytest -v

The current v1 development baseline is:

```text
256 passed
```

The dedicated benchmark suite is located under:

```text
tests/benchmarks/
```

and can be executed independently with:

```bash
python -m pytest tests/benchmarks -v
```

The benchmark suite currently contains **27 dedicated FEM benchmark tests**.

Additional formulation, solver, load, result-recovery, mesh, API, and regression
tests are located throughout the main `tests/` directory.

---

## 13. Current Limitations

Passing the validation suite does not imply that Carambola supports every form
of structural analysis.

The current kernel is intentionally focused on linear-static analysis.

The present v1 scope does **not** include:

- geometric nonlinearity;
- large-displacement analysis;
- material nonlinearity;
- plasticity;
- contact;
- dynamic time-history analysis;
- modal analysis;
- eigenvalue buckling;
- second-order analysis;
- nonlinear shell behaviour; or
- nonlinear stability analysis.

These capabilities require additional formulations and their own independent
verification benchmarks.

The current validation should therefore be interpreted specifically as
verification of the implemented **linear-elastic, small-displacement FEM
kernel**.

---

## 14. Validation Philosophy

Carambola treats verification as part of the finite element implementation
rather than as a separate final-stage activity.

New element formulations and analysis capabilities should be accompanied by
tests at several levels whenever applicable:

1. **Formulation tests**  
   Verify matrices, transformations, interpolation functions, and basic
   mathematical properties.

2. **Element tests**  
   Verify rigid-body modes, constant strain or curvature states, and element
   result recovery.

3. **Analytical benchmarks**  
   Compare numerical results against established structural mechanics
   solutions.

4. **Mesh tests**  
   Verify convergence as the discretisation is refined.

5. **Global tests**  
   Verify equilibrium, assembly, boundary conditions, and interaction between
   element types.

6. **Regression tests**  
   Preserve validated behaviour as the implementation evolves.

Future finite element capabilities should follow the same approach before they
are considered part of the stable Carambola analysis kernel.
