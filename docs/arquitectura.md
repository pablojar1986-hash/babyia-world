# Arquitectura de BabyIA World

## Separación de responsabilidades

```
BabyIA World/
│
├── config.py            ← Rutas, constantes, modos. Sin lógica.
├── main.py              ← Argparse, loop de episodios, orquestación.
|
|-- world/               <- Reglas fisicas del mundo. No sabe nada del cerebro.
|   |-- objects.py       <- Cell (incl. LEVEL_DOOR=12, OPTIONAL_DOOR=13 0.4.3); STATE_SIZE=40.
|   |-- rewards.py       <- REWARD_LEVEL_COMPLETED=120; REWARD_NEW_CELL=0.05 (0.4.3).
|   |-- level_doors.py   <- LevelDoor; LEVEL_DOOR_POSITIONS; attempt_level_door() (0.4.3).
|   |-- grid_world.py    <- Cuadricula 8x8; NEXT_LEVEL_DOOR bloqueante; level_completed (0.4.3).
|   |-- inventory.py     <- Inventario: energy, take_damage_by(), restore_energy() (0.4.2).
|   |-- interactions.py  <- Reglas causa-efecto puras (0.2).
|   |-- powerups.py      <- 8 powerups; apply_powerup_effect() ruteado a Inventory o BodyState (0.4.2).
|   |-- hazards.py       <- 8 hazards; apply_hazard_to_body() con bloqueo por estado corporal.
|   |-- doors.py         <- DoorRequirement.max_size; small_door max_size=1.2 (0.4.2).
|   |-- maze_generator.py <- BFS simple y BFS por etapas llave-puerta (0.2.2).
|   |-- level_factory.py  <- Laberintos por nivel: 0=vacio, 1=base, 4-6=llave-puerta (0.2.2).
|   |-- world_config.py   <- Tamanos de grid por nivel (8x8 -> 16x16); escala progresiva (0.4.5).
|   `-- path_diagnostics.py <- BFS: check_path_to_key_and_door(); accesibilidad de rutas (0.4.6b).
|
|-- brain/               <- Todo lo relacionado con el aprendizaje.
|   |-- baby_brain.py    <- DQN: red neuronal 40->128->64->5, Double DQN + PER, STATE_SIZE=40 (0.4.6).
|   |-- neural_debugger.py <- Inspeccion diagnostica: Q-values, activaciones por capa (0.4.1).
|   |-- survival.py      <- SurvivalEvaluator: risk_level, recommendation, diagnostico funcional (0.4.2).
|   |-- trainer.py       <- Orquesta mundo <-> cerebro <-> memoria; handlers powerup/hazard/door (0.4.2).
|   |-- body_state.py    <- BodyState: size, speed, shield, immunities; get_state_features() 8 features.
|   |-- causal_memory.py <- Relaciones causa-efecto con confianza; wired con eventos reales (0.4.2).
|   |-- utility_evaluator.py <- Utilidad heuristica; usa inventory.energy (fix 0.4.2).
|   |-- memory.py        <- Experiencias y autobiografia en JSON.
|   |-- emotions.py      <- Senales internas de control (no emociones reales).
|   |-- self_model.py    <- Modelo del yo: nivel, habilidades, objetivo.
|   |-- curriculum.py    <- Niveles 0-6; senaliza cambios de laberinto (0.2.1).
|   |-- metrics.py       <- Estadisticas persistentes + metricas por nivel y mundo (0.3).
|   |-- model_store.py   <- Versionado de pesos: latest, best, checkpoints.
|   |-- concepts.py      <- Memoria conceptual causa-efecto (0.2).
|   |-- strategy.py      <- Registro de estrategias emergentes (0.2).
|   |-- network_inspector.py <- Inspeccion de arquitectura DQN (0.2.1).
|   |-- world_memory.py  <- Historial de visitas a mundos (0.3).
|   |-- preferences.py   <- Preferencia simulada por mundos (0.3).
|   |-- home_drive.py    <- Impulso de regreso a casa (0.3).
|   |-- mission.py       <- MissionState; MissionTracker.compute() prioridad funcional (0.4.4).
|   |-- decision_context.py <- DecisionContext.build() — resumen por paso para UI/reward (0.4.4).
|   |-- mission_reward.py <- Reward shaping por mision; cap MAX_MISSION_REWARD_PER_EPISODE=8 (0.4.6b).
|   |-- visual_memory.py <- Objetos vistos; colisiones/hazards repetidos; stuck_zone_hint (0.4.5/0.4.6b).
|   `-- perception.py    <- Campo visual FOV real; SemanticMap; rangos desde body_state (0.4.5).
|
|-- worlds/              <- Sistema de mundos multiples (0.3). No sabe nada del cerebro.
|   |-- world_definition.py <- Dataclass: id, perfil, riesgo, nivel minimo, descripcion.
|   |-- portal.py           <- Portal: posicion en grid, destino, nivel requerido.
|   |-- reward_profiles.py  <- Perfiles de recompensa por tipo de mundo.
|   |-- world_registry.py   <- Registro de mundos y portales; fuente de verdad.
|   `-- world_manager.py    <- Detecta portales, gestiona transiciones, genera features DQN.
│
├── interface/           ← Solo visualización. Sin lógica de entrenamiento.
│   ├── pygame_view.py      ← Coordinador: ventana, grid, log inferior (0.4.1).
│   ├── layout.py           ← Constantes de geometria: areas, tamanios, pestanas (0.4.1).
│   ├── ui_components.py    ← Paleta de colores y primitivas de dibujo (0.4.1).
│   ├── panel_renderer.py   ← Sistema de 7 pestanas con scroll y navegacion (0.4.5).
│   ├── status_view.py      ← Pestana Estado: episodio, emociones, epsilon (0.4.1).
│   ├── world_info_view.py  ← Pestana Mundo: portales, retorno, historial (0.4.1).
│   ├── body_view.py        ← Pestana Cuerpo: size, speed, shield, energia, supervivencia (0.4.2).
│   ├── brain_view.py       ← Pestana Cerebro: Q-values, arquitectura DQN 40->128->64->5 (0.4.6).
│   ├── memory_view.py      ← Pestana Memoria: conceptos, relaciones causales, inventario (0.4.2).
│   ├── mission_view.py     ← Pestana Mision (tecla 6): objetivo, distancias, rutas BFS (0.4.6b).
│   ├── perception_view.py  ← Pestana Percepcion (tecla 7): FOV, objetos visibles (0.4.5).
│   ├── minimap_view.py     ← Brujula textual de navegacion hacia llave/puerta/amenazas (0.4.4).
│   ├── visual_theme.py     ← Paleta de colores centralizada por mision y estado (0.4.4).
│   ├── avatar_renderer.py  ← Avatar con indicadores de objetivo funcional por mision (0.4.4).
│   └── console_panel.py    ← Logs con Rich para la consola.
│
├── data/                ← Persistencia en JSON. No contiene código.
│   ├── memories.json
│   ├── autobiography.json
│   ├── training_stats.json
│   ├── concepts.json
│   ├── network_stats.json   (0.2.1)
│   ├── level_stats.json     (0.2.1)
│   └── skills.json
│
├── models/              ← Pesos del cerebro (.pt). No contiene código.
│   ├── babyia_latest.pt
│   ├── babyia_best.pt
│   └── checkpoints/
│
├── scripts/             ← Herramientas auxiliares (no son el proyecto principal).
│   └── health_check.py
│
├── docs/                ← Documentación interna.
├── tests/               ← Pruebas con pytest.
└── godot/               ← Reservado para fase gráfica futura.
```

## Principios de diseño

1. **world/ no importa de brain/**: el mundo no sabe cómo piensa BabyIA.
2. **interface/ no entrena**: la vista solo muestra, no calcula ni guarda.
3. **config.py centraliza rutas**: ningún path hardcodeado en el código.
4. **main.py orquesta**: todo el flujo de episodios vive en main.py.
5. **model_store gestiona el cerebro**: trainer.py ya no llama a brain.save().
6. **metrics.py es independiente**: puede usarse sin Pygame.
7. **interactions.py es puro**: devuelve dicts, no modifica estado directamente.
8. **trainer._full_obs() construye el estado de 40 features**: world (10) + inventory (8) + world_context (8) + body (8) + percepcion (6).
9. **level_factory es la fuente de verdad de laberintos**: trainer delega en ella al subir de nivel.
10. **network_inspector no toca el training loop**: solo lee arquitectura y escribe JSON.
11. **worlds/ no importa de brain/**: el sistema de mundos es independiente del aprendizaje.
12. **world_manager es una capa logica**: no modifica GridWorld; detecta portales por posicion.
13. **avatar_renderer es solo visual**: no contiene logica de entrenamiento ni estado del mundo.
14. **neural_debugger no tiene efectos secundarios**: usa forward hooks temporales; no modifica pesos, epsilon ni buffer.
15. **panel_renderer orquesta las pestanas**: delega en los *_view.py, aplica scroll con set_clip().
16. **layout.py es importable sin pygame**: define geometria pura (constantes); util en tests.
17. **SurvivalEvaluator es solo diagnostico**: no influye en el DQN ni en el replay buffer; informa paneles y get_status().
18. **Powerups/hazards/puertas son pasables**: el grid no bloquea movimiento; las interacciones ocurren despues del paso.
19. **apply_powerup_effect() enruta por tipo de efecto**: energy_restore -> Inventory; resto -> BodyState.
