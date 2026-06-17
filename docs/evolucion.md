# Ruta de evolución de BabyIA World

## Versiones planificadas

### 0.1 — Base (completado)
- Mundo 8×8 con paredes y meta
- DQN con PyTorch construido desde cero
- Sistema de recompensas
- Memoria episódica y autobiográfica en JSON
- Señales internas (curiosidad, confianza, frustración, energía)
- Modelo del yo (nivel, habilidades, objetivo)
- Sistema de 4 niveles con métricas de éxito
- Visualización Pygame + logs con Rich
- 21 tests con pytest

### 0.1.1 — Estabilizacion (completado)
- Modos de ejecucion: train, watch, evaluate
- Argumentos por consola (argparse)
- Metricas persistentes (training_stats.json)
- Versionado de modelos: latest, best, checkpoints
- Resets controlados: memory, model, stats, all
- Semilla de reproducibilidad (--seed)
- Health check del proyecto
- Documentacion interna (docs/)
- Nuevos tests de metricas, model_store, modos, health check
- config.py centralizado

### 0.2 — Objetos, inventario y causa-efecto (completado)
- Objetos interactivos: llave, puerta, comida, peligro, desconocido
- world/inventory.py — inventario de BabyIA por episodio
- world/interactions.py — reglas causa-efecto con reward_delta y concept_signal
- brain/concepts.py — memoria conceptual persistente en data/concepts.json
- brain/strategy.py — registro de estrategias emergentes
- STATE_SIZE 10 -> 18 (8 features nuevas de inventario y objetos)
- Metricas de interacciones en training_stats.json
- 4 nuevos tests; 110 tests totales pasando

### 0.2.1 — Observabilidad de red neuronal, control de commits y laberintos progresivos (completado)
- brain/network_inspector.py — inspeccion de arquitectura DQN (input_size, params, capas)
- world/maze_generator.py — generacion procedural de laberintos con semilla y BFS
- world/level_factory.py — laberintos progresivos por nivel 0-6 con validacion de solucionabilidad
- brain/curriculum.py — ampliado a 6 niveles con maze_needs_update / consume_maze_update()
- brain/metrics.py — metricas acumuladas por nivel (level_stats dict)
- brain/trainer.py — aplica laberinto nuevo en cada subida de nivel
- interface/pygame_view.py — muestra dificultad, semilla y estado de solucionabilidad
- data/network_stats.json y data/level_stats.json — persistencia de metadatos
- 4 nuevos archivos de tests; 161 tests totales pasando

### 0.2.2 — Estabilidad, seguridad de reset y progresion real de laberintos (actual)
- main.py: corregido --episodes 0 (era interpretado como False)
- main.py: flag --yes para confirmar resets destructivos con advertencia visible
- main.py: muestra arquitectura DQN al iniciar (input, output, params)
- world/level_factory.py: nivel 0 = mundo completamente abierto (frozenset vacio)
- world/level_factory.py: nivel 1 = paredes base; niveles 4-6 = validacion llave->puerta->meta
- world/maze_generator.py: is_solvable_with_key_door() con BFS por etapas
- world/maze_generator.py: generate_solvable_maze_with_key_door()
- brain/model_store.py: load() reporta errores claramente (last_load_error)
- brain/network_inspector.py: version actualizada a 0.2.2
- .vscode/tasks.json: tarea reset usa --yes para omitir advertencia
- 1 nuevo archivo de tests; tests actualizados; todos pasan

### 0.3 — Puertas a diferentes mundos, preferencias aprendidas y regreso a casa (completado)
- worlds/ — nuevo modulo con 5 definiciones de mundo (home, food, danger, curiosity, challenge)
- worlds/world_manager.py — detecta portales por posicion, gestiona transiciones de mundo
- worlds/reward_profiles.py — perfiles de recompensa distintos por tipo de mundo
- worlds/world_registry.py — portales de salida (blue, red, green, gold) y puerta de regreso
- brain/world_memory.py — registra visitas a mundos en data/world_history.json
- brain/preferences.py — calcula preferencia simulada (avg_reward + retorno*5 - riesgo*4)
- brain/home_drive.py — impulso de regreso a casa; penalizacion extra por pasos lejanos
- interface/avatar_renderer.py — avatar visual que cambia por nivel y senales internas
- brain/baby_brain.py — STATE_SIZE 18 -> 26 (+8 features de contexto de mundo)
- brain/trainer.py — integra WorldManager, HomeDrive, WorldMemory, PreferenceTracker
- brain/metrics.py — metricas de mundos: visitas, retorno a casa, episodios lejos
- interface/pygame_view.py — panel Mundo: nombre, retorno, portal usado, tasa de regreso
- config.py — MODEL_V3_LATEST/BEST; WORLD_HISTORY_FILE, WORLD_PREFS_FILE, HOME_STATS_FILE
- 5 nuevos archivos de tests; 21+ tests nuevos

### 0.3.1 — Integracion completa de recompensas por mundo (completado)
- brain/trainer.py: _apply_interactions llama world_manager.on_object_event() en ate_food, in_danger, found_unknown
- brain/trainer.py: end_episode aplica penalizacion de world_manager.on_episode_end() si fuera de casa
- tests/test_world_integration_031.py: 9 tests de integracion verifican el comportamiento

### 0.4.0 — Recompensas evolutivas: tamano, velocidad, energia, escudo e inmunidades (actual)
- brain/body_state.py — BodyState: size, speed, shield, fire_immunity, poison_immunity, vision_range
- world/powerups.py — 8 tipos de powerup: GROWTH_CRYSTAL, SPEED_BOOTS, SHIELD_ORB, etc.
- world/hazards.py — 8 peligros: FIRE_ZONE, POISON_ZONE, MUD, SHRINK_TRAP, SLOW_TRAP, etc.
- world/doors.py — 6 tipos de puertas con requisitos: HEAVY_DOOR, SPEED_DOOR, FIRE_DOOR, etc.
- brain/causal_memory.py — memoria de relaciones causa-efecto (powerup->efecto, hazard->daño)
- brain/utility_evaluator.py — calcula utilidad de recompensas segun objetivo y estado corporal
- STATE_SIZE 26 -> 34 (+8 features: size, speed, shield, immunities, proximidades)
- 6 nuevos archivos de test

### 0.4.1 — Peligros y supervivencia
- Peligros colocados en el grid (FIRE_ZONE, POISON_ZONE, MUD, etc.)
- BabyIA aprende a evitar peligros segun su estado corporal
- Interacciones con hazards en tiempo real

### 0.4.2 — Puertas con requisitos
- Puertas especiales colocadas en el grid con requisitos de acceso
- BabyIA aprende que necesita para abrir cada puerta
- Registro de intentos fallidos y exitosos

### 0.4.3 — Evaluador de utilidad y aprendizaje causa-efecto avanzado
- Utilidad integrada en toma de decisiones del agente
- Memoria causal completa con actualizacion por experiencia

### 0.5.0 — Lenguaje simple por plantillas
- Frases generadas por plantillas mas ricas
- Vocabulario basico de navegacion y objetos
- BabyIA puede "describir" lo que ve

### 0.6.0 — Interfaz Godot
- Comunicacion Python <-> Godot via sockets o JSON
- Visualizacion 2D/2.5D del mundo
- Animaciones de BabyIA segun estado interno
- El cerebro sigue siendo Python puro

### 1.0 — Juego-laboratorio completo
- Múltiples mundos y escenarios
- Sistema de lenguaje funcional
- Interfaz Godot estable
- Documentación pública
- Tests de integración Python-Godot

## Principio rector

Cada versión debe ser un sistema funcional y comprensible.
No se avanza a la siguiente versión hasta que la actual es estable,
tiene tests, documentación y puede explicarse claramente.
