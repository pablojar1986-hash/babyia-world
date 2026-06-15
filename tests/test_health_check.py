"""Tests del health check del proyecto."""
from pathlib import Path

import pytest
from scripts.health_check import (
    check_file_lengths,
    check_interface_purity,
    check_network_calls,
    check_selfmod,
    check_structure,
    check_tests,
    run_all_checks,
)

ROOT = Path(__file__).parent.parent


def test_run_all_returns_list():
    results = run_all_checks(ROOT)
    assert isinstance(results, list)
    assert len(results) > 0


def test_results_have_required_keys():
    results = run_all_checks(ROOT)
    for r in results:
        assert "status" in r
        assert "message" in r
        assert r["status"] in ("ok", "warn", "fail")


def test_main_project_structure_passes():
    results = check_structure(ROOT)
    fails = [r for r in results if r["status"] == "fail"]
    assert len(fails) == 0, f"Estructura incompleta: {fails}"


def test_no_network_calls_in_project():
    results = check_network_calls(ROOT)
    fails = [r for r in results if r["status"] == "fail"]
    assert len(fails) == 0, f"Llamadas de red detectadas: {fails}"


def test_no_selfmod_in_project():
    results = check_selfmod(ROOT)
    # Solo advertencias permitidas, no fallos
    fails = [r for r in results if r["status"] == "fail"]
    assert len(fails) == 0


def test_interface_is_pure():
    results = check_interface_purity(ROOT)
    warns = [r for r in results if r["status"] == "warn"]
    assert len(warns) == 0, f"interface/ mezcla lógica: {warns}"


def test_detects_long_file(tmp_path):
    content = "\n".join([f"x = {i}" for i in range(310)])
    (tmp_path / "long_module.py").write_text(content, encoding="utf-8")
    results = check_file_lengths(tmp_path)
    warns = [r for r in results if r["status"] == "warn"]
    assert any("long_module" in r["message"] for r in warns)


def test_detects_network_call(tmp_path):
    (tmp_path / "bad.py").write_text("import requests\nrequests.get('http://x.com')",
                                     encoding="utf-8")
    results = check_network_calls(tmp_path)
    assert any(r["status"] == "fail" for r in results)


def test_detects_missing_structure(tmp_path):
    results = check_structure(tmp_path)
    fails = [r for r in results if r["status"] == "fail"]
    assert len(fails) > 0  # faltan directorios en un tmp vacío


def test_tests_found_in_project():
    results = check_tests(ROOT)
    ok = [r for r in results if "encontrados" in r["message"]]
    # Acepta cualquier cantidad >= 7 (0.1.x tenia 7, 0.2 anade 4, 0.2.1 anade 4 mas)
    assert any(
        any(str(n) in r["message"] for n in range(7, 25))
        for r in ok
    )
