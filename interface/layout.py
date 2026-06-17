"""
Geometría de la interfaz BabyIA World 0.4.1.
Sin dependencias de pygame — importable en tests.
"""

CELL_SIZE = 58
MARGIN = 12
GRID_CELLS = 8

GRID_W = GRID_CELLS * CELL_SIZE  # 464
GRID_H = GRID_CELLS * CELL_SIZE  # 464

TAB_H = 34  # altura de la barra de pestañas (dentro del panel)
PANEL_W = 360  # ancho del panel lateral
BOTTOM_H = 130  # altura del panel de bitácora inferior

WINDOW_W = MARGIN + GRID_W + MARGIN + PANEL_W + MARGIN  # 860
WINDOW_H = MARGIN + GRID_H + MARGIN + BOTTOM_H  # 618

# ── Áreas (x, y, w, h) ────────────────────────────────────────────────────────

GRID_AREA = (
    MARGIN,
    MARGIN,
    GRID_W,
    GRID_H,
)

PANEL_AREA = (
    MARGIN + GRID_W + MARGIN,
    MARGIN,
    PANEL_W,
    GRID_H,
)

# Barra de pestañas: primeros TAB_H píxeles del panel
TAB_AREA = (
    PANEL_AREA[0],
    PANEL_AREA[1],
    PANEL_W,
    TAB_H,
)

# Contenido del panel: debajo de las pestañas
_panel_content_y = PANEL_AREA[1] + TAB_H + 4
PANEL_CONTENT = (
    PANEL_AREA[0] + 8,
    _panel_content_y,
    PANEL_W - 16,
    PANEL_AREA[3] - TAB_H - 8,
)

# Panel inferior de bitácora
_log_y = MARGIN + GRID_H + MARGIN
LOG_AREA = (
    MARGIN,
    _log_y,
    WINDOW_W - 2 * MARGIN,
    WINDOW_H - _log_y - MARGIN,
)

TABS = ["Estado", "Mundo", "Cuerpo", "Cerebro", "Memoria", "Mision"]
TAB_COUNT = len(TABS)
