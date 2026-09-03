from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ._carambola import (
    CircularSection,
    Material,
    Model,
    RectangularSection,
    ShellProperty,
)


FORMAT_NAME = "carambola"
FORMAT_VERSION = 1


class CarambolaFormatError(ValueError):
    """
    Raised when a .carambola document is malformed,
    unsupported, or internally inconsistent.
    """


_REQUIRED_TOP_LEVEL_FIELDS = (
    "materials",
    "sections",
    "shell_properties",
    "nodes",
    "trusses",
    "beams",
    "shells",
    "supports",
    "point_loads",
    "uniform_beam_loads",
    "uniform_shell_pressures",
)


def _require_keys(
    item: dict[str, Any],
    keys: tuple[str, ...],
    context: str,
) -> None:
    if not isinstance(item, dict):
        raise CarambolaFormatError(
            f"{context} must be an object"
        )

    for key in keys:
        if key not in item:
            raise CarambolaFormatError(
                f"{context} is missing required field "
                f"{key!r}"
            )


def _validate_id_table(
    items: list[Any],
    name: str,
) -> set[int]:
    ids: list[int] = []

    for index, item in enumerate(items):
        context = f"{name}[{index}]"

        _require_keys(
            item,
            ("id",),
            context,
        )

        try:
            item_id = int(item["id"])
        except (TypeError, ValueError) as exc:
            raise CarambolaFormatError(
                f"{context}.id must be an integer"
            ) from exc

        ids.append(item_id)

    if len(ids) != len(set(ids)):
        raise CarambolaFormatError(
            f"{name} contains duplicate IDs"
        )

    expected = list(range(len(items)))

    if sorted(ids) != expected:
        raise CarambolaFormatError(
            f"{name} IDs must be contiguous "
            f"and start at 0"
        )

    return set(ids)


def _validate_reference(
    value: Any,
    valid_ids: set[int],
    context: str,
) -> None:
    try:
        reference = int(value)
    except (TypeError, ValueError) as exc:
        raise CarambolaFormatError(
            f"{context} must be an integer ID"
        ) from exc

    if reference not in valid_ids:
        raise CarambolaFormatError(
            f"{context} references unknown ID "
            f"{reference}"
        )


def _validate_model_document(
    data: Any,
) -> None:
    if not isinstance(data, dict):
        raise CarambolaFormatError(
            "Carambola model document must be "
            "a JSON object"
        )

    if data.get("format") != FORMAT_NAME:
        raise CarambolaFormatError(
            "Not a Carambola model document"
        )

    if data.get("version") != FORMAT_VERSION:
        raise CarambolaFormatError(
            "Unsupported Carambola model format "
            f"version: {data.get('version')!r}"
        )

    for field in _REQUIRED_TOP_LEVEL_FIELDS:
        if field not in data:
            raise CarambolaFormatError(
                "Carambola model document is missing "
                f"required field {field!r}"
            )

        if not isinstance(data[field], list):
            raise CarambolaFormatError(
                f"{field!r} must be a list"
            )

    material_ids = _validate_id_table(
        data["materials"],
        "materials",
    )

    section_ids = _validate_id_table(
        data["sections"],
        "sections",
    )

    property_ids = _validate_id_table(
        data["shell_properties"],
        "shell_properties",
    )

    node_ids = _validate_id_table(
        data["nodes"],
        "nodes",
    )

    _validate_id_table(
        data["trusses"],
        "trusses",
    )

    beam_ids = _validate_id_table(
        data["beams"],
        "beams",
    )

    shell_ids = _validate_id_table(
        data["shells"],
        "shells",
    )

    # --------------------------------------------------------------
    # Materials
    # --------------------------------------------------------------

    for index, item in enumerate(
        data["materials"]
    ):
        _require_keys(
            item,
            (
                "id",
                "name",
                "E",
                "nu",
                "density",
            ),
            f"materials[{index}]",
        )

    # --------------------------------------------------------------
    # Sections
    # --------------------------------------------------------------

    for index, item in enumerate(
        data["sections"]
    ):
        context = f"sections[{index}]"

        _require_keys(
            item,
            ("id", "type"),
            context,
        )

        section_type = item["type"]

        if section_type == "rectangular":
            _require_keys(
                item,
                (
                    "id",
                    "type",
                    "width",
                    "height",
                ),
                context,
            )

        elif section_type == "circular":
            _require_keys(
                item,
                (
                    "id",
                    "type",
                    "radius",
                ),
                context,
            )

        else:
            raise CarambolaFormatError(
                f"{context} has unsupported section "
                f"type {section_type!r}"
            )

    # --------------------------------------------------------------
    # Shell properties
    # --------------------------------------------------------------

    for index, item in enumerate(
        data["shell_properties"]
    ):
        context = (
            f"shell_properties[{index}]"
        )

        _require_keys(
            item,
            (
                "id",
                "material",
                "thickness",
            ),
            context,
        )

        _validate_reference(
            item["material"],
            material_ids,
            f"{context}.material",
        )

    # --------------------------------------------------------------
    # Nodes
    # --------------------------------------------------------------

    for index, item in enumerate(
        data["nodes"]
    ):
        _require_keys(
            item,
            ("id", "x", "y", "z"),
            f"nodes[{index}]",
        )

    # --------------------------------------------------------------
    # Trusses
    # --------------------------------------------------------------

    for index, item in enumerate(
        data["trusses"]
    ):
        context = f"trusses[{index}]"

        _require_keys(
            item,
            (
                "id",
                "node_start",
                "node_end",
                "material",
                "section",
            ),
            context,
        )

        _validate_reference(
            item["node_start"],
            node_ids,
            f"{context}.node_start",
        )

        _validate_reference(
            item["node_end"],
            node_ids,
            f"{context}.node_end",
        )

        _validate_reference(
            item["material"],
            material_ids,
            f"{context}.material",
        )

        _validate_reference(
            item["section"],
            section_ids,
            f"{context}.section",
        )

    # --------------------------------------------------------------
    # Beams
    # --------------------------------------------------------------

    for index, item in enumerate(
        data["beams"]
    ):
        context = f"beams[{index}]"

        _require_keys(
            item,
            (
                "id",
                "node_start",
                "node_end",
                "material",
                "section",
                "orientation",
            ),
            context,
        )

        _validate_reference(
            item["node_start"],
            node_ids,
            f"{context}.node_start",
        )

        _validate_reference(
            item["node_end"],
            node_ids,
            f"{context}.node_end",
        )

        _validate_reference(
            item["material"],
            material_ids,
            f"{context}.material",
        )

        _validate_reference(
            item["section"],
            section_ids,
            f"{context}.section",
        )

        orientation = item["orientation"]

        if (
            not isinstance(orientation, list)
            or len(orientation) != 3
        ):
            raise CarambolaFormatError(
                f"{context}.orientation must contain "
                "exactly three values"
            )

    # --------------------------------------------------------------
    # Shells
    # --------------------------------------------------------------

    for index, item in enumerate(
        data["shells"]
    ):
        context = f"shells[{index}]"

        _require_keys(
            item,
            (
                "id",
                "nodes",
                "property",
            ),
            context,
        )

        node_refs = item["nodes"]

        if (
            not isinstance(node_refs, list)
            or len(node_refs) != 3
        ):
            raise CarambolaFormatError(
                f"{context}.nodes must contain "
                "exactly three node IDs"
            )

        for node_index, node_id in enumerate(
            node_refs
        ):
            _validate_reference(
                node_id,
                node_ids,
                (
                    f"{context}.nodes"
                    f"[{node_index}]"
                ),
            )

        _validate_reference(
            item["property"],
            property_ids,
            f"{context}.property",
        )

    # --------------------------------------------------------------
    # Supports
    # --------------------------------------------------------------

    for index, item in enumerate(
        data["supports"]
    ):
        context = f"supports[{index}]"

        _require_keys(
            item,
            (
                "node",
                "ux",
                "uy",
                "uz",
                "rx",
                "ry",
                "rz",
            ),
            context,
        )

        _validate_reference(
            item["node"],
            node_ids,
            f"{context}.node",
        )

    # --------------------------------------------------------------
    # Point loads
    # --------------------------------------------------------------

    for index, item in enumerate(
        data["point_loads"]
    ):
        context = f"point_loads[{index}]"

        _require_keys(
            item,
            (
                "node",
                "fx",
                "fy",
                "fz",
                "mx",
                "my",
                "mz",
            ),
            context,
        )

        _validate_reference(
            item["node"],
            node_ids,
            f"{context}.node",
        )

    # --------------------------------------------------------------
    # Uniform beam loads
    # --------------------------------------------------------------

    for index, item in enumerate(
        data["uniform_beam_loads"]
    ):
        context = (
            f"uniform_beam_loads[{index}]"
        )

        _require_keys(
            item,
            (
                "beam",
                "qx",
                "qy",
                "qz",
            ),
            context,
        )

        _validate_reference(
            item["beam"],
            beam_ids,
            f"{context}.beam",
        )

    # --------------------------------------------------------------
    # Uniform shell pressures
    # --------------------------------------------------------------

    for index, item in enumerate(
        data["uniform_shell_pressures"]
    ):
        context = (
            f"uniform_shell_pressures[{index}]"
        )

        _require_keys(
            item,
            (
                "shell",
                "pressure",
            ),
            context,
        )

        _validate_reference(
            item["shell"],
            shell_ids,
            f"{context}.shell",
        )


def _find_object_index(
    objects: list[Any],
    target: Any,
    kind: str,
) -> int:
    """
    Find the model-local index of a referenced C++ object.
    """

    for index, obj in enumerate(objects):
        if obj is target:
            return index

    for index, obj in enumerate(objects):
        if obj == target:
            return index

    raise ValueError(
        f"Referenced {kind} does not belong to this model"
    )


def model_to_dict(
    model: Model,
) -> dict[str, Any]:
    """
    Convert a Carambola Model to a JSON-compatible dictionary.

    The returned structure follows the Carambola model format v1.
    """

    if not isinstance(model, Model):
        raise TypeError(
            "model_to_dict() expects a carambola.Model"
        )

    truss_objects = list(model.trusses)
    beam_objects = list(model.beams)
    shell_objects = list(model.shells)

    materials: list[dict[str, Any]] = []
    sections: list[dict[str, Any]] = []
    shell_properties: list[dict[str, Any]] = []

    material_ids: dict[
        tuple[str, float, float, float],
        int,
    ] = {}

    section_ids: dict[
        tuple[Any, ...],
        int,
    ] = {}

    shell_property_ids: dict[
        tuple[int, float],
        int,
    ] = {}

    def material_id(
        material: Any,
    ) -> int:
        key = (
            str(material.name),
            float(material.E),
            float(material.nu),
            float(material.density),
        )

        existing = material_ids.get(key)

        if existing is not None:
            return existing

        index = len(materials)

        materials.append(
            {
                "id": index,
                "name": str(material.name),
                "E": float(material.E),
                "nu": float(material.nu),
                "density": float(
                    material.density
                ),
            }
        )

        material_ids[key] = index

        return index

    def section_id(
        section: Any,
    ) -> int:
        if isinstance(
            section,
            RectangularSection,
        ):
            key = (
                "rectangular",
                float(section.width),
                float(section.height),
            )

            section_data = {
                "type": "rectangular",
                "width": float(section.width),
                "height": float(section.height),
            }

        elif isinstance(
            section,
            CircularSection,
        ):
            key = (
                "circular",
                float(section.radius),
            )

            section_data = {
                "type": "circular",
                "radius": float(section.radius),
            }

        else:
            raise TypeError(
                "Unsupported section type: "
                f"{type(section).__name__}"
            )

        existing = section_ids.get(key)

        if existing is not None:
            return existing

        index = len(sections)

        sections.append(
            {
                "id": index,
                **section_data,
            }
        )

        section_ids[key] = index

        return index

    def shell_property_id(
        property_: Any,
    ) -> int:
        mat_id = material_id(
            property_.material
        )

        key = (
            mat_id,
            float(property_.thickness),
        )

        existing = shell_property_ids.get(
            key
        )

        if existing is not None:
            return existing

        index = len(shell_properties)

        shell_properties.append(
            {
                "id": index,
                "material": mat_id,
                "thickness": float(
                    property_.thickness
                ),
            }
        )

        shell_property_ids[key] = index

        return index

    # --------------------------------------------------------------
    # Nodes
    # --------------------------------------------------------------

    nodes = []

    for node_id in range(
        model.node_count
    ):
        node = model.node(node_id)

        nodes.append(
            {
                "id": int(node.id),
                "x": float(node.x),
                "y": float(node.y),
                "z": float(node.z),
            }
        )

    # --------------------------------------------------------------
    # Trusses
    # --------------------------------------------------------------

    trusses = []

    for truss_id, truss in enumerate(
        truss_objects
    ):
        trusses.append(
            {
                "id": truss_id,
                "node_start": int(
                    truss.node_start.id
                ),
                "node_end": int(
                    truss.node_end.id
                ),
                "material": material_id(
                    truss.material
                ),
                "section": section_id(
                    truss.section
                ),
            }
        )

    # --------------------------------------------------------------
    # Beams
    # --------------------------------------------------------------

    beams = []

    for beam_id, beam in enumerate(
        beam_objects
    ):
        orientation = beam.orientation

        beams.append(
            {
                "id": beam_id,
                "node_start": int(
                    beam.node_start.id
                ),
                "node_end": int(
                    beam.node_end.id
                ),
                "material": material_id(
                    beam.material
                ),
                "section": section_id(
                    beam.section
                ),
                "orientation": [
                    float(orientation[0]),
                    float(orientation[1]),
                    float(orientation[2]),
                ],
            }
        )

    # --------------------------------------------------------------
    # Shells
    # --------------------------------------------------------------

    shells = []

    for shell_id, shell in enumerate(
        shell_objects
    ):
        shells.append(
            {
                "id": shell_id,
                "nodes": [
                    int(shell.node_a.id),
                    int(shell.node_b.id),
                    int(shell.node_c.id),
                ],
                "property": shell_property_id(
                    shell.property
                ),
            }
        )

    # --------------------------------------------------------------
    # Supports
    # --------------------------------------------------------------

    supports = []

    for support in model.supports:
        supports.append(
            {
                "node": int(
                    support.node.id
                ),
                "ux": bool(support.ux),
                "uy": bool(support.uy),
                "uz": bool(support.uz),
                "rx": bool(support.rx),
                "ry": bool(support.ry),
                "rz": bool(support.rz),
            }
        )

    # --------------------------------------------------------------
    # Point loads
    # --------------------------------------------------------------

    point_loads = []

    for load in model.point_loads:
        point_loads.append(
            {
                "node": int(load.node.id),
                "fx": float(load.fx),
                "fy": float(load.fy),
                "fz": float(load.fz),
                "mx": float(load.mx),
                "my": float(load.my),
                "mz": float(load.mz),
            }
        )

    # --------------------------------------------------------------
    # Uniform beam loads
    # --------------------------------------------------------------

    uniform_beam_loads = []

    for load in model.uniform_beam_loads:
        beam_index = _find_object_index(
            beam_objects,
            load.beam,
            "beam",
        )

        uniform_beam_loads.append(
            {
                "beam": beam_index,
                "qx": float(load.qx),
                "qy": float(load.qy),
                "qz": float(load.qz),
            }
        )

    # --------------------------------------------------------------
    # Uniform shell pressures
    # --------------------------------------------------------------

    uniform_shell_pressures = []

    for load in model.uniform_shell_pressures:
        shell_index = _find_object_index(
            shell_objects,
            load.shell,
            "shell",
        )

        uniform_shell_pressures.append(
            {
                "shell": shell_index,
                "pressure": float(
                    load.pressure
                ),
            }
        )

    return {
        "format": FORMAT_NAME,
        "version": FORMAT_VERSION,
        "materials": materials,
        "sections": sections,
        "shell_properties": shell_properties,
        "nodes": nodes,
        "trusses": trusses,
        "beams": beams,
        "shells": shells,
        "supports": supports,
        "point_loads": point_loads,
        "uniform_beam_loads":
            uniform_beam_loads,
        "uniform_shell_pressures":
            uniform_shell_pressures,
    }


def model_from_dict(
    data: dict[str, Any],
) -> Model:
    """
    Reconstruct a Carambola Model from a format-v1 dictionary.
    """

    if not isinstance(data, dict):
        raise TypeError(
            "model_from_dict() expects a dictionary"
        )

    _validate_model_document(data)

    model = Model()

    # --------------------------------------------------------------
    # Materials
    # --------------------------------------------------------------

    materials: dict[int, Material] = {}

    for item in data["materials"]:
        item_id = int(item["id"])

        try:
            material = Material(
                str(item["name"]),
                float(item["E"]),
                float(item["nu"]),
                float(item["density"]),
            )

        except (
            TypeError,
            ValueError,
        ) as exc:
            raise CarambolaFormatError(
                f"Invalid material id {item_id}: "
                f"{exc}"
            ) from exc

        materials[item_id] = material

    # --------------------------------------------------------------
    # Sections
    # --------------------------------------------------------------

    sections: dict[int, Any] = {}

    for item in data["sections"]:
        item_id = int(item["id"])
        section_type = item["type"]

        try:
            if section_type == "rectangular":
                section = RectangularSection(
                    float(item["width"]),
                    float(item["height"]),
                )

            else:
                section = CircularSection(
                    float(item["radius"]),
                )

        except (
            TypeError,
            ValueError,
        ) as exc:
            raise CarambolaFormatError(
                f"Invalid section id {item_id}: "
                f"{exc}"
            ) from exc

        sections[item_id] = section

    # --------------------------------------------------------------
    # Shell properties
    # --------------------------------------------------------------

    shell_properties: dict[
        int,
        ShellProperty,
    ] = {}

    for item in data[
        "shell_properties"
    ]:
        item_id = int(item["id"])

        try:
            property_ = ShellProperty(
                materials[
                    int(item["material"])
                ],
                float(item["thickness"]),
            )

        except (
            TypeError,
            ValueError,
        ) as exc:
            raise CarambolaFormatError(
                "Invalid shell property id "
                f"{item_id}: {exc}"
            ) from exc

        shell_properties[
            item_id
        ] = property_

    # --------------------------------------------------------------
    # Nodes
    # --------------------------------------------------------------

    nodes: dict[int, Any] = {}

    for item in data["nodes"]:
        item_id = int(item["id"])

        try:
            node = model.add_node(
                float(item["x"]),
                float(item["y"]),
                float(item["z"]),
            )

        except (
            TypeError,
            ValueError,
        ) as exc:
            raise CarambolaFormatError(
                f"Invalid node id {item_id}: "
                f"{exc}"
            ) from exc

        nodes[item_id] = node

    # --------------------------------------------------------------
    # Trusses
    # --------------------------------------------------------------

    trusses: dict[int, Any] = {}

    for item in data["trusses"]:
        item_id = int(item["id"])

        try:
            truss = model.add_truss(
                nodes[
                    int(item["node_start"])
                ],
                nodes[
                    int(item["node_end"])
                ],
                materials[
                    int(item["material"])
                ],
                sections[
                    int(item["section"])
                ],
            )

        except (
            TypeError,
            ValueError,
        ) as exc:
            raise CarambolaFormatError(
                f"Invalid truss id {item_id}: "
                f"{exc}"
            ) from exc

        trusses[item_id] = truss

    # --------------------------------------------------------------
    # Beams
    # --------------------------------------------------------------

    beams: dict[int, Any] = {}

    for item in data["beams"]:
        item_id = int(item["id"])
        orientation = item["orientation"]

        try:
            beam = model.add_beam(
                nodes[
                    int(item["node_start"])
                ],
                nodes[
                    int(item["node_end"])
                ],
                materials[
                    int(item["material"])
                ],
                sections[
                    int(item["section"])
                ],
                orientation,
            )

        except (
            TypeError,
            ValueError,
        ) as exc:
            raise CarambolaFormatError(
                f"Invalid beam id {item_id}: "
                f"{exc}"
            ) from exc

        beams[item_id] = beam

    # --------------------------------------------------------------
    # Shells
    # --------------------------------------------------------------

    shells: dict[int, Any] = {}

    for item in data["shells"]:
        item_id = int(item["id"])
        node_ids = item["nodes"]

        try:
            shell = model.add_shell(
                nodes[int(node_ids[0])],
                nodes[int(node_ids[1])],
                nodes[int(node_ids[2])],
                shell_properties[
                    int(item["property"])
                ],
            )

        except (
            TypeError,
            ValueError,
        ) as exc:
            raise CarambolaFormatError(
                f"Invalid shell id {item_id}: "
                f"{exc}"
            ) from exc

        shells[item_id] = shell

    # --------------------------------------------------------------
    # Supports
    # --------------------------------------------------------------

    for index, item in enumerate(
        data["supports"]
    ):
        try:
            model.add_support(
                nodes[
                    int(item["node"])
                ],
                bool(item["ux"]),
                bool(item["uy"]),
                bool(item["uz"]),
                bool(item["rx"]),
                bool(item["ry"]),
                bool(item["rz"]),
            )

        except (
            TypeError,
            ValueError,
        ) as exc:
            raise CarambolaFormatError(
                f"Invalid support {index}: "
                f"{exc}"
            ) from exc

    # --------------------------------------------------------------
    # Point loads
    # --------------------------------------------------------------

    for index, item in enumerate(
        data["point_loads"]
    ):
        try:
            model.add_point_load(
                nodes[
                    int(item["node"])
                ],
                float(item["fx"]),
                float(item["fy"]),
                float(item["fz"]),
                float(item["mx"]),
                float(item["my"]),
                float(item["mz"]),
            )

        except (
            TypeError,
            ValueError,
        ) as exc:
            raise CarambolaFormatError(
                f"Invalid point load {index}: "
                f"{exc}"
            ) from exc

    # --------------------------------------------------------------
    # Uniform beam loads
    # --------------------------------------------------------------

    for index, item in enumerate(
        data["uniform_beam_loads"]
    ):
        try:
            model.add_uniform_beam_load(
                beams[
                    int(item["beam"])
                ],
                float(item["qx"]),
                float(item["qy"]),
                float(item["qz"]),
            )

        except (
            TypeError,
            ValueError,
        ) as exc:
            raise CarambolaFormatError(
                "Invalid uniform beam load "
                f"{index}: {exc}"
            ) from exc

    # --------------------------------------------------------------
    # Uniform shell pressures
    # --------------------------------------------------------------

    for index, item in enumerate(
        data["uniform_shell_pressures"]
    ):
        try:
            model.add_uniform_shell_pressure(
                shells[
                    int(item["shell"])
                ],
                float(item["pressure"]),
            )

        except (
            TypeError,
            ValueError,
        ) as exc:
            raise CarambolaFormatError(
                "Invalid uniform shell pressure "
                f"{index}: {exc}"
            ) from exc

    return model


def _normalize_carambola_path(
    path: str | Path,
) -> Path:
    """
    Normalize and validate a Carambola model path.
    """

    path = Path(path)

    if path.suffix != ".carambola":
        raise ValueError(
            "Carambola model files must use "
            "the '.carambola' extension"
        )

    return path


def save_model(
    model: Model,
    path: str | Path,
) -> None:
    """
    Save a Carambola model to a .carambola file.
    """

    path = _normalize_carambola_path(
        path
    )

    data = model_to_dict(model)

    with path.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            data,
            file,
            indent=2,
            ensure_ascii=False,
        )

        file.write("\n")


def load_model(
    path: str | Path,
) -> Model:
    """
    Load a Carambola model from a .carambola file.
    """

    path = _normalize_carambola_path(
        path
    )

    try:
        with path.open(
            "r",
            encoding="utf-8",
        ) as file:
            data = json.load(file)

    except json.JSONDecodeError as exc:
        raise CarambolaFormatError(
            f"Invalid JSON in {path}: "
            f"{exc.msg}"
        ) from exc

    return model_from_dict(data)
