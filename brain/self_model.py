class SelfModel:
    """Modelo del yo de BabyIA — lo que sabe sobre sí misma."""

    SKILL_MAP = {
        1: "Llegar a la meta",
        2: "Evitar paredes eficientemente",
        3: "Navegar con conceptos básicos de espacio",
    }

    LIMITATIONS = [
        "No puede editar su propio código",
        "No puede conectarse a internet",
        "No puede borrar memorias sin autorización",
        "No puede ejecutar código nuevo sin revisión humana",
    ]

    def __init__(self):
        self.name = "BabyIA"
        self.level = 0
        self.experiences = 0
        self.skills: list[str] = []
        self.objective = "Explorar el mundo y encontrar la meta"

    def level_up(self, new_level: int):
        self.level = new_level
        skill = self.SKILL_MAP.get(new_level)
        if skill and skill not in self.skills:
            self.skills.append(skill)
        objectives = {
            1: "Llegar a la meta de forma consistente",
            2: "Navegar sin chocar con paredes",
            3: "Formar y usar conceptos de navegación",
        }
        if new_level in objectives:
            self.objective = objectives[new_level]

    def to_dict(self):
        return {
            "name": self.name,
            "level": self.level,
            "experiences": self.experiences,
            "skills": self.skills,
            "limitations": self.LIMITATIONS,
            "objective": self.objective,
        }
