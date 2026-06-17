class Emotions:
    """
    Señales internas de control — no son emociones reales.
    Modulan la exploración y sirven como indicadores de estado funcional.
    'Confianza', 'curiosidad' y 'frustración' son variables numéricas,
    no estados subjetivos.
    """

    def __init__(self):
        self.curiosity = 0.8
        self.confidence = 0.5
        self.frustration = 0.0
        self.energy = 1.0
        self._steps_without_wall: int = 0

    def update(self, reward: float, hit_wall: bool, reached_goal: bool, events=None):
        ev = events or {}

        if hit_wall:
            self.frustration = min(1.0, self.frustration + 0.05)
            self.confidence = max(0.0, self.confidence - 0.02)
            self.curiosity = max(0.1, self.curiosity - 0.01)
            self._steps_without_wall = 0
        else:
            self._steps_without_wall += 1
            # Boost leve por evitar choques consecutivos (cada 10 pasos)
            if self._steps_without_wall % 10 == 0:
                self.confidence = min(1.0, self.confidence + 0.005)

        # Logros parciales suben confianza
        if ev.get("picked_key"):
            self.confidence = min(1.0, self.confidence + 0.08)
            self.frustration = max(0.0, self.frustration - 0.10)
        if ev.get("opened_door"):
            self.confidence = min(1.0, self.confidence + 0.05)
        if ev.get("level_completed"):
            self.confidence = min(1.0, self.confidence + 0.15)
            self.frustration = max(0.0, self.frustration - 0.30)
            self.curiosity = min(1.0, self.curiosity + 0.10)
        if ev.get("ate_food"):
            self.confidence = min(1.0, self.confidence + 0.01)
        if ev.get("visited_new"):
            self.confidence = min(1.0, self.confidence + 0.005)

        if reached_goal:
            self.confidence = min(1.0, self.confidence + 0.10)
            self.frustration = max(0.0, self.frustration - 0.30)
            self.curiosity = min(1.0, self.curiosity + 0.05)

        # Señal de recompensa positiva o negativa fuerte
        if reward > 0.5 and not hit_wall:
            self.confidence = min(1.0, self.confidence + 0.01)
        elif reward < -2.0:
            self.confidence = max(0.0, self.confidence - 0.02)

        # Eventos negativos específicos
        if ev.get("in_danger"):
            self.confidence = max(0.0, self.confidence - 0.04)
        if ev.get("hit_door_closed"):
            self.confidence = max(0.0, self.confidence - 0.01)

        self.energy = max(0.1, min(1.0, self.energy + (0.01 if reward > 0 else -0.005)))

        # Decaimiento natural por paso del tiempo
        self.frustration = max(0.0, self.frustration - 0.001)
        self.curiosity = max(0.1, min(1.0, self.curiosity + 0.002))

    def exploration_bonus(self):
        """Valor extra de exploración basado en curiosidad (suma a epsilon)."""
        return self.curiosity * 0.25

    def to_dict(self):
        return {
            "curiosity": round(self.curiosity, 3),
            "confidence": round(self.confidence, 3),
            "frustration": round(self.frustration, 3),
            "energy": round(self.energy, 3),
        }
