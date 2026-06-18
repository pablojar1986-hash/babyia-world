"""Tests de interface/layout.py — geometría de la interfaz."""

from interface.layout import (
    WINDOW_W,
    WINDOW_H,
    GRID_W,
    GRID_AREA,
    PANEL_AREA,
    LOG_AREA,
    TAB_AREA,
    PANEL_CONTENT,
    CELL_SIZE,
    MARGIN,
    PANEL_W,
    TABS,
    TAB_COUNT,
)


def test_window_width_positive():
    assert WINDOW_W > 0


def test_window_height_positive():
    assert WINDOW_H > 0


def test_grid_area_has_four_components():
    assert len(GRID_AREA) == 4


def test_panel_area_has_four_components():
    assert len(PANEL_AREA) == 4


def test_log_area_has_four_components():
    assert len(LOG_AREA) == 4


def test_grid_and_panel_same_height():
    assert GRID_AREA[3] == PANEL_AREA[3]


def test_grid_and_panel_do_not_overlap():
    grid_right = GRID_AREA[0] + GRID_AREA[2]
    panel_left = PANEL_AREA[0]
    assert panel_left >= grid_right


def test_panel_fits_in_window():
    panel_right = PANEL_AREA[0] + PANEL_AREA[2]
    assert panel_right <= WINDOW_W + MARGIN


def test_grid_fits_in_window():
    grid_bottom = GRID_AREA[1] + GRID_AREA[3]
    assert grid_bottom <= WINDOW_H


def test_log_area_below_grid():
    grid_bottom = GRID_AREA[1] + GRID_AREA[3]
    log_top = LOG_AREA[1]
    assert log_top >= grid_bottom


def test_log_area_within_window():
    log_bottom = LOG_AREA[1] + LOG_AREA[3]
    assert log_bottom <= WINDOW_H + MARGIN


def test_tab_area_within_panel():
    assert TAB_AREA[0] == PANEL_AREA[0]
    assert TAB_AREA[2] == PANEL_W


def test_panel_content_below_tabs():
    tab_bottom = TAB_AREA[1] + TAB_AREA[3]
    content_top = PANEL_CONTENT[1]
    assert content_top >= tab_bottom


def test_tabs_list_length():
    assert len(TABS) == TAB_COUNT


def test_tabs_contains_required_names():
    names = " ".join(TABS).lower()
    for required in ["estado", "mundo", "cuerpo", "cerebro", "memoria"]:
        assert required in names


def test_cell_size_positive():
    assert CELL_SIZE > 0


def test_grid_w_equals_cells_times_cell_size():
    from interface.layout import GRID_CELLS

    assert GRID_W == GRID_CELLS * CELL_SIZE


def test_window_large_enough_for_grid_and_panel():
    assert WINDOW_W >= GRID_W + PANEL_W
