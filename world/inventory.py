"""Inventario de BabyIA — objetos y energia durante un episodio."""

MAX_ENERGY        = 1.0
ENERGY_START      = 1.0
ENERGY_COST_DANGER = 0.2
ENERGY_GAIN_FOOD   = 0.3


class Inventory:
    """
    Registra lo que BabyIA lleva encima durante un episodio.
    Se reinicia al comienzo de cada episodio.
    """

    def __init__(self):
        self.reset()

    def reset(self):
        self.has_key    = False
        self.energy     = ENERGY_START
        self.food_count = 0
        self.touched_objects: list[str] = []

    # ── Acciones ──────────────────────────────────────────────────────────────

    def pick_key(self):
        self.has_key = True
        self._touch("key")

    def use_key(self):
        """Consume la llave al abrir una puerta."""
        self.has_key = False

    def eat_food(self) -> float:
        """Consume comida y devuelve la ganancia real de energia."""
        gain = min(ENERGY_GAIN_FOOD, MAX_ENERGY - self.energy)
        self.energy = min(MAX_ENERGY, self.energy + ENERGY_GAIN_FOOD)
        self.food_count += 1
        self._touch("food")
        return gain

    def take_damage(self) -> float:
        """Aplica dano de zona peligrosa y devuelve la perdida."""
        lost = min(ENERGY_COST_DANGER, self.energy)
        self.energy = max(0.0, self.energy - ENERGY_COST_DANGER)
        return lost

    def touch(self, obj_name: str):
        """Registra contacto con un objeto (sin efecto de estado)."""
        self._touch(obj_name)

    def first_touch(self, obj_name: str) -> bool:
        """True si es la primera vez que toca este objeto en el episodio."""
        return obj_name not in self.touched_objects

    # ── Serialización ─────────────────────────────────────────────────────────

    def to_dict(self) -> dict:
        return {
            "has_key"   : self.has_key,
            "energy"    : round(self.energy, 3),
            "food_count": self.food_count,
            "touched"   : self.touched_objects[-5:],
        }

    # ── Interno ───────────────────────────────────────────────────────────────

    def _touch(self, obj_name: str):
        if obj_name not in self.touched_objects:
            self.touched_objects.append(obj_name)
