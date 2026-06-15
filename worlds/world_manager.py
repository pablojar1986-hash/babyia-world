"""
Gestor de mundos: controla en que mundo esta BabyIA y gestiona transiciones.
Capa logica independiente: no modifica GridWorld.
"""
import numpy as np

from worlds.portal import Portal
from worlds.reward_profiles import REWARD_PROFILES, EPISODE_END_OUTSIDE_HOME
from worlds.world_definition import WorldDefinition
from worlds.world_registry import (
    ALL_WORLDS, HOME_PORTALS, HOME_WORLD_ID, RETURN_HOME_PORTAL, WORLD_IDS,
)

GRID_SIZE = 8
RETURN_SIGNAL_STEPS = 60  # pasos fuera de casa para activar senal de regreso


class WorldManager:
    """
    Controla el mundo actual de BabyIA, detecta portales y ajusta recompensas.
    Se llama desde Trainer.step(); GridWorld no sabe nada de mundos.
    """

    def __init__(self):
        self.current_world_id  = HOME_WORLD_ID
        self.is_at_home        = True
        self.reward_outside    = 0.0          # recompensa acumulada fuera de casa
        self.worlds_visited    : set[str] = {HOME_WORLD_ID}
        self._steps_outside    = 0
        self._explored         = False        # gano recompensa fuera antes de volver
        self._last_portal      : str | None = None
        self._pref_score       = 0.0
        self._portal_map       : dict[tuple, Portal] = {}
        self._build_portal_map()

    # ── Reset ─────────────────────────────────────────────────────────────────

    def reset(self):
        self.current_world_id = HOME_WORLD_ID
        self.is_at_home       = True
        self.reward_outside   = 0.0
        self.worlds_visited   = {HOME_WORLD_ID}
        self._steps_outside   = 0
        self._explored        = False
        self._last_portal     = None

    # ── Por paso ──────────────────────────────────────────────────────────────

    def process_step(self, pos: tuple, player_level: int) -> tuple[float, dict]:
        """
        Procesa la posicion de BabyIA cada paso.
        Retorna (reward_delta, events).
        """
        pos    = tuple(pos)
        delta  = 0.0
        events : dict = {}

        portal = self._portal_map.get(pos)
        if portal and portal.can_enter(player_level):
            if portal.target_world == HOME_WORLD_ID:
                if not self.is_at_home:
                    delta = self._do_return_home()
                    events["returned_home"] = True
                    events["return_reward"] = delta
            elif self.is_at_home and portal.target_world != self.current_world_id:
                self.current_world_id = portal.target_world
                self.is_at_home       = False
                self.worlds_visited.add(portal.target_world)
                self._last_portal     = portal.portal_id
                self._explored        = False
                events["entered_world"] = portal.target_world
                events["portal_used"]   = portal.portal_id

        # Recompensa de paso segun mundo actual
        if self.is_at_home:
            delta += self._profile().get("safe_step", 0.0)
        else:
            self._steps_outside += 1
            delta += self._profile().get("step_penalty", 0.0)

        return delta, events

    def on_object_event(self, event: str) -> float:
        """Ajusta recompensa de evento de objeto segun perfil del mundo actual."""
        mapping = {
            "ate_food"       : "eat_food",
            "in_danger"      : "danger_penalty",
            "found_unknown"  : "discover_unknown",
            "survive_danger" : "survive_danger_zone",
        }
        key   = mapping.get(event, "")
        delta = self._profile().get(key, 0.0)
        if delta > 0 and not self.is_at_home:
            self.reward_outside += delta
            self._explored = True
        return delta

    def on_episode_end(self) -> float:
        if not self.is_at_home:
            return EPISODE_END_OUTSIDE_HOME
        return 0.0

    # ── Consultas ─────────────────────────────────────────────────────────────

    def should_return_home(self) -> bool:
        return not self.is_at_home and self._steps_outside >= RETURN_SIGNAL_STEPS

    def get_current_world(self) -> WorldDefinition:
        return ALL_WORLDS[self.current_world_id]

    def get_state_features(self, baby_pos: tuple) -> np.ndarray:
        """8 features de contexto de mundo para el vector de observacion del DQN."""
        bx, by = baby_pos
        n      = float(GRID_SIZE - 1)
        # Indice de mundo normalizado [0,1]
        w_idx  = WORLD_IDS.index(self.current_world_id) / max(len(WORLD_IDS) - 1, 1)
        # Proximidad a casa (mayor = mas cerca)
        prox_home = 1.0 - (bx + by) / (2 * n)
        pref  = min(max(self._pref_score / 20.0, 0.0), 1.0)
        risk  = self.get_current_world().risk_level
        return np.array([
            w_idx,
            float(self.is_at_home),
            prox_home,
            min(self.reward_outside / 20.0, 1.0),
            pref,
            risk,
            len(self.worlds_visited) / len(ALL_WORLDS),
            float(self.should_return_home()),
        ], dtype=np.float32)

    def set_preference_score(self, score: float):
        self._pref_score = score

    def get_episode_summary(self) -> dict:
        return {
            "world_id"     : self.current_world_id,
            "is_at_home"   : self.is_at_home,
            "reward_outside": self.reward_outside,
            "worlds_visited": list(self.worlds_visited),
            "steps_outside" : self._steps_outside,
            "last_portal"   : self._last_portal,
        }

    def get_portals(self) -> list[Portal]:
        return list(HOME_PORTALS.values())

    # ── Internos ──────────────────────────────────────────────────────────────

    def _build_portal_map(self):
        for p in HOME_PORTALS.values():
            self._portal_map[p.position] = p
        self._portal_map[RETURN_HOME_PORTAL.position] = RETURN_HOME_PORTAL

    def _do_return_home(self) -> float:
        self.current_world_id = HOME_WORLD_ID
        self.is_at_home       = True
        self._steps_outside   = 0
        profile = REWARD_PROFILES["home"]
        if self._explored:
            self._explored = False
            return profile.get("return_after_explore", 20.0)
        return profile.get("return_home_base", 10.0)

    def _profile(self) -> dict:
        world = self.get_current_world()
        return REWARD_PROFILES.get(world.reward_profile, {})
