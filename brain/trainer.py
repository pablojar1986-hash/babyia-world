import numpy as np

from brain.baby_brain import BabyBrain
from brain.body_state import BodyState
from brain.causal_memory import CausalMemory
from brain.neural_debugger import get_brain_snapshot
from brain.concepts import ConceptMemory
from brain.survival import SurvivalEvaluator
from brain.curriculum import Curriculum
from brain.emotions import Emotions
from brain.home_drive import HomeDrive
from brain.memory import Memory
from brain.preferences import PreferenceTracker
from brain.self_model import SelfModel
from brain.strategy import StrategyTracker
from brain.utility_evaluator import UtilityEvaluator
from brain.world_memory import WorldMemory
from config import CAUSAL_MEMORY_FILE
from world.grid_world import GRID_SIZE, GridWorld
from world.interactions import (
    interact_danger,
    interact_door_closed,
    interact_food,
    interact_key,
    interact_unknown,
)
from world.inventory import Inventory
from worlds.world_manager import WorldManager

SAVE_EVERY = 10  # episodios entre guardados de memoria


class Trainer:
    """
    Orquesta el ciclo: mundo <-> cerebro <-> memoria.
    El guardado del cerebro lo gestiona ModelStore desde main.py.
    training=False desactiva aprendizaje (modos watch/evaluate).
    """

    def __init__(self, training: bool = True):
        self.world = GridWorld()
        self.brain = BabyBrain()
        self.memory = Memory()
        self.emotions = Emotions()
        self.self_model = SelfModel()
        self.curriculum = Curriculum()
        self.inventory = Inventory()
        self.concepts = ConceptMemory()
        self.strategies = StrategyTracker()

        # 0.3 — sistema de mundos multiples
        self.world_manager = WorldManager()
        self.world_memory = WorldMemory()
        self.preferences = PreferenceTracker()
        self.home_drive = HomeDrive()

        # 0.4 — estado corporal y aprendizaje causal
        self.body_state = BodyState()
        self.causal_memory = CausalMemory(CAUSAL_MEMORY_FILE)
        self.utility = UtilityEvaluator()

        # 0.4.2 — supervivencia funcional
        self.survival = SurvivalEvaluator()
        self._last_survival: dict = {}

        # 0.4.1 — diagnóstico de red neuronal (actualizado cada 5 pasos)
        self._last_brain_debug: dict = {}

        self.training = training
        self.episode = 0
        self.total_steps = 0

        self._ep_reward = 0.0
        self._ep_walls = 0
        self._ep_events: dict = {}  # eventos acumulados del episodio
        self._ep_ok = 0
        self._ep_fail = 0
        # 0.4.2 — contadores episódicos de powerups/hazards/puertas
        self._ep_powerups = 0
        self._ep_hazards = 0
        self._ep_hazards_blocked = 0
        self._ep_door_attempts = 0
        self._ep_door_successes = 0
        self._current_state: np.ndarray | None = None
        self._maze_info: dict = {
            "difficulty": "Basico",
            "seed": 0,
            "solvable": True,
            "level": 0,
        }

    # ── Control de episodio ────────────────────────────────────────────────────

    def start_episode(self):
        self.episode += 1
        self.self_model.experiences = self.episode
        self._ep_reward = 0.0
        self._ep_walls = 0
        self._ep_events = {}
        self._ep_ok = 0
        self._ep_fail = 0
        self._ep_powerups = 0
        self._ep_hazards = 0
        self._ep_hazards_blocked = 0
        self._ep_door_attempts = 0
        self._ep_door_successes = 0
        self.inventory.reset()
        self.world_manager.reset()
        self.home_drive.reset_episode()
        self.body_state.reset_for_episode()
        self.utility.reset_episode()
        base_obs = self.world.reset()
        self._current_state = self._full_obs(base_obs)

    def step(self):
        """Ejecuta un paso: accion -> mundo -> interacciones -> entrenamiento -> memoria."""
        state = self._current_state
        extra = self.emotions.exploration_bonus()
        action = self.brain.select_action(state, extra)

        base_next, base_reward, done, info = self.world.step(
            action, has_key=self.inventory.has_key
        )

        # Aplicar interacciones de objetos y calcular delta de recompensa
        obj_delta = self._apply_interactions(info)

        # 0.3: recompensa del mundo actual y transiciones de portal
        w_delta, w_events = self.world_manager.process_step(
            self.world.baby_pos, self.self_model.level
        )
        if not self.world_manager.is_at_home:
            self.home_drive.step_outside()
        if w_events.get("returned_home"):
            self.home_drive.register_return()
        if w_events:
            self._ep_events.update(w_events)

        reward = base_reward + obj_delta + w_delta

        # 0.4: tick de efectos corporales
        self.body_state.tick_effects()

        # 0.4.1: actualizar snapshot del cerebro cada 5 pasos (evita overhead)
        if self.total_steps % 5 == 0:
            exploration = self.brain.last_decision.get("decision_type") == "exploration"
            self._last_brain_debug = get_brain_snapshot(
                self.brain, state, action, exploration
            )

        # 0.4: registrar utilidad del paso (0.4.2: pasa inventory para fix energy bug)
        u = self.utility.evaluate_from_context(
            self.body_state,
            self.world_manager,
            self.causal_memory,
            base_reward=reward,
            step_count=self.world.steps,
            inventory=self.inventory,
        )
        self.utility.record_step_utility(u)

        # 0.4.2: supervivencia funcional (actualizado cada 5 pasos)
        if self.total_steps % 5 == 0:
            self._last_survival = self.survival.evaluate(
                self.body_state, self.inventory, self.world_manager
            )

        # Construir siguiente estado completo (con inventario ya actualizado)
        next_state = self._full_obs(base_next)

        if self.training:
            self.brain.remember(state, action, reward, next_state, done)
            self.brain.train()

        self.emotions.update(reward, info["hit_wall"], info["reached_goal"])
        self.memory.record_step(
            self.episode, self.world.steps, state, action, reward, info
        )

        if info["hit_wall"]:
            self._ep_walls += 1
        self._ep_reward += reward
        self.total_steps += 1
        self._current_state = next_state

        return action, reward, done, info

    def end_episode(self, reached_goal: bool) -> int | None:
        """
        Cierra el episodio, evalua nivel y guarda si toca.
        Devuelve el nuevo nivel si hubo subida, o None.
        """
        self.curriculum.record_episode(reached_goal, self._ep_walls)

        ev = dict(self._ep_events, reached_goal=reached_goal)
        phrase = self.memory.generate_phrase(
            self.episode,
            self._ep_reward,
            self._ep_walls,
            reached_goal,
            self.brain.epsilon,
            events=ev,
        )
        self.memory.record_autobiography(phrase)

        # Estrategias emergentes
        touched = self.inventory.touched_objects
        self.strategies.observe(ev, touched)

        new_level = self.curriculum.check_level_up()
        if new_level is not None:
            self.self_model.level_up(new_level)
            from world.level_factory import get_maze_for_level, save_level_stats

            maze = get_maze_for_level(new_level)
            self.world.set_walls(maze["walls"])
            self._maze_info = maze
            save_level_stats(maze)

        # 0.3 — registrar visita y actualizar preferencias
        ep_sum = self.world_manager.get_episode_summary()
        self.world_memory.record_visit(
            episode=self.episode,
            world_id=ep_sum["world_id"],
            entered_from=ep_sum["last_portal"] or "home",
            reward_gained=ep_sum["reward_outside"],
            risk_events=int(bool(self._ep_events.get("in_danger"))),
            returned_home=ep_sum["is_at_home"],
            steps_spent=ep_sum["steps_outside"],
        )
        self.preferences.update(
            world_id=ep_sum["world_id"],
            reward=ep_sum["reward_outside"],
            risk_events=int(bool(self._ep_events.get("in_danger"))),
            returned_home=ep_sum["is_at_home"],
            steps=ep_sum["steps_outside"],
        )
        self.home_drive.end_episode()
        pref = self.preferences.get_score(self.world_manager.current_world_id)
        self.world_manager.set_preference_score(pref)
        # 0.3.1: penalizar si episodio termino fuera de casa
        self._ep_reward += self.world_manager.on_episode_end()

        if self.episode % SAVE_EVERY == 0:
            self.memory.save()
            self.concepts.save()
            self.world_memory.save()
            self.preferences.save()
            self.home_drive.save()
            self.causal_memory.save()

        return new_level

    # ── Estado para la interfaz ────────────────────────────────────────────────

    def get_status(self) -> dict:
        stats = self.curriculum.get_stats()
        top_c = self.concepts.top_concepts(2)
        return {
            "episode": self.episode,
            "level": self.self_model.level,
            "epsilon": round(self.brain.epsilon, 3),
            "episode_reward": round(self._ep_reward, 2),
            "episode_walls": self._ep_walls,
            "total_steps": self.total_steps,
            "success_rate": stats["success_rate"],
            "avg_walls": stats["avg_walls"],
            "loss": round(self.brain.last_loss, 4),
            "emotions": self.emotions.to_dict(),
            "self_model": self.self_model.to_dict(),
            "last_log": self.memory.last_log_entries(4),
            "inventory": self.inventory.to_dict(),
            "concepts": top_c,
            "ep_events": dict(self._ep_events),
            "maze_info": self._maze_info,
            # 0.3
            "world_info": self.world_manager.get_episode_summary(),
            "home_drive": self.home_drive.to_dict(),
            # 0.4
            "body_state": self.body_state.to_dict(),
            "utility": self.utility.to_dict(),
            "causal_learned": self.causal_memory.count_learned(),
            # 0.4.1
            "brain_debug": self._last_brain_debug,
            # 0.4.2
            "survival": dict(self._last_survival),
            "causal_relations": [
                r.to_dict()
                for r in self.causal_memory.all_relations()[-6:]
            ],
            "ep_powerups": self._ep_powerups,
            "ep_hazards": self._ep_hazards,
            "ep_hazards_blocked": self._ep_hazards_blocked,
            "ep_door_attempts": self._ep_door_attempts,
            "ep_door_successes": self._ep_door_successes,
        }

    # ── Internos ──────────────────────────────────────────────────────────────

    def _full_obs(self, base_obs: np.ndarray) -> np.ndarray:
        """
        Vector de observacion completo para el DQN.
        10 base + 8 inventario/objetos + 8 contexto-mundo + 8 estado-corporal = 34
        """
        inv = self.inventory
        world = self.world
        bx, by = world.baby_pos
        n = float(GRID_SIZE - 1)
        obj = world.get_object_state()

        kx, ky = obj["key_pos"]
        dx, dy = obj["door_pos"]

        dist_key_x = (kx - bx) / n if obj["key_present"] else 0.0
        dist_key_y = (ky - by) / n if obj["key_present"] else 0.0

        extra = np.array(
            [
                float(inv.has_key),  # 11
                inv.energy,  # 12
                dist_key_x,  # 13
                dist_key_y,  # 14
                (dx - bx) / n,  # 15
                (dy - by) / n,  # 16
                float(world.door_open),  # 17
                float(world.danger_nearby()),  # 18
            ],
            dtype=np.float32,
        )

        # 0.3: 8 features de contexto de mundo (indices 18-25)
        world_feats = self.world_manager.get_state_features(tuple(self.world.baby_pos))
        # 0.4.2: features corporales con proximidad real (indices 26-33)
        pu_near = 1.0 if self.world.get_nearby_powerup() else 0.0
        hz_near = 1.0 if self.world.get_nearby_hazard() else 0.0
        sd_near = 1.0 if self.world.get_nearby_special_door() else 0.0
        body_feats = self.body_state.get_state_features(pu_near, hz_near, sd_near)
        return np.concatenate([base_obs, extra, world_feats, body_feats])

    def _apply_interactions(self, info: dict) -> float:
        """
        Aplica efectos de interacciones sobre Inventory y ConceptMemory.
        Devuelve el delta de recompensa total de objetos.
        """
        delta = 0.0
        inv = self.inventory

        if info.get("picked_key"):
            first = inv.first_touch("key")
            result = interact_key(inv.has_key, first)
            inv.pick_key()
            delta += result["reward_delta"]
            self.concepts.observe(result["concept_signal"], True, self.episode)
            self._ep_events["picked_key"] = True
            self._ep_ok += 1

        if info.get("opened_door"):
            result = interact_door_closed(has_key=True)
            inv.use_key()
            delta += result["reward_delta"]
            self.concepts.observe(result["concept_signal"], True, self.episode)
            self._ep_events["opened_door"] = True
            self._ep_ok += 1

        if info.get("hit_door_closed"):
            result = interact_door_closed(has_key=False)
            delta += result["reward_delta"]
            self.concepts.observe(result["concept_signal"], False, self.episode)
            self._ep_events["hit_door_closed"] = True
            self._ep_fail += 1

        if info.get("ate_food"):
            result = interact_food(inv.energy)
            self._ep_events["energy_before_food"] = inv.energy
            inv.eat_food()
            delta += result["reward_delta"] + self.world_manager.on_object_event(
                "ate_food"
            )
            self.concepts.observe(result["concept_signal"], True, self.episode)
            self._ep_events["ate_food"] = True
            self._ep_ok += 1

        if info.get("in_danger"):
            result = interact_danger()
            inv.take_damage()
            delta += result["reward_delta"] + self.world_manager.on_object_event(
                "in_danger"
            )
            self.concepts.observe(result["concept_signal"], False, self.episode)
            self._ep_events["in_danger"] = True
            self._ep_fail += 1

        if info.get("found_unknown"):
            first = inv.first_touch("unknown")
            result = interact_unknown(first)
            inv.touch("unknown")
            delta += result["reward_delta"] + self.world_manager.on_object_event(
                "found_unknown"
            )
            self.concepts.observe(result["concept_signal"], True, self.episode)
            self._ep_events["found_unknown"] = True
            self._ep_ok += 1

        # 0.4.2: powerups, hazards y puertas especiales
        if info.get("hit_powerup"):
            delta += self._handle_powerup(info["hit_powerup"])
        if info.get("hit_hazard"):
            delta += self._handle_hazard(info["hit_hazard"])
        if info.get("hit_special_door"):
            delta += self._handle_special_door(info["hit_special_door"])

        return delta

    # ── Handlers 0.4.2 ───────────────────────────────────────────────────────

    def _handle_powerup(self, powerup_id: str) -> float:
        from world.powerups import POWERUP_TYPES, apply_powerup_effect

        pu = POWERUP_TYPES.get(powerup_id)
        if not pu:
            return 0.0
        apply_powerup_effect(powerup_id, self.body_state, self.inventory)
        self.concepts.observe(pu.get_concept_signal(), True, self.episode)
        self.causal_memory.observe(powerup_id, pu.effect, True, self.episode)
        self._ep_events["last_powerup"] = powerup_id
        self._ep_powerups += 1
        return pu.reward_delta

    def _handle_hazard(self, hazard_id: str) -> float:
        from world.hazards import HAZARD_TYPES, apply_hazard_to_body

        hz = HAZARD_TYPES.get(hazard_id)
        if not hz:
            return 0.0
        energy_damage, blocked = apply_hazard_to_body(hazard_id, self.body_state)
        if energy_damage > 0 and not blocked:
            self.inventory.take_damage_by(energy_damage)
        self.causal_memory.observe(hazard_id, hz.effect, not blocked, self.episode)
        self._ep_events["last_hazard"] = hazard_id
        self._ep_events["last_hazard_blocked"] = blocked
        self._ep_hazards += 1
        if blocked:
            self._ep_hazards_blocked += 1
        return 0.0 if blocked else hz.reward_delta

    def _handle_special_door(self, door_id: str) -> float:
        from world.doors import DOOR_TYPES, attempt_door

        result = attempt_door(door_id, self.body_state, known_concepts=None)
        outcome = "opened" if result["success"] else "blocked"
        self.causal_memory.observe(door_id, outcome, result["success"], self.episode)
        self._ep_door_attempts += 1
        if result["success"]:
            self._ep_door_successes += 1
            self._ep_events[f"door_{door_id}"] = "ok"
        else:
            self._ep_events["last_door_fail"] = result["fail_reason"]
        return result["reward_delta"]
