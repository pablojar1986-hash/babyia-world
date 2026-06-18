# Reglas para agentes IA en BabyIA World

Este archivo define las reglas obligatorias para cualquier agente IA (Claude Code u otro)
que trabaje dentro del repositorio BabyIA World.

**Antes de programar**, el agente debe revisar `README.md`, `docs/evolucion.md` y este archivo.

---

## Reglas obligatorias

1. **No reconstruir el proyecto desde cero.**
   El proyecto ya existe y funciona. Identificar el archivo correcto a modificar antes de crear uno nuevo.

2. **No crear dependencias nuevas sin justificacion documentada.**
   `requirements.txt` debe mantenerse minimalista. Justificar cualquier adicion con un caso concreto.

3. **No crear abstracciones "para despues".**
   Si la abstraccion no se usa en esta version, no se implementa. Aplica principio Ponytail:
   ¿Esto realmente debe existir? ¿Ya existe algo que lo resuelve?

4. **No crear archivos mayores a 300 lineas.**
   Si una funcion nueva supera este limite, dividirla antes de hacer commit.
   Los archivos existentes que ya superan este limite son deuda tecnica conocida.

5. **No meter logica de aprendizaje en `interface/`.**
   Los modulos en `interface/` solo leen datos del status dict y los muestran.
   No calculan rewards, no modifican el buffer, no acceden a la red neuronal directamente.

6. **No meter logica de mundo en `main.py`.**
   `main.py` solo orquesta el loop de episodios. La logica de mundo va en `world/` o `brain/`.

7. **No ocultar errores importantes.**
   Los errores de carga de modelo (incompatibilidad de STATE_SIZE) deben reportarse claramente,
   no silenciarse. No usar `except: pass` en rutas criticas.

8. **No hacer commits automaticos.**
   El agente puede proponer un mensaje de commit, pero el commit lo hace el usuario.

9. **No usar APIs externas de IA.**
   BabyIA aprende por refuerzo puro con PyTorch local. No OpenAI, no Anthropic API, no LLM externo.

10. **No conectar BabyIA a internet.**
    El sistema es completamente local. Sin `requests`, `urllib`, `httpx`, `socket` en codigo de produccion.

11. **No afirmar que BabyIA tiene conciencia real.**
    "Ver", "recordar", "decidir", "preferir", "mision" y "supervivencia" son calculos funcionales.
    Ver `docs/no-conciencia-real.md` para la distincion correcta.

12. **Toda logica no trivial debe tener test.**
    Cualquier funcion nueva que no sea obvia (trivial) debe tener al menos un test en `tests/`.
    "Trivial" = una linea, sin branches, sin estado.

13. **Toda simplificacion intencional debe marcarse con:**
    ```python
    # ponytail: <limite>, mejorar cuando <condicion concreta>
    ```
    Ejemplo: `# ponytail: O(n^2), mejorar cuando grid > 32x32`

---

## Checklist antes de implementar algo nuevo

Antes de crear cualquier archivo o funcion nueva, verificar:

- [ ] ¿Esto realmente debe existir?
- [ ] ¿Ya existe un modulo que lo resuelve parcialmente?
- [ ] ¿Puede resolverse con una funcion simple en lugar de una clase?
- [ ] ¿Estoy creando una abstraccion innecesaria?
- [ ] ¿Estoy aumentando la deuda tecnica del proyecto?
- [ ] ¿Puede hacerse con menos lineas sin perder claridad?

---

## Arquitectura actual (0.4.7)

```
Algoritmo:      Double DQN + Prioritized Experience Replay
STATE_SIZE:     40 (10 base + 8 inventario + 8 mundo + 8 cuerpo + 6 percepcion)
Arquitectura:   40 → 128 → 64 → 5
REPLAY_CAPACITY: 50.000
EPSILON_DECAY:  0.998
APP_VERSION:    0.4.7
Modelos:        babyia_v0_4_6_latest.pt / babyia_v0_4_6_best.pt
```

## Que NO implementar todavia

- Lenguaje simple por plantillas (planificado para 0.5.0)
- Interfaz Godot (planificado para 0.6.0)
- Voz o TTS
- LLM local o externo
- Nuevos mundos jugables
- Auto-modificacion de codigo
- Conexion a internet
- Modelos preentrenados externos

---

## Referencias rapidas

| Archivo | Responsabilidad |
|---------|----------------|
| `config.py` | Rutas, constantes, APP_VERSION. Sin logica. |
| `main.py` | Loop de episodios, argparse, orquestacion. |
| `brain/baby_brain.py` | DQN, Double DQN, PER, STATE_SIZE. |
| `brain/trainer.py` | Orquesta mundo <-> cerebro <-> memoria. |
| `world/objects.py` | STATE_SIZE (debe coincidir con baby_brain.py). |
| `world/path_diagnostics.py` | BFS de accesibilidad de rutas. |
| `interface/*_view.py` | Solo visualizacion. Sin logica de entrenamiento. |
| `scripts/health_check.py` | Verificacion de integridad del proyecto. |
| `docs/no-conciencia-real.md` | Por que BabyIA no tiene conciencia real. |
