# ── Recompensas base de movimiento (0.1.x — sin cambios) ─────────────────────
REWARD_GOAL     =  10.0
REWARD_WALL     =  -1.0
REWARD_STEP     =  -0.05
REWARD_NEW_CELL =   1.0
REWARD_REPEAT   =  -0.2
REPEAT_WINDOW   =  5

# ── Recompensas de objetos (0.2) ──────────────────────────────────────────────
REWARD_KEY_FIRST    =  3.0   # primera vez que recoge una llave
REWARD_KEY_EXTRA    =  0.5   # llaves adicionales en el episodio
REWARD_OPEN_DOOR    =  5.0   # abrir puerta con llave
REWARD_DOOR_FAIL    = -0.5   # intentar abrir puerta sin llave
REWARD_FOOD_LOW     =  2.0   # comer cuando energia < 50%
REWARD_FOOD_OK      =  0.5   # comer con energia suficiente
REWARD_DANGER       = -2.0   # entrar en zona peligrosa
REWARD_UNKNOWN      =  1.0   # descubrir objeto desconocido por primera vez
REWARD_CONCEPT      =  2.0   # confirmar relacion causa-efecto


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
    return 0.0


def _is_repeating(action_history) -> bool:
    if len(action_history) < REPEAT_WINDOW:
        return False
    recent = action_history[-REPEAT_WINDOW:]
    return len(set(recent)) == 1 and recent[0] != 4
