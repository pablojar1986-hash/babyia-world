# BabyIA World 0.4.7

Laboratorio local de aprendizaje por refuerzo donde BabyIA nace sin
conocimiento previo, explora un mundo en grid, recibe recompensas/castigos,
guarda memoria funcional y mejora su politica con experiencia.

BabyIA **no usa APIs externas de IA**, no se conecta a internet y no usa
modelos preentrenados. Aprende localmente con PyTorch.

BabyIA tampoco tiene conciencia real. Palabras como "ver", "recordar",
"decidir", "preferir", "mision" o "supervivencia" nombran calculos
funcionales. Ver [docs/no-conciencia-real.md](docs/no-conciencia-real.md).

---

## Estado actual

| Area | Estado |
|---|---|
| Version | `APP_VERSION=0.4.7` |
| Algoritmo | Double DQN + Prioritized Experience Replay |
| Estado DQN | `STATE_SIZE=40` |
| Arquitectura | `40 -> 128 -> 64 -> 5` |
| Replay | `REPLAY_CAPACITY=50000` |
| Exploracion | `EPSILON_DECAY=0.998` |
| Vista | Mundo completo escalable por defecto (`F`) |
| Tests | Suite completa con pytest |

La version 0.4.7 es una fase de estabilizacion: alinea documentacion,
versionado de modelos, health check y reglas para agentes. La mejora visual
0.4.6c agrega vista completa escalable con fog of war y modo camara.

---

## Instalacion

```powershell
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Si el alias global `python` apunta a Microsoft Store, usa el ejecutable directo:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Dependencias directas mantenidas en `requirements.txt`: `numpy`, `pygame`,
`rich`, `pytest`, `pytest-cov` y `torch`.

---

## Ejecucion

### Entrenar

```powershell
python main.py --mode train
python main.py --mode train --episodes 500
python main.py --mode train --seed 42
```

### Observar el modelo aprendido

```powershell
python main.py --mode watch
```

### Evaluar sin entrenar

```powershell
python main.py --mode evaluate --episodes 100
```

### Reiniciar datos

```powershell
python main.py --reset-memory --yes
python main.py --reset-model --yes
python main.py --reset-stats --yes
python main.py --reset-concepts --yes
python main.py --reset-all --yes
```

---

## Validacion

```powershell
python scripts\health_check.py
python -m pytest tests -q
python -m pytest tests --cov=brain --cov=world
```

En Windows tambien puedes usar:

```powershell
.\.venv\Scripts\python.exe scripts\health_check.py
.\.venv\Scripts\python.exe -m pytest tests -q
```

---

## Controles de la interfaz

| Tecla | Accion |
|---|---|
| `F` | Vista completa del mundo (default) |
| `C`, `Z`, `V` | Modo camara/viewport clasico |
| `1`-`7` | Pestanas: Estado, Mundo, Cuerpo, Cerebro, Memoria, Mision, Percepcion |
| `TAB`, flechas | Navegacion entre pestanas y scroll |

---

## Objetos del mundo

| Simbolo | Tipo | Efecto |
|---|---|---|
| `K` | Llave | Necesaria para la puerta de nivel |
| `D` | Puerta cerrada | Bloqueante; se abre con llave |
| `O` | Puerta abierta/opcional | Transitable; puede ser sala opcional |
| `F` | Comida | Recupera energia |
| `X` | Zona peligrosa | Reduce energia |
| `?` | Objeto desconocido | Recompensa de curiosidad |
| `+` | Powerup | Modifica estado corporal |
| `!` | Hazard | Peligro corporal bloqueable |
| `S` | Puerta especial | Requiere condicion corporal |
| `N` | Puerta de nivel | Completa nivel con llave |

Puertas principales 0.4.3:

| Posicion | Tipo | Descripcion |
|---|---|---|
| Progreso dinamico | `NEXT_LEVEL_DOOR` | Completa nivel; requiere llave |
| Dinamica por grid | `TREASURE_DOOR` | Opcional; recompensa menor |
| Dinamica por grid | `TRAINING_ROOM` | Opcional; entrenamiento/recompensa menor |

---

## Estructura

```text
BabyIA World/
|-- config.py                # Rutas, constantes, APP_VERSION
|-- main.py                  # Argparse y loop de episodios
|-- brain/                   # DQN, memoria, mision, percepcion, metricas
|-- world/                   # Grid, objetos, recompensas, puertas, laberintos
|-- worlds/                  # Mundos logicos y portales
|-- interface/               # Visualizacion Pygame; no entrena
|-- scripts/health_check.py  # Integridad del proyecto
|-- docs/                    # Arquitectura, evolucion y continuidad
|-- data/                    # Persistencia JSON de entrenamiento
|-- models/                  # Pesos .pt y checkpoints locales
|-- tests/                   # Suite pytest
`-- godot/                   # Fase grafica futura
```

Referencias de arquitectura:

- [docs/arquitectura.md](docs/arquitectura.md)
- [docs/evolucion.md](docs/evolucion.md)
- [docs/continuacion.md](docs/continuacion.md)
- [AGENTS.md](AGENTS.md)

---

## Modelos guardados

| Archivo | Descripcion |
|---|---|
| `models/babyia_v0_4_6_latest.pt` | Modelo mas reciente para `STATE_SIZE=40` |
| `models/babyia_v0_4_6_best.pt` | Mejor modelo compatible con arquitectura 0.4.6+ |
| `models/checkpoints/episode_XXXX.pt` | Checkpoints periodicos |

Modelos anteriores (`babyia_latest.pt`, `babyia_v0_3_latest.pt`,
`babyia_v0_4_latest.pt`) pueden ser incompatibles por cambios de `STATE_SIZE`.
Los errores de carga deben reportarse claramente.

---

## Datos persistentes

| Archivo | Descripcion |
|---|---|
| `data/training_stats.json` | Metricas de entrenamiento, nivel, mision y mundo |
| `data/memories.json` | Experiencias episodicas |
| `data/autobiography.json` | Bitacora narrativa simulada |
| `data/concepts.json` | Conceptos causa-efecto |
| `data/causal_memory.json` | Relaciones causales con confianza |
| `data/world_history.json` | Historial de mundos visitados |
| `data/world_preferences.json` | Preferencias funcionales simuladas |
| `data/home_stats.json` | Metricas de retorno a casa |
| `data/network_stats.json` | Metadatos de arquitectura DQN |
| `data/level_stats.json` | Configuracion y estadisticas de niveles |

Estos archivos son resultado de entrenamiento. Antes de commitearlos, revisar
si representan una sesion que realmente se quiere preservar.

---

## Resumen de evolucion reciente

- **0.4.3**: progresion real por puerta de nivel, anti-estancamiento y reward
  balanceado contra reward hacking de exploracion.
- **0.4.4**: mision funcional, contexto de decision, reward shaping acotado,
  minimapa y pestana de mision.
- **0.4.5**: mundo escalable, camara, FOV real, memoria visual y percepcion.
- **0.4.6**: Double DQN, Prioritized Experience Replay y `STATE_SIZE=40`.
- **0.4.6b**: diagnostico BFS de rutas y penalizaciones anti-loop.
- **0.4.6c**: vista completa escalable con fog of war.
- **0.4.7**: consolidacion tecnica y documental.

El detalle completo esta en [docs/evolucion.md](docs/evolucion.md).

---

## Continuacion recomendada

Antes de empezar 0.5.0, seguir [docs/continuacion.md](docs/continuacion.md):

1. Validar health check y suite completa.
2. Medir aprendizaje con evaluaciones reproducibles.
3. Hacer ablations de reward/percepcion/PER si se cambia aprendizaje.
4. Mantener lenguaje por plantillas como salida explicativa, no como cerebro.
5. No implementar Godot, sockets, voz, LLMs ni internet hasta que la fase
   correspondiente este explicitamente aprobada.
