from __future__ import annotations

from dataclasses import dataclass
import json
import math
from pathlib import Path
from typing import Any

from ._carambola import (
    AnalysisResult,
    Model,
)


RESULT_FORMAT_NAME = "carambola-result"
RESULT_FORMAT_VERSION = 1
ANALYSIS_TYPE_LINEAR_STATIC = "linear_static"

RESULT_FILE_EXTENSION = ".carambola-result"


class CarambolaResultFormatError(ValueError):
    """
    Raised when a .carambola-result document is
    malformed, unsupported, or internally inconsistent.
    """


@dataclass(frozen=True)
class SerializedResult:
    analysis_type: str
    model_info: dict[str, int]
    displacements: list[dict[str, Any]]
    reactions: list[dict[str, Any]]

    @property
    def node_count(self) -> int:
        return self.model_info["node_count"]

    @property
    def truss_count(self) -> int:
        return self.model_info["truss_count"]

    @property
    def beam_count(self) -> int:
        return self.model_info["beam_count"]

    @property
    def shell_count(self) -> int:
        return self.model_info["shell_count"]

    def node_displacement(
        self,
        node_id: int,
    ) -> tuple[float, float, float]:
        entry = self.displacements[node_id]

        return (
            float(entry["ux"]),
            float(entry["uy"]),
            float(entry["uz"]),
        )

    def node_rotation(
        self,
        node_id: int,
    ) -> tuple[float, float, float]:
        entry = self.displacements[node_id]

        return (
            float(entry["rx"]),
            float(entry["ry"]),
            float(entry["rz"]),
        )

    def node_reaction(
        self,
        node_id: int,
    ) -> tuple[float, float, float]:
        entry = self.reactions[node_id]

        return (
            float(entry["fx"]),
            float(entry["fy"]),
            float(entry["fz"]),
        )

    def node_moment_reaction(
        self,
        node_id: int,
    ) -> tuple[float, float, float]:
        entry = self.reactions[node_id]

        return (
            float(entry["mx"]),
            float(entry["my"]),
            float(entry["mz"]),
        )


def _require_keys(
    item: dict[str, Any],
    keys: tuple[str, ...],
    context: str,
) -> None:
    for key in keys:
        if key not in item:
            raise CarambolaResultFormatError(
                f"{context} is missing required field "
                f"{key!r}"
            )


def _validate_non_negative_integer(
    value: Any,
    context: str,
) -> int:
    if isinstance(value, bool):
        raise CarambolaResultFormatError(
            f"{context} must be a non-negative integer"
        )

    if not isinstance(value, int):
        raise CarambolaResultFormatError(
            f"{context} must be a non-negative integer"
        )

    if value < 0:
        raise CarambolaResultFormatError(
            f"{context} must be a non-negative integer"
        )

    return value


def _validate_number(
    value: Any,
    context: str,
) -> float:
    if isinstance(value, bool):
        raise CarambolaResultFormatError(
            f"{context} must be a finite number"
        )

    if not isinstance(
        value,
        (int, float),
    ):
        raise CarambolaResultFormatError(
            f"{context} must be a finite number"
        )

    result = float(value)

    if not math.isfinite(result):
        raise CarambolaResultFormatError(
            f"{context} must be a finite number"
        )

    return result


def _validate_node_result_table(
    items: Any,
    *,
    name: str,
    node_count: int,
    value_fields: tuple[str, ...],
) -> None:
    if not isinstance(items, list):
        raise CarambolaResultFormatError(
            f"{name} must be a list"
        )

    if len(items) != node_count:
        raise CarambolaResultFormatError(
            f"{name} must contain exactly "
            f"{node_count} entries"
        )

    seen: set[int] = set()

    for index, item in enumerate(items):
        context = f"{name}[{index}]"

        if not isinstance(item, dict):
            raise CarambolaResultFormatError(
                f"{context} must be an object"
            )

        _require_keys(
            item,
            ("node",) + value_fields,
            context,
        )

        node_id = _validate_non_negative_integer(
            item["node"],
            f"{context}.node",
        )

        if node_id >= node_count:
            raise CarambolaResultFormatError(
                f"{context}.node references unknown "
                f"node {node_id}"
            )

        if node_id in seen:
            raise CarambolaResultFormatError(
                f"{name} contains duplicate node "
                f"ID {node_id}"
            )

        seen.add(node_id)

        for field in value_fields:
            _validate_number(
                item[field],
                f"{context}.{field}",
            )

    expected = set(
        range(node_count)
    )

    if seen != expected:
        missing = sorted(
            expected - seen
        )

        raise CarambolaResultFormatError(
            f"{name} is missing node IDs {missing}"
        )

    actual_order = [
        item["node"]
        for item in items
    ]

    expected_order = list(
        range(node_count)
    )

    if actual_order != expected_order:
        raise CarambolaResultFormatError(
            f"{name} node IDs must be ordered "
            "contiguously from zero"
        )


def _validate_result_document(
    data: Any,
) -> None:
    if not isinstance(data, dict):
        raise CarambolaResultFormatError(
            "Result document must be an object"
        )

    required_top_level = (
        "format",
        "version",
        "analysis",
        "model",
        "displacements",
        "reactions",
    )

    _require_keys(
        data,
        required_top_level,
        "result document",
    )

    if (
        data["format"]
        != RESULT_FORMAT_NAME
    ):
        raise CarambolaResultFormatError(
            "Unsupported result format"
        )

    if (
        data["version"]
        != RESULT_FORMAT_VERSION
    ):
        raise CarambolaResultFormatError(
            "Unsupported result format version"
        )

    analysis = data["analysis"]

    if not isinstance(
        analysis,
        dict,
    ):
        raise CarambolaResultFormatError(
            "analysis must be an object"
        )

    _require_keys(
        analysis,
        ("type",),
        "analysis",
    )

    if (
        analysis["type"]
        != ANALYSIS_TYPE_LINEAR_STATIC
    ):
        raise CarambolaResultFormatError(
            "Unsupported analysis type"
        )

    model_info = data["model"]

    if not isinstance(
        model_info,
        dict,
    ):
        raise CarambolaResultFormatError(
            "model must be an object"
        )

    model_fields = (
        "node_count",
        "truss_count",
        "beam_count",
        "shell_count",
    )

    _require_keys(
        model_info,
        model_fields,
        "model",
    )

    node_count = (
        _validate_non_negative_integer(
            model_info["node_count"],
            "model.node_count",
        )
    )

    _validate_non_negative_integer(
        model_info["truss_count"],
        "model.truss_count",
    )

    _validate_non_negative_integer(
        model_info["beam_count"],
        "model.beam_count",
    )

    _validate_non_negative_integer(
        model_info["shell_count"],
        "model.shell_count",
    )

    _validate_node_result_table(
        data["displacements"],
        name="displacements",
        node_count=node_count,
        value_fields=(
            "ux",
            "uy",
            "uz",
            "rx",
            "ry",
            "rz",
        ),
    )

    _validate_node_result_table(
        data["reactions"],
        name="reactions",
        node_count=node_count,
        value_fields=(
            "fx",
            "fy",
            "fz",
            "mx",
            "my",
            "mz",
        ),
    )


def validate_result_compatibility(
    result: SerializedResult,
    model: Model,
) -> None:
    """
    Check whether a stored result is structurally
    compatible with a Model.

    Version 1 uses model entity counts only.
    """

    if not isinstance(
        result,
        SerializedResult,
    ):
        raise TypeError(
            "validate_result_compatibility() expects "
            "a carambola.SerializedResult"
        )

    if not isinstance(
        model,
        Model,
    ):
        raise TypeError(
            "validate_result_compatibility() expects "
            "a carambola.Model"
        )

    expected = {
        "node_count":
            int(model.node_count),
        "truss_count":
            int(model.truss_count),
        "beam_count":
            int(model.beam_count),
        "shell_count":
            int(model.shell_count),
    }

    if result.model_info != expected:
        raise CarambolaResultFormatError(
            "Result is not compatible with the "
            "supplied model"
        )


def result_to_dict(
    result: AnalysisResult,
    model: Model,
) -> dict[str, Any]:
    """
    Convert a linear-static AnalysisResult to a
    JSON-compatible dictionary.
    """

    if not isinstance(
        result,
        AnalysisResult,
    ):
        raise TypeError(
            "result_to_dict() expects a "
            "carambola.AnalysisResult"
        )

    if not isinstance(
        model,
        Model,
    ):
        raise TypeError(
            "result_to_dict() expects a "
            "carambola.Model as its second argument"
        )

    displacements: list[
        dict[str, Any]
    ] = []

    reactions: list[
        dict[str, Any]
    ] = []

    for node_id in range(
        model.node_count
    ):
        node = model.node(
            node_id
        )

        displacement = (
            result.node_displacement(
                node
            )
        )

        rotation = (
            result.node_rotation(
                node
            )
        )

        reaction = (
            result.node_reaction(
                node
            )
        )

        moment_reaction = (
            result.node_moment_reaction(
                node
            )
        )

        displacement_entry = {
            "node": node_id,
            "ux": float(
                displacement[0]
            ),
            "uy": float(
                displacement[1]
            ),
            "uz": float(
                displacement[2]
            ),
            "rx": float(
                rotation[0]
            ),
            "ry": float(
                rotation[1]
            ),
            "rz": float(
                rotation[2]
            ),
        }

        reaction_entry = {
            "node": node_id,
            "fx": float(
                reaction[0]
            ),
            "fy": float(
                reaction[1]
            ),
            "fz": float(
                reaction[2]
            ),
            "mx": float(
                moment_reaction[0]
            ),
            "my": float(
                moment_reaction[1]
            ),
            "mz": float(
                moment_reaction[2]
            ),
        }

        for field in (
            "ux",
            "uy",
            "uz",
            "rx",
            "ry",
            "rz",
        ):
            _validate_number(
                displacement_entry[field],
                (
                    f"displacements[{node_id}]"
                    f".{field}"
                ),
            )

        for field in (
            "fx",
            "fy",
            "fz",
            "mx",
            "my",
            "mz",
        ):
            _validate_number(
                reaction_entry[field],
                (
                    f"reactions[{node_id}]"
                    f".{field}"
                ),
            )

        displacements.append(
            displacement_entry
        )

        reactions.append(
            reaction_entry
        )

    return {
        "format":
            RESULT_FORMAT_NAME,

        "version":
            RESULT_FORMAT_VERSION,

        "analysis": {
            "type":
                ANALYSIS_TYPE_LINEAR_STATIC,
        },

        "model": {
            "node_count":
                int(model.node_count),

            "truss_count":
                int(model.truss_count),

            "beam_count":
                int(model.beam_count),

            "shell_count":
                int(model.shell_count),
        },

        "displacements":
            displacements,

        "reactions":
            reactions,
    }


def result_from_dict(
    data: dict[str, Any],
) -> SerializedResult:
    """
    Reconstruct a lightweight persisted result from
    a result dictionary.

    This does not create a native AnalysisResult and
    does not perform FEM analysis.
    """

    if not isinstance(
        data,
        dict,
    ):
        raise TypeError(
            "result_from_dict() expects a dictionary"
        )

    _validate_result_document(
        data
    )

    model_info = data["model"]

    normalized_model_info = {
        "node_count":
            int(
                model_info["node_count"]
            ),

        "truss_count":
            int(
                model_info["truss_count"]
            ),

        "beam_count":
            int(
                model_info["beam_count"]
            ),

        "shell_count":
            int(
                model_info["shell_count"]
            ),
    }

    normalized_displacements = [
        {
            "node":
                int(item["node"]),

            "ux":
                float(item["ux"]),

            "uy":
                float(item["uy"]),

            "uz":
                float(item["uz"]),

            "rx":
                float(item["rx"]),

            "ry":
                float(item["ry"]),

            "rz":
                float(item["rz"]),
        }
        for item in data[
            "displacements"
        ]
    ]

    normalized_reactions = [
        {
            "node":
                int(item["node"]),

            "fx":
                float(item["fx"]),

            "fy":
                float(item["fy"]),

            "fz":
                float(item["fz"]),

            "mx":
                float(item["mx"]),

            "my":
                float(item["my"]),

            "mz":
                float(item["mz"]),
        }
        for item in data[
            "reactions"
        ]
    ]

    return SerializedResult(
        analysis_type=(
            data["analysis"]["type"]
        ),
        model_info=(
            normalized_model_info
        ),
        displacements=(
            normalized_displacements
        ),
        reactions=(
            normalized_reactions
        ),
    )


def serialized_result_to_dict(
    result: SerializedResult,
) -> dict[str, Any]:
    """
    Convert a SerializedResult back to its canonical
    dictionary representation.
    """

    if not isinstance(
        result,
        SerializedResult,
    ):
        raise TypeError(
            "serialized_result_to_dict() expects "
            "a carambola.SerializedResult"
        )

    data = {
        "format":
            RESULT_FORMAT_NAME,

        "version":
            RESULT_FORMAT_VERSION,

        "analysis": {
            "type":
                result.analysis_type,
        },

        "model": {
            "node_count":
                int(
                    result.node_count
                ),

            "truss_count":
                int(
                    result.truss_count
                ),

            "beam_count":
                int(
                    result.beam_count
                ),

            "shell_count":
                int(
                    result.shell_count
                ),
        },

        "displacements": [
            dict(item)
            for item in (
                result.displacements
            )
        ],

        "reactions": [
            dict(item)
            for item in (
                result.reactions
            )
        ],
    }

    _validate_result_document(
        data
    )

    return data


def _normalize_result_path(
    path: str | Path,
) -> Path:
    """
    Validate and normalize a Carambola result path.
    """

    normalized = Path(path)

    if not str(
        normalized
    ).endswith(
        RESULT_FILE_EXTENSION
    ):
        raise ValueError(
            "Carambola result files must use the "
            f"{RESULT_FILE_EXTENSION} extension"
        )

    return normalized


def save_result(
    result: (
        AnalysisResult
        | SerializedResult
    ),
    path: str | Path,
    model: Model | None = None,
) -> Path:
    """
    Save a Carambola analysis result.

    Native AnalysisResult objects require their Model.

    SerializedResult objects can be saved directly.
    """

    normalized_path = (
        _normalize_result_path(
            path
        )
    )

    if isinstance(
        result,
        AnalysisResult,
    ):
        if model is None:
            raise TypeError(
                "save_result() requires a Model "
                "when saving an AnalysisResult"
            )

        data = result_to_dict(
            result,
            model,
        )

    elif isinstance(
        result,
        SerializedResult,
    ):
        if model is not None:
            raise TypeError(
                "save_result() does not accept a "
                "Model when saving a SerializedResult"
            )

        data = (
            serialized_result_to_dict(
                result
            )
        )

    else:
        raise TypeError(
            "save_result() expects an AnalysisResult "
            "or SerializedResult"
        )

    text = json.dumps(
        data,
        indent=2,
        ensure_ascii=False,
        allow_nan=False,
    )

    normalized_path.write_text(
        text + "\n",
        encoding="utf-8",
    )

    return normalized_path


def load_result(
    path: str | Path,
    model: Model | None = None,
) -> SerializedResult:
    """
    Load a .carambola-result file.

    If a Model is supplied, compatibility is checked
    against the stored model metadata.
    """

    normalized_path = (
        _normalize_result_path(
            path
        )
    )

    text = normalized_path.read_text(
        encoding="utf-8",
    )

    try:
        data = json.loads(
            text
        )

    except json.JSONDecodeError as exc:
        raise CarambolaResultFormatError(
            "Invalid Carambola result JSON"
        ) from exc

    result = result_from_dict(
        data
    )

    if model is not None:
        validate_result_compatibility(
            result,
            model,
        )

    return result
