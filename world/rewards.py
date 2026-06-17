# ── Recompensas base de movimiento ────────────────────────────────────────────
# 0.4.3: REWARD_NEW_CELL reducido de 1.0 a 0.05 para evitar reward hacking por exploracion.
# REWARD_STEP suavizado de -0.05 a -0.02 para no penalizar demasiado el aprendizaje temprano.
REWARD_GOAL = 10.0  # compatibilidad con tests existentes (no usado en nuevo curriculum)
REWARD_WALL = -1.0
REWARD_STEP = -0.02  # era -0.05
REWARD_NEW_CELL = 0.05  # era 1.0 — reducido drasticamente para que no domine
REWARD_REPEAT = -0.2
REPEAT_WINDOW = 5

# ── Recompensas de objetos (0.2) ──────────────────────────────────────────────
REWARD_KEY_FIRST = 8.0  # era 3.0 — mas importante ahora que la llave abre nivel
REWARD_KEY_EXTRA = 0.5
REWARD_OPEN_DOOR = 6.0  # era 5.0
REWARD_DOOR_FAIL = -0.5
REWARD_FOOD_LOW = 2.0
REWARD_FOOD_OK = 0.5
REWARD_DANGER = -2.0
REWARD_UNKNOWN = 1.0
REWARD_CONCEPT = 2.0

# ── Recompensas de progresion de nivel (0.4.3) ────────────────────────────────
REWARD_NEXT_LEVEL_DOOR = 80.0  # abrir la puerta de progreso con llave
REWARD_LEVEL_COMPLETED = 120.0  # bonus adicional al completar el nivel
REWARD_TREASURE_ROOM = 10.0  # entrar a sala de tesoro
REWARD_TRAINING_ROOM = 5.0  # entrar a sala de entrenamiento
REWARD_DANGER_ROOM_SURVIVED = 15.0  # sobrevivir sala peligrosa
REWARD_WRONG_DOOR = -1.0  # abrir puerta opcional cuando era la de progreso?
REWARD_NEXT_DOOR_WITHOUT_KEY = -5.0  # intentar abrir puerta de nivel sin llave


def calculate_reward(hit_wall, reached_goal, visited_new, action_history) -> float:
    """Recompensa de movimiento base. Compatible con 0.1.x."""
    reward = REWARD_STEP
    if hit_wall:
        reward += REWARD_WALL
    if reached_goal:
        reward += REWARD_GOAL
    if visited_new:
        reward += REWARD_NEW_CELL
    if _is_repeating(action_history):
        reward += REWARD_REPEAT
    return round(reward, 4)


def object_reward(event: str, context: dict | None = None) -> float:
    """
    Devuelve la recompensa correspondiente a un evento de objeto.
    event: nombre del evento (coincide con claves de interaction dicts).
    context: informacion adicional (ej. energy actual).
    """
    ctx = context or {}
    if event == "picked_key":
        return REWARD_KEY_FIRST if ctx.get("first_time") else REWARD_KEY_EXTRA
    if event == "opened_door":
        return REWARD_OPEN_DOOR
    if event == "hit_door_closed":
        return REWARD_DOOR_FAIL
    if event == "ate_food":
        return REWARD_FOOD_LOW if ctx.get("energy", 1.0) < 0.5 else REWARD_FOOD_OK
    if event == "in_danger":
        return REWARD_DANGER
    if event == "found_unknown":
        return REWARD_UNKNOWN
    if event == "concept_confirmed":
        return REWARD_CONCEPT
    # 0.4.3: eventos de puertas de nivel
    if event == "level_completed":
        return REWARD_LEVEL_COMPLETED
    if event == "next_level_door_opened":
        return REWARD_NEXT_LEVEL_DOOR
    if event == "treasure_room_entered":
        return REWARD_TREASURE_ROOM
    if event == "training_room_entered":
        return REWARD_TRAINING_ROOM
    if event == "next_door_without_key":
        return REWARD_NEXT_DOOR_WITHOUT_KEY
    return 0.0


def _is_repeating(action_history) -> bool:
    if len(action_history) < REPEAT_WINDOW:
        return False
    recent = action_history[-REPEAT_WINDOW:]
    return len(set(recent)) == 1 and recent[0] != 4
