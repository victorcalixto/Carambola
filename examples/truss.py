"""Simple axial truss example for Carambola.

A 2 m steel bar is fixed at one end and subjected to a 10 kN
axial tensile load at the other.

Analytical solution:

    u = F L / (E A)

For:

    F = 10,000 N
    L = 2.0 m
    E = 210 GPa
    A = 0.01 m²

the expected displacement is approximately:

    9.52381e-6 m

and the axial force is:

    10,000 N
"""

import carambola


# ---------------------------------------------------------------------------
# Material and section
# ---------------------------------------------------------------------------

steel = carambola.Material(
    "Steel",
    210e9,   # Young's modulus [Pa]
    0.3,     # Poisson's ratio
    7850.0,  # density [kg/m³]
)

section = carambola.RectangularSection(
    0.1,  # width [m]
    0.1,  # height [m]
)


# ---------------------------------------------------------------------------
# Model
# ---------------------------------------------------------------------------

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

model.add_truss(
    n0,
    n1,
    steel,
    section,
)


# ---------------------------------------------------------------------------
# Boundary conditions
# ---------------------------------------------------------------------------

# Fix translations at the first node.
#
# Rotational degrees of freedom do not contribute stiffness for a Truss3D,
# so they are restrained here to prevent free rotational DOFs in the global
# system.
model.add_support(
    n0,
    True,
    True,
    True,
    True,
    True,
    True,
)

# Prevent rigid-body motion transverse to the truss while allowing
# axial displacement at the loaded end.
model.add_support(
    n1,
    False,
    True,
    True,
    True,
    True,
    True,
)


# ---------------------------------------------------------------------------
# Load
# ---------------------------------------------------------------------------

load = 10_000.0  # N

model.add_point_load(
    n1,
    load,
    0.0,
    0.0,
    0.0,
    0.0,
    0.0,
)


# ---------------------------------------------------------------------------
# Analysis
# ---------------------------------------------------------------------------

result = carambola.LinearStaticSolver(model).solve()


# ---------------------------------------------------------------------------
# Results
# ---------------------------------------------------------------------------

displacement = result.node_displacement(n1)
reaction = result.node_reaction(n0)

truss = model.truss(0)
axial_force = result.truss_force(truss)

print("Carambola — axial truss example")
print()

print("Loaded-node displacement:")
print(displacement)
print()

print("Support reaction:")
print(reaction)
print()


# ---------------------------------------------------------------------------
# Analytical comparison
# ---------------------------------------------------------------------------

length = 2.0
area = 0.1 * 0.1
youngs_modulus = 210e9

expected_displacement = (
    load * length
    / (youngs_modulus * area)
)

print("Analytical axial displacement:")
print(expected_displacement)
print()

print(
    "Absolute displacement error:",
    abs(displacement[0] - expected_displacement),
)


# ---------------------------------------------------------------------------
# Serialization
# ---------------------------------------------------------------------------

output_path = "examples/truss.carambola"

carambola.save_model(
    model,
    output_path,
)

print()
print(f"Model written to {output_path}")

deformation = result.truss_deformation(truss)
strain = result.truss_strain(truss)
stress = result.truss_stress(truss)
axial_force = result.truss_force(truss)

print("Truss deformation:")
print(deformation)
print()

print("Truss strain:")
print(strain)
print()

print("Truss stress:")
print(stress)
print()

print("Truss axial force:")
print(axial_force)
