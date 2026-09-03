import json

import carambola as cb

from carambola.cli import (
    _default_result_path,
    main,
)


def build_cli_test_model():
    model = cb.Model()

    material = cb.Material(
        "Steel",
        210.0e9,
        0.3,
        7850.0,
    )

    section = cb.RectangularSection(
        0.1,
        0.2,
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

    model.add_beam(
        n0,
        n1,
        material,
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

    return model


def test_default_result_path():
    path = _default_result_path(
        "bridge.carambola"
    )

    assert (
        path.name
        == "bridge.carambola-result"
    )


def test_cli_without_command_returns_zero():
    assert main([]) == 0


def test_cli_solve_creates_result_file(
    tmp_path,
):
    model = build_cli_test_model()

    model_path = (
        tmp_path
        / "beam.carambola"
    )

    cb.save_model(
        model,
        model_path,
    )

    return_code = main(
        [
            "solve",
            str(model_path),
        ]
    )

    result_path = (
        tmp_path
        / "beam.carambola-result"
    )

    assert return_code == 0
    assert result_path.exists()

    result = cb.load_result(
        result_path,
        model,
    )

    assert result.node_count == 2
    assert result.beam_count == 1


def test_cli_solve_custom_output(
    tmp_path,
):
    model = build_cli_test_model()

    model_path = (
        tmp_path
        / "beam.carambola"
    )

    output_path = (
        tmp_path
        / "custom.carambola-result"
    )

    cb.save_model(
        model,
        model_path,
    )

    return_code = main(
        [
            "solve",
            str(model_path),
            "--output",
            str(output_path),
        ]
    )

    assert return_code == 0
    assert output_path.exists()


def test_cli_result_is_valid_json(
    tmp_path,
):
    model = build_cli_test_model()

    model_path = (
        tmp_path
        / "beam.carambola"
    )

    cb.save_model(
        model,
        model_path,
    )

    main(
        [
            "solve",
            str(model_path),
        ]
    )

    result_path = (
        tmp_path
        / "beam.carambola-result"
    )

    data = json.loads(
        result_path.read_text(
            encoding="utf-8"
        )
    )

    assert (
        data["format"]
        == "carambola-result"
    )

    assert (
        data["analysis"]["type"]
        == "linear_static"
    )

def test_cli_inspect_model(
    tmp_path,
    capsys,
):
    model = build_cli_test_model()

    model_path = (
        tmp_path
        / "beam.carambola"
    )

    cb.save_model(
        model,
        model_path,
    )

    return_code = main(
        [
            "inspect",
            str(model_path),
        ]
    )

    output = capsys.readouterr().out

    assert return_code == 0

    assert (
        "Carambola model"
        in output
    )

    assert (
        "Nodes: 2"
        in output
    )

    assert (
        "Beams: 1"
        in output
    )

    assert (
        "Supports: 1"
        in output
    )

    assert (
        "Point loads: 1"
        in output
    )


def test_cli_inspect_result(
    tmp_path,
    capsys,
):
    model = build_cli_test_model()

    model_path = (
        tmp_path
        / "beam.carambola"
    )

    result_path = (
        tmp_path
        / "beam.carambola-result"
    )

    cb.save_model(
        model,
        model_path,
    )

    main(
        [
            "solve",
            str(model_path),
            "--output",
            str(result_path),
        ]
    )

    capsys.readouterr()

    return_code = main(
        [
            "inspect",
            str(result_path),
        ]
    )

    output = capsys.readouterr().out

    assert return_code == 0

    assert (
        "Carambola result"
        in output
    )

    assert (
        "Analysis: linear_static"
        in output
    )

    assert (
        "Nodes: 2"
        in output
    )

    assert (
        "Beams: 1"
        in output
    )

    assert (
        "Displacement records: 2"
        in output
    )

    assert (
        "Reaction records: 2"
        in output
    )

def test_cli_inspect_rejects_unknown_extension(
    tmp_path,
    capsys,
):
    path = (
        tmp_path
        / "something.json"
    )

    path.write_text(
        "{}",
        encoding="utf-8",
    )

    return_code = main(
        [
            "inspect",
            str(path),
        ]
    )

    captured = capsys.readouterr()

    assert return_code == 2

    assert (
        ".carambola"
        in captured.err
    )

    assert (
        "Traceback"
        not in captured.err
    )

def test_cli_inspect_missing_file(
    tmp_path,
    capsys,
):
    path = (
        tmp_path
        / "missing.carambola"
    )

    return_code = main(
        [
            "inspect",
            str(path),
        ]
    )

    captured = capsys.readouterr()

    assert return_code == 3

    assert (
        "file not found"
        in captured.err
    )

    assert (
        "Traceback"
        not in captured.err
    )


def test_cli_solve_missing_file(
    tmp_path,
    capsys,
):
    path = (
        tmp_path
        / "missing.carambola"
    )

    return_code = main(
        [
            "solve",
            str(path),
        ]
    )

    captured = capsys.readouterr()

    assert return_code == 3

    assert (
        "file not found"
        in captured.err
    )


def test_cli_inspect_invalid_extension(
    tmp_path,
    capsys,
):
    path = (
        tmp_path
        / "model.json"
    )

    path.write_text(
        "{}",
        encoding="utf-8",
    )

    return_code = main(
        [
            "inspect",
            str(path),
        ]
    )

    captured = capsys.readouterr()

    assert return_code == 2

    assert (
        "inspect expects"
        in captured.err
    )


def test_cli_solve_invalid_output_extension(
    tmp_path,
    capsys,
):
    model = build_cli_test_model()

    model_path = (
        tmp_path
        / "beam.carambola"
    )

    cb.save_model(
        model,
        model_path,
    )

    return_code = main(
        [
            "solve",
            str(model_path),
            "--output",
            str(
                tmp_path
                / "result.json"
            ),
        ]
    )

    captured = capsys.readouterr()

    assert return_code == 2

    assert (
        ".carambola-result"
        in captured.err
    )


def test_cli_inspect_invalid_model_file(
    tmp_path,
    capsys,
):
    path = (
        tmp_path
        / "invalid.carambola"
    )

    path.write_text(
        "{}",
        encoding="utf-8",
    )

    return_code = main(
        [
            "inspect",
            str(path),
        ]
    )

    captured = capsys.readouterr()

    assert return_code == 3

    assert (
        "invalid model file"
        in captured.err
    )


def test_cli_inspect_invalid_result_file(
    tmp_path,
    capsys,
):
    path = (
        tmp_path
        / "invalid.carambola-result"
    )

    path.write_text(
        "{}",
        encoding="utf-8",
    )

    return_code = main(
        [
            "inspect",
            str(path),
        ]
    )

    captured = capsys.readouterr()

    assert return_code == 3

    assert (
        "invalid result file"
        in captured.err
    )

def test_cli_module_main_exists():
    from carambola.cli import main as cli_main

    assert callable(cli_main)
