from collections import deque

EVAL_WINDOW = 20
MAX_LEVEL = 6
STAGNATION_THRESHOLD = 100  # episodios sin completar nivel → anti-estancamiento

# nivel_actual -> completions_minimas para subir
_LEVEL_COMPLETIONS: dict[int, int] = {
    0: 1,  # basta con 1 completion para salir del nivel 0
    1: 3,
    2: 5,
    3: 7,
    4: 9,
    5: 12,
}

# nivel_actual -> (success_rate_minima, max_avg_walls_o_None)
# Mantenido para compatibilidad con get_stats()
_THRESHOLDS: dict[int, tuple] = {
    0: (0.10, None),  # umbral muy bajo; completar 1 nivel basta
    1: (0.70, 3.0),
    2: (0.80, 1.0),
    3: (0.80, 1.0),
    4: (0.85, 1.0),
    5: (0.90, 1.0),
}


class Curriculum:
    """
    Gestiona el sistema de niveles (0-6).
    0.4.3: sube de nivel por level_completed, no por reached_goal.
    Anti-estancamiento: si pasan STAGNATION_THRESHOLD episodios sin completar,
    activa una senial para que el entorno aumente epsilon temporalmente.
    """

    def __init__(self):
        self.current_level = 0
        self.maze_needs_update = False
        self._successes = deque(maxlen=EVAL_WINDOW)
        self._wall_counts = deque(maxlen=EVAL_WINDOW)
        # 0.4.3
        self._level_completions = 0  # completions en el nivel actual
        self.episodes_without_progress = 0
        self._stagnation_active = False

    def record_episode(
        self, reached_goal: bool, wall_hits: int, level_completed: bool = False
    ):
        """
        0.4.3: level_completed es el disparador principal del curriculum.
        reached_goal mantenido para compatibilidad con tests existentes.
        """
        progress = level_completed or reached_goal
        self._successes.append(1 if progress else 0)
        self._wall_counts.append(wall_hits)

        if level_completed:
            self._level_completions += 1
            self.episodes_without_progress = 0
            self._stagnation_active = False
        else:
            self.episodes_without_progress += 1
            if self.episodes_without_progress >= STAGNATION_THRESHOLD:
                self._stagnation_active = True

    def check_level_up(self) -> int | None:
        """
        0.4.3: sube de nivel cuando se alcanzan las completions requeridas.
        Devuelve el nuevo nivel si hay subida, o None.
        """
        if self.current_level >= MAX_LEVEL:
            return None
        required = _LEVEL_COMPLETIONS.get(self.current_level, 999)
        if self._level_completions >= required:
            self.current_level += 1
            self._level_completions = 0
            self.episodes_without_progress = 0
            self._stagnation_active = False
            self.maze_needs_update = True
            return self.current_level
        return None

    def consume_maze_update(self) -> bool:
        """Devuelve True y resetea la bandera si hay cambio de laberinto pendiente."""
        if self.maze_needs_update:
            self.maze_needs_update = False
            return True
        return False

    @property
    def stagnation_active(self) -> bool:
        """True si BabyIA lleva demasiados episodios sin completar nivel."""
        return self._stagnation_active

    def get_stats(self) -> dict:
        n = len(self._successes)
        return {
            "success_rate": round(sum(self._successes) / n, 3) if n else 0.0,
            "avg_walls": round(sum(self._wall_counts) / n, 1) if n else 0.0,
            "level_completions": self._level_completions,
            "episodes_without_progress": self.episodes_without_progress,
            "stagnation_active": self._stagnation_active,
            "curriculum": {
                "current_level": self.current_level,
                "required": _LEVEL_COMPLETIONS.get(self.current_level, 0),
                "completed_so_far": self._level_completions,
            },
        }
