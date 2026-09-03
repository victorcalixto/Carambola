import json

import carambola as cb


def build_serialization_model():
    model = cb.Model()

    # --------------------------------------------------------------
    # Definitions
    # --------------------------------------------------------------

    steel = cb.Material(
        "Steel",
        210.0e9,
        0.3,
        7850.0,
    )

    rectangular = cb.RectangularSection(
        0.2,
        0.4,
    )

    circular = cb.CircularSection(
        0.1
    )

    shell_property = cb.ShellProperty(
        steel,
        0.02,
    )

    # --------------------------------------------------------------
    # Nodes
    # --------------------------------------------------------------

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

    n2 = model.add_node(
        0.0,
        2.0,
        0.0,
    )

    n3 = model.add_node(
        2.0,
        2.0,
        0.0,
    )

    # --------------------------------------------------------------
    # Elements
    # --------------------------------------------------------------

    model.add_truss(
        n0,
        n1,
        steel,
        circular,
    )

    beam = model.add_beam(
        n1,
        n3,
        steel,
        rectangular,
    )

    shell = model.add_shell(
        n0,
        n1,
        n2,
        shell_property,
    )

    # --------------------------------------------------------------
    # Boundary conditions
    # --------------------------------------------------------------

    model.add_support(
        n0,
        True,
        True,
        True,
        True,
        False,
        True,
    )

    # --------------------------------------------------------------
    # Loads
    # --------------------------------------------------------------

    model.add_point_load(
        n3,
        100.0,
        -200.0,
        -300.0,
        10.0,
        20.0,
        30.0,
    )

    model.add_uniform_beam_load(
        beam,
        1.0,
        2.0,
        3.0,
    )

    model.add_uniform_shell_pressure(
        shell,
        -5.0,
    )

    return model


def test_model_to_dict_header():
    model = cb.Model()

    data = cb.model_to_dict(model)

    assert data["format"] == "carambola"
    assert data["version"] == 1


def test_empty_model_serialization():
    model = cb.Model()

    data = cb.model_to_dict(model)

    assert data == {
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
        "uniform_shell_pressures": [],
    }


def test_model_to_dict_nodes():
    model = build_serialization_model()

    data = cb.model_to_dict(model)

    assert data["nodes"] == [
        {
            "id": 0,
            "x": 0.0,
            "y": 0.0,
            "z": 0.0,
        },
        {
            "id": 1,
            "x": 2.0,
            "y": 0.0,
            "z": 0.0,
        },
        {
            "id": 2,
            "x": 0.0,
            "y": 2.0,
            "z": 0.0,
        },
        {
            "id": 3,
            "x": 2.0,
            "y": 2.0,
            "z": 0.0,
        },
    ]


def test_model_to_dict_definitions():
    model = build_serialization_model()

    data = cb.model_to_dict(model)

    assert data["materials"] == [
        {
            "id": 0,
            "name": "Steel",
            "E": 210.0e9,
            "nu": 0.3,
            "density": 7850.0,
        }
    ]

    assert data["sections"] == [
        {
            "id": 0,
            "type": "circular",
            "radius": 0.1,
        },
        {
            "id": 1,
            "type": "rectangular",
            "width": 0.2,
            "height": 0.4,
        },
    ]

    assert data["shell_properties"] == [
        {
            "id": 0,
            "material": 0,
            "thickness": 0.02,
        }
    ]


def test_model_to_dict_elements():
    model = build_serialization_model()

    data = cb.model_to_dict(model)

    assert data["trusses"] == [
        {
            "id": 0,
            "node_start": 0,
            "node_end": 1,
            "material": 0,
            "section": 0,
        }
    ]

    assert data["beams"] == [
        {
            "id": 0,
            "node_start": 1,
            "node_end": 3,
            "material": 0,
            "section": 1,
            "orientation": [
                0.0,
                0.0,
                1.0,
            ],
        }
    ]

    assert data["shells"] == [
        {
            "id": 0,
            "nodes": [
                0,
                1,
                2,
            ],
            "property": 0,
        }
    ]


def test_model_to_dict_supports():
    model = build_serialization_model()

    data = cb.model_to_dict(model)

    assert data["supports"] == [
        {
            "node": 0,
            "ux": True,
            "uy": True,
            "uz": True,
            "rx": True,
            "ry": False,
            "rz": True,
        }
    ]


def test_model_to_dict_point_loads():
    model = build_serialization_model()

    data = cb.model_to_dict(model)

    assert data["point_loads"] == [
        {
            "node": 3,
            "fx": 100.0,
            "fy": -200.0,
            "fz": -300.0,
            "mx": 10.0,
            "my": 20.0,
            "mz": 30.0,
        }
    ]


def test_model_to_dict_uniform_beam_loads():
    model = build_serialization_model()

    data = cb.model_to_dict(model)

    assert data["uniform_beam_loads"] == [
        {
            "beam": 0,
            "qx": 1.0,
            "qy": 2.0,
            "qz": 3.0,
        }
    ]


def test_model_to_dict_uniform_shell_pressures():
    model = build_serialization_model()

    data = cb.model_to_dict(model)

    assert data[
        "uniform_shell_pressures"
    ] == [
        {
            "shell": 0,
            "pressure": -5.0,
        }
    ]


def test_model_to_dict_is_json_serializable():
    model = build_serialization_model()

    data = cb.model_to_dict(model)

    encoded = json.dumps(data)

    decoded = json.loads(encoded)

    assert decoded == data


def test_model_to_dict_reuses_shared_material():
    model = cb.Model()

    steel = cb.Material(
        "Steel",
        210.0e9,
        0.3,
        7850.0,
    )

    section_a = cb.RectangularSection(
        0.2,
        0.4,
    )

    section_b = cb.CircularSection(
        0.1
    )

    n0 = model.add_node(
        0.0,
        0.0,
        0.0,
    )

    n1 = model.add_node(
        1.0,
        0.0,
        0.0,
    )

    n2 = model.add_node(
        2.0,
        0.0,
        0.0,
    )

    model.add_truss(
        n0,
        n1,
        steel,
        section_a,
    )

    model.add_truss(
        n1,
        n2,
        steel,
        section_b,
    )

    data = cb.model_to_dict(model)

    assert len(data["materials"]) == 1

    assert (
        data["trusses"][0]["material"]
        == 0
    )

    assert (
        data["trusses"][1]["material"]
        == 0
    )


def test_model_to_dict_reuses_equivalent_definitions():
    model = cb.Model()

    steel_a = cb.Material(
        "Steel",
        210.0e9,
        0.3,
        7850.0,
    )

    steel_b = cb.Material(
        "Steel",
        210.0e9,
        0.3,
        7850.0,
    )

    section_a = cb.RectangularSection(
        0.2,
        0.4,
    )

    section_b = cb.RectangularSection(
        0.2,
        0.4,
    )

    n0 = model.add_node(
        0.0,
        0.0,
        0.0,
    )

    n1 = model.add_node(
        1.0,
        0.0,
        0.0,
    )

    n2 = model.add_node(
        2.0,
        0.0,
        0.0,
    )

    model.add_truss(
        n0,
        n1,
        steel_a,
        section_a,
    )

    model.add_truss(
        n1,
        n2,
        steel_b,
        section_b,
    )

    data = cb.model_to_dict(model)

    assert len(data["materials"]) == 1
    assert len(data["sections"]) == 1


def test_model_to_dict_rejects_non_model():
    try:
        cb.model_to_dict("not a model")
    except TypeError:
        pass
    else:
        raise AssertionError(
            "Expected TypeError"
        )


def test_model_from_dict_empty_model():
    data = {
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
        "uniform_shell_pressures": [],
    }

    model = cb.model_from_dict(data)

    assert model.node_count == 0
    assert model.truss_count == 0
    assert model.beam_count == 0
    assert model.shell_count == 0


def test_model_from_dict_reconstructs_model():
    original = build_serialization_model()

    data = cb.model_to_dict(original)

    model = cb.model_from_dict(data)

    assert model.node_count == 4
    assert model.truss_count == 1
    assert model.beam_count == 1
    assert model.shell_count == 1

    assert model.support_count == 1
    assert model.point_load_count == 1

    assert (
        model.uniform_beam_load_count
        == 1
    )

    assert (
        model.uniform_shell_pressure_count
        == 1
    )


def test_model_from_dict_reconstructs_nodes():
    original = build_serialization_model()

    data = cb.model_to_dict(original)

    model = cb.model_from_dict(data)

    assert model.node(0).x == 0.0
    assert model.node(0).y == 0.0
    assert model.node(0).z == 0.0

    assert model.node(3).x == 2.0
    assert model.node(3).y == 2.0
    assert model.node(3).z == 0.0


def test_model_from_dict_reconstructs_element_definitions():
    original = build_serialization_model()

    data = cb.model_to_dict(original)

    model = cb.model_from_dict(data)

    truss = model.truss(0)
    beam = model.beam(0)
    shell = model.shell(0)

    assert truss.material.name == "Steel"
    assert truss.material.E == 210.0e9

    assert isinstance(
        truss.section,
        cb.CircularSection,
    )

    assert truss.section.radius == 0.1

    assert isinstance(
        beam.section,
        cb.RectangularSection,
    )

    assert beam.section.width == 0.2
    assert beam.section.height == 0.4

    assert shell.property.thickness == 0.02

    assert (
        shell.property.material.name
        == "Steel"
    )


def test_model_from_dict_reconstructs_references():
    original = build_serialization_model()

    data = cb.model_to_dict(original)

    model = cb.model_from_dict(data)

    truss = model.truss(0)
    beam = model.beam(0)
    shell = model.shell(0)

    assert truss.node_start.id == 0
    assert truss.node_end.id == 1

    assert beam.node_start.id == 1
    assert beam.node_end.id == 3

    assert shell.node_a.id == 0
    assert shell.node_b.id == 1
    assert shell.node_c.id == 2

    assert model.supports[0].node.id == 0
    assert model.point_loads[0].node.id == 3

    assert (
        model.uniform_beam_loads[0]
        .beam
        .node_start
        .id
        == 1
    )

    assert (
        model.uniform_shell_pressures[0]
        .shell
        .node_a
        .id
        == 0
    )

def test_model_from_dict_preserves_beam_orientation():
    original = build_serialization_model()

    data = cb.model_to_dict(original)

    # The test beam runs along global +Y, so the orientation
    # vector must not be parallel to the beam axis.
    data["beams"][0]["orientation"] = [
        1.0,
        0.0,
        0.0,
    ]

    model = cb.model_from_dict(data)

    orientation = model.beam(0).orientation

    assert orientation[0] == 1.0
    assert orientation[1] == 0.0
    assert orientation[2] == 0.0

def test_model_from_dict_keeps_definitions_alive():
    import gc

    data = cb.model_to_dict(
        build_serialization_model()
    )

    model = cb.model_from_dict(data)

    gc.collect()

    truss = model.truss(0)
    beam = model.beam(0)
    shell = model.shell(0)

    assert truss.material.name == "Steel"
    assert beam.material.name == "Steel"

    assert truss.section.radius == 0.1

    assert beam.section.width == 0.2
    assert beam.section.height == 0.4

    assert shell.property.thickness == 0.02

    assert (
        shell.property.material.name
        == "Steel"
    )


def test_model_from_dict_rejects_non_dictionary():
    try:
        cb.model_from_dict("invalid")
    except TypeError:
        pass
    else:
        raise AssertionError(
            "Expected TypeError"
        )


def test_model_from_dict_rejects_wrong_format():
    data = {
        "format": "something-else",
        "version": 1,
    }

    try:
        cb.model_from_dict(data)
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected ValueError"
        )


def test_model_from_dict_rejects_unsupported_version():
    data = {
        "format": "carambola",
        "version": 999,
    }

    try:
        cb.model_from_dict(data)
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected ValueError"
        )


def test_save_model_creates_carambola_file(
    tmp_path,
):
    model = build_serialization_model()

    path = tmp_path / "model.carambola"

    cb.save_model(model, path)

    assert path.exists()
    assert path.is_file()


def test_save_model_writes_json(
    tmp_path,
):
    model = build_serialization_model()

    path = tmp_path / "model.carambola"

    cb.save_model(model, path)

    text = path.read_text(
        encoding="utf-8"
    )

    data = json.loads(text)

    assert data["format"] == "carambola"
    assert data["version"] == 1

    assert len(data["nodes"]) == 4
    assert len(data["trusses"]) == 1
    assert len(data["beams"]) == 1
    assert len(data["shells"]) == 1


def test_load_model_reconstructs_model(
    tmp_path,
):
    original = build_serialization_model()

    path = tmp_path / "model.carambola"

    cb.save_model(
        original,
        path,
    )

    model = cb.load_model(path)

    assert model.node_count == 4
    assert model.truss_count == 1
    assert model.beam_count == 1
    assert model.shell_count == 1

    assert model.support_count == 1
    assert model.point_load_count == 1

    assert (
        model.uniform_beam_load_count
        == 1
    )

    assert (
        model.uniform_shell_pressure_count
        == 1
    )


def test_load_model_preserves_model_data(
    tmp_path,
):
    original = build_serialization_model()

    path = tmp_path / "model.carambola"

    cb.save_model(
        original,
        path,
    )

    loaded = cb.load_model(path)

    original_data = cb.model_to_dict(
        original
    )

    loaded_data = cb.model_to_dict(
        loaded
    )

    assert loaded_data == original_data


def test_save_model_requires_carambola_extension(
    tmp_path,
):
    model = build_serialization_model()

    path = tmp_path / "model.json"

    try:
        cb.save_model(
            model,
            path,
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected ValueError"
        )


def test_load_model_requires_carambola_extension(
    tmp_path,
):
    path = tmp_path / "model.json"

    path.write_text(
        "{}",
        encoding="utf-8",
    )

    try:
        cb.load_model(path)
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected ValueError"
        )


def test_save_model_accepts_string_path(
    tmp_path,
):
    model = build_serialization_model()

    path = tmp_path / "model.carambola"

    cb.save_model(
        model,
        str(path),
    )

    assert path.exists()


def test_load_model_accepts_string_path(
    tmp_path,
):
    original = build_serialization_model()

    path = tmp_path / "model.carambola"

    cb.save_model(
        original,
        path,
    )

    model = cb.load_model(
        str(path)
    )

    assert model.node_count == 4


def test_save_model_writes_utf8_material_name(
    tmp_path,
):
    model = cb.Model()

    material = cb.Material(
        "Aço estrutural",
        210.0e9,
        0.3,
        7850.0,
    )

    section = cb.CircularSection(
        0.1
    )

    n0 = model.add_node(
        0.0,
        0.0,
        0.0,
    )

    n1 = model.add_node(
        1.0,
        0.0,
        0.0,
    )

    model.add_truss(
        n0,
        n1,
        material,
        section,
    )

    path = tmp_path / "unicode.carambola"

    cb.save_model(
        model,
        path,
    )

    text = path.read_text(
        encoding="utf-8"
    )

    assert "Aço estrutural" in text

    loaded = cb.load_model(path)

    assert (
        loaded.truss(0).material.name
        == "Aço estrutural"
    )

def test_model_from_dict_rejects_missing_top_level_field():
    data = cb.model_to_dict(
        build_serialization_model()
    )

    del data["nodes"]

    try:
        cb.model_from_dict(data)
    except cb.CarambolaFormatError:
        pass
    else:
        raise AssertionError(
            "Expected CarambolaFormatError"
        )


def test_model_from_dict_rejects_non_list_collection():
    data = cb.model_to_dict(
        build_serialization_model()
    )

    data["nodes"] = {}

    try:
        cb.model_from_dict(data)
    except cb.CarambolaFormatError:
        pass
    else:
        raise AssertionError(
            "Expected CarambolaFormatError"
        )


def test_model_from_dict_rejects_duplicate_ids():
    data = cb.model_to_dict(
        build_serialization_model()
    )

    data["nodes"][1]["id"] = 0

    try:
        cb.model_from_dict(data)
    except cb.CarambolaFormatError:
        pass
    else:
        raise AssertionError(
            "Expected CarambolaFormatError"
        )


def test_model_from_dict_rejects_unknown_node_reference():
    data = cb.model_to_dict(
        build_serialization_model()
    )

    data["trusses"][0]["node_end"] = 999

    try:
        cb.model_from_dict(data)
    except cb.CarambolaFormatError:
        pass
    else:
        raise AssertionError(
            "Expected CarambolaFormatError"
        )


def test_model_from_dict_rejects_unknown_material_reference():
    data = cb.model_to_dict(
        build_serialization_model()
    )

    data["beams"][0]["material"] = 999

    try:
        cb.model_from_dict(data)
    except cb.CarambolaFormatError:
        pass
    else:
        raise AssertionError(
            "Expected CarambolaFormatError"
        )


def test_model_from_dict_rejects_invalid_shell_nodes():
    data = cb.model_to_dict(
        build_serialization_model()
    )

    data["shells"][0]["nodes"] = [
        0,
        1,
    ]

    try:
        cb.model_from_dict(data)
    except cb.CarambolaFormatError:
        pass
    else:
        raise AssertionError(
            "Expected CarambolaFormatError"
        )


def test_model_from_dict_rejects_unknown_shell_property():
    data = cb.model_to_dict(
        build_serialization_model()
    )

    data["shells"][0]["property"] = 999

    try:
        cb.model_from_dict(data)
    except cb.CarambolaFormatError:
        pass
    else:
        raise AssertionError(
            "Expected CarambolaFormatError"
        )


def test_model_from_dict_rejects_unknown_beam_load_reference():
    data = cb.model_to_dict(
        build_serialization_model()
    )

    data["uniform_beam_loads"][0]["beam"] = 999

    try:
        cb.model_from_dict(data)
    except cb.CarambolaFormatError:
        pass
    else:
        raise AssertionError(
            "Expected CarambolaFormatError"
        )


def test_model_from_dict_rejects_unknown_shell_pressure_reference():
    data = cb.model_to_dict(
        build_serialization_model()
    )

    data[
        "uniform_shell_pressures"
    ][0]["shell"] = 999

    try:
        cb.model_from_dict(data)
    except cb.CarambolaFormatError:
        pass
    else:
        raise AssertionError(
            "Expected CarambolaFormatError"
        )


def test_model_from_dict_rejects_unsupported_section_type():
    data = cb.model_to_dict(
        build_serialization_model()
    )

    data["sections"][0]["type"] = "triangle"

    try:
        cb.model_from_dict(data)
    except cb.CarambolaFormatError:
        pass
    else:
        raise AssertionError(
            "Expected CarambolaFormatError"
        )


def test_load_model_rejects_invalid_json(
    tmp_path,
):
    path = tmp_path / "broken.carambola"

    path.write_text(
        "{ definitely not json",
        encoding="utf-8",
    )

    try:
        cb.load_model(path)
    except cb.CarambolaFormatError:
        pass
    else:
        raise AssertionError(
            "Expected CarambolaFormatError"
        )


def test_model_from_dict_wraps_invalid_geometry():
    data = cb.model_to_dict(
        build_serialization_model()
    )

    data["nodes"][1]["x"] = 0.0
    data["nodes"][1]["y"] = 0.0
    data["nodes"][1]["z"] = 0.0

    try:
        cb.model_from_dict(data)
    except cb.CarambolaFormatError as exc:
        assert "truss" in str(exc).lower()
    else:
        raise AssertionError(
            "Expected CarambolaFormatError"
             )

def test_model_dictionary_round_trip_is_stable():
    original = build_serialization_model()

    data_1 = cb.model_to_dict(original)

    reconstructed = cb.model_from_dict(
        data_1
    )

    data_2 = cb.model_to_dict(
        reconstructed
    )

    assert data_2 == data_1


def test_model_file_round_trip_is_stable(
    tmp_path,
):
    original = build_serialization_model()

    path = tmp_path / "model.carambola"

    cb.save_model(
        original,
        path,
    )

    loaded = cb.load_model(path)

    assert (
        cb.model_to_dict(loaded)
        == cb.model_to_dict(original)
    )


def test_repeated_file_round_trip_is_stable(
    tmp_path,
):
    original = build_serialization_model()

    first_path = (
        tmp_path
        / "first.carambola"
    )

    second_path = (
        tmp_path
        / "second.carambola"
    )

    cb.save_model(
        original,
        first_path,
    )

    loaded = cb.load_model(
        first_path
    )

    cb.save_model(
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


def test_repeated_file_round_trip_text_is_deterministic(
    tmp_path,
):
    original = build_serialization_model()

    first_path = (
        tmp_path
        / "first.carambola"
    )

    second_path = (
        tmp_path
        / "second.carambola"
    )

    cb.save_model(
        original,
        first_path,
    )

    loaded = cb.load_model(
        first_path
    )

    cb.save_model(
        loaded,
        second_path,
    )

    first_text = first_path.read_text(
        encoding="utf-8"
    )

    second_text = second_path.read_text(
        encoding="utf-8"
    )

    assert second_text == first_text


def test_round_trip_preserves_all_collection_counts(
    tmp_path,
):
    original = build_serialization_model()

    path = tmp_path / "model.carambola"

    cb.save_model(
        original,
        path,
    )

    loaded = cb.load_model(path)

    assert (
        loaded.node_count
        == original.node_count
    )

    assert (
        loaded.truss_count
        == original.truss_count
    )

    assert (
        loaded.beam_count
        == original.beam_count
    )

    assert (
        loaded.shell_count
        == original.shell_count
    )

    assert (
        loaded.support_count
        == original.support_count
    )

    assert (
        loaded.point_load_count
        == original.point_load_count
    )

    assert (
        loaded.uniform_beam_load_count
        == original.uniform_beam_load_count
    )

    assert (
        loaded.uniform_shell_pressure_count
        == original.uniform_shell_pressure_count
    )


def test_round_trip_definitions_remain_alive(
    tmp_path,
):
    import gc

    original = build_serialization_model()

    path = tmp_path / "model.carambola"

    cb.save_model(
        original,
        path,
    )

    loaded = cb.load_model(path)

    gc.collect()

    truss = loaded.truss(0)
    beam = loaded.beam(0)
    shell = loaded.shell(0)

    assert truss.material.name == "Steel"
    assert beam.material.name == "Steel"

    assert (
        shell.property.material.name
        == "Steel"
    )

    assert truss.section.radius > 0.0
    assert beam.section.width > 0.0
    assert shell.property.thickness > 0.0


def test_round_trip_preserves_beam_orientation(
    tmp_path,
):
    original = build_serialization_model()

    original_data = cb.model_to_dict(
        original
    )

    path = tmp_path / "model.carambola"

    cb.save_model(
        original,
        path,
    )

    loaded = cb.load_model(path)

    loaded_data = cb.model_to_dict(
        loaded
    )

    assert (
        loaded_data["beams"][0]["orientation"]
        == original_data["beams"][0]["orientation"]
    )


def test_round_trip_preserves_load_values(
    tmp_path,
):
    original = build_serialization_model()

    path = tmp_path / "model.carambola"

    cb.save_model(
        original,
        path,
    )

    loaded = cb.load_model(path)

    original_data = cb.model_to_dict(
        original
    )

    loaded_data = cb.model_to_dict(
        loaded
    )

    assert (
        loaded_data["point_loads"]
        == original_data["point_loads"]
    )

    assert (
        loaded_data["uniform_beam_loads"]
        == original_data["uniform_beam_loads"]
    )

    assert (
        loaded_data[
            "uniform_shell_pressures"
        ]
        == original_data[
            "uniform_shell_pressures"
        ]
    )
