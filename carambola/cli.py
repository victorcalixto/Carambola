from __future__ import annotations

import argparse
from pathlib import Path
import sys
from typing import Sequence

from . import (
    CarambolaFormatError,
    CarambolaResultFormatError,
    LinearStaticSolver,
    load_model,
    load_result,
    save_result,
)


EXIT_SUCCESS = 0
EXIT_USAGE = 2
EXIT_INPUT_ERROR = 3
EXIT_ANALYSIS_ERROR = 4
EXIT_OUTPUT_ERROR = 5


class CLIError(Exception):
    def __init__(
        self,
        message: str,
        exit_code: int,
    ) -> None:
        super().__init__(message)

        self.exit_code = exit_code


def _default_result_path(
    model_path: str | Path,
) -> Path:
    path = Path(model_path)

    return path.with_suffix(
        ".carambola-result"
    )


def _load_model_for_cli(
    path: Path,
):
    try:
        return load_model(path)

    except FileNotFoundError as exc:
        raise CLIError(
            f"file not found: {path}",
            EXIT_INPUT_ERROR,
        ) from exc

    except PermissionError as exc:
        raise CLIError(
            f"cannot read file: {path}",
            EXIT_INPUT_ERROR,
        ) from exc

    except CarambolaFormatError as exc:
        raise CLIError(
            f"invalid model file: {exc}",
            EXIT_INPUT_ERROR,
        ) from exc

    except ValueError as exc:
        raise CLIError(
            str(exc),
            EXIT_USAGE,
        ) from exc

    except OSError as exc:
        raise CLIError(
            f"cannot read file: {path}: {exc}",
            EXIT_INPUT_ERROR,
        ) from exc


def _load_result_for_cli(
    path: Path,
):
    try:
        return load_result(path)

    except FileNotFoundError as exc:
        raise CLIError(
            f"file not found: {path}",
            EXIT_INPUT_ERROR,
        ) from exc

    except PermissionError as exc:
        raise CLIError(
            f"cannot read file: {path}",
            EXIT_INPUT_ERROR,
        ) from exc

    except (
        CarambolaResultFormatError
    ) as exc:
        raise CLIError(
            f"invalid result file: {exc}",
            EXIT_INPUT_ERROR,
        ) from exc

    except ValueError as exc:
        raise CLIError(
            str(exc),
            EXIT_USAGE,
        ) from exc

    except OSError as exc:
        raise CLIError(
            f"cannot read file: {path}: {exc}",
            EXIT_INPUT_ERROR,
        ) from exc


def _solve_command(
    args: argparse.Namespace,
) -> int:
    model_path = Path(
        args.model
    )

    if not str(
        model_path
    ).endswith(
        ".carambola"
    ):
        raise CLIError(
            "solve expects a .carambola model file",
            EXIT_USAGE,
        )

    if args.output is None:
        output_path = (
            _default_result_path(
                model_path
            )
        )

    else:
        output_path = Path(
            args.output
        )

    if not str(
        output_path
    ).endswith(
        ".carambola-result"
    ):
        raise CLIError(
            "output must use the "
            ".carambola-result extension",
            EXIT_USAGE,
        )

    model = _load_model_for_cli(
        model_path
    )

    try:
        solver = LinearStaticSolver(
            model
        )

        result = solver.solve()

    except RuntimeError as exc:
        raise CLIError(
            f"analysis failed: {exc}",
            EXIT_ANALYSIS_ERROR,
        ) from exc

    try:
        save_result(
            result,
            output_path,
            model,
        )

    except PermissionError as exc:
        raise CLIError(
            f"cannot write result file: "
            f"{output_path}",
            EXIT_OUTPUT_ERROR,
        ) from exc

    except OSError as exc:
        raise CLIError(
            f"cannot write result file: "
            f"{output_path}: {exc}",
            EXIT_OUTPUT_ERROR,
        ) from exc

    except ValueError as exc:
        raise CLIError(
            str(exc),
            EXIT_USAGE,
        ) from exc

    print(
        f"Result written to {output_path}"
    )

    return EXIT_SUCCESS


def _inspect_model(
    path: Path,
) -> int:
    model = _load_model_for_cli(
        path
    )

    print("Carambola model")
    print(f"File: {path}")
    print()

    print(
        f"Nodes: {model.node_count}"
    )

    print(
        f"Trusses: {model.truss_count}"
    )

    print(
        f"Beams: {model.beam_count}"
    )

    print(
        f"Shells: {model.shell_count}"
    )

    print(
        f"Supports: {model.support_count}"
    )

    print(
        "Point loads: "
        f"{model.point_load_count}"
    )

    print(
        "Uniform beam loads: "
        f"{model.uniform_beam_load_count}"
    )

    print(
        "Uniform shell pressures: "
        f"{model.uniform_shell_pressure_count}"
    )

    return EXIT_SUCCESS


def _inspect_result(
    path: Path,
) -> int:
    result = _load_result_for_cli(
        path
    )

    print("Carambola result")
    print(f"File: {path}")
    print()

    print(
        "Analysis: "
        f"{result.analysis_type}"
    )

    print()

    print(
        f"Nodes: {result.node_count}"
    )

    print(
        f"Trusses: {result.truss_count}"
    )

    print(
        f"Beams: {result.beam_count}"
    )

    print(
        f"Shells: {result.shell_count}"
    )

    print()

    print(
        "Displacement records: "
        f"{len(result.displacements)}"
    )

    print(
        "Reaction records: "
        f"{len(result.reactions)}"
    )

    return EXIT_SUCCESS


def _inspect_command(
    args: argparse.Namespace,
) -> int:
    path = Path(
        args.file
    )

    if str(path).endswith(
        ".carambola-result"
    ):
        return _inspect_result(
            path
        )

    if str(path).endswith(
        ".carambola"
    ):
        return _inspect_model(
            path
        )

    raise CLIError(
        "inspect expects a .carambola "
        "or .carambola-result file",
        EXIT_USAGE,
    )


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="carambola",
        description=(
            "Carambola finite element analysis"
        ),
    )

    subparsers = parser.add_subparsers(
        dest="command",
    )

    solve_parser = (
        subparsers.add_parser(
            "solve",
            help=(
                "solve a Carambola model"
            ),
        )
    )

    solve_parser.add_argument(
        "model",
        help=(
            "input .carambola model file"
        ),
    )

    solve_parser.add_argument(
        "-o",
        "--output",
        help=(
            "output .carambola-result file"
        ),
    )

    solve_parser.set_defaults(
        handler=_solve_command
    )

    inspect_parser = (
        subparsers.add_parser(
            "inspect",
            help=(
                "inspect a model or result file"
            ),
        )
    )

    inspect_parser.add_argument(
        "file",
        help=(
            ".carambola or "
            ".carambola-result file"
        ),
    )

    inspect_parser.set_defaults(
        handler=_inspect_command
    )

    return parser


def main(
    argv: Sequence[str] | None = None,
) -> int:
    parser = _build_parser()

    args = parser.parse_args(
        argv
    )

    if not hasattr(
        args,
        "handler",
    ):
        parser.print_help()
        return EXIT_SUCCESS

    try:
        return int(
            args.handler(args)
        )

    except CLIError as exc:
        print(
            f"carambola: error: {exc}",
            file=sys.stderr,
        )

        return exc.exit_code


if __name__ == "__main__":
    raise SystemExit(
        main()
    )
