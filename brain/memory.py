import json
from datetime import datetime
from pathlib import Path

DATA_DIR = Path("data")
MAX_STEPS_IN_RAM  = 1000
MAX_AUTOBIOGRAPHY = 200


class Memory:
    """
    Sistema de memoria persistente en JSON.
    Guarda experiencias de episodios y la autobiografia de BabyIA.
    Nota: estas frases son narrativas simuladas, no conciencia real.
    """

    def __init__(self):
        self.episodes: list[dict] = []
        self.autobiography: list[dict] = []
        self._load()

    # ── Registro de experiencias ───────────────────────────────────────────────

    def record_step(self, episode, step, state, action, reward, info):
        entry = {
            "episode"      : episode,
            "step"         : step,
            "state"        : state.tolist() if hasattr(state, "tolist") else list(state),
            "action"       : int(action),
            "reward"       : reward,
            "hit_wall"     : info.get("hit_wall", False),
            "reached_goal" : info.get("reached_goal", False),
            "timestamp"    : datetime.now().isoformat(),
        }
        self.episodes.append(entry)
        if len(self.episodes) > MAX_STEPS_IN_RAM:
            self.episodes = self.episodes[-MAX_STEPS_IN_RAM:]

    def record_autobiography(self, phrase: str):
        self.autobiography.append({
            "timestamp": datetime.now().isoformat(),
            "text"     : phrase,
        })
        if len(self.autobiography) > MAX_AUTOBIOGRAPHY:
            self.autobiography = self.autobiography[-MAX_AUTOBIOGRAPHY:]

    # ── Generacion de frases autobiograficas (0.2 ampliado) ───────────────────

    def generate_phrase(self, episode, total_reward, wall_hits,
                        reached_goal, epsilon,
                        events: dict | None = None) -> str:
        """
        Genera una frase narrativa sobre el episodio.
        events puede contener claves de interaccion (0.2).
        Estas frases son simuladas; BabyIA no tiene experiencias reales.
        """
        ev = events or {}

        # Eventos de objetos (0.2)
        if ev.get("opened_door"):
            return "Use una llave y la puerta se abrio. Aprendi que la llave sirve para algo."
        if ev.get("picked_key") and reached_goal:
            return f"Recogi una llave y llegue a la meta. Episodio {episode}."
        if ev.get("picked_key"):
            return "Encontre una llave por primera vez. Que sirve para abrir?"
        if ev.get("hit_door_closed"):
            return "Intente abrir una puerta, pero no pude. Necesito algo."
        if ev.get("in_danger"):
            return "Entre en una zona peligrosa. Perdi energia. Debo evitarla."
        if ev.get("ate_food") and ev.get("reached_goal"):
            return f"Comi, recupere energia y llegue a la meta. Episodio {episode}."
        if ev.get("ate_food"):
            return "Comi algo. La comida parece restaurar mi energia."
        if ev.get("found_unknown"):
            return "Encontre un objeto que no conozco. Que hace?"

        # Eventos base (0.1.x)
        if reached_goal:
            if episode <= 10:
                return "Encontre la meta por primera vez. Fue un momento importante."
            elif epsilon > 0.4:
                return f"Llegue a la meta en el episodio {episode}. Aun estoy explorando."
            else:
                return f"Alcance la meta en el episodio {episode}. Mi confianza crece."
        if wall_hits > 10:
            return "Choque demasiadas veces. Debo cambiar de estrategia."
        if wall_hits > 0:
            return "Choque con algunas paredes. Estoy aprendiendo los limites del mundo."
        if total_reward < -5:
            return "Este episodio fue dificil. Debo explorar nuevas rutas."
        return f"Explore el mundo en el episodio {episode}. Sigo aprendiendo."

    # ── Acceso a datos ─────────────────────────────────────────────────────────

    def last_log_entries(self, n: int = 5) -> list[str]:
        return [e["text"] for e in self.autobiography[-n:]]

    # ── Persistencia ───────────────────────────────────────────────────────────

    def save(self):
        DATA_DIR.mkdir(exist_ok=True)
        with open(DATA_DIR / "memories.json", "w", encoding="utf-8") as f:
            json.dump(self.episodes[-100:], f, indent=2, ensure_ascii=False)
        with open(DATA_DIR / "autobiography.json", "w", encoding="utf-8") as f:
            json.dump(self.autobiography, f, indent=2, ensure_ascii=False)

    def _load(self):
        for filename, attr in [
            ("memories.json",     "episodes"),
            ("autobiography.json","autobiography"),
        ]:
            path = DATA_DIR / filename
            try:
                with open(path, encoding="utf-8") as f:
                    setattr(self, attr, json.load(f))
            except (FileNotFoundError, json.JSONDecodeError):
                setattr(self, attr, [])
