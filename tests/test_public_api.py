import carambola as cb


def public_names(obj):
    return {
        name
        for name in dir(obj)
        if not name.startswith("_")
    }


def test_core_public_types_exist():
    expected = {
        "Node",
        "Material",
        "RectangularSection",
        "CircularSection",
        "Truss3D",
        "Beam3D",
        "ShellProperty",
        "Shell3D",
        "Support",
        "PointLoad",
        "UniformBeamLoad",
        "UniformShellPressure",
        "Model",
        "Assembler",
        "LinearStaticSolver",
        "AnalysisResult",
        "ShellMesh",
    }

    for name in expected:
        assert hasattr(cb, name), (
            f"Missing public API symbol: {name}"
        )


def test_public_utility_functions_exist():
    expected = {
        "rectangular_shell_mesh",
        "plane_stress_von_mises",
        "plane_principal_stresses",
        "plane_principal_angle",
        "version",
    }

    for name in expected:
        assert hasattr(cb, name), (
            f"Missing public API function: {name}"
        )


def test_shell3d_public_api():
    expected = {
        "area",
        "bending_curvature",
        "bending_moments",
        "bending_stress",
        "local_x",
        "local_y",
        "local_z",
        "membrane_strain",
        "membrane_stress",
        "pressure_load_vector",
        "rotation_matrix",
        "stiffness_matrix",
        "node_a",
        "node_b",
        "node_c",
        "property",
    }

    assert public_names(cb.Shell3D) == expected


def test_shell3d_low_level_api_is_internal():
    internal = {
        "_strain_displacement_matrix",
        "_constitutive_matrix",
        "_local_membrane_stiffness_matrix",
        "_membrane_stiffness_matrix",
        "_local_membrane_displacements",
        "_bending_constitutive_matrix",
        "_full_transformation_matrix",
        "_local_bending_displacements",
        "_local_coordinates",
        "_bending_edge_geometry",
        "_bending_edge_coefficients",
        "_bending_shape_functions",
        "_bending_shape_function_derivatives",
        "_dkt_rotation_coefficients",
        "_dkt_rotation_interpolation",
        "_dkt_rotation_derivatives",
        "_dkt_bending_strain_displacement_matrix",
        "_local_bending_stiffness_matrix",
        "_local_stiffness_matrix",
        "_drilling_stiffness",
    }

    for name in internal:
        assert hasattr(cb.Shell3D, name)

    public = public_names(cb.Shell3D)

    for name in internal:
        assert name not in public

def test_model_collection_api():
    expected = {
        "trusses",
        "beams",
        "shells",
        "supports",
        "point_loads",
        "uniform_beam_loads",
        "uniform_shell_pressures",
        "node_count",
        "truss_count",
        "beam_count",
        "shell_count",
        "support_count",
        "point_load_count",
        "uniform_beam_load_count",
        "uniform_shell_pressure_count",
    }

    public = public_names(cb.Model)

    assert expected <= public

def test_analysis_result_core_api():
    expected = {
        "displacements",
        "reactions",
        "node_displacement",
        "node_rotation",
        "node_reaction",
        "node_moment_reaction",
        "truss_deformation",
        "truss_strain",
        "truss_stress",
        "truss_force",
        "beam_local_end_forces",
        "beam_axial_force",
        "beam_torsion",
        "beam_shear_y",
        "beam_shear_z",
        "beam_moment_y",
        "beam_moment_z",
        "shell_membrane_strain",
        "shell_membrane_stress",
        "shell_bending_curvature",
        "shell_bending_moments",
        "shell_bending_stress",
        "shell_top_stress",
        "shell_bottom_stress",
        "shell_top_von_mises",
        "shell_bottom_von_mises",
        "shell_top_principal_stresses",
        "shell_bottom_principal_stresses",
        "shell_top_principal_angle",
        "shell_bottom_principal_angle",
    }

    public = public_names(cb.AnalysisResult)

    assert expected <= public
