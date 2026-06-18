# Godot — fase futura

Esta carpeta esta reservada para una interfaz grafica avanzada de BabyIA World.
No forma parte de la version actual 0.4.7.

## Cuándo se usara

- Cuando el cerebro Python este estable y medido con evaluaciones reproducibles.
- Cuando la fase 0.5.0 de lenguaje por plantillas este cerrada.
- Cuando exista una decision explicita sobre el canal Python <-> Godot.

## Objetivo inicial

La primera integracion debe ser un visualizador, no un segundo motor de reglas:

- Python conserva el cerebro, el mundo, las recompensas y el entrenamiento.
- Godot renderiza snapshots exportados por Python.
- Godot no modifica pesos, replay buffer, rewards ni memoria.

## Canal permitido por defecto

Usar archivos JSON compartidos o snapshots exportados. Esto respeta la regla
actual de no usar `socket` en codigo de produccion.

Cualquier comunicacion en tiempo real debe aprobarse antes en `AGENTS.md`,
documentarse y tener tests especificos.

## Posible arquitectura

```text
Python                           Godot
------                           -----
main.py / trainer.py      ->     SnapshotReader.gd
data/*.json               ->     paneles de inspeccion
world/grid_world.py       ->     WorldView.gd
brain/status dict         ->     BabyIAView.gd
```

## No implementar todavia

- Sockets TCP.
- Control remoto del entrenamiento desde Godot.
- Nuevos mundos jugables.
- Voz, TTS o LLMs.
- Reglas de recompensa duplicadas en GDScript.
