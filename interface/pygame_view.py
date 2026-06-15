import pygame
from interface.avatar_renderer import AvatarRenderer
from world.objects import Cell, ACTION_NAMES, GRID_SIZE

# ── Paleta de colores ─────────────────────────────────────────────────────────
BG           = (22,  24,  33)
CELL_EMPTY   = (42,  44,  56)
CELL_VISIT   = (55,  80, 130)
CELL_WALL    = (90,  90, 100)
CELL_GOAL    = (50, 200,  90)
CELL_BABY    = (255, 200,  50)
CELL_KEY     = (255, 220,  80)
CELL_DOOR_C  = (160,  80,  40)
CELL_DOOR_O  = (100, 160,  80)
CELL_FOOD    = (80,  200, 120)
CELL_DANGER  = (200,  60,  60)
CELL_UNKNOWN = (140,  80, 200)
GRID_LINE    = (15,  17,  25)
PANEL_BG     = (16,  18,  26)
TEXT         = (220, 220, 230)
TEXT_DIM     = (110, 115, 135)
ACCENT       = ( 90, 170, 255)
BAR_BG       = ( 35,  38,  52)
BAR_OK       = ( 90, 170, 255)
BAR_WARN     = (255, 165,  50)
BAR_DANGER   = (220,  70,  70)
COLOR_POS    = (100, 220, 100)
COLOR_NEG    = (220,  90,  90)

# Colores de portales (0.3)
PORTAL_COLORS = {
    (7, 2): ( 50, 130, 220),   # blue_door  → food_world
    (7, 4): (210,  50,  50),   # red_door   → danger_world
    (7, 6): ( 50, 200,  80),   # green_door → curiosity_world
    (6, 7): (255, 200,   0),   # gold_door  → challenge_world
    (0, 0): (200, 200, 255),   # home_door  → return home
}

# ── Etiquetas de celda ────────────────────────────────────────────────────────
CELL_LABELS = {
    Cell.GOAL         : ("META", (10,  40, 20)),
    Cell.KEY          : ("K",    (80,  60, 10)),
    Cell.DOOR_CLOSED  : ("D",    (60,  30, 10)),
    Cell.DOOR_OPEN    : ("O",    (30,  60, 20)),
    Cell.FOOD         : ("F",    (20,  60, 30)),
    Cell.DANGER       : ("X",    (80,  20, 20)),
    Cell.UNKNOWN_OBJECT: ("?",   (50,  20, 80)),
}

CELL_COLORS = {
    int(Cell.WALL)         : CELL_WALL,
    int(Cell.GOAL)         : CELL_GOAL,
    int(Cell.KEY)          : CELL_KEY,
    int(Cell.DOOR_CLOSED)  : CELL_DOOR_C,
    int(Cell.DOOR_OPEN)    : CELL_DOOR_O,
    int(Cell.FOOD)         : CELL_FOOD,
    int(Cell.DANGER)       : CELL_DANGER,
    int(Cell.UNKNOWN_OBJECT): CELL_UNKNOWN,
}

# ── Geometria ─────────────────────────────────────────────────────────────────
CELL_SIZE = 58
MARGIN    = 14
PANEL_W   = 300
GRID_W    = GRID_SIZE * CELL_SIZE
WINDOW_W  = MARGIN + GRID_W + MARGIN + PANEL_W + MARGIN
WINDOW_H  = MARGIN + GRID_W + MARGIN


class PygameView:
    def __init__(self, title="BabyIA World 0.3"):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_W, WINDOW_H))
        pygame.display.set_caption(title)
        self.clock   = pygame.time.Clock()
        self.f_big   = pygame.font.SysFont("consolas", 17, bold=True)
        self.f_med   = pygame.font.SysFont("consolas", 14)
        self.f_sm    = pygame.font.SysFont("consolas", 12)
        self.f_xs    = pygame.font.SysFont("consolas", 11)
        self.avatar  = AvatarRenderer()
        self.running = True

    # ── Bucle principal ───────────────────────────────────────────────────────

    def handle_events(self) -> bool:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.running = False
        return self.running

    def render(self, world, status):
        self.screen.fill(BG)
        self._draw_grid(world, status)
        self._draw_panel(status)
        pygame.display.flip()
        self.clock.tick(60)

    def quit(self):
        pygame.quit()

    # ── Grid ──────────────────────────────────────────────────────────────────

    def _draw_grid(self, world, status=None):
        grid    = world.get_grid()
        visited = world.visited
        bx, by  = world.baby_pos
        ox, oy  = MARGIN, MARGIN

        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                x    = ox + col * CELL_SIZE
                y    = oy + row * CELL_SIZE
                rect = pygame.Rect(x, y, CELL_SIZE - 2, CELL_SIZE - 2)
                val  = grid[row][col]

                # Portales 0.3 — dibujados como marco de color sobre celda vacia
                portal_color = PORTAL_COLORS.get((col, row))
                base_color   = CELL_COLORS.get(val,
                               CELL_VISIT if (col, row) in visited else CELL_EMPTY)
                pygame.draw.rect(self.screen, base_color, rect, border_radius=5)
                if portal_color:
                    pygame.draw.rect(self.screen, portal_color, rect,
                                     width=3, border_radius=5)
                    p_lbl = self.f_xs.render("P", True, portal_color)
                    self.screen.blit(p_lbl, (x + CELL_SIZE // 2 - 4, y + 4))

                # Etiqueta de celda
                cell_enum = Cell(val) if val in [c.value for c in Cell] else None
                if cell_enum and cell_enum in CELL_LABELS:
                    lbl_text, lbl_color = CELL_LABELS[cell_enum]
                    lbl = self.f_xs.render(lbl_text, True, lbl_color)
                    self.screen.blit(lbl, (x + CELL_SIZE // 2 - 6, y + CELL_SIZE // 2 - 6))

        # BabyIA — avatar con AvatarRenderer (0.3)
        cx = ox + bx * CELL_SIZE + CELL_SIZE // 2 - 1
        cy = oy + by * CELL_SIZE + CELL_SIZE // 2 - 1
        emotions = status.get("emotions", {}) if status else {}
        level    = status.get("level", 0) if status else 0
        self.avatar.draw(self.screen, cx, cy, CELL_SIZE, level, emotions)

    # ── Panel lateral ─────────────────────────────────────────────────────────

    def _draw_panel(self, status):
        px = MARGIN + GRID_W + MARGIN
        py = MARGIN
        panel_h = WINDOW_H - 2 * MARGIN
        pygame.draw.rect(self.screen, PANEL_BG,
                         (px - 6, py - 6, PANEL_W + 6, panel_h + 12), border_radius=8)

        # Titulo + modo
        self._txt("BabyIA World 0.3", px, py, self.f_big, ACCENT)
        py += 22
        mode_str   = status.get("mode", "train").upper()
        mode_color = {"TRAIN": (100,200,100), "WATCH": (100,170,255),
                      "EVALUATE": (255,180,50)}.get(mode_str, ACCENT)
        self._txt(f"● {mode_str}", px, py, self.f_xs, mode_color)
        py += 14
        self._divider(px, py, PANEL_W - 8); py += 10

        # Episodio / nivel
        self._txt(f"Episodio : {status['episode']}", px, py, self.f_med, TEXT); py += 19
        self._txt(f"Nivel    : {status['level']}",   px, py, self.f_med, TEXT); py += 19
        self._txt(f"e explor : {status['epsilon']:.3f}", px, py, self.f_sm, TEXT_DIM); py += 16
        ep_r = status["episode_reward"]
        self._txt(f"Recomp.  : {ep_r:+.2f}", px, py, self.f_sm,
                  COLOR_POS if ep_r >= 0 else COLOR_NEG); py += 16
        self._txt(f"Exito 20ep: {status['success_rate']*100:.0f}%", px, py, self.f_sm, TEXT); py += 16
        avg_r = status.get("avg_reward")
        avg_s = status.get("avg_steps")
        if avg_r is not None:
            self._txt(f"Prom recomp: {avg_r:+.2f}", px, py, self.f_xs, TEXT_DIM); py += 14
        if avg_s is not None:
            self._txt(f"Prom pasos : {avg_s:.0f}", px, py, self.f_xs, TEXT_DIM); py += 14
        py += 4
        self._divider(px, py, PANEL_W - 8); py += 10

        # Laberinto (0.2.1)
        self._txt("Laberinto", px, py, self.f_med, ACCENT); py += 20
        maze = status.get("maze_info", {})
        diff = maze.get("difficulty", "Basico")
        seed = maze.get("seed", 0)
        solv = maze.get("solvable", True)
        solv_color = (100, 220, 100) if solv else (220, 90, 90)
        self._txt(f"Nivel:    {diff}", px, py, self.f_sm, TEXT); py += 16
        self._txt(f"Semilla:  {seed}", px, py, self.f_xs, TEXT_DIM); py += 14
        self._txt(f"Solucion: {'OK' if solv else 'NO'}", px, py, self.f_xs, solv_color)
        py += 14
        py += 4
        self._divider(px, py, PANEL_W - 8); py += 10

        # Mundo actual (0.3)
        self._txt("Mundo", px, py, self.f_med, ACCENT); py += 20
        wi = status.get("world_info", {})
        wname = wi.get("world_id", "home").replace("_", " ")
        home_c = (100, 220, 100) if wi.get("is_at_home", True) else (255, 180, 50)
        self._txt(f"Mundo: {wname[:18]}", px, py, self.f_sm, home_c); py += 16
        at_home = "SI" if wi.get("is_at_home", True) else "NO"
        self._txt(f"En casa: {at_home}", px, py, self.f_xs, home_c); py += 14
        portal = wi.get("last_portal") or "-"
        self._txt(f"Portal: {portal[:18]}", px, py, self.f_xs, TEXT_DIM); py += 14
        hd = status.get("home_drive", {})
        rhr = hd.get("return_home_rate", 0.0)
        self._txt(f"Retorno: {rhr*100:.0f}%", px, py, self.f_xs, TEXT_DIM); py += 14
        py += 4
        self._divider(px, py, PANEL_W - 8); py += 10

        # Inventario (0.2)
        self._txt("Inventario", px, py, self.f_med, ACCENT); py += 20
        inv = status.get("inventory", {})
        key_color = (255, 220, 80) if inv.get("has_key") else TEXT_DIM
        self._txt(f"Llave: {'SI' if inv.get('has_key') else 'NO'}", px, py, self.f_sm, key_color)
        py += 16
        energy = inv.get("energy", 1.0)
        self._bar(px, py, PANEL_W - 8, "Energia", energy, warn_at=0.3); py += 22
        self._txt(f"Comida: {inv.get('food_count', 0)}", px, py, self.f_xs, TEXT_DIM); py += 14
        py += 4
        self._divider(px, py, PANEL_W - 8); py += 10

        # Senales internas
        self._txt("Senales internas", px, py, self.f_med, ACCENT); py += 22
        em = status["emotions"]
        for label, key, warn in [
            ("Curiosidad",   "curiosity",   None),
            ("Confianza",    "confidence",  None),
            ("Frustracion",  "frustration", 0.6),
            ("Energia int.", "energy",      None),
        ]:
            self._bar(px, py, PANEL_W - 8, label, em[key], warn); py += 22
        py += 4
        self._divider(px, py, PANEL_W - 8); py += 10

        # Conceptos descubiertos (0.2)
        self._txt("Conceptos", px, py, self.f_med, ACCENT); py += 20
        top_c = status.get("concepts", [])
        if top_c:
            for c in top_c[:2]:
                rel = f"{c['relation']}:{c['value']}"[:28]
                conf = c["confidence"]
                self._txt(f"  {rel}", px, py, self.f_xs, (130, 210, 140)); py += 14
                self._txt(f"    conf={conf:.2f}", px, py, self.f_xs, TEXT_DIM); py += 14
        else:
            self._txt("  Ninguno aun", px, py, self.f_xs, TEXT_DIM); py += 14
        py += 4
        self._divider(px, py, PANEL_W - 8); py += 10

        # Bitacora
        self._txt("Bitacora", px, py, self.f_med, ACCENT); py += 20
        for entry in status["last_log"][-3:]:
            if len(entry) > 40:
                mid = entry[:40].rfind(" ")
                mid = mid if mid > 20 else 40
                self._txt(entry[:mid], px, py, self.f_xs, TEXT_DIM); py += 14
                self._txt(entry[mid:].strip()[:40], px + 6, py, self.f_xs, TEXT_DIM)
            else:
                self._txt(entry, px, py, self.f_xs, TEXT_DIM)
            py += 18

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _bar(self, x, y, width, label, value, warn_at=None):
        lbl = self.f_sm.render(f"{label}:", True, TEXT_DIM)
        self.screen.blit(lbl, (x, y))
        bar_x = x + 108
        bar_w = width - 150
        bar_h = 12
        pygame.draw.rect(self.screen, BAR_BG, (bar_x, y + 2, bar_w, bar_h), border_radius=4)
        fill = max(1, int(bar_w * value))
        if warn_at and value <= warn_at:
            color = BAR_DANGER if value <= warn_at * 0.5 else BAR_WARN
        else:
            color = BAR_OK
        pygame.draw.rect(self.screen, color, (bar_x, y + 2, fill, bar_h), border_radius=4)
        val_s = self.f_xs.render(f"{value:.2f}", True, TEXT)
        self.screen.blit(val_s, (bar_x + bar_w + 4, y + 1))

    def _divider(self, x, y, width):
        pygame.draw.line(self.screen, (40, 44, 60), (x, y), (x + width, y))

    def _txt(self, text, x, y, font, color):
        self.screen.blit(font.render(str(text), True, color), (x, y))
