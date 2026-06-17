# BabyIA World 0.4

Una IA que nace desde cero, aprende por experiencia y evoluciona por etapas.

> **0.4 introduce estado corporal evolutivo (tamano, velocidad, escudo, inmunidades),
> memoria causal causa→efecto, y un evaluador de utilidad explicativo.**
> BabyIA todavia no tiene conciencia real.
> Todos los atributos corporales son mecanismos de juego, no indicadores biologicos.

---

## Que es BabyIA World?

BabyIA World es un laboratorio de aprendizaje donde una IA empieza sin ningun conocimiento previo,
se mueve en un mundo pequeno, choca, explora, recibe recompensas y castigos, guarda memorias
y mejora su conducta paso a paso.

**No usa APIs externas** como OpenAI, Claude ni modelos preentrenados.
**Aprende desde cero** usando Deep Q-Network (DQN) con PyTorch.

---

## Instalacion

```bash
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

---

## Modos de ejecucion

### Entrenar
```bash
python main.py --mode train
python main.py --mode train --episodes 500
python main.py --mode train --seed 42
```

### Observar el modelo aprendido
```bash
python main.py --mode watch
```

### Evaluar sin entrenar
```bash
python main.py --mode evaluate --episodes 100
```

### Reiniciar datos
```bash
python main.py --reset-memory
python main.py --reset-model
python main.py --reset-stats
python main.py --reset-concepts
python main.py --reset-all
```

---

## Objetos del mundo (0.2)

| Simbolo | Tipo            | Efecto                                          |
|---------|-----------------|--------------------------------------------------|
| K       | Llave           | BabyIA la recoge; sirve para abrir puertas       |
| D       | Puerta cerrada  | Bloqueante; se abre con llave                    |
| O       | Puerta abierta  | Transitable                                      |
| F       | Comida          | Recupera energia al tocarla                      |
| X       | Zona peligrosa  | Reduce energia al entrar                         |
| ?       | Objeto desconocido | Otorga curiosidad y recompensa al descubrirlo |

---

## Tests

```bash
pytest tests
pytest tests -v
pytest tests --cov=brain --cov=world
```

---

## Health check

```bash
python scripts/health_check.py
```

---

## Estructura del proyecto

```
BabyIA World/
|-- config.py               <- Rutas y constantes centralizadas
|-- main.py                 <- Argparse, modos, bucle de episodios
|
|-- brain/
|   |-- baby_brain.py       <- DQN con PyTorch (STATE_SIZE=34)
|   |-- trainer.py          <- Orquesta mundo <-> cerebro <-> memoria
|   |-- body_state.py       <- Estado corporal evolutivo (0.4)
|   |-- causal_memory.py    <- Memoria causa->efecto persistente (0.4)
|   |-- utility_evaluator.py <- Capa explicativa de utilidad (0.4)
|   |-- memory.py           <- Memorias episodicas y autobiografia
|   |-- emotions.py         <- Senales internas de control
|   |-- self_model.py       <- Modelo del yo (nivel, habilidades)
|   |-- curriculum.py       <- Niveles 0-6; senaliza cambios de laberinto
|   |-- metrics.py          <- Estadisticas persistentes + por nivel + corporal
|   |-- model_store.py      <- Versionado latest/best/checkpoints
|   |-- concepts.py         <- Memoria conceptual (0.2)
|   |-- strategy.py         <- Registro de estrategias emergentes (0.2)
|   `-- network_inspector.py <- Observabilidad de arquitectura DQN (0.2.1)
|
|-- world/
|   |-- grid_world.py       <- Mundo 8x8 con objetos interactivos
|   |-- objects.py          <- Enumeraciones y constantes
|   |-- rewards.py          <- Calculo de recompensas
|   |-- inventory.py        <- Inventario de BabyIA (0.2)
|   |-- interactions.py     <- Reglas causa-efecto (0.2)
|   |-- powerups.py         <- 8 tipos de powerup (0.4)
|   |-- hazards.py          <- 8 peligros bloqueables (0.4)
|   |-- doors.py            <- 6 puertas con requisitos (0.4)
|   |-- maze_generator.py   <- Generacion procedural de laberintos (0.2.1)
|   `-- level_factory.py    <- Laberintos por nivel 0-6 con BFS (0.2.1)
|
|-- interface/
|   |-- pygame_view.py      <- Ventana grafica con panel de estado
|   `-- console_panel.py    <- Logs con Rich
|
|-- scripts/
|   `-- health_check.py     <- Verificacion de integridad del proyecto
|
|-- docs/                   <- Documentacion interna
|-- data/                   <- Memorias, estadisticas y conceptos en JSON
|-- models/                 <- Pesos del cerebro (.pt)
|-- tests/                  <- 307 tests con pytest
`-- godot/                  <- Reservado para fase futura
```

---

## Modelos guardados

| Archivo | Descripcion |
|---|---|
| `models/babyia_latest.pt` | Modelo mas reciente (cada 10 episodios) |
| `models/babyia_best.pt` | Mejor modelo (solo si mejora) |
| `models/checkpoints/episode_XXXX.pt` | Copias cada 100 episodios |

---

## Datos persistentes

| Archivo | Descripcion |
|---|---|
| `data/training_stats.json` | Metricas de entrenamiento + por nivel (0.2.1) |
| `data/concepts.json` | Conceptos causa-efecto descubiertos (0.2) |
| `data/memories.json` | Experiencias episodicas |
| `data/autobiography.json` | Bitacora narrativa simulada |
| `data/network_stats.json` | Metadatos de arquitectura DQN (0.2.1) |
| `data/level_stats.json` | Configuracion del laberinto actual (0.2.1) |

---

## Sistema de senales internas

| Senal | Funcion |
|-------|---------|
| Curiosidad | Modula la exploracion |
| Confianza | Refleja el exito reciente |
| Frustracion | Se acumula con los choques |
| Energia | Disponibilidad general |

Estas senales **no son emociones reales**.
Ver: [docs/no-conciencia-real.md](docs/no-conciencia-real.md)

---

## Que se implemento en 0.2.2

- `main.py` — corriegido `--episodes 0` (antes era ignorado por `or`)
- `main.py` — flag `--yes` para confirmar resets; muestra arquitectura DQN al iniciar
- `world/level_factory.py` — nivel 0 realmente vacio; niveles 4-6 con BFS llave->puerta
- `world/maze_generator.py` — `is_solvable_with_key_door()` y `generate_solvable_maze_with_key_door()`
- `brain/model_store.py` — `load()` reporta errores en `last_load_error` (no silencia excepciones)
- `brain/network_inspector.py` — version 0.2.2
- `scripts/health_check.py` — verifica nivel 0 abierto y tarea reset con --episodes 0
- 1 nuevo archivo de tests (`test_stability.py`); tests actualizados

## Que se implemento en 0.2.1

- `brain/network_inspector.py` — inspeccion de arquitectura DQN (input, output, params)
- `world/maze_generator.py` — generacion procedural con semilla y validacion BFS
- `world/level_factory.py` — laberintos progresivos para niveles 0-6
- `brain/curriculum.py` — extendido a 6 niveles; senaliza cambios de laberinto
- `brain/metrics.py` — metricas acumuladas por nivel (level_stats)
- `brain/trainer.py` — aplica nuevo laberinto automaticamente al subir de nivel
- `interface/pygame_view.py` — muestra dificultad, semilla y estado de solucionabilidad
- `data/network_stats.json`, `data/level_stats.json` — persistencia de metadatos
- 4 nuevos archivos de tests; 161 tests totales pasando

## Que se implemento en 0.2

- Objetos interactivos: llave, puerta cerrada/abierta, comida, peligro, desconocido
- `world/inventory.py` — inventario de BabyIA por episodio
- `world/interactions.py` — reglas causa-efecto con reward_delta y concept_signal
- `brain/concepts.py` — memoria conceptual persistente en `data/concepts.json`
- `brain/strategy.py` — registro de estrategias emergentes
- STATE_SIZE 10 -> 18 (8 features nuevas: llave, energia, distancias, puerta, peligro)
- Metricas de interacciones (llaves, puertas, comida, peligro, conceptos)

## Novedades en 0.4.0

- `brain/body_state.py` — BodyState: size, speed, shield, fire_immunity, poison_immunity, vision_range, memory_focus
- `world/powerups.py` — 8 tipos de powerup (growth_crystal, speed_boots, shield_orb, etc.)
- `world/hazards.py` — 8 peligros (fire_zone, poison_zone, mud, spikes, etc.) con bloqueo por estado corporal
- `world/doors.py` — 6 tipos de puertas con requisitos de acceso (heavy_door, fire_door, etc.)
- `brain/causal_memory.py` — memoria de relaciones causa→efecto con nivel de confianza persistido en data/causal_memory.json
- `brain/utility_evaluator.py` — capa explicativa de utilidad (no reemplaza DQN)
- STATE_SIZE 26 → 34 (+8 features: size, speed, shield, inmunidades, proximidades)
- Avatar actualizado: radio escala con size, halo de escudo, iconos de inmunidad
- Panel "Cuerpo" en la vista: tamano, velocidad, escudo, inmunidades, utilidad del paso
- 6 nuevos archivos de tests; 307 tests totales pasando

## Novedades en 0.3

- `worlds/` — sistema de 5 mundos (casa, comida, peligro, curiosidad, desafio)
- Portales en el grid 8x8: puertas azul, roja, verde y dorada
- `brain/world_memory.py` — historial de visitas a mundos
- `brain/preferences.py` — preferencia simulada: avg_reward + retorno*5 - riesgo*4
- `brain/home_drive.py` — impulso de regreso a casa con penalizacion por pasos lejanos
- `interface/avatar_renderer.py` — avatar visual que evoluciona con el nivel
- STATE_SIZE 18 → 26 (+8 features de contexto de mundo); modelo v0.3 incompatible con v0.2
- 5 nuevos archivos de tests

## Que queda para 0.4.1+

- Peligros y powerups colocados fisicamente en el grid
- Puertas especiales con requisitos en posiciones del laberinto
- Lenguaje simple: frases generadas por plantillas (0.5)

Ver: [docs/evolucion.md](docs/evolucion.md)
