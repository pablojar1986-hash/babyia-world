"""
Health check de BabyIA World.

Uso: python scripts/health_check.py
"""

from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

ROOT = Path(__file__).parent.parent

REQUIRED_DIRS  = ["brain", "world", "worlds", "interface", "data", "models",
                  "tests", "godot", ".vscode"]
REQUIRED_FILES = [
    "main.py", "README.md", "requirements.txt", ".gitignore", "config.py",
    # 0.2
    "brain/concepts.py", "world/interactions.py", "world/inventory.py",
    # 0.2.1
    "brain/network_inspector.py", "world/level_factory.py", "world/maze_generator.py",
    # 0.3
    "worlds/world_definition.py", "worlds/portal.py", "worlds/reward_profiles.py",
    "worlds/world_registry.py", "worlds/world_manager.py",
    "brain/world_memory.py", "brain/preferences.py", "brain/home_drive.py",
    "interface/avatar_renderer.py",
]
REQUIRED_TESTS = [
    "tests/test_world.py", "tests/test_rewards.py", "tests/test_memory.py",
    # 0.2
    "tests/test_interactions.py", "tests/test_inventory.py",
    "tests/test_concepts.py", "tests/test_objects_v02.py",
    # 0.2.1
    "tests/test_level_factory.py", "tests/test_maze_generator.py",
    "tests/test_network_inspector.py", "tests/test_curriculum_levels.py",
    # 0.3
    "tests/test_world_manager.py", "tests/test_portals.py",
    "tests/test_world_preferences.py", "tests/test_home_drive.py",
    "tests/test_avatar_renderer.py",
]
NETWORK_IMPORTS = ["requests", "urllib.request", "httpx", "aiohttp", "socket"]
MAX_LINES = 300


# ── Funciones de verificacion (importables en tests) ──────────────────────────

def check_structure(root: Path = ROOT) -> list[dict]:
    results = []
    for d in REQUIRED_DIRS:
        exists = (root / d).is_dir()
        results.append({
            "status" : "ok" if exists else "fail",
            "message": f"Carpeta {d}/" + (" encontrada" if exists else " FALTA"),
        })
    for f in REQUIRED_FILES:
        exists = (root / f).is_file()
        results.append({
            "status" : "ok" if exists else "warn",
            "message": f"Archivo {f}" + (" encontrado" if exists else " no encontrado"),
        })
    return results


def check_tests(root: Path = ROOT) -> list[dict]:
    results = []
    for t in REQUIRED_TESTS:
        exists = (root / t).is_file()
        results.append({
            "status" : "ok" if exists else "fail",
            "message": f"Test {t}" + (" encontrado" if exists else " FALTA"),
        })
    py_files = list((root / "tests").glob("test_*.py")) if (root / "tests").is_dir() else []
    results.append({
        "status" : "ok",
        "message": f"Archivos de test encontrados: {len(py_files)}",
    })
    return results


def check_file_lengths(root: Path = ROOT) -> list[dict]:
    results = []
    for py in root.rglob("*.py"):
        if any(part in py.parts for part in [".venv", "__pycache__", ".git"]):
            continue
        try:
            lines = len(py.read_text(encoding="utf-8").splitlines())
        except Exception:
            continue
        if lines > MAX_LINES:
            rel = py.relative_to(root)
            results.append({
                "status" : "warn",
                "message": f"{rel} tiene {lines} lineas (max recomendado: {MAX_LINES})",
            })
    if not results:
        results.append({"status": "ok", "message": f"Todos los archivos <= {MAX_LINES} lineas"})
    return results


def check_network_calls(root: Path = ROOT) -> list[dict]:
    results = []
    found   = []
    for py in root.rglob("*.py"):
        if any(part in py.parts for part in [".venv", "__pycache__", ".git", "scripts", "tests"]):
            continue
        try:
            text = py.read_text(encoding="utf-8")
        except Exception:
            continue
        for pattern in NETWORK_IMPORTS:
            if pattern in text:
                found.append(f"{py.relative_to(root)} usa '{pattern}'")
    if found:
        for f in found:
            results.append({"status": "fail", "message": f"Llamada de red: {f}"})
    else:
        results.append({"status": "ok", "message": "No se detectaron llamadas de red"})
    return results


def check_selfmod(root: Path = ROOT) -> list[dict]:
    results = []
    found   = []
    dangerous = ["exec(", "eval("]
    for py in root.rglob("*.py"):
        if any(part in py.parts for part in [".venv", "__pycache__", ".git"]):
            continue
        try:
            text = py.read_text(encoding="utf-8")
        except Exception:
            continue
        for pattern in dangerous:
            if pattern in text:
                found.append(f"{py.relative_to(root)} contiene '{pattern}'")
    if found:
        for f in found:
            results.append({"status": "warn", "message": f"Posible auto-modificacion: {f}"})
    else:
        results.append({"status": "ok", "message": "No se detecto auto-modificacion de codigo"})
    return results


def check_interface_purity(root: Path = ROOT) -> list[dict]:
    """Verifica que interface/ no contenga logica de entrenamiento."""
    results = []
    iface   = root / "interface"
    if not iface.is_dir():
        return [{"status": "warn", "message": "Carpeta interface/ no encontrada"}]
    training_keywords = ["brain.train(", "remember(", "replay_buffer", "optimizer.step"]
    for py in iface.glob("*.py"):
        try:
            text = py.read_text(encoding="utf-8")
        except Exception:
            continue
        hits = [kw for kw in training_keywords if kw in text]
        if hits:
            results.append({
                "status" : "warn",
                "message": f"{py.name} contiene logica de entrenamiento: {hits}",
            })
    if not results:
        results.append({"status": "ok", "message": "interface/ no mezcla logica de entrenamiento"})
    return results


def check_data_files(root: Path = ROOT) -> list[dict]:
    """Verifica archivos de datos persistentes (pueden no existir si no hay entrenamientos)."""
    data = root / "data"
    results = []
    for fname in [
        "concepts.json", "training_stats.json",
        "network_stats.json", "level_stats.json",   # 0.2.1+
        "world_history.json", "world_preferences.json", "home_stats.json",  # 0.3
    ]:
        path = data / fname
        results.append({
            "status" : "ok" if path.exists() else "warn",
            "message": f"data/{fname}" + (" existe" if path.exists() else " aun no creado"),
        })
    return results


def check_worlds_have_return(root: Path = ROOT) -> list[dict]:
    """Verifica que todos los mundos no-home tengan home_return_required=True."""
    try:
        import sys as _sys
        _sys.path.insert(0, str(root))
        from worlds.world_registry import ALL_WORLDS, HOME_WORLD_ID
        bad = [
            w.world_id for w in ALL_WORLDS.values()
            if w.world_id != HOME_WORLD_ID and not w.home_return_required
        ]
        if bad:
            return [{"status": "fail",
                     "message": f"Mundos sin retorno a casa: {bad}"}]
        return [{"status": "ok",
                 "message": "Todos los mundos no-home tienen home_return_required=True"}]
    except Exception as e:
        return [{"status": "warn", "message": f"No se pudo verificar mundos: {e}"}]


def check_level0_is_open(root: Path = ROOT) -> list[dict]:
    """Verifica que nivel 0 sea mundo completamente abierto (sin paredes)."""
    try:
        import sys as _sys
        _sys.path.insert(0, str(root))
        from world.level_factory import get_maze_for_level
        info = get_maze_for_level(0)
        ok = info["wall_count"] == 0
        return [{
            "status" : "ok" if ok else "fail",
            "message": ("Nivel 0 es mundo abierto (0 paredes)"
                        if ok else f"Nivel 0 tiene {info['wall_count']} paredes (debe ser 0)"),
        }]
    except Exception as e:
        return [{"status": "warn", "message": f"No se pudo verificar nivel 0: {e}"}]


def check_tasks_reset_zero(root: Path = ROOT) -> list[dict]:
    """Verifica que la tarea de reset en tasks.json usa --episodes 0."""
    import json as _json
    tasks_file = root / ".vscode" / "tasks.json"
    if not tasks_file.exists():
        return [{"status": "warn", "message": "tasks.json no encontrado"}]
    try:
        with open(tasks_file, encoding="utf-8") as f:
            tasks = _json.load(f)
        for task in tasks.get("tasks", []):
            if "reset" in task.get("label", "").lower():
                cmd = task.get("command", "")
                if "--episodes 0" in cmd:
                    return [{"status": "ok", "message": "Tarea reset usa --episodes 0"}]
        return [{"status": "warn", "message": "Tarea reset no encontrada o sin --episodes 0"}]
    except Exception as e:
        return [{"status": "warn", "message": f"Error leyendo tasks.json: {e}"}]


def run_all_checks(root: Path = ROOT) -> list[dict]:
    checks = []
    checks.extend(check_structure(root))
    checks.extend(check_tests(root))
    checks.extend(check_file_lengths(root))
    checks.extend(check_network_calls(root))
    checks.extend(check_selfmod(root))
    checks.extend(check_interface_purity(root))
    checks.extend(check_data_files(root))
    checks.extend(check_level0_is_open(root))     # 0.2.2
    checks.extend(check_tasks_reset_zero(root))   # 0.2.2
    checks.extend(check_worlds_have_return(root)) # 0.3
    return checks


# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    console = Console(legacy_windows=False)
    results = run_all_checks()

    icons = {
        "ok"  : "[green] OK [/green]",
        "warn": "[yellow]WARN[/yellow]",
        "fail": "[red]FAIL[/red]",
    }

    t = Table(box=box.SIMPLE, show_header=False, padding=(0, 1))
    t.add_column("s", no_wrap=True)
    t.add_column("msg")

    for r in results:
        t.add_row(icons[r["status"]], r["message"])

    totals  = {s: sum(1 for r in results if r["status"] == s) for s in ("ok", "warn", "fail")}
    summary = (f"[green]{totals['ok']} OK[/green]  "
               f"[yellow]{totals['warn']} advertencias[/yellow]  "
               f"[red]{totals['fail']} errores[/red]")

    console.print(Panel(t, title="[bold cyan]BabyIA Health Check[/bold cyan]",
                        subtitle=summary, border_style="cyan"))

    if totals["fail"] > 0:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
