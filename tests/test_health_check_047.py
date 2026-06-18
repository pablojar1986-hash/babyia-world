"""Tests del health check 0.4.7 — verifica que check_047_integrity funciona."""

from pathlib import Path
from scripts.health_check import check_047_integrity, run_all_checks

ROOT = Path(__file__).parent.parent


def test_check_047_returns_list():
    results = check_047_integrity(ROOT)
    assert isinstance(results, list)
    assert len(results) > 0


def test_check_047_results_have_required_keys():
    results = check_047_integrity(ROOT)
    for r in results:
        assert "status" in r
        assert "message" in r
        assert r["status"] in ("ok", "warn", "fail")


def test_check_047_no_failures():
    results = check_047_integrity(ROOT)
    failures = [r for r in results if r["status"] == "fail"]
    assert (
        failures == []
    ), f"check_047_integrity encontro errores: {[r['message'] for r in failures]}"


def test_run_all_checks_includes_047():
    results = run_all_checks(ROOT)
    messages = [r["message"] for r in results]
    has_047 = any(
        "0.4.7" in m or "APP_VERSION" in m or "AGENTS.md" in m for m in messages
    )
    assert has_047, "run_all_checks no incluye verificaciones de 0.4.7"


def test_check_047_verifies_app_version():
    results = check_047_integrity(ROOT)
    version_checks = [r for r in results if "APP_VERSION" in r["message"]]
    assert len(version_checks) >= 1, "check_047_integrity no verifica APP_VERSION"
    assert all(
        r["status"] == "ok" for r in version_checks
    ), f"APP_VERSION check fallo: {[r['message'] for r in version_checks]}"


def test_check_047_verifies_agents_md():
    results = check_047_integrity(ROOT)
    agents_checks = [r for r in results if "AGENTS.md" in r["message"]]
    assert len(agents_checks) >= 1, "check_047_integrity no verifica AGENTS.md"
    assert any(
        r["status"] == "ok" for r in agents_checks
    ), f"AGENTS.md check fallo: {[r['message'] for r in agents_checks]}"


def test_check_047_verifies_model_v4_6():
    results = check_047_integrity(ROOT)
    model_checks = [r for r in results if "MODEL_V4_6" in r["message"]]
    assert len(model_checks) >= 1, "check_047_integrity no verifica MODEL_V4_6"
    assert any(
        r["status"] == "ok" for r in model_checks
    ), f"MODEL_V4_6 check fallo: {[r['message'] for r in model_checks]}"
