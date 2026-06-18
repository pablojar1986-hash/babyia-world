# Continuacion de BabyIA World

Documento de trabajo para continuar desde la base 0.4.7 sin romper el proyecto.

## Estado de partida

- Version actual: `APP_VERSION=0.4.7`.
- Arquitectura actual: Double DQN + PER, `STATE_SIZE=40`, red `40 -> 128 -> 64 -> 5`.
- Vista actual: mundo completo escalable por defecto, con modo camara disponible.
- Regla central: BabyIA aprende localmente por refuerzo; no usa APIs externas,
  internet, LLMs ni modelos preentrenados.

## Antes de tocar codigo

1. Leer `AGENTS.md`, `README.md` y `docs/evolucion.md`.
2. Ejecutar:

```powershell
.\.venv\Scripts\python.exe scripts\health_check.py
.\.venv\Scripts\python.exe -m pytest tests -q
```

3. Revisar `git status --short`. Los JSON de `data/` pueden cambiar por
   entrenamiento; no commitearlos sin decidirlo explicitamente.

## Prioridad inmediata

La siguiente fase no deberia agregar sistemas grandes. Primero conviene medir
lo que ya existe:

- Tasa de completar nivel por cada nivel.
- Pasos promedio hasta recoger llave.
- Pasos promedio desde llave hasta puerta de progreso.
- Episodios sin progreso antes/despues del anti-estancamiento.
- Reward promedio separado por recompensa base, mision y mundo.
- Diferencia entre `train`, `watch` y `evaluate`.

## Evaluaciones recomendadas

Crear scripts pequenos solo si hacen falta y con tests:

- `evaluate --episodes N --seed S` para comparar semillas.
- Tabla por nivel: completions, reward, pasos, wall hits, hazards.
- Ablations controladas:
  - mission reward activado/desactivado,
  - percepcion en estado activada/desactivada,
  - PER activado/desactivado,
  - epsilon decay actual vs mas lento.

No mezclar ablations con features nuevas. Una variable por corrida.

## Fase 0.5.0: lenguaje simple

El lenguaje planificado debe ser salida explicativa por plantillas, no un nuevo
cerebro. Debe leer del `status`/contexto funcional ya existente.

Permitido:

- Frases sobre objetivo actual.
- Frases sobre objeto visible o recordado.
- Frases sobre eventos concretos: llave, puerta, hazard, powerup, nivel.
- Vocabulario acotado y testeable.

No permitido:

- LLM local o externo.
- APIs de IA.
- Generacion libre sin plantillas.
- Afirmar conciencia, deseos reales o voluntad propia.

Ubicacion sugerida:

- Logica pura en `brain/` si usa estado funcional.
- Render o texto de UI en `interface/` solo si recibe datos ya calculados.
- Tests en `tests/` para cada regla no trivial.

## Fase 0.6.0: Godot

Godot sigue reservado. Antes de implementarlo hay que resolver explicitamente
el canal Python <-> Godot, porque `AGENTS.md` prohibe `socket` en codigo de
produccion.

Opcion segura inicial:

- Exportar snapshots JSON desde Python.
- Godot lee snapshots como visualizador.
- Sin control remoto del entrenamiento.

Cualquier comunicacion en tiempo real requiere actualizar reglas, riesgos y
tests antes de programar.

## Deuda tecnica conocida

Archivos existentes que superan 300 lineas y no deben crecer mas:

- `main.py`
- `brain/trainer.py`
- `world/grid_world.py`
- `scripts/health_check.py`

Si se toca uno de ellos, preferir extracciones pequenas y testeadas. No crear
abstracciones "para despues".

## Checklist de cierre de cada cambio

- `scripts/health_check.py` sin errores.
- `pytest tests -q` sin fallos.
- `requirements.txt` sin dependencias no usadas.
- `README.md` actualizado si cambia arquitectura, comandos o modelos.
- `docs/evolucion.md` actualizado si cambia version o comportamiento.
- Sin commits automaticos por agentes.
