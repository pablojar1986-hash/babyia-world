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

### 0.4.0 — Recompensas evolutivas: tamano, velocidad, energia, escudo e inmunidades (completado)
- brain/body_state.py — BodyState: size, speed, shield, fire_immunity, poison_immunity, vision_range
- world/powerups.py — 8 tipos de powerup: GROWTH_CRYSTAL, SPEED_BOOTS, SHIELD_ORB, etc.
- world/hazards.py — 8 peligros: FIRE_ZONE, POISON_ZONE, MUD, SHRINK_TRAP, SLOW_TRAP, etc.
- world/doors.py — 6 tipos de puertas con requisitos: HEAVY_DOOR, SPEED_DOOR, FIRE_DOOR, etc.
- brain/causal_memory.py — memoria de relaciones causa-efecto (powerup->efecto, hazard->daño)
- brain/utility_evaluator.py — calcula utilidad de recompensas segun objetivo y estado corporal
- STATE_SIZE 26 -> 34 (+8 features: size, speed, shield, immunities, proximidades)
- 6 nuevos archivos de test

### 0.4.1 — Interfaz avanzada y red neuronal visible (completado)
- interface/ dividido en 8 modulos: layout.py, ui_components.py, panel_renderer.py,
  status_view.py, world_info_view.py, body_view.py, brain_view.py, memory_view.py
- Panel de 5 pestanas (1-5 / TAB / flechas): Estado, Mundo, Cuerpo, Cerebro, Memoria
- brain/neural_debugger.py — inspeccion diagnostica del DQN sin efectos secundarios:
  Q-values por accion, activaciones por capa via forward hooks, snapshot completo
- brain/baby_brain.py — last_decision con tracking exploration/exploitation
- brain/trainer.py — get_status() incluye brain_debug calculado cada 5 pasos
- Panel Cerebro: arquitectura 34->128->64->5, barras Q-values, epsilon, loss, replay buffer
- Bitacora separada en panel inferior; borde de color por mundo en el grid
- Ventana 860x618px (antes 810x490); 3 nuevos archivos de test; 351 tests pasando

### 0.4.2 — Integracion jugable real de powerups, hazards, puertas especiales y supervivencia (completado)
- world/objects.py: Cell.POWERUP=9, Cell.HAZARD=10, Cell.SPECIAL_DOOR=11
- world/grid_world.py: posiciones estaticas de 4 powerups, 3 hazards y 2 puertas especiales en grid;
  step() registra interacciones; get_grid() renderiza nuevas celdas; 3 metodos de proximidad
- world/powerups.py: apply_powerup_effect() — energy_food ruteada a Inventory.restore_energy()
- world/hazards.py: apply_hazard_to_body() — daño variable por tipo
- world/doors.py: DoorRequirement.max_size — small_door solo pasa size <= 1.2
- world/inventory.py: take_damage_by(), restore_energy() — daño y recarga variables
- brain/survival.py (NUEVO): SurvivalEvaluator.evaluate() — calcula risk_level, recommendation,
  needs_food, danger_without_protection. Solo diagnostico; no influye en DQN.
- brain/trainer.py: _handle_powerup/hazard/special_door(), 5 contadores de episodio,
  survival calculado cada 5 pasos, causal_memory.observe() con eventos reales
- brain/utility_evaluator.py: bug fix — usa inventory.energy (no body_state.shield)
- brain/body_state.py: get_state_features() acepta powerup_nearby/hazard_nearby/door_req_nearby
- interface/body_view.py: muestra energia de inventario, supervivencia funcional, ultimo evento
- interface/memory_view.py: muestra ultimas relaciones causales aprendidas
- interface/pygame_view.py: colores/etiquetas para Cell.POWERUP/HAZARD/SPECIAL_DOOR; log de eventos
- scripts/health_check.py: check_042_integrity() — 5 nuevas verificaciones de integridad
- 7 nuevos archivos de test; 413 tests pasando

### 0.4.3 — Progresion real por puertas de nivel, curriculo anti-estancamiento y recompensa orientada a completar niveles (actual, fix 2)
- PROBLEMA resuelto: BabyIA podia acumular alta recompensa (hasta 64 pts por exploracion)
  sin completar nunca el nivel. REWARD_NEW_CELL=0.05 (antes 1.0) elimina este reward hacking.
- world/level_doors.py (NUEVO): LevelDoor, LEVEL_DOOR_POSITIONS (3 puertas), attempt_level_door()
- world/objects.py: Cell.LEVEL_DOOR=12, Cell.OPTIONAL_DOOR=13; STATE_SIZE corregido a 34
- world/rewards.py: REWARD_LEVEL_COMPLETED=120, REWARD_NEXT_LEVEL_DOOR=80, REWARD_NEW_CELL=0.05
- world/grid_world.py: (7,7) es NEXT_LEVEL_DOOR; bloquea sin llave; step() devuelve level_completed;
  puertas opcionales en (4,7) y (7,0); get_grid() renderiza LEVEL_DOOR/OPTIONAL_DOOR
- brain/curriculum.py: record_episode() acepta level_completed; nivel 0 sube con 1 completion;
  episodes_without_progress; stagnation_active; anti-estancamiento (threshold=100 episodios)
- brain/trainer.py: _handle_powerup/hazard/special_door() ampliados con eventos 0.4.3;
  contadores ep_level_completed/ep_optional_rooms/ep_treasure_rooms/ep_training_rooms/ep_next_door_blocked;
  current_objective computado en get_status()
- brain/memory.py: frases autobiograficas para level_completed, puertas bloqueadas, salas opcionales
- brain/metrics.py: level_completed_count, next_level_door_attempts/successes/fails, optional_rooms
- main.py: run_episode devuelve level_completed; end_episode recibe level_completed;
  anti-estancamiento aumenta epsilon; titulo "BabyIA World 0.4.3"
- interface/status_view.py: muestra current_objective, episodes_without_progress, level_completions
- interface/world_info_view.py: seccion de puertas de nivel con estado de bloqueo y evento
- interface/pygame_view.py: colores dorado/turquesa para LEVEL_DOOR/OPTIONAL_DOOR; log de eventos
- scripts/health_check.py: check_043_integrity() — 6 nuevas verificaciones
- 5 nuevos archivos de test; 476 tests pasando
- **fix 2**: Trainer.__init__ aplica level_factory(0) = mapa abierto; inv.use_key() eliminado de
  opened_door (la llave persiste para next_level_door); status actualizado tras end_episode;
  1 nuevo archivo de test; 495 tests pasando

### 0.4.4 — Inteligencia orientada a misiones, mejor diseno visual y senales de decision mas claras (actual)
- brain/mission.py (NUEVO): MissionState dataclass; MissionTracker.compute() calcula funcionalmente
  FIND_KEY / GO_TO_NEXT_LEVEL_DOOR / AVOID_DANGER / LEVEL_COMPLETED por prioridad funcional
- brain/decision_context.py (NUEVO): DecisionContext.build() sintetiza estado por paso en dict
  con distancias, amenazas, estado de inventario y objetivo de mision
- brain/mission_reward.py (NUEVO): MissionReward con APPROACH bonuses (0.3), MOVE_AWAY penalty (-0.2),
  MISSION_SWITCH_BONUS (1.0), OPTIONAL_DISTRACTION_PENALTY (-0.3); todo < REWARD_LEVEL_COMPLETED (120)
- interface/visual_theme.py (NUEVO): paleta de colores centralizada por mision, distancia y energia
- interface/mission_view.py (NUEVO): pestana "Mision" (tecla 6) — objetivo, razon, distancias,
  reward shaping, llave SI/NO, puerta cerca, episodios sin progreso
- interface/minimap_view.py (NUEVO): brujula textual de navegacion — direcciones a llave, puerta
  dorada, amenazas y powerups
- brain/trainer.py: importa y usa MissionTracker/DecisionContext/MissionReward en step();
  CRITICAL FIX: _full_obs() indices 14-15-16 ahora apuntan a puerta de progreso (7,7),
  no a puerta normal (3,6) — el DQN ya tiene senal correcta hacia el objetivo real;
  start_episode() inicializa contexto inicial para que get_status() sea valido antes del primer step
- brain/strategy.py: 4 nuevas estrategias de progreso de nivel
- brain/metrics.py: 5 nuevos campos de mision (reward, progress_steps, regression_steps,
  mission_switches, mission_goal_counts)
- interface/avatar_renderer.py: indicadores de objetivo funcional segun mision
  (punto K=FIND_KEY, anillo=GO_TO_NEXT_LEVEL_DOOR, borde rojo=AVOID_DANGER, aura=LEVEL_COMPLETED)
- interface/brain_view.py: seccion de objetivo funcional de mision con reward y pasos
- interface/layout.py: "Mision" como 6a pestana; TAB_COUNT=6
- interface/panel_renderer.py: ruta de vista a mission_view; tecla K_6→pestana 5
- main.py: pasa 5 campos de mision a metrics.record_episode()
- scripts/health_check.py: check_044_integrity() — 5 verificaciones especificas 0.4.4
- 6 nuevos archivos de test; 582 tests pasando
- NOTA: _full_obs() cambio en indices 14-16 — los pesos .pt guardados son incompatibles.
  Usar --reset-model para empezar desde cero con la nueva observacion.

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
