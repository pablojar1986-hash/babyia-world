"""
BabyIA World 0.4 — punto de entrada.

Modos:
  python main.py                              -> train (por defecto)
  python main.py --mode train --episodes 500
  python main.py --mode watch
  python main.py --mode evaluate --episodes 50
  python main.py --seed 42
  python main.py --reset-memory
  python main.py --reset-model
  python main.py --reset-stats
  python main.py --reset-all --yes
  python main.py --reset-all --episodes 0    (reset sin entrenar)
"""

import argparse
import random
from dataclasses import dataclass

import numpy as np
import torch

from brain.metrics import TrainingMetrics
from brain.model_store import ModelStore
from brain.network_inspector import save_network_stats
from brain.trainer import Trainer
from config import (
    DEFAULT_EPISODES,
    INFERENCE_EPSILON,
    MODE_EVALUATE,
    MODE_TRAIN,
    MODE_WATCH,
    MODEL_V4_BEST,
    MODEL_V4_LATEST,
    SAVE_LATEST_EVERY,
    SAVE_METRICS_EVERY,
)
from interface.console_panel import (
    console,
    log_episode_end,
    log_episode_start,
    log_level_up,
    log_start,
)
from interface.pygame_view import PygameView

LOG_EVERY = 5


@dataclass
class RunConfig:
    mode: str = MODE_TRAIN
    episodes: int = DEFAULT_EPISODES[MODE_TRAIN]
    seed: int | None = None
    reset_memory: bool = False
    reset_model: bool = False
    reset_stats: bool = False
    reset_concepts: bool = False
    yes: bool = False  # 0.2.2: confirmar operaciones destructivas


# ── Argumentos ────────────────────────────────────────────────────────────────


def parse_args() -> RunConfig:
    parser = argparse.ArgumentParser(
        description="BabyIA World — IA que aprende desde cero",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--mode",
        choices=[MODE_TRAIN, MODE_WATCH, MODE_EVALUATE],
        default=MODE_TRAIN,
        help="Modo de ejecucion",
    )
    parser.add_argument(
        "--episodes",
        type=int,
        default=None,
        help="Cantidad de episodios a ejecutar (0 = solo reset)",
    )
    parser.add_argument(
        "--seed", type=int, default=None, help="Semilla para reproducibilidad"
    )
    parser.add_argument(
        "--reset-memory",
        action="store_true",
        help="Borra memorias JSON antes de iniciar",
    )
    parser.add_argument(
        "--reset-model",
        action="store_true",
        help="Borra pesos .pt antes de iniciar (nace desde cero)",
    )
    parser.add_argument(
        "--reset-stats", action="store_true", help="Borra estadisticas de entrenamiento"
    )
    parser.add_argument(
        "--reset-concepts",
        action="store_true",
        help="Borra conceptos aprendidos (data/concepts.json)",
    )
    parser.add_argument(
        "--reset-all",
        action="store_true",
        help="Borra memorias, modelo, estadisticas y conceptos",
    )
    parser.add_argument(
        "--yes",
        action="store_true",
        help="Confirma operaciones destructivas sin advertencia",
    )

    args = parser.parse_args()

    if args.reset_all:
        args.reset_memory = True
        args.reset_model = True
        args.reset_stats = True
        args.reset_concepts = True

    # 0.2.2: usar is not None para que --episodes 0 no sea ignorado
    episodes = (
        args.episodes if args.episodes is not None else DEFAULT_EPISODES[args.mode]
    )

    return RunConfig(
        mode=args.mode,
        episodes=episodes,
        seed=args.seed,
        reset_memory=args.reset_memory,
        reset_model=args.reset_model,
        reset_stats=args.reset_stats,
        reset_concepts=getattr(args, "reset_concepts", False),
        yes=args.yes,
    )


# ── Helpers ───────────────────────────────────────────────────────────────────


def set_seed(seed: int):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)


def handle_resets(
    cfg: RunConfig, trainer: Trainer, metrics: TrainingMetrics, store: ModelStore
):
    any_reset = (
        cfg.reset_memory or cfg.reset_model or cfg.reset_stats or cfg.reset_concepts
    )
    if any_reset and not cfg.yes:
        console.print(
            "[bold red]ADVERTENCIA: operacion destructiva en curso. "
            "Usa --yes para omitir esta advertencia.[/bold red]"
        )
    if cfg.reset_memory:
        trainer.memory.episodes = []
        trainer.memory.autobiography = []
        trainer.memory.save()
        console.print("[yellow]Memorias reiniciadas.[/yellow]")
    if cfg.reset_model:
        store.reset()
        console.print("[yellow]Modelos eliminados. BabyIA nace desde cero.[/yellow]")
    if cfg.reset_stats:
        metrics.reset()
        console.print("[yellow]Estadisticas reiniciadas.[/yellow]")
    if cfg.reset_concepts:
        trainer.concepts.reset()
        console.print("[yellow]Conceptos reiniciados.[/yellow]")


def build_status(trainer: Trainer, metrics: TrainingMetrics, mode: str) -> dict:
    """Combina estado del trainer con metricas agregadas para la vista."""
    return {
        **trainer.get_status(),
        "mode": mode,
        "avg_reward": metrics.average_reward,
        "avg_steps": metrics.average_steps,
    }


# ── Bucle de episodio ─────────────────────────────────────────────────────────


def run_episode(
    trainer: Trainer, view: PygameView, metrics: TrainingMetrics, mode: str
) -> tuple[bool, bool, dict]:
    trainer.start_episode()
    log_episode_start(trainer.episode, trainer.self_model.level)

    done, reached_goal, level_completed = False, False, False

    while not done and view.running:
        if not view.handle_events():
            break

        action, reward, done, info = trainer.step()

        if info.get("reached_goal"):
            reached_goal = True
        if info.get("level_completed"):
            level_completed = True

        view.render(trainer.world, build_status(trainer, metrics, mode))

    return reached_goal, level_completed, trainer.get_status()


# ── Main ──────────────────────────────────────────────────────────────────────


def main():
    cfg = parse_args()

    if cfg.seed is not None:
        set_seed(cfg.seed)

    is_training = cfg.mode == MODE_TRAIN

    log_start()
    console.print(
        f"[dim]Modo: {cfg.mode.upper()}  Episodios: {cfg.episodes}"
        + (f"  Seed: {cfg.seed}" if cfg.seed else "")
        + "[/dim]"
    )

    trainer = Trainer(training=is_training)
    metrics = TrainingMetrics()
    store = ModelStore(
        trainer.brain, model_latest=MODEL_V4_LATEST, model_best=MODEL_V4_BEST
    )
    view = PygameView(title="BabyIA World 0.4.3")

    # 0.2.2: guardar y mostrar metadatos de arquitectura al iniciar
    net_info = save_network_stats(trainer.brain.q_net)
    console.print(
        f"[dim]Red DQN: input={net_info['input_size']} "
        f"output={net_info['output_size']} "
        f"params={net_info['total_params']} "
        f"v{net_info['version']}[/dim]"
    )

    handle_resets(cfg, trainer, metrics, store)

    # Cargar modelo (si no fue reseteado)
    if not cfg.reset_model:
        loaded = store.load()
        if loaded:
            console.print("[dim]Modelo cargado desde babyia_latest.pt[/dim]")
        elif store.last_load_error:
            console.print(f"[yellow]{store.last_load_error}[/yellow]")

    # Inicializar mejor tasa conocida (para no sobreescribir el mejor modelo)
    store.init_best_rate(metrics.best_success_rate)

    # En watch/evaluate, epsilon minimo
    if not is_training:
        trainer.brain.epsilon = INFERENCE_EPSILON

    try:
        for ep_idx in range(cfg.episodes):
            if not view.running:
                break

            reached_goal, level_completed, status = run_episode(
                trainer, view, metrics, cfg.mode
            )
            new_level = trainer.end_episode(
                reached_goal, level_completed=level_completed
            )

            # 0.4.3: anti-estancamiento progresivo — fija un piso de epsilon
            # proporcional a la gravedad (el decay no puede bajar de ese piso)
            if is_training and status.get("stagnation_active"):
                ewp = status.get("episodes_without_progress", 0)
                if ewp > 500:
                    stag_floor, stag_label = 0.85, "CRITICO"
                elif ewp > 300:
                    stag_floor, stag_label = 0.65, "severo"
                elif ewp > 200:
                    stag_floor, stag_label = 0.45, "moderado"
                else:
                    stag_floor, stag_label = 0.25, "leve"
                if trainer.brain.epsilon < stag_floor:
                    trainer.brain.epsilon = stag_floor
                    console.print(
                        f"[yellow]Anti-estancamiento {stag_label} "
                        f"({ewp}ep): epsilon={stag_floor}[/yellow]"
                    )

            ev = status.get("ep_events", {})
            inv = status.get("inventory", {})
            world_info = status.get("world_info", {})
            metrics.record_episode(
                reached_goal=reached_goal,
                reward=status["episode_reward"],
                steps=trainer.world.steps,
                wall_hits=status["episode_walls"],
                epsilon=trainer.brain.epsilon,
                level=trainer.self_model.level,
                keys=1 if ev.get("picked_key") else 0,
                doors=1 if ev.get("opened_door") else 0,
                food=inv.get("food_count", 0),
                danger=1 if ev.get("in_danger") else 0,
                concepts=trainer.concepts.total(),
                ok=status.get("ep_events", {}).get("picked_key", 0),
                fail=0,
                world_id=world_info.get("world_id", "home"),
                returned_home=world_info.get("is_at_home", True),
                # 0.4.2 — powerups, hazards y puertas especiales
                powerups=status.get("ep_powerups", 0),
                hazards=status.get("ep_hazards", 0),
                hazards_blocked=status.get("ep_hazards_blocked", 0),
                door_attempts=status.get("ep_door_attempts", 0),
                door_successes=status.get("ep_door_successes", 0),
                causal_learned=status.get("causal_learned", 0),
                # 0.4.3 — puertas de nivel
                level_completed=level_completed,
                next_door_attempts=status.get("ep_next_door_blocked", 0),
                next_door_successes=1 if level_completed else 0,
                next_door_fails_no_key=status.get("ep_next_door_blocked", 0),
                optional_rooms=status.get("ep_optional_rooms", 0),
                treasure_rooms=status.get("ep_treasure_rooms", 0),
                episodes_without_progress=status.get("episodes_without_progress", 0),
            )

            if is_training:
                if trainer.episode % SAVE_LATEST_EVERY == 0:
                    store.save_latest()
                    store.save_best(metrics.recent_success_rate)
                store.save_checkpoint(trainer.episode)
                if trainer.episode % SAVE_METRICS_EVERY == 0:
                    metrics.save()

            if new_level is not None:
                log_level_up(new_level)

            if (ep_idx + 1) % LOG_EVERY == 0:
                log_episode_end(build_status(trainer, metrics, cfg.mode))

    except KeyboardInterrupt:
        console.print("\n[yellow]Interrumpido por el usuario.[/yellow]")

    finally:
        trainer.memory.save()
        trainer.concepts.save()
        metrics.save()
        if is_training:
            store.save_latest()
        view.quit()
        console.print(
            "[bold green]BabyIA guardo su progreso. Hasta pronto.[/bold green]"
        )


if __name__ == "__main__":
    main()
