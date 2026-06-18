# BabyIA World 0.4.7 (0.4.6c)

Una IA que nace desde cero, aprende por experiencia y evoluciona por etapas.

> **0.4.6c — Vista completa escalable del mundo.**
> `interface/grid_renderer.py` + `interface/grid_scaler.py`: el mundo se escala para caber entero en pantalla.
> Tecla **F** activa vista completa (default); **C/Z/V** activa viewport de camara clasico.
> Fog of war: celdas no visitadas se oscurecen. Etiquetas adaptativas segun tamano de celda.
> 16×16 (nivel max) cabe en 464×464px con cell_size=29px — cada celda sigue siendo legible.
>
> **0.4.7 — Estabilizacion, limpieza tecnica y coherencia documental.**
> Documentacion alineada con 0.4.6 real: STATE_SIZE=40, DQN 40→128→64→5.
> Modelos renombrados a `babyia_v0_4_6_latest.pt` para reflejar la arquitectura actual.
> AGENTS.md con reglas obligatorias para agentes IA que contribuyan al proyecto.
> Health check actualizado para verificar coherencia de 0.4.7.
> Sin nuevas funciones jugables — version de consolidacion.
>
> **0.4.6b — Diagnostico de rutas y anti-estancamiento real.**
> `check_path_to_key_and_door()` usa BFS para verificar si existe ruta accesible baby→llave y llave→puerta.
> VisualMemory registra colisiones repetidas, entradas repetidas a hazards y frecuencia de visita por celda.
> `stuck_zone_hint` identifica la zona de maximo estancamiento del episodio.
> MissionReward aplica `WALL_REPEAT_PENALTY`, `HAZARD_REPEAT_PENALTY` y `OSCILLATION_PENALTY`.
> El cap `MAX_MISSION_REWARD_PER_EPISODE=8.0` evita que el shaping de mision domine la politica.
> La UI (pestana Mision) muestra el estado de las rutas BFS en tiempo real.
>
> **0.4.6 mejora el algoritmo central de aprendizaje.**
> Double DQN elimina la sobreestimacion de Q-values usando redes separadas para seleccionar y evaluar acciones.
> Prioritized Experience Replay muestrea experiencias por error TD — aprende mas de las sorpresas.
> El vector de estado DQN crece de 34 a 40 features incluyendo percepcion (key_visible, door_visible, exploration_ratio).
> REPLAY_CAPACITY aumenta a 50.000 y EPSILON_DECAY se ralentiza a 0.998 para grids grandes.
>
> **0.4.5 introduce mundo escalable (8x8 a 16x16), camara viewport y percepcion funcional real.**
> BabyIA ahora "ve" objetos cercanos con campo visual real — las paredes bloquean la vision (FOV).
> El rango de vision viene de `body_state.vision_range` (modificable por powerups).
> VisualMemory recuerda posiciones vistas durante el episodio; SemanticMap clasifica objetos por utilidad.
> DecisionContext integra percepcion y memoria visual para orientar misiones hacia objetivos visibles o recordados.
> MissionTracker usa la posicion visible/recordada de llave y puerta; detecta COLLECT_USEFUL_POWERUP.
> Nueva pestana "Percep." (tecla 7). Minimapa con posiciones dinamicas segun tamano de grid.
> STATE_SIZE=34 se mantiene — la percepcion va al contexto de decision y UI, no al DQN.
> BabyIA no tiene conciencia real. "Ver", "recordar" y "decidir" son calculos funcionales
> basados en observacion, recompensa, utilidad, memoria, riesgo y progreso.

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

## Objetos del mundo

| Simbolo | Tipo              | Efecto                                               |
|---------|-------------------|------------------------------------------------------|
| K       | Llave             | BabyIA la recoge; necesaria para la puerta de nivel  |
| D       | Puerta cerrada    | Bloqueante; se abre con llave                        |
| O       | Puerta abierta    | Transitable                                          |
| F       | Comida            | Recupera energia al tocarla                          |
| X       | Zona peligrosa    | Reduce energia al entrar                             |
| ?       | Objeto desconocido| Otorga curiosidad y recompensa al descubrirlo        |
| +       | Powerup           | Efecto corporal al recoger (0.4.2)                   |
| !       | Hazard            | Peligro con efecto corporal; puede ser bloqueado (0.4.2) |
| S       | Puerta especial   | Requiere condicion corporal (0.4.2)                  |
| N       | Puerta de nivel   | Dorada; requiere llave; completa el nivel (0.4.3)    |
| O       | Puerta opcional   | Turquesa; sala de tesoro o entrenamiento (0.4.3)     |

### Puertas de nivel (0.4.3)

| Posicion | Tipo              | Descripcion                                   |
|----------|-------------------|-----------------------------------------------|
| (7,7)    | NEXT_LEVEL_DOOR   | Completa el nivel. Requiere llave. Recompensa: +200 |
| (4,7)    | TREASURE_DOOR     | Opcional. Sin requisito. Recompensa: +10       |
| (7,0)    | TRAINING_ROOM     | Opcional. Sin requisito. Recompensa: +5        |

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
|   |-- baby_brain.py       <- DQN con PyTorch (STATE_SIZE=34); last_decision (0.4.1)
|   |-- neural_debugger.py  <- Inspeccion diagnostica: Q-values, activaciones (0.4.1)
|   |-- trainer.py          <- Orquesta mundo <-> cerebro <-> memoria
|   |-- body_state.py       <- Estado corporal evolutivo (0.4)
|   |-- survival.py         <- SurvivalEvaluator: risk_level, diagnostico funcional (0.4.2)
|   |-- causal_memory.py    <- Memoria causa->efecto persistente; wired con eventos reales (0.4.2)
|   |-- utility_evaluator.py <- Capa explicativa de utilidad; usa inventory.energy (fix 0.4.2)
|   |-- memory.py           <- Memorias episodicas y autobiografia
|   |-- emotions.py         <- Senales internas de control
|   |-- self_model.py       <- Modelo del yo (nivel, habilidades)
|   |-- curriculum.py       <- Niveles 0-6; level_completed como disparador; anti-estancamiento (0.4.3)
|   |-- metrics.py          <- Estadisticas persistentes + por nivel + corporal
|   |-- model_store.py      <- Versionado latest/best/checkpoints
|   |-- concepts.py         <- Memoria conceptual (0.2)
|   |-- strategy.py         <- Registro de estrategias emergentes (0.2)
|   `-- network_inspector.py <- Observabilidad de arquitectura DQN (0.2.1)
|
|-- world/
|   |-- grid_world.py       <- Mundo 8x8; level_completed; NEXT_LEVEL_DOOR bloqueante (0.4.3)
|   |-- objects.py          <- Cell.LEVEL_DOOR=12, Cell.OPTIONAL_DOOR=13; STATE_SIZE=34 (0.4.3)
|   |-- level_doors.py      <- LevelDoor; LEVEL_DOOR_POSITIONS; attempt_level_door() (0.4.3)
|   |-- rewards.py          <- REWARD_LEVEL_COMPLETED=120; REWARD_NEW_CELL=0.05 (0.4.3)
|   |-- inventory.py        <- take_damage_by(), restore_energy() (0.4.2)
|   |-- interactions.py     <- Reglas causa-efecto (0.2)
|   |-- powerups.py         <- 8 powerups; apply_powerup_effect() (0.4.2)
|   |-- hazards.py          <- 8 peligros bloqueables (0.4)
|   |-- doors.py            <- DoorRequirement.max_size; small_door max_size=1.2 (0.4.2)
|   |-- maze_generator.py   <- Generacion procedural de laberintos (0.2.1)
|   `-- level_factory.py    <- Laberintos por nivel 0-6 con BFS (0.2.1)
|
|-- interface/
|   |-- pygame_view.py      <- Coordinador: ventana, grid, log inferior (0.4.1)
|   |-- layout.py           <- Geometria: areas, tamanios, pestanas (0.4.1)
|   |-- ui_components.py    <- Paleta de colores y primitivas de dibujo (0.4.1)
|   |-- panel_renderer.py   <- 5 pestanas con scroll y navegacion (0.4.1)
|   |-- status_view.py      <- Pestana Estado (0.4.1)
|   |-- world_info_view.py  <- Pestana Mundo (0.4.1)
|   |-- body_view.py        <- Pestana Cuerpo: energia, supervivencia, eventos (0.4.2)
|   |-- brain_view.py       <- Pestana Cerebro: Q-values y DQN (0.4.1)
|   |-- memory_view.py      <- Pestana Memoria: relaciones causales, inventario (0.4.2)
|   |-- avatar_renderer.py  <- Avatar visual de BabyIA (0.3)
|   `-- console_panel.py    <- Logs con Rich
|
|-- scripts/
|   `-- health_check.py     <- Verificacion de integridad del proyecto
|
|-- docs/                   <- Documentacion interna
|-- data/                   <- Memorias, estadisticas y conceptos en JSON
|-- models/                 <- Pesos del cerebro (.pt)
|-- tests/                  <- 476 tests con pytest
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

## Novedades en 0.4.2

- `world/objects.py` — `Cell.POWERUP=9`, `Cell.HAZARD=10`, `Cell.SPECIAL_DOOR=11`
- `world/grid_world.py` — 4 powerups, 3 hazards y 2 puertas especiales colocados en el grid;
  `step()` detecta y registra interacciones; 3 metodos de proximidad (8-vecinos)
- `world/powerups.py` — `apply_powerup_effect()` — `energy_food` ruteado a `Inventory.restore_energy()`
- `world/doors.py` — `DoorRequirement.max_size`; `small_door` usa `max_size=1.2`
- `world/inventory.py` — `take_damage_by(amount)`, `restore_energy(amount)`
- `brain/survival.py` (NUEVO) — `SurvivalEvaluator.evaluate()` → `risk_level`, `recommendation`,
  `needs_food`, `danger_without_protection`. Solo diagnostico, no afecta al DQN.
- `brain/trainer.py` — `_handle_powerup/hazard/special_door()`, 5 contadores de episodio,
  `causal_memory.observe()` con eventos reales, `get_status()` incluye `survival` y `causal_relations`
- `brain/utility_evaluator.py` — bug fix: usaba `body_state.shield` como proxy de energia; ahora usa `inventory.energy`
- `interface/body_view.py` — muestra energia del inventario, supervivencia funcional, ultimo evento corporal
- `interface/memory_view.py` — muestra las ultimas relaciones causales con confianza
- `interface/pygame_view.py` — colores (cian/naranja/violeta) y etiquetas para nuevas celdas
- `scripts/health_check.py` — `check_042_integrity()`: small_door.max_size, energy_food.effect,
  utility_evaluator sin shield-as-energy, survival importable, get_status con survival+causal_relations
- 7 nuevos archivos de test; 413 tests totales pasando

## Novedades en 0.4.1

- `interface/` dividido en 8 modulos: layout.py, ui_components.py, panel_renderer.py,
  status_view.py, world_info_view.py, body_view.py, brain_view.py, memory_view.py
- Panel de 5 pestanas navegables con teclado (1-5 / TAB / flechas) y scroll
- `brain/neural_debugger.py` — inspeccion diagnostica del DQN:
  Q-values por accion, activaciones intermedias via forward hooks, snapshot completo
- `brain/baby_brain.py` — `last_decision` registra tipo de decision (exploration/exploitation)
- `brain/trainer.py` — `get_status()` incluye `brain_debug` (calculado cada 5 pasos)
- Panel Cerebro: arquitectura 34→128→64→5, barras Q-values, epsilon, loss, replay buffer
- Bitacora en panel inferior separado; borde de color por mundo en el grid
- Ventana 860×618 px; 3 nuevos archivos de test; 351 tests totales pasando

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

## Que queda para 0.4.2+

- Peligros y powerups colocados fisicamente en el grid
- Puertas especiales con requisitos en posiciones del laberinto
- Lenguaje simple: frases generadas por plantillas (0.5)

Ver: [docs/evolucion.md](docs/evolucion.md)
