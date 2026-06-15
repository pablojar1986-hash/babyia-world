class Emotions:
    """
    Señales internas de control — no son emociones reales.
    Modulan la exploración y sirven como indicadores de estado.
    """

    def __init__(self):
        self.curiosity = 0.8     # impulso a explorar lo desconocido
        self.confidence = 0.5    # seguridad en las decisiones tomadas
        self.frustration = 0.0   # acumulada por choques y fracasos
        self.energy = 1.0        # disponibilidad general para actuar

    def update(self, reward, hit_wall, reached_goal):
        if hit_wall:
            self.frustration = min(1.0, self.frustration + 0.05)
            self.confidence = max(0.0, self.confidence - 0.02)
            self.curiosity = max(0.1, self.curiosity - 0.01)

        if reached_goal:
            self.confidence = min(1.0, self.confidence + 0.1)
            self.frustration = max(0.0, self.frustration - 0.3)
            self.curiosity = min(1.0, self.curiosity + 0.05)

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
