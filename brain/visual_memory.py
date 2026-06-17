"""
brain/visual_memory.py — Memoria visual por episodio para BabyIA 0.4.5.

Recuerda posiciones de objetos vistos durante el episodio actual.
"Recordar" = persistir coordenadas en sets/dicts en RAM por episodio.
No reemplaza CausalMemory: VisualMemory recuerda posicion; CausalMemory recuerda efecto.
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
        }
