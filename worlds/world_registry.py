"""
Registro de todos los mundos y portales de BabyIA World 0.3.
Fuente de verdad para la topologia de mundos.
"""
from worlds.portal import Portal
from worlds.world_definition import WorldDefinition

# ── IDs de mundos ─────────────────────────────────────────────────────────────
HOME_WORLD_ID      = "home"
FOOD_WORLD_ID      = "food_world"
DANGER_WORLD_ID    = "danger_world"
CURIOSITY_WORLD_ID = "curiosity_world"
CHALLENGE_WORLD_ID = "challenge_world"

WORLD_IDS = [
    HOME_WORLD_ID, FOOD_WORLD_ID, DANGER_WORLD_ID,
    CURIOSITY_WORLD_ID, CHALLENGE_WORLD_ID,
]

# ── Definiciones de mundos ────────────────────────────────────────────────────
ALL_WORLDS: dict[str, WorldDefinition] = {
    HOME_WORLD_ID: WorldDefinition(
        world_id=HOME_WORLD_ID, name="Casa de BabyIA",
        reward_profile="home", risk_level=0.0, complexity=1,
        home_return_required=False, min_level=0,
        description="Zona segura. Punto de partida y regreso.",
    ),
    FOOD_WORLD_ID: WorldDefinition(
        world_id=FOOD_WORLD_ID, name="Mundo de Comida",
        reward_profile="food", risk_level=0.2, complexity=1,
        home_return_required=True, min_level=0,
        description="Rico en comida. Baja dificultad.",
    ),
    DANGER_WORLD_ID: WorldDefinition(
        world_id=DANGER_WORLD_ID, name="Mundo de Peligro",
        reward_profile="danger", risk_level=0.8, complexity=3,
        home_return_required=True, min_level=1,
        description="Zonas peligrosas. Alta recompensa al sobrevivir.",
    ),
    CURIOSITY_WORLD_ID: WorldDefinition(
        world_id=CURIOSITY_WORLD_ID, name="Mundo de Curiosidad",
        reward_profile="curiosity", risk_level=0.4, complexity=2,
        home_return_required=True, min_level=2,
        description="Objetos desconocidos. Recompensa por descubrir.",
    ),
    CHALLENGE_WORLD_ID: WorldDefinition(
        world_id=CHALLENGE_WORLD_ID, name="Mundo Desafio",
        reward_profile="challenge", risk_level=0.6, complexity=4,
        home_return_required=True, min_level=3,
        description="Laberinto complejo. Mayor recompensa.",
    ),
}

# ── Portales de salida (en posiciones vacias del grid 8x8) ────────────────────
# Posiciones elegidas para no solapar con paredes ni objetos existentes.
HOME_PORTALS: dict[str, Portal] = {
    "blue_door": Portal(
        portal_id="blue_door", target_world=FOOD_WORLD_ID,
        label="Puerta Azul", required_level=0,
        position=(7, 2), color=(50, 130, 220),
    ),
    "red_door": Portal(
        portal_id="red_door", target_world=DANGER_WORLD_ID,
        label="Puerta Roja", required_level=1,
        position=(7, 4), color=(210, 50, 50),
    ),
    "green_door": Portal(
        portal_id="green_door", target_world=CURIOSITY_WORLD_ID,
        label="Puerta Verde", required_level=2,
        position=(7, 6), color=(50, 200, 80),
    ),
    "gold_door": Portal(
        portal_id="gold_door", target_world=CHALLENGE_WORLD_ID,
        label="Puerta Dorada", required_level=3,
        position=(6, 7), color=(255, 200, 0),
    ),
}

# Puerta de regreso a casa (START_POS del grid)
RETURN_HOME_PORTAL = Portal(
    portal_id="home_door", target_world=HOME_WORLD_ID,
    label="Volver a Casa", required_level=0,
    position=(0, 0), color=(200, 200, 255),
)
