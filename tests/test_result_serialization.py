import json

import carambola as cb


def build_result_test_model():
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
        [
            0.0,
            0.0,
            1.0,
        ],
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


def solve_result_test_model():
    model = build_result_test_model()

    solver = cb.LinearStaticSolver(
        model
    )

    result = solver.solve()

    return model, result


def test_result_to_dict_header():
    model, result = (
        solve_result_test_model()
    )

    data = cb.result_to_dict(
        result,
        model,
    )

    assert (
        data["format"]
        == "carambola-result"
    )

    assert data["version"] == 1

    assert data["analysis"] == {
        "type": "linear_static",
    }


def test_result_to_dict_model_info():
    model, result = (
        solve_result_test_model()
    )

    data = cb.result_to_dict(
        result,
        model,
    )

    assert data["model"] == {
        "node_count": 2,
        "truss_count": 0,
        "beam_count": 1,
        "shell_count": 0,
    }


def test_result_to_dict_displacements():
    model, result = (
        solve_result_test_model()
    )

    data = cb.result_to_dict(
        result,
        model,
    )

    assert len(
        data["displacements"]
    ) == model.node_count

    fixed = data[
        "displacements"
    ][0]

    free = data[
        "displacements"
    ][1]

    assert fixed["node"] == 0
    assert fixed["ux"] == 0.0
    assert fixed["uy"] == 0.0
    assert fixed["uz"] == 0.0
    assert fixed["rx"] == 0.0
    assert fixed["ry"] == 0.0
    assert fixed["rz"] == 0.0

    assert free["node"] == 1

    assert free["uz"] < 0.0


def test_result_to_dict_reactions():
    model, result = (
        solve_result_test_model()
    )

    data = cb.result_to_dict(
        result,
        model,
    )

    assert len(
        data["reactions"]
    ) == model.node_count

    fixed = data["reactions"][0]
    free = data["reactions"][1]

    assert fixed["node"] == 0

    assert abs(
        fixed["fz"] - 1000.0
    ) < 1.0e-9

    assert free["node"] == 1

    assert abs(
        free["fx"]
    ) < 1.0e-9

    assert abs(
        free["fy"]
    ) < 1.0e-9

    assert abs(
        free["fz"]
    ) < 1.0e-9


def test_result_to_dict_is_json_serializable():
    model, result = (
        solve_result_test_model()
    )

    data = cb.result_to_dict(
        result,
        model,
    )

    text = json.dumps(data)

    decoded = json.loads(text)

    assert decoded == data


def test_result_to_dict_rejects_non_result():
    model = build_result_test_model()

    try:
        cb.result_to_dict(
            object(),
            model,
        )

    except TypeError as exc:
        assert "AnalysisResult" in str(
            exc
        )

    else:
        raise AssertionError(
            "Expected TypeError"
        )


def test_result_to_dict_rejects_non_model():
    model, result = (
        solve_result_test_model()
    )

    try:
        cb.result_to_dict(
            result,
            object(),
        )

    except TypeError as exc:
        assert "Model" in str(exc)

    else:
        raise AssertionError(
            "Expected TypeError"
        )


def test_result_from_dict_returns_serialized_result():
    model, result = (
        solve_result_test_model()
    )

    data = cb.result_to_dict(
        result,
        model,
    )

    stored = cb.result_from_dict(
        data
    )

    assert isinstance(
        stored,
        cb.SerializedResult,
    )

    assert (
        stored.analysis_type
        == "linear_static"
    )


def test_result_from_dict_model_info():
    model, result = (
        solve_result_test_model()
    )

    data = cb.result_to_dict(
        result,
        model,
    )

    stored = cb.result_from_dict(
        data
    )

    assert stored.node_count == 2
    assert stored.truss_count == 0
    assert stored.beam_count == 1
    assert stored.shell_count == 0


def test_result_from_dict_displacement_access():
    model, result = (
        solve_result_test_model()
    )

    data = cb.result_to_dict(
        result,
        model,
    )

    stored = cb.result_from_dict(
        data
    )

    displacement = (
        stored.node_displacement(1)
    )

    rotation = (
        stored.node_rotation(1)
    )

    assert len(displacement) == 3
    assert len(rotation) == 3

    assert displacement[2] < 0.0


def test_result_from_dict_reaction_access():
    model, result = (
        solve_result_test_model()
    )

    data = cb.result_to_dict(
        result,
        model,
    )

    stored = cb.result_from_dict(
        data
    )

    reaction = (
        stored.node_reaction(0)
    )

    moment = (
        stored.node_moment_reaction(0)
    )

    assert abs(
        reaction[2] - 1000.0
    ) < 1.0e-9

    assert len(moment) == 3


def test_result_from_dict_preserves_values():
    model, result = (
        solve_result_test_model()
    )

    data = cb.result_to_dict(
        result,
        model,
    )

    stored = cb.result_from_dict(
        data
    )

    assert (
        stored.displacements
        == data["displacements"]
    )

    assert (
        stored.reactions
        == data["reactions"]
    )


def test_result_from_dict_rejects_non_dict():
    try:
        cb.result_from_dict(
            []
        )

    except TypeError as exc:
        assert "dictionary" in str(
            exc
        )

    else:
        raise AssertionError(
            "Expected TypeError"
        )


def test_save_and_load_result(
    tmp_path,
):
    model, result = (
        solve_result_test_model()
    )

    path = (
        tmp_path
        / "analysis.carambola-result"
    )

    cb.save_result(
        result,
        path,
        model,
    )

    loaded = cb.load_result(
        path
    )

    assert isinstance(
        loaded,
        cb.SerializedResult,
    )

    assert loaded.node_count == 2
    assert loaded.beam_count == 1


def test_save_result_writes_json(
    tmp_path,
):
    model, result = (
        solve_result_test_model()
    )

    path = (
        tmp_path
        / "analysis.carambola-result"
    )

    cb.save_result(
        result,
        path,
        model,
    )

    data = json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )

    assert (
        data["format"]
        == "carambola-result"
    )

    assert data["version"] == 1


def test_save_result_has_trailing_newline(
    tmp_path,
):
    model, result = (
        solve_result_test_model()
    )

    path = (
        tmp_path
        / "analysis.carambola-result"
    )

    cb.save_result(
        result,
        path,
        model,
    )

    text = path.read_text(
        encoding="utf-8"
    )

    assert text.endswith("\n")


def test_save_serialized_result(
    tmp_path,
):
    model, result = (
        solve_result_test_model()
    )

    data = cb.result_to_dict(
        result,
        model,
    )

    stored = cb.result_from_dict(
        data
    )

    path = (
        tmp_path
        / "analysis.carambola-result"
    )

    cb.save_result(
        stored,
        path,
    )

    loaded = cb.load_result(
        path
    )

    assert (
        loaded.displacements
        == stored.displacements
    )

    assert (
        loaded.reactions
        == stored.reactions
    )


def test_save_result_requires_model_for_analysis_result(
    tmp_path,
):
    model, result = (
        solve_result_test_model()
    )

    path = (
        tmp_path
        / "analysis.carambola-result"
    )

    try:
        cb.save_result(
            result,
            path,
        )

    except TypeError as exc:
        assert "requires a Model" in str(
            exc
        )

    else:
        raise AssertionError(
            "Expected TypeError"
        )


def test_result_file_extension_required(
    tmp_path,
):
    model, result = (
        solve_result_test_model()
    )

    path = tmp_path / "analysis.json"

    try:
        cb.save_result(
            result,
            path,
            model,
        )

    except ValueError as exc:
        assert (
            ".carambola-result"
            in str(exc)
        )

    else:
        raise AssertionError(
            "Expected ValueError"
        )


def test_load_result_rejects_wrong_extension(
    tmp_path,
):
    path = tmp_path / "analysis.json"

    path.write_text(
        "{}",
        encoding="utf-8",
    )

    try:
        cb.load_result(path)

    except ValueError as exc:
        assert (
            ".carambola-result"
            in str(exc)
        )

    else:
        raise AssertionError(
            "Expected ValueError"
        )


def test_load_result_invalid_json(
    tmp_path,
):
    path = (
        tmp_path
        / "analysis.carambola-result"
    )

    path.write_text(
        "{ invalid json",
        encoding="utf-8",
    )

    try:
        cb.load_result(path)

    except ValueError as exc:
        assert (
            "Invalid Carambola result JSON"
            in str(exc)
        )

    else:
        raise AssertionError(
            "Expected ValueError"
        )

def test_result_from_dict_rejects_missing_field():
    model, result = (
        solve_result_test_model()
    )

    data = cb.result_to_dict(
        result,
        model,
    )

    del data["reactions"]

    try:
        cb.result_from_dict(
            data
        )

    except (
        cb.CarambolaResultFormatError
    ) as exc:
        assert "reactions" in str(
            exc
        )

    else:
        raise AssertionError(
            "Expected "
            "CarambolaResultFormatError"
        )


def test_result_from_dict_rejects_wrong_format():
    model, result = (
        solve_result_test_model()
    )

    data = cb.result_to_dict(
        result,
        model,
    )

    data["format"] = "something-else"

    try:
        cb.result_from_dict(
            data
        )

    except (
        cb.CarambolaResultFormatError
    ):
        pass

    else:
        raise AssertionError(
            "Expected "
            "CarambolaResultFormatError"
        )


def test_result_from_dict_rejects_wrong_version():
    model, result = (
        solve_result_test_model()
    )

    data = cb.result_to_dict(
        result,
        model,
    )

    data["version"] = 999

    try:
        cb.result_from_dict(
            data
        )

    except (
        cb.CarambolaResultFormatError
    ):
        pass

    else:
        raise AssertionError(
            "Expected "
            "CarambolaResultFormatError"
        )


def test_result_from_dict_rejects_invalid_analysis():
    model, result = (
        solve_result_test_model()
    )

    data = cb.result_to_dict(
        result,
        model,
    )

    data["analysis"]["type"] = (
        "modal"
    )

    try:
        cb.result_from_dict(
            data
        )

    except (
        cb.CarambolaResultFormatError
    ):
        pass

    else:
        raise AssertionError(
            "Expected "
            "CarambolaResultFormatError"
        )


def test_result_from_dict_rejects_invalid_count():
    model, result = (
        solve_result_test_model()
    )

    data = cb.result_to_dict(
        result,
        model,
    )

    data["model"]["node_count"] = -1

    try:
        cb.result_from_dict(
            data
        )

    except (
        cb.CarambolaResultFormatError
    ):
        pass

    else:
        raise AssertionError(
            "Expected "
            "CarambolaResultFormatError"
        )


def test_result_from_dict_rejects_duplicate_node_ids():
    model, result = (
        solve_result_test_model()
    )

    data = cb.result_to_dict(
        result,
        model,
    )

    data["displacements"][1][
        "node"
    ] = 0

    try:
        cb.result_from_dict(
            data
        )

    except (
        cb.CarambolaResultFormatError
    ) as exc:
        assert "duplicate" in str(
            exc
        )

    else:
        raise AssertionError(
            "Expected "
            "CarambolaResultFormatError"
        )


def test_result_from_dict_rejects_unknown_node():
    model, result = (
        solve_result_test_model()
    )

    data = cb.result_to_dict(
        result,
        model,
    )

    data["reactions"][1][
        "node"
    ] = 100

    try:
        cb.result_from_dict(
            data
        )

    except (
        cb.CarambolaResultFormatError
    ) as exc:
        assert "unknown node" in str(
            exc
        )

    else:
        raise AssertionError(
            "Expected "
            "CarambolaResultFormatError"
        )


def test_result_from_dict_rejects_wrong_result_count():
    model, result = (
        solve_result_test_model()
    )

    data = cb.result_to_dict(
        result,
        model,
    )

    data["displacements"].pop()

    try:
        cb.result_from_dict(
            data
        )

    except (
        cb.CarambolaResultFormatError
    ) as exc:
        assert "exactly" in str(
            exc
        )

    else:
        raise AssertionError(
            "Expected "
            "CarambolaResultFormatError"
        )


def test_result_from_dict_rejects_missing_component():
    model, result = (
        solve_result_test_model()
    )

    data = cb.result_to_dict(
        result,
        model,
    )

    del data[
        "displacements"
    ][0]["uz"]

    try:
        cb.result_from_dict(
            data
        )

    except (
        cb.CarambolaResultFormatError
    ) as exc:
        assert "uz" in str(
            exc
        )

    else:
        raise AssertionError(
            "Expected "
            "CarambolaResultFormatError"
        )


def test_result_from_dict_rejects_nan():
    model, result = (
        solve_result_test_model()
    )

    data = cb.result_to_dict(
        result,
        model,
    )

    data["displacements"][0][
        "ux"
    ] = float("nan")

    try:
        cb.result_from_dict(
            data
        )

    except (
        cb.CarambolaResultFormatError
    ) as exc:
        assert "finite" in str(
            exc
        )

    else:
        raise AssertionError(
            "Expected "
            "CarambolaResultFormatError"
        )


def test_result_from_dict_rejects_infinity():
    model, result = (
        solve_result_test_model()
    )

    data = cb.result_to_dict(
        result,
        model,
    )

    data["reactions"][0][
        "fz"
    ] = float("inf")

    try:
        cb.result_from_dict(
            data
        )

    except (
        cb.CarambolaResultFormatError
    ) as exc:
        assert "finite" in str(
            exc
        )

    else:
        raise AssertionError(
            "Expected "
            "CarambolaResultFormatError"
        )


def test_result_compatibility_accepts_matching_model():
    model, result = (
        solve_result_test_model()
    )

    stored = cb.result_from_dict(
        cb.result_to_dict(
            result,
            model,
        )
    )

    cb.validate_result_compatibility(
        stored,
        model,
    )


def test_result_compatibility_rejects_different_model():
    model, result = (
        solve_result_test_model()
    )

    stored = cb.result_from_dict(
        cb.result_to_dict(
            result,
            model,
        )
    )

    other = cb.Model()

    try:
        cb.validate_result_compatibility(
            stored,
            other,
        )

    except (
        cb.CarambolaResultFormatError
    ) as exc:
        assert "not compatible" in str(
            exc
        )

    else:
        raise AssertionError(
            "Expected "
            "CarambolaResultFormatError"
        )


def test_load_result_checks_model_compatibility(
    tmp_path,
):
    model, result = (
        solve_result_test_model()
    )

    path = (
        tmp_path
        / "analysis.carambola-result"
    )

    cb.save_result(
        result,
        path,
        model,
    )

    loaded = cb.load_result(
        path,
        model,
    )

    assert loaded.node_count == 2


def test_load_result_rejects_incompatible_model(
    tmp_path,
):
    model, result = (
        solve_result_test_model()
    )

    path = (
        tmp_path
        / "analysis.carambola-result"
    )

    cb.save_result(
        result,
        path,
        model,
    )

    other = cb.Model()

    try:
        cb.load_result(
            path,
            other,
        )

    except (
        cb.CarambolaResultFormatError
    ):
        pass

    else:
        raise AssertionError(
            "Expected "
            "CarambolaResultFormatError"
        )

def test_result_dictionary_round_trip_is_stable():
    model, result = (
        solve_result_test_model()
    )

    data_1 = cb.result_to_dict(
        result,
        model,
    )

    stored = cb.result_from_dict(
        data_1
    )

    data_2 = (
        cb.serialized_result_to_dict(
            stored
        )
    )

    assert data_2 == data_1


def test_result_file_round_trip_is_stable(
    tmp_path,
):
    model, result = (
        solve_result_test_model()
    )

    path = (
        tmp_path
        / "analysis.carambola-result"
    )

    original_data = cb.result_to_dict(
        result,
        model,
    )

    cb.save_result(
        result,
        path,
        model,
    )

    loaded = cb.load_result(
        path,
        model,
    )

    loaded_data = (
        cb.serialized_result_to_dict(
            loaded
        )
    )

    assert loaded_data == original_data


def test_result_repeated_file_round_trip_is_stable(
    tmp_path,
):
    model, result = (
        solve_result_test_model()
    )

    first_path = (
        tmp_path
        / "first.carambola-result"
    )

    second_path = (
        tmp_path
        / "second.carambola-result"
    )

    cb.save_result(
        result,
        first_path,
        model,
    )

    loaded = cb.load_result(
        first_path,
        model,
    )

    cb.save_result(
        loaded,
        second_path,
    )

    first_data = json.loads(
        first_path.read_text(
            encoding="utf-8"
        )
    )

    second_data = json.loads(
        second_path.read_text(
            encoding="utf-8"
        )
    )

    assert second_data == first_data


def test_result_repeated_file_text_is_deterministic(
    tmp_path,
):
    model, result = (
        solve_result_test_model()
    )

    first_path = (
        tmp_path
        / "first.carambola-result"
    )

    second_path = (
        tmp_path
        / "second.carambola-result"
    )

    cb.save_result(
        result,
        first_path,
        model,
    )

    loaded = cb.load_result(
        first_path,
        model,
    )

    cb.save_result(
        loaded,
        second_path,
    )

    first_text = (
        first_path.read_text(
            encoding="utf-8"
        )
    )

    second_text = (
        second_path.read_text(
            encoding="utf-8"
        )
    )

    assert second_text == first_text


def test_loaded_result_matches_live_nodal_results(
    tmp_path,
):
    model, result = (
        solve_result_test_model()
    )

    path = (
        tmp_path
        / "analysis.carambola-result"
    )

    cb.save_result(
        result,
        path,
        model,
    )

    loaded = cb.load_result(
        path,
        model,
    )

    for node_id in range(
        model.node_count
    ):
        node = model.node(
            node_id
        )

        live_displacement = (
            result.node_displacement(
                node
            )
        )

        live_rotation = (
            result.node_rotation(
                node
            )
        )

        live_reaction = (
            result.node_reaction(
                node
            )
        )

        live_moment_reaction = (
            result.node_moment_reaction(
                node
            )
        )

        stored_displacement = (
            loaded.node_displacement(
                node_id
            )
        )

        stored_rotation = (
            loaded.node_rotation(
                node_id
            )
        )

        stored_reaction = (
            loaded.node_reaction(
                node_id
            )
        )

        stored_moment_reaction = (
            loaded.node_moment_reaction(
                node_id
            )
        )

        for i in range(3):
            assert (
                stored_displacement[i]
                == float(
                    live_displacement[i]
                )
            )

            assert (
                stored_rotation[i]
                == float(
                    live_rotation[i]
                )
            )

            assert (
                stored_reaction[i]
                == float(
                    live_reaction[i]
                )
            )

            assert (
                stored_moment_reaction[i]
                == float(
                    live_moment_reaction[i]
                )
            )


def test_loaded_result_preserves_model_metadata(
    tmp_path,
):
    model, result = (
        solve_result_test_model()
    )

    path = (
        tmp_path
        / "analysis.carambola-result"
    )

    cb.save_result(
        result,
        path,
        model,
    )

    loaded = cb.load_result(
        path,
        model,
    )

    assert (
        loaded.node_count
        == model.node_count
    )

    assert (
        loaded.truss_count
        == model.truss_count
    )

    assert (
        loaded.beam_count
        == model.beam_count
    )

    assert (
        loaded.shell_count
        == model.shell_count
    )
