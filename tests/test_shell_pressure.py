import numpy as np
import pytest

import carambola as cb


def make_pressure_model():
    model = cb.Model()

    n0 = model.add_node(0.0, 0.0, 0.0)
    n1 = model.add_node(2.0, 0.0, 0.0)
    n2 = model.add_node(0.0, 1.0, 0.0)

    material = cb.Material(
        "Steel",
        200e9,
        0.3,
        7850.0,
    )

    prop = cb.ShellProperty(
        material,
        0.01,
    )

    shell = model.add_shell(
        n0,
        n1,
        n2,
        prop,
    )

    return model, shell, n0, n1, n2


def test_model_add_uniform_shell_pressure():
    model, shell, *_ = make_pressure_model()

    load = model.add_uniform_shell_pressure(
        shell,
        -900.0,
    )

    assert load.pressure == pytest.approx(
        -900.0
    )

    assert (
        model.uniform_shell_pressure_count
        == 1
    )


def test_shell_pressure_assembled_force_vector():
    model, shell, *_ = make_pressure_model()

    model.add_uniform_shell_pressure(
        shell,
        -900.0,
    )

    f = cb.Assembler(
        model
    ).force_vector()

    expected = np.zeros(18)

    expected[2] = -300.0
    expected[8] = -300.0
    expected[14] = -300.0

    assert np.allclose(
        f,
        expected,
    )


def test_shell_pressure_global_resultant():
    model, shell, *_ = make_pressure_model()

    pressure = -1200.0

    model.add_uniform_shell_pressure(
        shell,
        pressure,
    )

    f = cb.Assembler(
        model
    ).force_vector()

    resultant_z = (
        f[2]
        + f[8]
        + f[14]
    )

    assert resultant_z == pytest.approx(
        pressure * shell.area
    )


def test_multiple_shell_pressures_accumulate():
    model, shell, *_ = make_pressure_model()

    model.add_uniform_shell_pressure(
        shell,
        -300.0,
    )

    model.add_uniform_shell_pressure(
        shell,
        -600.0,
    )

    f = cb.Assembler(
        model
    ).force_vector()

    assert f[2] == pytest.approx(-300.0)
    assert f[8] == pytest.approx(-300.0)
    assert f[14] == pytest.approx(-300.0)


def test_shell_pressure_assembler_has_no_direct_moments():
    model, shell, *_ = make_pressure_model()

    model.add_uniform_shell_pressure(
        shell,
        -900.0,
    )

    f = cb.Assembler(
        model
    ).force_vector()

    rotational_dofs = [
        3, 4, 5,
        9, 10, 11,
        15, 16, 17,
    ]

    assert np.allclose(
        f[rotational_dofs],
        0.0,
    )


def test_shell_pressure_solver_equilibrium():
    model, shell, n0, n1, n2 = make_pressure_model()

    pressure = -900.0

    model.add_uniform_shell_pressure(
        shell,
        pressure,
    )

    # n0 and n1 fully fixed.
    for node in (n0, n1):
        model.add_support(
            node,
            True,
            True,
            True,
            True,
            True,
            True,
        )

    # n2 has only UZ free.
    model.add_support(
        n2,
        True,   # UX
        True,   # UY
        False,  # UZ
        True,   # RX
        True,   # RY
        True,   # RZ
    )

    solver = cb.LinearStaticSolver(
        model
    )

    result = solver.solve()

    displacement = result.node_displacement(
        n2
    )

    # Negative pressure on an XY shell acts in -Z.
    assert displacement[2] < 0.0

    reaction_n0 = result.node_reaction(
        n0
    )

    reaction_n1 = result.node_reaction(
        n1
    )

    reaction_n2 = result.node_reaction(
        n2
    )

    total_reaction_z = (
        reaction_n0[2]
        + reaction_n1[2]
        + reaction_n2[2]
    )

    applied_force_z = (
        pressure
        * shell.area
    )

    assert total_reaction_z == pytest.approx(
        -applied_force_z
    )

    # n2 UZ is free, so it must not have
    # a support reaction in Z.
    assert reaction_n2[2] == pytest.approx(
        0.0,
        abs=1e-9,
    )
