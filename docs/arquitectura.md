# Arquitectura de BabyIA World

## Separación de responsabilidades

```
BabyIA World/
│
├── config.py            ← Rutas, constantes, modos. Sin lógica.
├── main.py              ← Argparse, loop de episodios, orquestación.
|
|-- world/               <- Reglas fisicas del mundo. No sabe nada del cerebro.
|   |-- objects.py       <- Enumeraciones: Cell, Action, STATE_SIZE=18.
|   |-- rewards.py       <- Calculo de recompensas base + objetos (0.2).
|   |-- grid_world.py    <- Cuadricula 8x8, objetos, step(has_key), set_walls (0.2.1).
|   |-- inventory.py     <- Inventario de BabyIA por episodio (0.2).
|   |-- interactions.py  <- Reglas causa-efecto puras (0.2).
|   |-- maze_generator.py <- BFS simple y BFS por etapas llave-puerta (0.2.2).
|   `-- level_factory.py  <- Laberintos por nivel: 0=vacio, 1=base, 4-6=llave-puerta (0.2.2).
|
|-- brain/               <- Todo lo relacionado con el aprendizaje.
|   |-- baby_brain.py    <- DQN: red neuronal 18->128->64->5, replay buffer.
|   |-- trainer.py       <- Orquesta mundo <-> cerebro <-> memoria; _full_obs.
|   |-- memory.py        <- Experiencias y autobiografia en JSON.
|   |-- emotions.py      <- Senales internas de control (no emociones reales).
|   |-- self_model.py    <- Modelo del yo: nivel, habilidades, objetivo.
|   |-- curriculum.py    <- Niveles 0-6; senaliza cambios de laberinto (0.2.1).
|   |-- metrics.py       <- Estadisticas persistentes + metricas por nivel (0.2.1).
|   |-- model_store.py   <- Versionado de pesos: latest, best, checkpoints.
|   |-- concepts.py      <- Memoria conceptual causa-efecto (0.2).
|   |-- strategy.py      <- Registro de estrategias emergentes (0.2).
|   `-- network_inspector.py <- Inspeccion de arquitectura DQN (0.2.1).
│
├── interface/           ← Solo visualización. Sin lógica de entrenamiento.
│   ├── pygame_view.py   ← Ventana gráfica: cuadrícula + panel lateral.
│   └── console_panel.py ← Logs con Rich para la consola.
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
8. **trainer._full_obs() construye el estado de 18 features**: world (10) + inventory (8).
9. **level_factory es la fuente de verdad de laberintos**: trainer delega en ella al subir de nivel.
10. **network_inspector no toca el training loop**: solo lee arquitectura y escribe JSON.
