from enum import IntEnum


class Cell(IntEnum):
    EMPTY          = 0
    WALL           = 1
    GOAL           = 2
    KEY            = 3
    DOOR_CLOSED    = 4
    DOOR_OPEN      = 5
    FOOD           = 6
    DANGER         = 7
    UNKNOWN_OBJECT = 8
    POWERUP        = 9    # 0.4.2: powerup recogible
    HAZARD         = 10   # 0.4.2: peligro especial con efecto corporal
    SPECIAL_DOOR   = 11   # 0.4.2: puerta con requisito corporal


class Action(IntEnum):
    UP    = 0
    DOWN  = 1
    LEFT  = 2
    RIGHT = 3
    WAIT  = 4


ACTION_NAMES = {
    0: "arriba",
    1: "abajo",
    2: "izquierda",
    3: "derecha",
    4: "esperar",
}

GRID_SIZE   = 8
# 0.2: ampliado de 10 a 18 (+has_key, energy, dist_llave, dist_puerta, door_open, peligro_cercano)
STATE_SIZE  = 18
ACTION_SIZE = 5
