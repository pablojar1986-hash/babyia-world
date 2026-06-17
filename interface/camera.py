"""
interface/camera.py — Sistema de camara/viewport para BabyIA 0.4.5.

Permite mostrar una ventana del mundo cuando el grid es mayor que la pantalla.
No contiene logica de entrenamiento.
"""

from __future__ import annotations

from world.world_config import VIEWPORT_SIZE


class Camera:
    """
    Convierte coordenadas mundo <-> pantalla y determina celdas visibles.

    Si grid_size <= viewport_size, muestra todo el mapa.
    Si grid_size > viewport_size, sigue a BabyIA centrando el viewport.
    """

    def __init__(self, viewport_cells: int = VIEWPORT_SIZE):
        self.viewport = viewport_cells
        self._offset_x: int = 0
        self._offset_y: int = 0
        self._grid_size: int = viewport_cells

    def update(self, baby_pos: tuple, grid_size: int):
        """Actualiza la posicion de la camara siguiendo a BabyIA."""
        self._grid_size = grid_size
        if grid_size <= self.viewport:
            self._offset_x = 0
            self._offset_y = 0
            return

        bx, by = baby_pos
        half = self.viewport // 2

        ox = bx - half
        oy = by - half

        max_offset = grid_size - self.viewport
        self._offset_x = max(0, min(ox, max_offset))
        self._offset_y = max(0, min(oy, max_offset))

    def world_to_screen(
        self, wx: int, wy: int, cell_size: int, origin_x: int, origin_y: int
    ) -> tuple[int, int]:
        """Convierte posicion del mundo a coordenadas de pantalla."""
        sx = origin_x + (wx - self._offset_x) * cell_size
        sy = origin_y + (wy - self._offset_y) * cell_size
        return sx, sy

    def is_visible(self, wx: int, wy: int) -> bool:
        """True si la celda del mundo esta dentro del viewport actual."""
        return (
            self._offset_x <= wx < self._offset_x + self.viewport
            and self._offset_y <= wy < self._offset_y + self.viewport
        )

    def get_visible_bounds(self) -> tuple[int, int, int, int]:
        """Devuelve (min_x, min_y, max_x, max_y) del area visible."""
        return (
            self._offset_x,
            self._offset_y,
            min(self._offset_x + self.viewport, self._grid_size),
            min(self._offset_y + self.viewport, self._grid_size),
        )

    def get_visible_cells_count(self) -> int:
        """Numero de celdas mostradas actualmente."""
        return self.viewport * self.viewport

    @property
    def offset(self) -> tuple[int, int]:
        return (self._offset_x, self._offset_y)
