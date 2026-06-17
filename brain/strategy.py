"""
Registro de estrategias emergentes de BabyIA (0.2).

Este modulo NO reemplaza al DQN. Solo registra estrategias observadas
para explicabilidad y seguimiento. BabyIA no ejecuta estas estrategias
directamente; emergen de la politica aprendida.
"""

from __future__ import annotations

KNOWN_STRATEGIES = [
    # 0.2: estrategias base
    "buscar_llave_antes_de_puerta",
    "evitar_zona_peligrosa",
    "buscar_comida_con_energia_baja",
    "volver_a_puerta_con_llave",
    "explorar_sistematicamente",
    # 0.4.4: estrategias de progreso de nivel
    "completar_nivel_con_llave",
    "buscar_llave_y_luego_puerta_dorada",
    "ignorar_puertas_opcionales_sin_llave",
    "evitar_peligro_sin_proteccion",
]


class StrategyTracker:
    """
    Detecta y registra estrategias emergentes a partir del comportamiento.
    El Trainer lo actualiza al final de cada episodio.
    """

    def __init__(self):
        self.active: dict[str, int] = {}  # estrategia → veces detectada

    def observe(self, events: dict, inventory_log: list[str]):
        """Detecta estrategias a partir de los eventos del episodio."""
        # Busco llave antes de puerta
        if "picked_key" in inventory_log:
            idx_key = (
                inventory_log.index("picked_key")
                if "picked_key" in inventory_log
                else -1
            )
            idx_door = (
                inventory_log.index("opened_door")
                if "opened_door" in inventory_log
                else -1
            )
            if idx_key != -1 and idx_door != -1 and idx_key < idx_door:
                self._register("buscar_llave_antes_de_puerta")

        # Comer con energia baja
        if events.get("ate_food") and events.get("energy_before_food", 1.0) < 0.5:
            self._register("buscar_comida_con_energia_baja")

        # Abrio puerta (implica tenia llave)
        if events.get("opened_door"):
            self._register("volver_a_puerta_con_llave")

        # 0.4.4: estrategias de progreso de nivel
        if events.get("level_completed"):
            self._register("completar_nivel_con_llave")
            # Si en el mismo episodio recogió llave Y completó nivel
            if events.get("picked_key"):
                self._register("buscar_llave_y_luego_puerta_dorada")

        # Ignorar salas opcionales y completar nivel
        if events.get("level_completed") and not events.get("entered_treasure_room"):
            self._register("ignorar_puertas_opcionales_sin_llave")

        # Evitar peligro sin proteccion (no entro en zona de peligro con poca energia)
        if not events.get("in_danger") and events.get("level_completed"):
            self._register("evitar_peligro_sin_proteccion")

    def top(self, n: int = 3) -> list[tuple[str, int]]:
        """Devuelve las n estrategias mas frecuentes."""
        ranked = sorted(self.active.items(), key=lambda x: x[1], reverse=True)
        return ranked[:n]

    def to_dict(self) -> dict:
        return {"strategies": self.active}

    def _register(self, name: str):
        self.active[name] = self.active.get(name, 0) + 1
