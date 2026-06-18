"""
Evaluador de utilidad de BabyIA World 0.4.
Calcula la utilidad esperada de una accion o situacion.
NO reemplaza al DQN — es una capa explicativa para metricas y visualizacion.
Formula:
  utility = expected_reward
          + usefulness_for_goal
          + return_home_bonus
          - expected_risk
          - energy_cost
          - time_cost
"""


class UtilityEvaluator:
    def __init__(self):
        self._last_utility: float = 0.0
        self._last_breakdown: dict = {}
        self._episode_utilities: list[float] = []

    # ── Calculo principal ─────────────────────────────────────────────────────

    def evaluate(
        self,
        expected_reward: float = 0.0,
        usefulness_for_goal: float = 0.0,
        return_home_bonus: float = 0.0,
        expected_risk: float = 0.0,
        energy_cost: float = 0.0,
        time_cost: float = 0.0,
    ) -> float:
        utility = (
            expected_reward
            + usefulness_for_goal
            + return_home_bonus
            - expected_risk
            - energy_cost
            - time_cost
        )
        self._last_utility = round(utility, 4)
        self._last_breakdown = {
            "expected_reward": expected_reward,
            "usefulness_for_goal": usefulness_for_goal,
            "return_home_bonus": return_home_bonus,
            "expected_risk": expected_risk,
            "energy_cost": energy_cost,
            "time_cost": time_cost,
            "total": self._last_utility,
        }
        return self._last_utility

    def evaluate_from_context(
        self,
        body_state,
        world_manager,
        causal_memory,
        base_reward: float = 0.0,
        step_count: int = 0,
        inventory=None,
    ) -> float:
        """
        Calcula utilidad a partir de objetos del sistema.
        Resumen heuristico — no usa inferencia profunda.
        """
        # Costo por energia baja (usa Inventory.energy; 0.4.2 fix)
        energy = inventory.energy if inventory is not None else 1.0
        energy_cost = max(0.0, 1.0 - energy) * 0.5

        # Costo de tiempo creciente si lleva muchos pasos fuera
        time_cost = min(1.0, step_count / 200.0)

        # Riesgo basado en nivel del mundo actual
        wdef = None
        if hasattr(world_manager, "current_world"):
            wid = world_manager.current_world
            from worlds.world_registry import ALL_WORLDS

            wdef = ALL_WORLDS.get(wid)
        expected_risk = wdef.risk_level if wdef else 0.0

        # Bonus de regreso a casa si lleva muchos pasos fuera
        return_home_bonus = 0.0
        if hasattr(world_manager, "should_return_home"):
            if world_manager.should_return_home():
                return_home_bonus = 2.0

        # Utilidad de aprendizaje causal
        usefulness = 0.0
        if causal_memory and causal_memory.count_learned() > 0:
            usefulness = min(1.0, causal_memory.count_learned() * 0.1)

        return self.evaluate(
            expected_reward=base_reward,
            usefulness_for_goal=usefulness,
            return_home_bonus=return_home_bonus,
            expected_risk=expected_risk,
            energy_cost=energy_cost,
            time_cost=time_cost,
        )

    # ── Seguimiento episodico ─────────────────────────────────────────────────

    def record_step_utility(self, utility: float):
        self._episode_utilities.append(utility)

    def reset_episode(self):
        self._episode_utilities = []
        self._last_utility = 0.0
        self._last_breakdown = {}

    def average_episode_utility(self) -> float:
        if not self._episode_utilities:
            return 0.0
        return round(sum(self._episode_utilities) / len(self._episode_utilities), 4)

    # ── Consultas ─────────────────────────────────────────────────────────────

    @property
    def last_utility(self) -> float:
        return self._last_utility

    @property
    def last_breakdown(self) -> dict:
        return dict(self._last_breakdown)

    def to_dict(self) -> dict:
        return {
            "last_utility": self._last_utility,
            "avg_episode_utility": self.average_episode_utility(),
            "steps_evaluated": len(self._episode_utilities),
            "last_breakdown": self._last_breakdown,
        }
