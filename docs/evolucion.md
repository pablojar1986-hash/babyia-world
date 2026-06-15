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

### 0.3 — Lenguaje simple
- Frases generadas por plantillas más ricas
- Vocabulario básico de navegación y objetos
- BabyIA puede "describir" lo que ve
- data/skills.json activo con habilidades rastreadas

### 0.4 — Interfaz Godot
- Comunicación Python ↔ Godot vía sockets o JSON
- Visualización 2D/2.5D del mundo
- Animaciones de BabyIA según estado interno
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
