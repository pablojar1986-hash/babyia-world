from enum import IntEnum


class Cell(IntEnum):
    EMPTY = 0
    WALL = 1
    GOAL = 2
    KEY = 3
    DOOR_CLOSED = 4
    DOOR_OPEN = 5
    FOOD = 6
    DANGER = 7
    UNKNOWN_OBJECT = 8
    POWERUP = 9  # 0.4.2: powerup recogible
    HAZARD = 10  # 0.4.2: peligro especial con efecto corporal
    SPECIAL_DOOR = 11  # 0.4.2: puerta con requisito corporal
    LEVEL_DOOR = 12  # 0.4.3: puerta de progreso de nivel (requiere llave)
    OPTIONAL_DOOR = 13  # 0.4.3: puerta opcional (tesoro, entrenamiento, peligro)


class Action(IntEnum):
    UP = 0
    DOWN = 1
    LEFT = 2
    RIGHT = 3
    WAIT = 4


ACTION_NAMES = {
    0: "arriba",
    1: "abajo",
    2: "izquierda",
    3: "derecha",
    4: "esperar",
}

GRID_SIZE = 8
# 0.4.6: ampliado a 40 (10 base + 8 extra + 8 mundo + 8 cuerpo + 6 percepcion)
STATE_SIZE = 40
ACTION_SIZE = 5
