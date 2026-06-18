"""Tests de existencia y contenido de AGENTS.md — BabyIA 0.4.7."""

import pytest
from pathlib import Path

AGENTS_PATH = Path("AGENTS.md")


@pytest.fixture(scope="module")
def agents_text():
    if not AGENTS_PATH.exists():
        pytest.skip("AGENTS.md no encontrado")
    return AGENTS_PATH.read_text(encoding="utf-8")


def test_agents_md_exists():
    assert AGENTS_PATH.exists(), "AGENTS.md no existe en la raiz del proyecto"


def test_agents_prohibits_auto_commits(agents_text):
    assert (
        "commits automati" in agents_text.lower()
        or "auto-commit" in agents_text.lower()
    ), "AGENTS.md no prohíbe los commits automaticos"


def test_agents_prohibits_consciousness_claim(agents_text):
    assert (
        "conciencia real" in agents_text.lower()
    ), "AGENTS.md no prohíbe afirmar que BabyIA tiene conciencia real"


def test_agents_requires_tests(agents_text):
    assert (
        "test" in agents_text.lower()
    ), "AGENTS.md no menciona la obligatoriedad de tests"


def test_agents_prohibits_internet(agents_text):
    has_internet = (
        "internet" in agents_text.lower()
        or "api externa" in agents_text.lower()
        or "requests" in agents_text.lower()
    )
    assert has_internet, "AGENTS.md no prohíbe conexion a internet o APIs externas"


def test_agents_has_architecture_section(agents_text):
    has_arch = (
        "STATE_SIZE" in agents_text
        or "40" in agents_text
        or "arquitectura" in agents_text.lower()
    )
    assert has_arch, "AGENTS.md no documenta la arquitectura actual"


def test_agents_prohibits_reconstruction(agents_text):
    assert (
        "reconstruir" in agents_text.lower() or "desde cero" in agents_text.lower()
    ), "AGENTS.md no prohíbe reconstruir el proyecto desde cero"


def test_agents_mentions_no_conciencia_doc(agents_text):
    has_ref = (
        "no-conciencia" in agents_text.lower()
        or "no_conciencia" in agents_text.lower()
        or "conciencia-real" in agents_text.lower()
    )
    assert has_ref, "AGENTS.md no referencia docs/no-conciencia-real.md"


def test_agents_mentions_300_line_limit(agents_text):
    assert (
        "300" in agents_text
    ), "AGENTS.md no menciona el limite de 300 lineas por archivo"
