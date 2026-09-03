# Carambola Result Format

## Overview

Carambola analysis results are stored in a JSON-based format using the
`.carambola-result` file extension.

The result format stores the primary output of a completed analysis while
keeping the structural model separate.

A result document therefore does not duplicate geometry, materials,
sections, elements, supports, or loads from the corresponding `.carambola`
model file.

The initial format is designed for the Carambola linear static solver.

---

## Design principles

The result format follows several principles:

1. The structural model and analysis results are separate.
2. Only primary solver results are persisted.
3. Derived element results are calculated when required.
4. Node and element references use model-local integer IDs.
5. The file format is explicitly versioned.
6. Result dimensions are validated when loading.
7. The format remains independent of Blender and Sverchok.

---

## File extension

Carambola result files use:

```text
.carambola-result
```

Example:

```text
cantilever.carambola
cantilever.carambola-result
```

---

## Top-level structure

A version 1 result document has the following structure:

```json
{
  "format": "carambola-result",
  "version": 1,
  "analysis": {
    "type": "linear_static"
  },
  "model": {
    "node_count": 0,
    "truss_count": 0,
    "beam_count": 0,
    "shell_count": 0
  },
  "displacements": [],
  "reactions": []
}
```

---

## Format identifier

The `format` field must contain:

```json
"format": "carambola-result"
```

This allows result files to be distinguished from Carambola model files.

---

## Version

The initial result format version is:

```json
"version": 1
```

Future changes to the serialized structure may introduce additional format
versions.

---

## Analysis

The `analysis` object identifies the analysis that produced the result.

For version 1:

```json
{
  "analysis": {
    "type": "linear_static"
  }
}
```

The only supported analysis type in result format version 1 is:

```text
linear_static
```

Future versions may support analysis types such as:

- modal
- buckling
- nonlinear static
- transient
- optimisation

These are outside the scope of result format version 1.

---

## Model compatibility information

The result file stores basic information about the model used for the
analysis:

```json
{
  "model": {
    "node_count": 4,
    "truss_count": 1,
    "beam_count": 1,
    "shell_count": 1
  }
}
```

These values do not reconstruct the model.

They are used to detect obvious incompatibility between a result and a
different model.

The model itself remains stored separately in a `.carambola` file.

---

## Displacements

The `displacements` array contains one entry for each model node.

Each node stores the six global degrees of freedom:

```json
{
  "node": 0,
  "ux": 0.0,
  "uy": 0.0,
  "uz": 0.0,
  "rx": 0.0,
  "ry": 0.0,
  "rz": 0.0
}
```

The complete array may therefore look like:

```json
{
  "displacements": [
    {
      "node": 0,
      "ux": 0.0,
      "uy": 0.0,
      "uz": 0.0,
      "rx": 0.0,
      "ry": 0.0,
      "rz": 0.0
    },
    {
      "node": 1,
      "ux": 0.000001,
      "uy": 0.0,
      "uz": -0.0025,
      "rx": 0.0,
      "ry": 0.0012,
      "rz": 0.0
    }
  ]
}
```

All displacement and rotation components use the global coordinate system.

The node IDs must correspond to the model node IDs.

---

## Reactions

The `reactions` array contains nodal reaction forces and moments.

Each entry uses:

```json
{
  "node": 0,
  "fx": 0.0,
  "fy": 0.0,
  "fz": 1000.0,
  "mx": 0.0,
  "my": 2000.0,
  "mz": 0.0
}
```

The complete structure is:

```json
{
  "reactions": [
    {
      "node": 0,
      "fx": 0.0,
      "fy": 0.0,
      "fz": 1000.0,
      "mx": 0.0,
      "my": 2000.0,
      "mz": 0.0
    }
  ]
}
```

Reaction quantities use the global coordinate system.

Version 1 may serialize reactions for every node, including zero-valued
reactions. This produces a deterministic result representation and avoids
special handling of supported and unsupported nodes.

---

## Degrees of freedom

Carambola uses six global degrees of freedom per node:

```text
UX
UY
UZ
RX
RY
RZ
```

The serialized result representation mirrors this six-degree-of-freedom
architecture.

For displacement data:

```text
ux, uy, uz
```

represent translations, while:

```text
rx, ry, rz
```

represent rotations.

For reaction data:

```text
fx, fy, fz
```

represent reaction forces, while:

```text
mx, my, mz
```

represent reaction moments.

---

## Derived results

Derived results are intentionally not required in result format version 1.

Examples include:

### Truss results

- axial force
- axial stress

### Beam results

- axial force
- torsion
- shear forces
- bending moments
- local end forces

### Shell results

- membrane strain
- membrane stress
- bending curvature
- bending moments
- top and bottom surface stress
- von Mises stress
- principal stresses
- principal stress angle

These quantities can be recovered from:

1. the structural model, and
2. the stored displacement vector.

Avoiding duplication reduces file size and prevents inconsistencies between
stored displacement data and separately stored derived results.

---

## Complete example

```json
{
  "format": "carambola-result",
  "version": 1,
  "analysis": {
    "type": "linear_static"
  },
  "model": {
    "node_count": 2,
    "truss_count": 0,
    "beam_count": 1,
    "shell_count": 0
  },
  "displacements": [
    {
      "node": 0,
      "ux": 0.0,
      "uy": 0.0,
      "uz": 0.0,
      "rx": 0.0,
      "ry": 0.0,
      "rz": 0.0
    },
    {
      "node": 1,
      "ux": 0.0,
      "uy": 0.0,
      "uz": -0.001587301587,
      "rx": 0.0,
      "ry": 0.001190476190,
      "rz": 0.0
    }
  ],
  "reactions": [
    {
      "node": 0,
      "fx": 0.0,
      "fy": 0.0,
      "fz": 1000.0,
      "mx": 0.0,
      "my": 2000.0,
      "mz": 0.0
    },
    {
      "node": 1,
      "fx": 0.0,
      "fy": 0.0,
      "fz": 0.0,
      "mx": 0.0,
      "my": 0.0,
      "mz": 0.0
    }
  ]
}
```

---

## Model/result relationship

A `.carambola-result` file is meaningful only in relation to the model that
produced it.

Version 1 performs structural compatibility checks using model counts.

For example:

```text
node_count
truss_count
beam_count
shell_count
```

A future format may introduce a model fingerprint or hash for stronger model
identity verification.

A cryptographic model fingerprint is deliberately not required for version 1.

---

## Numerical values

All numerical result values are serialized as JSON numbers.

Carambola does not round numerical values before serialization.

The serializer should preserve normal Python floating-point precision.

---

## Coordinate system

All nodal displacement and reaction values stored in version 1 are expressed
in the global coordinate system.

Element-local quantities are derived after loading rather than persisted in
the result document.

---

## Validation

A version 1 result loader should reject documents with:

- an incorrect `format` value
- an unsupported version
- an unsupported analysis type
- missing required top-level fields
- malformed `analysis` or `model` objects
- malformed displacement entries
- malformed reaction entries
- duplicate node IDs
- missing node IDs
- node IDs outside the model range
- displacement counts inconsistent with the model
- reaction counts inconsistent with the model
- invalid numerical values
- result/model count mismatches when compatibility checking is requested

---

## Scope of version 1

Result format version 1 supports:

- linear static analysis
- six degrees of freedom per node
- nodal translations
- nodal rotations
- nodal reaction forces
- nodal reaction moments
- basic model compatibility metadata

It does not currently persist:

- element-derived forces
- element stresses
- shell recovery fields
- modal results
- eigenvalues
- buckling factors
- nonlinear history
- load-step history
- optimisation history
- BESO results
- Blender or Sverchok metadata

These may be introduced independently in future versions.

---

## Stability

The version 1 serializer should produce deterministic output.

A canonical result generated by Carambola should satisfy:

```text
AnalysisResult
    ↓
dictionary
    ↓
serialized file
    ↓
loaded result
    ↓
dictionary
```

with equivalent numerical and structural content.
