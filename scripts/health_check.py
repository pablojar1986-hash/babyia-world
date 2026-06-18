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

REQUIRED_DIRS = [
    "brain",
    "world",
    "worlds",
    "interface",
    "data",
    "models",
    "tests",
    "godot",
    ".vscode",
]
REQUIRED_FILES = [
    "main.py",
    "README.md",
    "requirements.txt",
    ".gitignore",
    "config.py",
    # 0.2
    "brain/concepts.py",
    "world/interactions.py",
    "world/inventory.py",
    # 0.2.1
    "brain/network_inspector.py",
    "world/level_factory.py",
    "world/maze_generator.py",
    # 0.3
    "worlds/world_definition.py",
    "worlds/portal.py",
    "worlds/reward_profiles.py",
    "worlds/world_registry.py",
    "worlds/world_manager.py",
    "brain/world_memory.py",
    "brain/preferences.py",
    "brain/home_drive.py",
    "interface/avatar_renderer.py",
    # 0.4
    "brain/body_state.py",
    "brain/causal_memory.py",
    "brain/utility_evaluator.py",
    "world/powerups.py",
    "world/hazards.py",
    "world/doors.py",
    # 0.4.1
    "brain/neural_debugger.py",
    "interface/layout.py",
    "interface/ui_components.py",
    "interface/panel_renderer.py",
    "interface/brain_view.py",
    "interface/status_view.py",
    "interface/world_info_view.py",
    "interface/body_view.py",
    "interface/memory_view.py",
    # 0.4.2
    "brain/survival.py",
    # 0.4.3
    "world/level_doors.py",
    # 0.4.4
    "brain/mission.py",
    "brain/decision_context.py",
    "brain/mission_reward.py",
    "interface/visual_theme.py",
    "interface/mission_view.py",
    "interface/minimap_view.py",
]
REQUIRED_TESTS = [
    "tests/test_world.py",
    "tests/test_rewards.py",
    "tests/test_memory.py",
    # 0.2
    "tests/test_interactions.py",
    "tests/test_inventory.py",
    "tests/test_concepts.py",
    "tests/test_objects_v02.py",
    # 0.2.1
    "tests/test_level_factory.py",
    "tests/test_maze_generator.py",
    "tests/test_network_inspector.py",
    "tests/test_curriculum_levels.py",
    # 0.3
    "tests/test_world_manager.py",
    "tests/test_portals.py",
    "tests/test_world_preferences.py",
    "tests/test_home_drive.py",
    "tests/test_avatar_renderer.py",
    # 0.4
    "tests/test_body_state.py",
    "tests/test_powerups.py",
    "tests/test_hazards.py",
    "tests/test_doors_requirements.py",
    "tests/test_causal_memory.py",
    "tests/test_utility_evaluator.py",
    # 0.4.1
    "tests/test_neural_debugger.py",
    "tests/test_brain_decision_debug.py",
    "tests/test_ui_layout.py",
    # 0.4.2
    "tests/test_powerups_integration.py",
    "tests/test_hazards_integration.py",
    "tests/test_special_doors_integration.py",
    "tests/test_survival.py",
    "tests/test_utility_evaluator_context.py",
    "tests/test_causal_memory_integration.py",
    "tests/test_visual_status_payload.py",
    # 0.4.3
    "tests/test_level_progression_doors.py",
    "tests/test_curriculum_progression.py",
    "tests/test_reward_balance.py",
    "tests/test_optional_rooms.py",
    "tests/test_progress_ui_payload.py",
    # 0.4.4
    "tests/test_mission_state.py",
    "tests/test_decision_context.py",
    "tests/test_mission_reward.py",
    "tests/test_strategy_progress.py",
    "tests/test_mission_ui_payload.py",
    "tests/test_visual_theme.py",
    # 0.4.6
    "tests/test_double_dqn.py",
    "tests/test_per.py",
    "tests/test_perception_in_state.py",
    # 0.4.6b
    "tests/test_path_diagnostics.py",
    "tests/test_visual_memory_stagnation.py",
    "tests/test_mission_reward_anti_loop.py",
    "tests/test_version_consistency.py",
    "tests/test_stagnation_status_payload.py",
    # 0.4.7
    "tests/test_version_047.py",
    "tests/test_model_versioning_047.py",
    "tests/test_agents_rules.py",
    "tests/test_health_check_047.py",
    # 0.4.6c
    "tests/test_grid_scaler.py",
    "tests/test_full_world_view.py",
    "tests/test_view_mode_toggle.py",
    "tests/test_grid_renderer.py",
]
NETWORK_IMPORTS = ["requests", "urllib.request", "httpx", "aiohttp", "socket"]
MAX_LINES = 300


# ── Funciones de verificacion (importables en tests) ──────────────────────────


def check_structure(root: Path = ROOT) -> list[dict]:
    results = []
    for d in REQUIRED_DIRS:
        exists = (root / d).is_dir()
        results.append(
            {
                "status": "ok" if exists else "fail",
                "message": f"Carpeta {d}/" + (" encontrada" if exists else " FALTA"),
            }
        )
    for f in REQUIRED_FILES:
        exists = (root / f).is_file()
        results.append(
            {
                "status": "ok" if exists else "warn",
                "message": f"Archivo {f}"
                + (" encontrado" if exists else " no encontrado"),
            }
        )
    return results


def check_tests(root: Path = ROOT) -> list[dict]:
    results = []
    for t in REQUIRED_TESTS:
        exists = (root / t).is_file()
        results.append(
            {
                "status": "ok" if exists else "fail",
                "message": f"Test {t}" + (" encontrado" if exists else " FALTA"),
            }
        )
    py_files = (
        list((root / "tests").glob("test_*.py")) if (root / "tests").is_dir() else []
    )
    results.append(
        {
            "status": "ok",
            "message": f"Archivos de test encontrados: {len(py_files)}",
        }
    )
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
            results.append(
                {
                    "status": "warn",
                    "message": f"{rel} tiene {lines} lineas (max recomendado: {MAX_LINES})",
                }
            )
    if not results:
        results.append(
            {"status": "ok", "message": f"Todos los archivos <= {MAX_LINES} lineas"}
        )
    return results


def check_network_calls(root: Path = ROOT) -> list[dict]:
    results = []
    found = []
    for py in root.rglob("*.py"):
        if any(
            part in py.parts
            for part in [".venv", "__pycache__", ".git", "scripts", "tests"]
        ):
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
    found = []
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
            results.append(
                {"status": "warn", "message": f"Posible auto-modificacion: {f}"}
            )
    else:
        results.append(
            {"status": "ok", "message": "No se detecto auto-modificacion de codigo"}
        )
    return results


def check_interface_purity(root: Path = ROOT) -> list[dict]:
    """Verifica que interface/ no contenga logica de entrenamiento."""
    results = []
    iface = root / "interface"
    if not iface.is_dir():
        return [{"status": "warn", "message": "Carpeta interface/ no encontrada"}]
    training_keywords = [
        "brain.train(",
        ".remember(",
        "buffer.append(",
        "optimizer.step(",
    ]
    for py in iface.glob("*.py"):
        try:
            text = py.read_text(encoding="utf-8")
        except Exception:
            continue
        hits = [kw for kw in training_keywords if kw in text]
        if hits:
            results.append(
                {
                    "status": "warn",
                    "message": f"{py.name} contiene logica de entrenamiento: {hits}",
                }
            )
    if not results:
        results.append(
            {"status": "ok", "message": "interface/ no mezcla logica de entrenamiento"}
        )
    return results


def check_data_files(root: Path = ROOT) -> list[dict]:
    """Verifica archivos de datos persistentes (pueden no existir si no hay entrenamientos)."""
    data = root / "data"
    results = []
    for fname in [
        "concepts.json",
        "training_stats.json",
        "network_stats.json",
        "level_stats.json",  # 0.2.1+
        "world_history.json",
        "world_preferences.json",
        "home_stats.json",  # 0.3
        "causal_memory.json",  # 0.4
    ]:
        path = data / fname
        results.append(
            {
                "status": "ok" if path.exists() else "warn",
                "message": f"data/{fname}"
                + (" existe" if path.exists() else " aun no creado"),
            }
        )
    return results


def check_worlds_have_return(root: Path = ROOT) -> list[dict]:
    """Verifica que todos los mundos no-home tengan home_return_required=True."""
    try:
        import sys as _sys

        _sys.path.insert(0, str(root))
        from worlds.world_registry import ALL_WORLDS, HOME_WORLD_ID

        bad = [
            w.world_id
            for w in ALL_WORLDS.values()
            if w.world_id != HOME_WORLD_ID and not w.home_return_required
        ]
        if bad:
            return [{"status": "fail", "message": f"Mundos sin retorno a casa: {bad}"}]
        return [
            {
                "status": "ok",
                "message": "Todos los mundos no-home tienen home_return_required=True",
            }
        ]
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
        return [
            {
                "status": "ok" if ok else "fail",
                "message": (
                    "Nivel 0 es mundo abierto (0 paredes)"
                    if ok
                    else f"Nivel 0 tiene {info['wall_count']} paredes (debe ser 0)"
                ),
            }
        ]
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
        return [
            {
                "status": "warn",
                "message": "Tarea reset no encontrada o sin --episodes 0",
            }
        ]
    except Exception as e:
        return [{"status": "warn", "message": f"Error leyendo tasks.json: {e}"}]


def check_042_integrity(root: Path = ROOT) -> list[dict]:
    """Verifica correcciones especificas introducidas en 0.4.2."""
    results = []
    import sys as _sys

    _sys.path.insert(0, str(root))

    # 1. small_door tiene max_size
    try:
        from world.doors import DOOR_TYPES

        sd = DOOR_TYPES.get("small_door")
        if sd is None:
            results.append(
                {"status": "fail", "message": "small_door no encontrada en DOOR_TYPES"}
            )
        elif not hasattr(sd, "max_size") or sd.max_size >= 999.0:
            results.append(
                {
                    "status": "fail",
                    "message": f"small_door.max_size no configurado (valor={getattr(sd, 'max_size', 'N/A')})",
                }
            )
        else:
            results.append(
                {
                    "status": "ok",
                    "message": f"small_door.max_size={sd.max_size} correctamente configurado",
                }
            )
    except Exception as e:
        results.append(
            {"status": "warn", "message": f"No se pudo verificar small_door: {e}"}
        )

    # 2. energy_food tiene efecto energy_restore
    try:
        from world.powerups import POWERUP_TYPES

        ef = POWERUP_TYPES.get("energy_food")
        if ef is None:
            results.append(
                {
                    "status": "fail",
                    "message": "energy_food no encontrada en POWERUP_TYPES",
                }
            )
        elif ef.effect != "energy_restore":
            results.append(
                {
                    "status": "fail",
                    "message": f"energy_food.effect='{ef.effect}' (esperado 'energy_restore')",
                }
            )
        else:
            results.append(
                {
                    "status": "ok",
                    "message": "energy_food.effect=energy_restore correcto",
                }
            )
    except Exception as e:
        results.append(
            {"status": "warn", "message": f"No se pudo verificar energy_food: {e}"}
        )

    # 3. UtilityEvaluator no usa body_state.shield como energia
    try:
        ue_path = root / "brain" / "utility_evaluator.py"
        text = ue_path.read_text(encoding="utf-8")
        if '"shield"' in text and "energy = " in text and "body_state.shield" in text:
            results.append(
                {
                    "status": "fail",
                    "message": "utility_evaluator.py aun usa body_state.shield como energia",
                }
            )
        else:
            results.append(
                {
                    "status": "ok",
                    "message": "utility_evaluator.py no usa shield como proxy de energia",
                }
            )
    except Exception as e:
        results.append(
            {
                "status": "warn",
                "message": f"No se pudo verificar utility_evaluator: {e}",
            }
        )

    # 4. brain/survival.py existe y tiene SurvivalEvaluator
    try:
        from brain.survival import SurvivalEvaluator

        SurvivalEvaluator()
        results.append(
            {
                "status": "ok",
                "message": "brain/survival.py: SurvivalEvaluator importable",
            }
        )
    except Exception as e:
        results.append({"status": "fail", "message": f"brain/survival.py: {e}"})

    # 5. get_status() incluye survival y causal_relations
    try:
        from brain.trainer import Trainer
        import inspect

        src = inspect.getsource(Trainer.get_status)
        has_survival = '"survival"' in src
        has_causal = '"causal_relations"' in src
        if has_survival and has_causal:
            results.append(
                {
                    "status": "ok",
                    "message": "Trainer.get_status incluye survival y causal_relations",
                }
            )
        else:
            missing = []
            if not has_survival:
                missing.append("survival")
            if not has_causal:
                missing.append("causal_relations")
            results.append(
                {"status": "fail", "message": f"Trainer.get_status falta: {missing}"}
            )
    except Exception as e:
        results.append(
            {
                "status": "warn",
                "message": f"No se pudo verificar Trainer.get_status: {e}",
            }
        )

    return results


def check_043_integrity(root: Path = ROOT) -> list[dict]:
    """Verifica correcciones especificas introducidas en 0.4.3."""
    results = []
    import sys as _sys

    _sys.path.insert(0, str(root))

    # 1. world/level_doors.py existe y contiene LEVEL_DOOR_POSITIONS
    try:
        from world.level_doors import LEVEL_DOOR_POSITIONS, LEVEL_DOOR_TYPES

        if len(LEVEL_DOOR_POSITIONS) >= 3:
            results.append(
                {
                    "status": "ok",
                    "message": f"level_doors.py: {len(LEVEL_DOOR_POSITIONS)} puertas definidas",
                }
            )
        else:
            results.append(
                {
                    "status": "fail",
                    "message": f"level_doors.py: solo {len(LEVEL_DOOR_POSITIONS)} puertas (esperadas >=3)",
                }
            )
    except Exception as e:
        results.append({"status": "fail", "message": f"level_doors.py: {e}"})

    # 2. Curriculum acepta level_completed
    try:
        from brain.curriculum import Curriculum
        import inspect

        src = inspect.getsource(Curriculum.record_episode)
        if "level_completed" in src:
            results.append(
                {
                    "status": "ok",
                    "message": "Curriculum.record_episode acepta level_completed",
                }
            )
        else:
            results.append(
                {
                    "status": "fail",
                    "message": "Curriculum.record_episode NO tiene level_completed",
                }
            )
    except Exception as e:
        results.append(
            {"status": "warn", "message": f"No se pudo verificar Curriculum: {e}"}
        )

    # 3. REWARD_LEVEL_COMPLETED > exploracion maxima (64 * REWARD_NEW_CELL)
    try:
        from world.rewards import REWARD_LEVEL_COMPLETED, REWARD_NEW_CELL

        max_exploration = 64 * REWARD_NEW_CELL
        if REWARD_LEVEL_COMPLETED > max_exploration:
            results.append(
                {
                    "status": "ok",
                    "message": (
                        f"REWARD_LEVEL_COMPLETED={REWARD_LEVEL_COMPLETED} "
                        f"> exploracion_max={max_exploration:.1f}"
                    ),
                }
            )
        else:
            results.append(
                {
                    "status": "fail",
                    "message": (
                        f"REWARD_LEVEL_COMPLETED={REWARD_LEVEL_COMPLETED} "
                        f"<= exploracion_max={max_exploration:.1f} (reward hacking activo)"
                    ),
                }
            )
    except Exception as e:
        results.append(
            {"status": "warn", "message": f"No se pudo verificar rewards: {e}"}
        )

    # 4. NEXT_LEVEL_DOOR no es siempre pasable (requiere llave)
    try:
        from world.level_doors import LEVEL_DOOR_TYPES

        nd = LEVEL_DOOR_TYPES.get("next_level_door")
        if nd and nd.requires_key:
            results.append(
                {
                    "status": "ok",
                    "message": "next_level_door.requires_key=True (no siempre pasable)",
                }
            )
        else:
            results.append(
                {
                    "status": "fail",
                    "message": "next_level_door deberia tener requires_key=True",
                }
            )
    except Exception as e:
        results.append(
            {"status": "warn", "message": f"No se pudo verificar level_doors: {e}"}
        )

    # 5. world/objects.py STATE_SIZE coincide con brain/baby_brain.py STATE_SIZE
    try:
        from world.objects import STATE_SIZE as WS
        from brain.baby_brain import STATE_SIZE as BS

        if WS == BS:
            results.append(
                {
                    "status": "ok",
                    "message": f"STATE_SIZE consistente: {WS} en objects y baby_brain",
                }
            )
        else:
            results.append(
                {
                    "status": "fail",
                    "message": f"STATE_SIZE inconsistente: objects={WS} vs baby_brain={BS}",
                }
            )
    except Exception as e:
        results.append(
            {"status": "warn", "message": f"No se pudo verificar STATE_SIZE: {e}"}
        )

    # 6. README menciona version 0.4.3
    try:
        readme = (root / "README.md").read_text(encoding="utf-8")
        if "0.4.3" in readme:
            results.append(
                {"status": "ok", "message": "README.md menciona version 0.4.3"}
            )
        else:
            results.append(
                {"status": "warn", "message": "README.md no menciona version 0.4.3"}
            )
    except Exception as e:
        results.append({"status": "warn", "message": f"No se pudo leer README: {e}"})

    return results


def check_044_integrity(root: Path = ROOT) -> list[dict]:
    """Verifica correcciones e integridad especificas de BabyIA 0.4.4."""
    results = []
    import sys as _sys

    _sys.path.insert(0, str(root))

    # 1. Nuevos modulos de mision existen e importan
    for mod, cls_name in [
        ("brain.mission", "MissionTracker"),
        ("brain.decision_context", "DecisionContext"),
        ("brain.mission_reward", "MissionReward"),
    ]:
        try:
            m = __import__(mod, fromlist=[cls_name])
            getattr(m, cls_name)
            results.append({"status": "ok", "message": f"{mod}.{cls_name} importable"})
        except Exception as e:
            results.append({"status": "fail", "message": f"{mod}: {e}"})

    # 2. Archivos de interfaz existen
    for iface_file in [
        "interface/visual_theme.py",
        "interface/mission_view.py",
        "interface/minimap_view.py",
    ]:
        exists = (root / iface_file).is_file()
        results.append(
            {
                "status": "ok" if exists else "fail",
                "message": f"{iface_file}" + (" existe" if exists else " FALTA"),
            }
        )

    # 3. Mission reward < REWARD_LEVEL_COMPLETED
    try:
        from brain.mission_reward import (
            APPROACH_KEY_BONUS,
            APPROACH_DOOR_BONUS,
            MISSION_SWITCH_BONUS,
        )
        from world.rewards import REWARD_LEVEL_COMPLETED

        max_mission_single = max(
            APPROACH_KEY_BONUS, APPROACH_DOOR_BONUS, MISSION_SWITCH_BONUS
        )
        if max_mission_single < REWARD_LEVEL_COMPLETED:
            results.append(
                {
                    "status": "ok",
                    "message": (
                        f"Max mission reward ({max_mission_single}) "
                        f"< REWARD_LEVEL_COMPLETED ({REWARD_LEVEL_COMPLETED})"
                    ),
                }
            )
        else:
            results.append(
                {
                    "status": "fail",
                    "message": (
                        f"Mission reward ({max_mission_single}) >= "
                        f"REWARD_LEVEL_COMPLETED ({REWARD_LEVEL_COMPLETED}) — posible reward hacking"
                    ),
                }
            )
    except Exception as e:
        results.append(
            {"status": "warn", "message": f"No se pudo verificar mission reward: {e}"}
        )

    # 4. _full_obs() usa puerta de progreso dinamica (no hardcodeada)
    try:
        trainer_path = root / "brain" / "trainer.py"
        text = trainer_path.read_text(encoding="utf-8")
        # 0.4.4: usaba "pdx, pdy = 7, 7"; 0.4.5: usa "world.progress_door_pos"
        uses_progress_door = (
            "pdx, pdy = 7, 7" in text
            or "PROGRESS_DOOR_POS" in text
            or "world.progress_door_pos" in text
        )
        uses_old_normal_door = "(3, 6)" in text and "dist to normal door" in text
        if uses_progress_door and not uses_old_normal_door:
            results.append(
                {
                    "status": "ok",
                    "message": "trainer._full_obs() apunta a puerta de progreso (dinamica 0.4.5)",
                }
            )
        else:
            results.append(
                {
                    "status": "fail",
                    "message": "trainer._full_obs() puede estar usando puerta normal (3,6) en vez de (7,7)",
                }
            )
    except Exception as e:
        results.append(
            {"status": "warn", "message": f"No se pudo verificar _full_obs: {e}"}
        )

    # 5. README menciona version 0.4.4
    try:
        readme = (root / "README.md").read_text(encoding="utf-8")
        if "0.4.4" in readme:
            results.append(
                {"status": "ok", "message": "README.md menciona version 0.4.4"}
            )
        else:
            results.append(
                {"status": "warn", "message": "README.md no menciona version 0.4.4"}
            )
    except Exception as e:
        results.append({"status": "warn", "message": f"No se pudo leer README: {e}"})

    return results


def check_045_integrity(root: Path = ROOT) -> list[dict]:
    """Verifica integridad especifica de BabyIA 0.4.5 (mundo escalable, percepcion)."""
    results = []
    import sys as _sys

    _sys.path.insert(0, str(root))

    # 1. Archivos nuevos de 0.4.5 presentes
    new_files = [
        "world/world_config.py",
        "interface/camera.py",
        "interface/effects.py",
        "interface/perception_view.py",
        "brain/perception.py",
        "brain/semantic_map.py",
        "brain/visual_memory.py",
    ]
    for f in new_files:
        exists = (root / f).exists()
        results.append(
            {
                "status": "ok" if exists else "fail",
                "message": f"{f} {'existe' if exists else 'FALTA (0.4.5)'}",
            }
        )

    # 2. Tests nuevos de 0.4.5 presentes
    new_tests = [
        "tests/test_world_config.py",
        "tests/test_grid_world_scaling.py",
        "tests/test_camera.py",
        "tests/test_perception.py",
        "tests/test_semantic_map.py",
        "tests/test_visual_memory.py",
        "tests/test_large_world_mission.py",
        "tests/test_minimap_large_world.py",
    ]
    for t in new_tests:
        exists = (root / t).exists()
        results.append(
            {
                "status": "ok" if exists else "fail",
                "message": f"{t} {'existe' if exists else 'FALTA (0.4.5)'}",
            }
        )

    # 3. get_grid_size_for_level devuelve valores correctos
    try:
        from world.world_config import get_grid_size_for_level

        assert get_grid_size_for_level(0) == 8
        assert get_grid_size_for_level(1) == 10
        assert get_grid_size_for_level(4) == 16
        results.append(
            {
                "status": "ok",
                "message": "get_grid_size_for_level() escala correctamente",
            }
        )
    except Exception as e:
        results.append(
            {"status": "fail", "message": f"get_grid_size_for_level error: {e}"}
        )

    # 4. GridWorld acepta grid_size y expone key_pos y progress_door_pos dinamicos
    try:
        from world.grid_world import GridWorld

        w8 = GridWorld(grid_size=8)
        w16 = GridWorld(grid_size=16)
        assert w8.key_pos == (1, 6)
        assert w16.progress_door_pos == (15, 15)
        results.append(
            {"status": "ok", "message": "GridWorld.grid_size escala correctamente"}
        )
    except Exception as e:
        results.append({"status": "fail", "message": f"GridWorld scaling error: {e}"})

    # 5. PerceptionSystem importable y funcional
    try:
        from brain.perception import PerceptionSystem
        from world.grid_world import GridWorld

        p = PerceptionSystem()
        w = GridWorld()
        r = p.observe(w, (0, 0))
        assert "vision_range" in r
        results.append(
            {"status": "ok", "message": "PerceptionSystem.observe() funciona"}
        )
    except Exception as e:
        results.append({"status": "fail", "message": f"PerceptionSystem error: {e}"})

    # 6. Trainer.get_status() incluye perception y visual_memory
    try:
        from brain.trainer import Trainer

        tr = Trainer(training=False)
        tr.start_episode()
        status = tr.get_status()
        assert "perception" in status
        assert "visual_memory" in status
        assert "grid_size" in status
        results.append(
            {"status": "ok", "message": "Trainer.get_status() incluye 0.4.5 fields"}
        )
    except Exception as e:
        results.append(
            {"status": "fail", "message": f"Trainer 0.4.5 status error: {e}"}
        )

    return results


def check_045b_integrity(root: Path = ROOT) -> list[dict]:
    """Verifica integridad especifica de BabyIA 0.4.5b (vision real, percepcion util)."""
    results = []
    import sys as _sys

    _sys.path.insert(0, str(root))

    # 1. Tests nuevos de 0.4.5b presentes
    new_tests = [
        "tests/test_world_scaling_8_10_12_16.py",
        "tests/test_camera_viewport_bounds.py",
        "tests/test_perception_uses_body_vision_range.py",
        "tests/test_fov_wall_blocks_visibility.py",
        "tests/test_visual_memory_remembers_seen_key.py",
        "tests/test_decision_context_uses_perception.py",
        "tests/test_mission_uses_visible_or_remembered_target.py",
        "tests/test_minimap_hides_unknown_cells.py",
        "tests/test_semantic_map_best_visible_object.py",
    ]
    for t in new_tests:
        exists = (root / t).exists()
        results.append(
            {
                "status": "ok" if exists else "fail",
                "message": f"{t} {'existe' if exists else 'FALTA (0.4.5b)'}",
            }
        )

    # 2. PerceptionSystem usa body_state.vision_range
    try:
        perc_path = root / "brain" / "perception.py"
        text = perc_path.read_text(encoding="utf-8")
        if "body_state.vision_range" in text and "fov_active" in text:
            results.append(
                {
                    "status": "ok",
                    "message": "perception.py: vision_range dinamico + fov_active",
                }
            )
        else:
            results.append(
                {
                    "status": "fail",
                    "message": "perception.py: falta vision_range dinamico o fov_active",
                }
            )
    except Exception as e:
        results.append(
            {"status": "warn", "message": f"No se pudo verificar perception.py: {e}"}
        )

    # 3. DecisionContext incluye campos de percepcion
    try:
        dc_path = root / "brain" / "decision_context.py"
        text = dc_path.read_text(encoding="utf-8")
        required = [
            "key_visible",
            "progress_door_visible",
            "visible_objects_count",
            "remembered_key_position",
            "perception_result",
            "visual_memory",
        ]
        missing = [k for k in required if k not in text]
        if not missing:
            results.append(
                {
                    "status": "ok",
                    "message": "decision_context.py: todos los campos 0.4.5b presentes",
                }
            )
        else:
            results.append(
                {"status": "fail", "message": f"decision_context.py: faltan {missing}"}
            )
    except Exception as e:
        results.append(
            {
                "status": "warn",
                "message": f"No se pudo verificar decision_context.py: {e}",
            }
        )

    # 4. MissionTracker acepta perception_result y visual_memory
    try:
        from brain.mission import MissionTracker
        import inspect

        src = inspect.getsource(MissionTracker.compute)
        if (
            "perception_result" in src
            and "visual_memory" in src
            and "COLLECT_USEFUL_POWERUP" in src
        ):
            results.append(
                {
                    "status": "ok",
                    "message": "MissionTracker.compute: percepcion + COLLECT_USEFUL_POWERUP",
                }
            )
        else:
            results.append(
                {
                    "status": "fail",
                    "message": "MissionTracker.compute: faltan campos 0.4.5b",
                }
            )
    except Exception as e:
        results.append(
            {"status": "warn", "message": f"No se pudo verificar MissionTracker: {e}"}
        )

    # 5. Trainer.get_status() incluye key_pos y progress_door_pos
    try:
        from brain.trainer import Trainer
        import inspect

        src = inspect.getsource(Trainer.get_status)
        if '"key_pos"' in src and '"progress_door_pos"' in src:
            results.append(
                {
                    "status": "ok",
                    "message": "Trainer.get_status incluye key_pos y progress_door_pos",
                }
            )
        else:
            results.append(
                {
                    "status": "fail",
                    "message": "Trainer.get_status: falta key_pos o progress_door_pos",
                }
            )
    except Exception as e:
        results.append(
            {"status": "warn", "message": f"No se pudo verificar Trainer: {e}"}
        )

    # 6. minimap_view usa posiciones dinamicas (no KEY_POS=(1,6) hardcodeado como constante global)
    try:
        mm_path = root / "interface" / "minimap_view.py"
        text = mm_path.read_text(encoding="utf-8")
        if "status.get" in text and "key_pos" in text:
            results.append(
                {
                    "status": "ok",
                    "message": "minimap_view.py usa posiciones dinamicas del status",
                }
            )
        else:
            results.append(
                {
                    "status": "fail",
                    "message": "minimap_view.py no usa posiciones dinamicas",
                }
            )
    except Exception as e:
        results.append(
            {"status": "warn", "message": f"No se pudo verificar minimap_view.py: {e}"}
        )

    # 7. README menciona version 0.4.5
    try:
        readme = (root / "README.md").read_text(encoding="utf-8")
        if "0.4.5" in readme:
            results.append(
                {"status": "ok", "message": "README.md menciona version 0.4.5"}
            )
        else:
            results.append(
                {"status": "warn", "message": "README.md no menciona version 0.4.5"}
            )
    except Exception as e:
        results.append({"status": "warn", "message": f"No se pudo leer README: {e}"})

    return results


def check_046_integrity(root: Path = ROOT) -> list[dict]:
    """Verifica integridad de BabyIA 0.4.6 (Double DQN, PER, percepcion en estado)."""
    results = []
    import sys as _sys

    _sys.path.insert(0, str(root))

    # 1. STATE_SIZE == 40
    try:
        from brain.baby_brain import STATE_SIZE

        if STATE_SIZE == 40:
            results.append(
                {"status": "ok", "message": f"STATE_SIZE={STATE_SIZE} (40 features)"}
            )
        else:
            results.append(
                {"status": "fail", "message": f"STATE_SIZE={STATE_SIZE} (esperado 40)"}
            )
    except Exception as e:
        results.append(
            {"status": "warn", "message": f"No se pudo verificar STATE_SIZE: {e}"}
        )

    # 2. Double DQN en baby_brain.py
    try:
        bb_path = root / "brain" / "baby_brain.py"
        text = bb_path.read_text(encoding="utf-8")
        if "q_net(ns).argmax" in text and "target_net(ns).gather" in text:
            results.append(
                {"status": "ok", "message": "baby_brain.py: Double DQN implementado"}
            )
        else:
            results.append(
                {"status": "fail", "message": "baby_brain.py: Double DQN no detectado"}
            )
    except Exception as e:
        results.append(
            {"status": "warn", "message": f"No se pudo verificar Double DQN: {e}"}
        )

    # 3. Prioritized Experience Replay en baby_brain.py
    try:
        bb_path = root / "brain" / "baby_brain.py"
        text = bb_path.read_text(encoding="utf-8")
        if "_SumTree" in text and "_PrioritizedReplayBuffer" in text:
            results.append(
                {"status": "ok", "message": "baby_brain.py: PER implementado"}
            )
        else:
            results.append(
                {"status": "fail", "message": "baby_brain.py: PER no detectado"}
            )
    except Exception as e:
        results.append({"status": "warn", "message": f"No se pudo verificar PER: {e}"})

    # 4. Percepcion en _full_obs
    try:
        import inspect
        from brain.trainer import Trainer

        src = inspect.getsource(Trainer._full_obs)
        if "perc_feats" in src and "key_visible" in src and "exploration_ratio" in src:
            results.append(
                {
                    "status": "ok",
                    "message": "Trainer._full_obs: percepcion en estado DQN",
                }
            )
        else:
            results.append(
                {
                    "status": "fail",
                    "message": "Trainer._full_obs: faltan features de percepcion",
                }
            )
    except Exception as e:
        results.append(
            {"status": "warn", "message": f"No se pudo verificar _full_obs: {e}"}
        )

    # 5. REPLAY_CAPACITY >= 50000
    try:
        from brain.baby_brain import REPLAY_CAPACITY

        if REPLAY_CAPACITY >= 50_000:
            results.append(
                {"status": "ok", "message": f"REPLAY_CAPACITY={REPLAY_CAPACITY}"}
            )
        else:
            results.append(
                {
                    "status": "fail",
                    "message": f"REPLAY_CAPACITY={REPLAY_CAPACITY} (esperado >=50000)",
                }
            )
    except Exception as e:
        results.append(
            {"status": "warn", "message": f"No se pudo verificar REPLAY_CAPACITY: {e}"}
        )

    # 6. STATE_SIZE sincronizado en objects.py
    try:
        from world.objects import STATE_SIZE as OBJECTS_STATE_SIZE

        if OBJECTS_STATE_SIZE == 40:
            results.append(
                {
                    "status": "ok",
                    "message": f"world/objects.py STATE_SIZE={OBJECTS_STATE_SIZE}",
                }
            )
        else:
            results.append(
                {
                    "status": "fail",
                    "message": f"world/objects.py STATE_SIZE={OBJECTS_STATE_SIZE} (esperado 40)",
                }
            )
    except Exception as e:
        results.append(
            {
                "status": "warn",
                "message": f"No se pudo verificar objects STATE_SIZE: {e}",
            }
        )

    # 7. Tests nuevos de 0.4.6 presentes
    new_tests = [
        "tests/test_double_dqn.py",
        "tests/test_per.py",
        "tests/test_perception_in_state.py",
    ]
    for t in new_tests:
        exists = (root / t).exists()
        results.append(
            {
                "status": "ok" if exists else "fail",
                "message": f"{t} {'existe' if exists else 'FALTA (0.4.6)'}",
            }
        )

    # 8. README menciona version 0.4.6
    try:
        readme = (root / "README.md").read_text(encoding="utf-8")
        if "0.4.6" in readme:
            results.append(
                {"status": "ok", "message": "README.md menciona version 0.4.6"}
            )
        else:
            results.append(
                {"status": "warn", "message": "README.md no menciona version 0.4.6"}
            )
    except Exception as e:
        results.append({"status": "warn", "message": f"No se pudo leer README: {e}"})

    return results


def check_046b_integrity(root: Path = ROOT) -> list[dict]:
    """Verifica integridad de BabyIA 0.4.6b (diagnostico de rutas, anti-estancamiento)."""
    results = []

    # 1. world/path_diagnostics.py existe y contiene check_path_to_key_and_door
    try:
        pd_path = root / "world" / "path_diagnostics.py"
        if pd_path.exists():
            text = pd_path.read_text(encoding="utf-8")
            if "check_path_to_key_and_door" in text:
                results.append(
                    {
                        "status": "ok",
                        "message": "world/path_diagnostics.py: check_path implementado",
                    }
                )
            else:
                results.append(
                    {
                        "status": "fail",
                        "message": "path_diagnostics.py: falta check_path_to_key_and_door",
                    }
                )
        else:
            results.append(
                {"status": "fail", "message": "world/path_diagnostics.py FALTA"}
            )
    except Exception as e:
        results.append(
            {"status": "warn", "message": f"No se pudo verificar path_diagnostics: {e}"}
        )

    # 2. MissionReward tiene MAX_MISSION_REWARD_PER_EPISODE
    try:
        mr_path = root / "brain" / "mission_reward.py"
        text = mr_path.read_text(encoding="utf-8")
        if "MAX_MISSION_REWARD_PER_EPISODE" in text:
            results.append(
                {
                    "status": "ok",
                    "message": "mission_reward.py: MAX_MISSION_REWARD_PER_EPISODE presente",
                }
            )
        else:
            results.append(
                {
                    "status": "fail",
                    "message": "mission_reward.py: falta MAX_MISSION_REWARD_PER_EPISODE",
                }
            )
    except Exception as e:
        results.append(
            {"status": "warn", "message": f"No se pudo verificar mission_reward: {e}"}
        )

    # 3. VisualMemory tiene repeated_collision_count
    try:
        vm_path = root / "brain" / "visual_memory.py"
        text = vm_path.read_text(encoding="utf-8")
        if "repeated_collision_count" in text:
            results.append(
                {
                    "status": "ok",
                    "message": "visual_memory.py: repeated_collision_count presente",
                }
            )
        else:
            results.append(
                {
                    "status": "fail",
                    "message": "visual_memory.py: falta repeated_collision_count",
                }
            )
    except Exception as e:
        results.append(
            {"status": "warn", "message": f"No se pudo verificar visual_memory: {e}"}
        )

    # 4. path_diagnostics expuesto en get_status()
    try:
        tr_path = root / "brain" / "trainer.py"
        text = tr_path.read_text(encoding="utf-8")
        if "path_diagnostics" in text and "check_path_to_key_and_door" in text:
            results.append(
                {"status": "ok", "message": "trainer.py: path_diagnostics integrado"}
            )
        else:
            results.append(
                {
                    "status": "fail",
                    "message": "trainer.py: path_diagnostics no integrado",
                }
            )
    except Exception as e:
        results.append(
            {"status": "warn", "message": f"No se pudo verificar trainer: {e}"}
        )

    # 5. Tests nuevos de 0.4.6b presentes
    new_tests = [
        "tests/test_path_diagnostics.py",
        "tests/test_visual_memory_stagnation.py",
        "tests/test_mission_reward_anti_loop.py",
        "tests/test_version_consistency.py",
        "tests/test_stagnation_status_payload.py",
    ]
    for t in new_tests:
        exists = (root / t).exists()
        results.append(
            {
                "status": "ok" if exists else "fail",
                "message": f"{t} {'existe' if exists else 'FALTA (0.4.6b)'}",
            }
        )

    return results


def check_047_integrity(root: Path = ROOT) -> list[dict]:
    """Verifica integridad de BabyIA 0.4.7 (estabilizacion, coherencia documental)."""
    results = []

    # 1. APP_VERSION es 0.4.7
    try:
        from config import APP_VERSION

        if APP_VERSION.startswith("0.4.7"):
            results.append({"status": "ok", "message": f"APP_VERSION={APP_VERSION!r}"})
        else:
            results.append(
                {
                    "status": "fail",
                    "message": f"APP_VERSION={APP_VERSION!r} (esperado 0.4.7)",
                }
            )
    except Exception as e:
        results.append(
            {"status": "warn", "message": f"No se pudo verificar APP_VERSION: {e}"}
        )

    # 2. MODEL_V4_6_LATEST y MODEL_V4_6_BEST en config.py
    try:
        cfg_text = (root / "config.py").read_text(encoding="utf-8")
        if "MODEL_V4_6_LATEST" in cfg_text and "MODEL_V4_6_BEST" in cfg_text:
            results.append(
                {
                    "status": "ok",
                    "message": "config.py: MODEL_V4_6_LATEST y MODEL_V4_6_BEST presentes",
                }
            )
        else:
            results.append(
                {
                    "status": "fail",
                    "message": "config.py: faltan MODEL_V4_6_LATEST o MODEL_V4_6_BEST",
                }
            )
    except Exception as e:
        results.append(
            {"status": "warn", "message": f"No se pudo verificar config.py: {e}"}
        )

    # 3. main.py usa MODEL_V4_6_LATEST
    try:
        main_text = (root / "main.py").read_text(encoding="utf-8")
        if "MODEL_V4_6_LATEST" in main_text:
            results.append(
                {"status": "ok", "message": "main.py: usa MODEL_V4_6_LATEST"}
            )
        else:
            results.append(
                {"status": "fail", "message": "main.py: no usa MODEL_V4_6_LATEST"}
            )
    except Exception as e:
        results.append(
            {"status": "warn", "message": f"No se pudo verificar main.py: {e}"}
        )

    # 4. AGENTS.md existe
    agents_md = root / "AGENTS.md"
    if agents_md.exists():
        results.append({"status": "ok", "message": "AGENTS.md existe"})
    else:
        results.append({"status": "fail", "message": "AGENTS.md FALTA"})

    # 5. AGENTS.md prohibe auto-commits
    try:
        agents_text = agents_md.read_text(encoding="utf-8")
        if "commits automaticos" in agents_text or "commits automáticos" in agents_text:
            results.append(
                {
                    "status": "ok",
                    "message": "AGENTS.md: regla de no auto-commits presente",
                }
            )
        else:
            results.append(
                {
                    "status": "warn",
                    "message": "AGENTS.md: regla de no auto-commits no encontrada",
                }
            )
    except Exception as e:
        results.append({"status": "warn", "message": f"No se pudo leer AGENTS.md: {e}"})

    # 6. AGENTS.md menciona conciencia real
    try:
        if "conciencia real" in agents_text:
            results.append(
                {
                    "status": "ok",
                    "message": "AGENTS.md: prohibicion de afirmar conciencia real",
                }
            )
        else:
            results.append(
                {
                    "status": "warn",
                    "message": "AGENTS.md: prohibicion de conciencia real no encontrada",
                }
            )
    except Exception:
        pass

    # 7. README menciona 0.4.7
    try:
        readme = (root / "README.md").read_text(encoding="utf-8")
        if "0.4.7" in readme:
            results.append(
                {"status": "ok", "message": "README.md menciona version 0.4.7"}
            )
        else:
            results.append(
                {"status": "warn", "message": "README.md no menciona version 0.4.7"}
            )
    except Exception as e:
        results.append({"status": "warn", "message": f"No se pudo leer README: {e}"})

    # 8. docs/evolucion.md menciona 0.4.7
    try:
        evo = (root / "docs" / "evolucion.md").read_text(encoding="utf-8")
        if "0.4.7" in evo:
            results.append(
                {"status": "ok", "message": "docs/evolucion.md menciona 0.4.7"}
            )
        else:
            results.append(
                {"status": "warn", "message": "docs/evolucion.md no menciona 0.4.7"}
            )
    except Exception as e:
        results.append(
            {"status": "warn", "message": f"No se pudo leer evolucion.md: {e}"}
        )

    # 9. Tests nuevos de 0.4.7 presentes
    new_tests = [
        "tests/test_version_047.py",
        "tests/test_model_versioning_047.py",
        "tests/test_agents_rules.py",
        "tests/test_health_check_047.py",
    ]
    for t in new_tests:
        exists = (root / t).exists()
        results.append(
            {
                "status": "ok" if exists else "fail",
                "message": f"{t} {'existe' if exists else 'FALTA (0.4.7)'}",
            }
        )

    return results


def check_046c_integrity(root: Path = ROOT) -> list[dict]:
    """Verifica integridad de BabyIA 0.4.6c (vista completa escalable del mundo)."""
    results = []

    # 1. interface/grid_scaler.py existe
    gs_path = root / "interface" / "grid_scaler.py"
    results.append(
        {
            "status": "ok" if gs_path.exists() else "fail",
            "message": "interface/grid_scaler.py "
            + ("existe" if gs_path.exists() else "FALTA"),
        }
    )

    # 2. interface/grid_renderer.py existe
    gr_path = root / "interface" / "grid_renderer.py"
    results.append(
        {
            "status": "ok" if gr_path.exists() else "fail",
            "message": "interface/grid_renderer.py "
            + ("existe" if gr_path.exists() else "FALTA"),
        }
    )

    # 3. pygame_view.py usa view_mode="full" por defecto
    try:
        pv_text = (root / "interface" / "pygame_view.py").read_text(encoding="utf-8")
        if 'self.view_mode = "full"' in pv_text or "self.view_mode = 'full'" in pv_text:
            results.append(
                {
                    "status": "ok",
                    "message": "pygame_view.py: view_mode='full' por defecto",
                }
            )
        else:
            results.append(
                {"status": "fail", "message": "pygame_view.py: falta view_mode='full'"}
            )
    except Exception as e:
        results.append(
            {"status": "warn", "message": f"No se pudo verificar pygame_view: {e}"}
        )

    # 4. 16x16 cabe en GRID_AREA con cell_size >= 28
    try:
        import sys as _sys

        _sys.path.insert(0, str(root))
        from interface.grid_scaler import get_scaled_cell_size
        from interface.layout import GRID_AREA

        cs = get_scaled_cell_size(GRID_AREA, 16)
        if cs >= 28:
            results.append(
                {
                    "status": "ok",
                    "message": f"16x16 en GRID_AREA: cell_size={cs}px >= 28",
                }
            )
        else:
            results.append(
                {
                    "status": "fail",
                    "message": f"16x16: cell_size={cs}px < 28 (ilegible)",
                }
            )
    except Exception as e:
        results.append(
            {"status": "warn", "message": f"No se pudo verificar cell_size 16x16: {e}"}
        )

    # 5. grid_scaler.py y grid_renderer.py <= 300 lineas
    for fname in ["interface/grid_scaler.py", "interface/grid_renderer.py"]:
        try:
            lines = len((root / fname).read_text(encoding="utf-8").splitlines())
            if lines <= 300:
                results.append(
                    {"status": "ok", "message": f"{fname}: {lines} lineas (<= 300)"}
                )
            else:
                results.append(
                    {"status": "fail", "message": f"{fname}: {lines} lineas (> 300)"}
                )
        except Exception as e:
            results.append(
                {"status": "warn", "message": f"No se pudo verificar {fname}: {e}"}
            )

    # 6. Tests nuevos de 0.4.6c presentes
    new_tests = [
        "tests/test_grid_scaler.py",
        "tests/test_full_world_view.py",
        "tests/test_view_mode_toggle.py",
        "tests/test_grid_renderer.py",
    ]
    for t in new_tests:
        exists = (root / t).exists()
        results.append(
            {
                "status": "ok" if exists else "fail",
                "message": f"{t} {'existe' if exists else 'FALTA (0.4.6c)'}",
            }
        )

    return results


def run_all_checks(root: Path = ROOT) -> list[dict]:
    checks = []
    checks.extend(check_structure(root))
    checks.extend(check_tests(root))
    checks.extend(check_file_lengths(root))
    checks.extend(check_network_calls(root))
    checks.extend(check_selfmod(root))
    checks.extend(check_interface_purity(root))
    checks.extend(check_data_files(root))
    checks.extend(check_level0_is_open(root))  # 0.2.2
    checks.extend(check_tasks_reset_zero(root))  # 0.2.2
    checks.extend(check_worlds_have_return(root))  # 0.3
    checks.extend(check_042_integrity(root))  # 0.4.2
    checks.extend(check_043_integrity(root))  # 0.4.3
    checks.extend(check_044_integrity(root))  # 0.4.4
    checks.extend(check_045_integrity(root))  # 0.4.5
    checks.extend(check_045b_integrity(root))  # 0.4.5b
    checks.extend(check_046_integrity(root))  # 0.4.6
    checks.extend(check_046b_integrity(root))  # 0.4.6b
    checks.extend(check_047_integrity(root))  # 0.4.7
    checks.extend(check_046c_integrity(root))  # 0.4.6c
    return checks


# ── CLI ───────────────────────────────────────────────────────────────────────


def main():
    console = Console(legacy_windows=False)
    results = run_all_checks()

    icons = {
        "ok": "[green] OK [/green]",
        "warn": "[yellow]WARN[/yellow]",
        "fail": "[red]FAIL[/red]",
    }

    t = Table(box=box.SIMPLE, show_header=False, padding=(0, 1))
    t.add_column("s", no_wrap=True)
    t.add_column("msg")

    for r in results:
        t.add_row(icons[r["status"]], r["message"])

    totals = {
        s: sum(1 for r in results if r["status"] == s) for s in ("ok", "warn", "fail")
    }
    summary = (
        f"[green]{totals['ok']} OK[/green]  "
        f"[yellow]{totals['warn']} advertencias[/yellow]  "
        f"[red]{totals['fail']} errores[/red]"
    )

    console.print(
        Panel(
            t,
            title="[bold cyan]BabyIA Health Check[/bold cyan]",
            subtitle=summary,
            border_style="cyan",
        )
    )

    if totals["fail"] > 0:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
