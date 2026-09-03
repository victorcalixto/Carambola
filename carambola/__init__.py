from ._carambola import (
    AnalysisResult,
    Assembler,
    Beam3D,
    CircularSection,
    LinearStaticSolver,
    Material,
    Model,
    Node,
    PointLoad,
    RectangularSection,
    Section,
    Shell3D,
    ShellMesh,
    ShellProperty,
    Support,
    Truss3D,
    UniformBeamLoad,
    UniformShellPressure,
    plane_principal_angle,
    plane_principal_stresses,
    plane_stress_von_mises,
    rectangular_shell_mesh,
    version,
)

from .serialization import (
    CarambolaFormatError,
    load_model,
    model_from_dict,
    model_to_dict,
    save_model,
)

from .result_serialization import (
    CarambolaResultFormatError,
    SerializedResult,
    load_result,
    result_from_dict,
    result_to_dict,
    save_result,
    serialized_result_to_dict,
    validate_result_compatibility,
)


__all__ = [
    # Core model
    "Model",
    "Node",
    "Material",
    "Section",
    "RectangularSection",
    "CircularSection",

    # Elements
    "Truss3D",
    "Beam3D",
    "Shell3D",
    "ShellProperty",

    # Loads and supports
    "Support",
    "PointLoad",
    "UniformBeamLoad",
    "UniformShellPressure",

    # Analysis
    "Assembler",
    "LinearStaticSolver",
    "AnalysisResult",

    # Mesh
    "ShellMesh",
    "rectangular_shell_mesh",

    # Stress utilities
    "plane_stress_von_mises",
    "plane_principal_stresses",
    "plane_principal_angle",

    # Model serialization
    "CarambolaFormatError",
    "save_model",
    "load_model",
    "model_to_dict",
    "model_from_dict",

    # Result serialization
    "CarambolaResultFormatError",
    "SerializedResult",
    "save_result",
    "load_result",
    "result_to_dict",
    "result_from_dict",
    "serialized_result_to_dict",
    "validate_result_compatibility",

    # Package
    "version",
]
