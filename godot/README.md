# Godot — Fase futura

Esta carpeta está reservada para la interfaz gráfica avanzada de BabyIA World.

## Cuándo se usará

- Cuando el cerebro de BabyIA esté estable (Nivel 3 superado)
- Cuando el sistema de memoria y conceptos esté consolidado
- Cuando BabyIA demuestre conducta consistente en múltiples episodios

## Qué se construirá aquí

- Mundo 2D o 2.5D con objetos interactivos (llaves, puertas, NPCs)
- Animaciones de BabyIA con estados visuales
- Sistema de lenguaje visual (burbujas de pensamiento)
- Comunicación en tiempo real entre Python (cerebro) y Godot (cuerpo)

## Arquitectura planeada

```
Python (cerebro)          Godot (cuerpo)
──────────────────        ──────────────────
trainer.py          ←→   BabyIA.gd
brain/baby_brain.py       World.gd
data/*.json         ←→   MemoryReader.gd
```

**Canal de comunicación:** sockets TCP o archivos JSON compartidos con polling.

## BabyIA 0.2 (siguiente versión Python)

Antes de Godot, se añadirán en Python:
- Objetos interactivos (llaves, puertas)
- Sistema de lenguaje simple (frases generadas)
- Memoria episódica más rica
- Múltiples metas en el mismo episodio
