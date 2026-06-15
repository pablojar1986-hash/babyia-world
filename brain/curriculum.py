from collections import deque

EVAL_WINDOW = 20
MAX_LEVEL   = 6

# nivel_actual -> (success_rate_minima, max_avg_walls_o_None)
_THRESHOLDS: dict[int, tuple] = {
    0: (0.70, None),
    1: (0.70, 3.0),
    2: (0.80, 1.0),
    3: (0.80, 1.0),
    4: (0.85, 1.0),
    5: (0.90, 1.0),
}


class Curriculum:
    """
    Gestiona el sistema de niveles (0-6).
    BabyIA solo sube de nivel si cumple metricas de exito sostenidas.
    Senaliza cambios de laberinto via maze_needs_update / consume_maze_update().
    """

    def __init__(self):
        self.current_level     = 0
        self.maze_needs_update = False
        self._successes        = deque(maxlen=EVAL_WINDOW)
        self._wall_counts      = deque(maxlen=EVAL_WINDOW)

    def record_episode(self, reached_goal: bool, wall_hits: int):
        self._successes.append(1 if reached_goal else 0)
        self._wall_counts.append(wall_hits)

    def check_level_up(self) -> int | None:
        """Devuelve el nuevo nivel si se cumplen los criterios, o None."""
        if len(self._successes) < EVAL_WINDOW or self.current_level >= MAX_LEVEL:
            return None

        success_rate = sum(self._successes) / EVAL_WINDOW
        avg_walls    = sum(self._wall_counts) / EVAL_WINDOW
        threshold    = _THRESHOLDS.get(self.current_level)

        if threshold is None:
            return None

        min_sr, max_w = threshold
        walls_ok = (max_w is None) or (avg_walls <= max_w)

        if success_rate >= min_sr and walls_ok:
            self.current_level    += 1
            self.maze_needs_update = True
            return self.current_level

        return None

    def consume_maze_update(self) -> bool:
        """Devuelve True y resetea la bandera si hay cambio de laberinto pendiente."""
        if self.maze_needs_update:
            self.maze_needs_update = False
            return True
        return False

    def get_stats(self) -> dict:
        if not self._successes:
            return {"success_rate": 0.0, "avg_walls": 0.0}
        return {
            "success_rate": round(sum(self._successes) / len(self._successes), 3),
            "avg_walls"   : round(sum(self._wall_counts) / len(self._wall_counts), 1),
        }
