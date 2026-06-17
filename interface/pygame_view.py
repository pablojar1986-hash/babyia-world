"""
BabyIA World 0.4.2 — Coordinador de la interfaz gráfica.
Gestiona la ventana y delega dibujo a módulos especializados.
No contiene lógica de aprendizaje.
"""

import pygame
from interface.avatar_renderer import AvatarRenderer
from interface.layout import WINDOW_W, WINDOW_H, GRID_AREA, LOG_AREA, CELL_SIZE
from interface.panel_renderer import PanelRenderer
from interface.ui_components import BG, LOG_BG, TEXT_DIM, ACCENT, divider
from world.objects import Cell, GRID_SIZE

# ── Colores específicos del grid ───────────────────────────────────────────────
_EMPTY = (42, 44, 56)
_VISIT = (55, 80, 130)
_WALL = (90, 90, 100)
_GOAL = (50, 200, 90)
_KEY = (255, 220, 80)
_DOOR_C = (160, 80, 40)
_DOOR_O = (100, 160, 80)
_FOOD = (80, 200, 120)
_DANGER = (200, 60, 60)
_UNKNWN = (140, 80, 200)
_POWERUP = (60, 200, 240)    # 0.4.2: cian
_HAZARD = (240, 110, 30)     # 0.4.2: naranja
_SPDOOR = (180, 90, 200)     # 0.4.2: violeta

PORTAL_COLORS = {
    (7, 2): (50, 130, 220),
    (7, 4): (210, 50, 50),
    (7, 6): (50, 200, 80),
    (6, 7): (255, 200, 0),
    (0, 0): (200, 200, 255),
}

CELL_COLORS = {
    int(Cell.WALL): _WALL,
    int(Cell.GOAL): _GOAL,
    int(Cell.KEY): _KEY,
    int(Cell.DOOR_CLOSED): _DOOR_C,
    int(Cell.DOOR_OPEN): _DOOR_O,
    int(Cell.FOOD): _FOOD,
    int(Cell.DANGER): _DANGER,
    int(Cell.UNKNOWN_OBJECT): _UNKNWN,
    int(Cell.POWERUP): _POWERUP,      # 0.4.2
    int(Cell.HAZARD): _HAZARD,        # 0.4.2
    int(Cell.SPECIAL_DOOR): _SPDOOR,  # 0.4.2
}

CELL_LABELS = {
    Cell.GOAL: ("META", (10, 40, 20)),
    Cell.KEY: ("K", (80, 60, 10)),
    Cell.DOOR_CLOSED: ("D", (60, 30, 10)),
    Cell.DOOR_OPEN: ("O", (30, 60, 20)),
    Cell.FOOD: ("F", (20, 60, 30)),
    Cell.DANGER: ("X", (80, 20, 20)),
    Cell.UNKNOWN_OBJECT: ("?", (50, 20, 80)),
    Cell.POWERUP: ("+", (10, 70, 90)),     # 0.4.2
    Cell.HAZARD: ("!", (90, 30, 10)),      # 0.4.2
    Cell.SPECIAL_DOOR: ("S", (60, 20, 70)),  # 0.4.2
}

_LEGEND = [
    ("P", "Portal"),
    ("F", "Comida"),
    ("X", "Peligro"),
    ("K", "Llave"),
    ("D", "Puerta"),
    ("?", "Desc."),
]


class PygameView:
    def __init__(self, title: str = "BabyIA World 0.4.2"):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_W, WINDOW_H))
        pygame.display.set_caption(title)
        self.clock = pygame.time.Clock()
        self.fonts = {
            "big": pygame.font.SysFont("consolas", 17, bold=True),
            "med": pygame.font.SysFont("consolas", 14),
            "sm": pygame.font.SysFont("consolas", 12),
            "xs": pygame.font.SysFont("consolas", 11),
        }
        self.avatar = AvatarRenderer()
        self.panels = PanelRenderer()
        self.panels.set_fonts(self.fonts)
        self.running = True

    # ── Bucle principal ───────────────────────────────────────────────────────

    def handle_events(self) -> bool:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                else:
                    self.panels.handle_key(event.key, pygame.key.get_mods())
        return self.running

    def render(self, world, status: dict):
        self.screen.fill(BG)
        self._draw_world_border(status)
        self._draw_grid(world, status)
        self.panels.render(self.screen, status)
        self._draw_log(status)
        pygame.display.flip()
        self.clock.tick(60)

    def quit(self):
        pygame.quit()

    # ── Grid ──────────────────────────────────────────────────────────────────

    def _draw_grid(self, world, status: dict):
        grid = world.get_grid()
        visited = world.visited
        bx, by = world.baby_pos
        ox, oy = GRID_AREA[0], GRID_AREA[1]
        gs = CELL_SIZE

        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                cx = ox + col * gs
                cy_ = oy + row * gs
                rect = pygame.Rect(cx, cy_, gs - 2, gs - 2)
                val = grid[row][col]

                portal_c = PORTAL_COLORS.get((col, row))
                base_color = CELL_COLORS.get(
                    val, _VISIT if (col, row) in visited else _EMPTY
                )
                pygame.draw.rect(self.screen, base_color, rect, border_radius=4)

                if portal_c:
                    pygame.draw.rect(
                        self.screen, portal_c, rect, width=3, border_radius=4
                    )
                    p = self.fonts["xs"].render("P", True, portal_c)
                    self.screen.blit(p, (cx + gs // 2 - 4, cy_ + 3))

                cell_e = Cell(val) if val in [c.value for c in Cell] else None
                if cell_e and cell_e in CELL_LABELS:
                    lbl_txt, lbl_clr = CELL_LABELS[cell_e]
                    lbl = self.fonts["xs"].render(lbl_txt, True, lbl_clr)
                    self.screen.blit(lbl, (cx + gs // 2 - 6, cy_ + gs // 2 - 6))

        # Avatar
        av_cx = ox + bx * gs + gs // 2
        av_cy = oy + by * gs + gs // 2
        self.avatar.draw(
            self.screen,
            av_cx,
            av_cy,
            gs,
            status.get("level", 0),
            status.get("emotions", {}),
            status.get("body_state", {}),
        )

    def _draw_world_border(self, status: dict):
        """Marco de color según el mundo actual."""
        wi = status.get("world_info", {})
        wid = wi.get("world_id", "home")
        colors = {
            "home": (50, 60, 80),
            "food_world": (40, 100, 60),
            "danger_world": (120, 40, 40),
            "curiosity_world": (60, 40, 120),
            "challenge_world": (120, 100, 20),
        }
        clr = colors.get(wid, (50, 60, 80))
        gx, gy, gw, gh = GRID_AREA
        pygame.draw.rect(
            self.screen, clr, (gx - 3, gy - 3, gw + 6, gh + 6), width=3, border_radius=4
        )

    # ── Panel inferior de bitácora ─────────────────────────────────────────────

    def _draw_log(self, status: dict):
        lx, ly, lw, lh = LOG_AREA
        pygame.draw.rect(
            self.screen, LOG_BG, (lx - 4, ly, lw + 8, lh + 8), border_radius=4
        )
        py = ly + 6
        self.screen.blit(
            self.fonts["sm"].render("Bitacora", True, ACCENT), (lx + 4, py)
        )
        py += 18
        divider(self.screen, lx + 4, py, lw - 8)
        py += 8
        entries = self._format_log(status)
        for entry in entries[:4]:
            self.screen.blit(
                self.fonts["xs"].render(entry[:110], True, TEXT_DIM), (lx + 4, py)
            )
            py += 15

    def _format_log(self, status: dict) -> list[str]:
        lines = list(status.get("last_log", []))
        ep = status.get("episode", 0)
        ev = status.get("ep_events", {})
        if ev.get("picked_key"):
            lines.append(f"E{ep}: Recogida llave")
        if ev.get("ate_food"):
            lines.append(f"E{ep}: Comio alimento")
        if ev.get("in_danger"):
            lines.append(f"E{ep}: En zona de peligro")
        if ev.get("returned_home"):
            lines.append(f"E{ep}: Regreso a casa")
        # 0.4.2: eventos de powerup/hazard/puerta especial
        pu = ev.get("last_powerup")
        if pu:
            lines.append(f"E{ep}: Recogido {pu}")
        hz = ev.get("last_hazard")
        if hz:
            blk = ev.get("last_hazard_blocked", False)
            lines.append(f"E{ep}: {'Bloqueado' if blk else 'Afectado'} {hz}")
        door_fail = ev.get("last_door_fail")
        if door_fail:
            lines.append(f"E{ep}: Puerta: {door_fail}")
        return lines[-6:]
