"""
BabyIA World — Coordinador de la interfaz gráfica.
Gestiona la ventana y delega dibujo a módulos especializados.
No contiene lógica de aprendizaje.
"""

import pygame
from config import APP_VERSION
from interface.avatar_renderer import AvatarRenderer
from interface.camera import Camera
from interface.grid_renderer import (
    draw_camera_world,
    draw_full_world,
    draw_view_info,
)
from interface.layout import WINDOW_W, WINDOW_H, GRID_AREA, LOG_AREA, CELL_SIZE
from interface.panel_renderer import PanelRenderer
from interface.ui_components import BG, LOG_BG, TEXT_DIM, ACCENT, divider


class PygameView:
    def __init__(self, title: str = f"BabyIA World {APP_VERSION}"):
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
        self._cam = Camera()
        self.view_mode: str = "full"
        self.running = True

    # ── Bucle principal ───────────────────────────────────────────────────────

    def handle_events(self) -> bool:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_f:
                    self.view_mode = "full"
                elif event.key in (pygame.K_c, pygame.K_z, pygame.K_v):
                    self.view_mode = "camera"
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
        world_size = getattr(world, "size", 8)
        if self.view_mode == "full":
            cs = draw_full_world(
                self.screen, world, status, self.fonts, self.avatar, GRID_AREA
            )
        else:
            cs = CELL_SIZE
            draw_camera_world(
                self.screen,
                world,
                status,
                self.fonts,
                self.avatar,
                self._cam,
                GRID_AREA,
                CELL_SIZE,
            )
        draw_view_info(
            self.screen, self.fonts, GRID_AREA, self.view_mode, world_size, cs
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
        entries = self._dedup_log(self._format_log(status))
        for entry in entries[:4]:
            self.screen.blit(
                self.fonts["xs"].render(entry[:110], True, TEXT_DIM), (lx + 4, py)
            )
            py += 15

    def _dedup_log(self, lines: list[str]) -> list[str]:
        """Colapsa consecutivos idénticos en 'mensaje ×N'."""
        out: list[str] = []
        for line in lines:
            if out and out[-1].split(" ×")[0] == line:
                base, _, count = out[-1].partition(" ×")
                out[-1] = f"{base} ×{int(count or 1) + 1}"
            else:
                out.append(line)
        return out

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
        # 0.4.3: eventos de puertas de nivel
        if ev.get("level_completed"):
            lines.append(f"E{ep}: *** NIVEL COMPLETADO ***")
        if ev.get("hit_next_level_door"):
            req = ev.get("missing_requirement", "algo")
            lines.append(f"E{ep}: Puerta nivel bloqueada: {req}")
        if ev.get("entered_treasure_room"):
            lines.append(f"E{ep}: Entro sala del tesoro")
        if ev.get("entered_training_room"):
            lines.append(f"E{ep}: Entro sala de entrenamiento")
        return lines[-6:]
