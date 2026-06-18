"""
brain/visual_memory.py — Memoria visual por episodio para BabyIA 0.4.5.

Recuerda posiciones de objetos vistos durante el episodio actual.
"Recordar" = persistir coordenadas en sets/dicts en RAM por episodio.
No reemplaza CausalMemory: VisualMemory recuerda posicion; CausalMemory recuerda efecto.

0.4.6b: registra colisiones, hazards y frecuencia de visita para detectar estancamiento.
"""

from __future__ import annotations


class VisualMemory:
    """
    Rastrea objetos vistos durante un episodio.
    Se reinicia con reset_episode() al inicio de cada episodio.
    """

    def __init__(self):
        self.reset_episode()

    def reset_episode(self):
        self.seen_positions: set = set()
        self.seen_objects: list = []
        self.last_seen_key: list | None = None
        self.last_seen_progress_door: list | None = None
        self.last_seen_hazards: list = []
        self.known_safe_cells: set = set()
        self.known_danger_cells: set = set()
        self.times_key_seen: int = 0
        self.times_progress_door_seen: int = 0
        self.times_hazard_avoided: int = 0
        # 0.4.6b: seguimiento de estancamiento
        self._collision_counts: dict[tuple, int] = {}
        self._hazard_hit_counts: dict[tuple, int] = {}
        self._cell_visit_counts: dict[tuple, int] = {}
        self.last_progress_cell: tuple | None = None

    # ── Actualizacion perceptual ──────────────────────────────────────────────

    def update(self, perception_result: dict, baby_pos: tuple):
        """Actualiza la memoria con los objetos detectados en este paso."""
        bx, by = baby_pos
        self.seen_positions.add((bx, by))

        for obj in perception_result.get("visible_objects", []):
            pos = obj.get("position")
            category = obj.get("category", "")

            if pos:
                pos_t = tuple(pos)
                self.seen_positions.add(pos_t)

                if category == "danger":
                    self.known_danger_cells.add(pos_t)
                elif category in ("reward", "goal"):
                    self.known_safe_cells.add(pos_t)

        nk = perception_result.get("nearest_key")
        if nk:
            self.last_seen_key = nk["position"]
            self.times_key_seen += 1

        nd = perception_result.get("nearest_progress_door")
        if nd:
            self.last_seen_progress_door = nd["position"]
            self.times_progress_door_seen += 1

        nh = perception_result.get("nearest_hazard")
        if nh:
            hpos = nh["position"]
            if hpos not in self.last_seen_hazards:
                self.last_seen_hazards.append(hpos)

        # Celda actual es segura si BabyIA esta viva aqui
        self.known_safe_cells.add((bx, by))

    # ── Registro de eventos de estancamiento ─────────────────────────────────

    def register_collision(self, baby_pos: tuple) -> bool:
        """
        Registra un choque desde baby_pos.
        Devuelve True si ya habia chocado antes desde esta misma posicion (repeticion).
        """
        count = self._collision_counts.get(baby_pos, 0)
        self._collision_counts[baby_pos] = count + 1
        return count > 0

    def register_hazard(self, hazard_pos: tuple) -> bool:
        """
        Registra un impacto en hazard_pos.
        Devuelve True si ya habia entrado antes en este hazard (repeticion).
        """
        count = self._hazard_hit_counts.get(hazard_pos, 0)
        self._hazard_hit_counts[hazard_pos] = count + 1
        return count > 0

    def register_visit(self, baby_pos: tuple):
        """Registra una visita a baby_pos para tracking de frecuencia."""
        self._cell_visit_counts[baby_pos] = self._cell_visit_counts.get(baby_pos, 0) + 1

    def register_progress(self, baby_pos: tuple):
        """Registra la ultima celda donde BabyIA hizo progreso real."""
        self.last_progress_cell = baby_pos

    # ── Propiedades de estancamiento ──────────────────────────────────────────

    @property
    def repeated_collision_count(self) -> int:
        """Numero total de choques repetidos desde la misma posicion."""
        return sum(max(0, c - 1) for c in self._collision_counts.values())

    @property
    def repeated_hazard_count(self) -> int:
        """Numero total de entradas repetidas al mismo hazard."""
        return sum(max(0, c - 1) for c in self._hazard_hit_counts.values())

    @property
    def stuck_zone_hint(self) -> tuple | None:
        """Posicion mas visitada si supera umbral de 5 visitas, indicando zona de oscilacion."""
        if not self._cell_visit_counts:
            return None
        most_visited = max(self._cell_visit_counts, key=self._cell_visit_counts.get)
        if self._cell_visit_counts[most_visited] >= 5:
            return most_visited
        return None

    # ── Consultas ─────────────────────────────────────────────────────────────

    def has_seen_key(self) -> bool:
        return self.last_seen_key is not None

    def has_seen_progress_door(self) -> bool:
        return self.last_seen_progress_door is not None

    def is_known_safe(self, pos: tuple) -> bool:
        return pos in self.known_safe_cells

    def is_known_danger(self, pos: tuple) -> bool:
        return pos in self.known_danger_cells

    def exploration_ratio(self, grid_size: int) -> float:
        """Fraccion de celdas vistas sobre el total del grid."""
        total = grid_size * grid_size
        return min(1.0, len(self.seen_positions) / max(1, total))

    def to_dict(self) -> dict:
        return {
            "seen_positions_count": len(self.seen_positions),
            "seen_objects_count": len(self.seen_objects),
            "last_seen_key": self.last_seen_key,
            "last_seen_progress_door": self.last_seen_progress_door,
            "last_seen_hazards_count": len(self.last_seen_hazards),
            "known_safe_count": len(self.known_safe_cells),
            "known_danger_count": len(self.known_danger_cells),
            "times_key_seen": self.times_key_seen,
            "times_progress_door_seen": self.times_progress_door_seen,
            # 0.4.6b
            "repeated_collision_count": self.repeated_collision_count,
            "repeated_hazard_count": self.repeated_hazard_count,
            "stuck_zone_hint": (
                list(self.stuck_zone_hint) if self.stuck_zone_hint else None
            ),
            "last_progress_cell": (
                list(self.last_progress_cell) if self.last_progress_cell else None
            ),
        }
