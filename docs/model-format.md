# Carambola Model Format

Carambola model files use the `.carambola` extension.

The v1 format is JSON-based and stores the information required to reconstruct
a linear-static Carambola model.

The format is intentionally explicit and human-readable so that models can be
created, inspected, versioned, generated, and transformed outside Carambola.

---

## 1. Format Version

Every model file must contain a format version.

```json
{
  "format": "carambola",
  "version": 1
}
```

The `format` field identifies the file as a Carambola model.

The `version` field identifies the schema version.

Readers must reject unsupported future versions rather than silently attempting
to interpret them.

---

## 2. Top-Level Structure

A v1 `.carambola` model has the following top-level structure:

```json
{
  "format": "carambola",
  "version": 1,

  "materials": [],
  "sections": [],
  "shell_properties": [],

  "nodes": [],

  "trusses": [],
  "beams": [],
  "shells": [],

  "supports": [],

  "point_loads": [],
  "uniform_beam_loads": [],
  "uniform_shell_pressures": []
}
```

Collections may be empty, but the serializer should write all supported
top-level collections for consistency.

---

## 3. IDs and References

Objects that may be referenced by other objects use explicit integer IDs.

IDs are local to each collection.

For example:

```json
{
  "materials": [
    {
      "id": 0,
      "name": "Steel",
      "E": 210000000000.0,
      "nu": 0.3,
      "density": 7850.0
    }
  ]
}
```

An element may then reference that material using:

```json
{
  "material": 0
}
```

Node references follow the same convention.

IDs should be:

- non-negative integers;
- unique within their collection;
- stable within a serialized model.

---

## 4. Materials

Materials store isotropic linear-elastic properties.

```json
{
  "id": 0,
  "name": "Steel",
  "E": 210000000000.0,
  "nu": 0.3,
  "density": 7850.0
}
```

Fields:

- `id`: material identifier;
- `name`: material name;
- `E`: Young's modulus;
- `nu`: Poisson's ratio;
- `density`: mass density.

Shear modulus `G` does not need to be serialized independently if it is derived
from `E` and `nu`.

---

## 5. Sections

Sections use a type-discriminated representation.

### Rectangular section

```json
{
  "id": 0,
  "type": "rectangular",
  "width": 0.2,
  "height": 0.4
}
```

### Circular section

```json
{
  "id": 1,
  "type": "circular",
  "radius": 0.1
}
```

The v1 format supports:

- `rectangular`;
- `circular`.

Derived section properties such as area and second moments of area are not
serialized because they can be reconstructed from the defining geometry.

---

## 6. Shell Properties

Shell properties reference a material and define shell thickness.

```json
{
  "id": 0,
  "material": 0,
  "thickness": 0.02
}
```

Fields:

- `id`: shell-property identifier;
- `material`: referenced material ID;
- `thickness`: shell thickness.

---

## 7. Nodes

Nodes are represented explicitly by ID and coordinates.

```json
{
  "id": 0,
  "x": 0.0,
  "y": 0.0,
  "z": 0.0
}
```

Coordinates are stored in model units.

Carambola v1 does not impose a specific physical unit system. A model must use
a consistent unit system throughout.

---

## 8. Truss Elements

A truss references two nodes, one material, and one section.

```json
{
  "id": 0,
  "node_start": 0,
  "node_end": 1,
  "material": 0,
  "section": 0
}
```

Fields:

- `id`: truss identifier;
- `node_start`: first node ID;
- `node_end`: second node ID;
- `material`: material ID;
- `section`: section ID.

---

## 9. Beam Elements

A beam references two nodes, one material, one section, and an orientation
vector.

```json
{
  "id": 0,
  "node_start": 0,
  "node_end": 1,
  "material": 0,
  "section": 0,
  "orientation": [0.0, 0.0, 1.0]
}
```

The orientation vector is required so that the beam local coordinate system can
be reconstructed deterministically.

Fields:

- `id`: beam identifier;
- `node_start`: first node ID;
- `node_end`: second node ID;
- `material`: material ID;
- `section`: section ID;
- `orientation`: three-component orientation vector.

---

## 10. Shell Elements

A triangular shell references three nodes and one shell property.

```json
{
  "id": 0,
  "nodes": [0, 1, 2],
  "property": 0
}
```

The node order is significant because it determines the shell orientation and
local normal.

---

## 11. Supports

Supports reference a node and store six Boolean restraint states.

```json
{
  "node": 0,
  "ux": true,
  "uy": true,
  "uz": true,
  "rx": false,
  "ry": false,
  "rz": false
}
```

Fields correspond to the six global nodal degrees of freedom:

```text
UX UY UZ RX RY RZ
```

---

## 12. Point Loads

Point loads reference a node and contain forces and moments.

```json
{
  "node": 1,
  "fx": 0.0,
  "fy": 0.0,
  "fz": -1000.0,
  "mx": 0.0,
  "my": 0.0,
  "mz": 0.0
}
```

Fields:

- `fx`, `fy`, `fz`: global force components;
- `mx`, `my`, `mz`: global moment components.

---

## 13. Uniform Beam Loads

Uniform beam loads reference a beam.

```json
{
  "beam": 0,
  "qx": 0.0,
  "qy": -1000.0,
  "qz": 0.0
}
```

The components are expressed in the beam local coordinate system.

Fields:

- `beam`: beam ID;
- `qx`: local axial distributed load;
- `qy`: local distributed load along local y;
- `qz`: local distributed load along local z.

---

## 14. Uniform Shell Pressure

Uniform shell pressure references a shell.

```json
{
  "shell": 0,
  "pressure": -5000.0
}
```

Pressure follows the shell local-normal convention used by Carambola.

---

## 15. Complete Example

The following example represents a single cantilever beam.

```json
{
  "format": "carambola",
  "version": 1,

  "materials": [
    {
      "id": 0,
      "name": "Steel",
      "E": 210000000000.0,
      "nu": 0.3,
      "density": 7850.0
    }
  ],

  "sections": [
    {
      "id": 0,
      "type": "rectangular",
      "width": 0.2,
      "height": 0.4
    }
  ],

  "shell_properties": [],

  "nodes": [
    {
      "id": 0,
      "x": 0.0,
      "y": 0.0,
      "z": 0.0
    },
    {
      "id": 1,
      "x": 2.0,
      "y": 0.0,
      "z": 0.0
    }
  ],

  "trusses": [],

  "beams": [
    {
      "id": 0,
      "node_start": 0,
      "node_end": 1,
      "material": 0,
      "section": 0,
      "orientation": [0.0, 0.0, 1.0]
    }
  ],

  "shells": [],

  "supports": [
    {
      "node": 0,
      "ux": true,
      "uy": true,
      "uz": true,
      "rx": true,
      "ry": true,
      "rz": true
    }
  ],

  "point_loads": [
    {
      "node": 1,
      "fx": 0.0,
      "fy": 0.0,
      "fz": -1000.0,
      "mx": 0.0,
      "my": 0.0,
      "mz": 0.0
    }
  ],

  "uniform_beam_loads": [],
  "uniform_shell_pressures": []
}
```

---

## 16. Serialization Principles

The v1 serializer should follow these rules:

1. Serialize physical input data, not derived FEM matrices.
2. Use explicit IDs for references.
3. Preserve element order.
4. Preserve shell node order.
5. Preserve beam orientation.
6. Do not serialize derived section properties.
7. Do not serialize stiffness matrices.
8. Do not serialize solver state.
9. Use finite JSON numbers only.
10. Reject invalid references during deserialization.

---

## 17. Forward Compatibility

Future versions may add fields or new element types.

The schema therefore includes an explicit integer version.

A v1 reader should accept only:

```json
{
  "format": "carambola",
  "version": 1
}
```

If a future file declares a version that the installed Carambola release does
not support, loading should fail with a clear error.

Future schema migrations should be implemented explicitly rather than through
silent interpretation.

---

## 18. File Extension

The canonical extension is:

```text
.carambola
```

Although the content is JSON, the dedicated extension distinguishes Carambola
models from arbitrary JSON documents.

Example:

```text
cantilever.carambola
roof.carambola
shell_plate.carambola
```
