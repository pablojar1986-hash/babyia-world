# BabyIA World 0.2.1

Una IA que nace desde cero, aprende por experiencia y evoluciona por etapas.

> **0.2.1 agrega observabilidad de red neuronal y laberintos progresivos por nivel.**
> BabyIA todavia no tiene lenguaje avanzado ni conciencia real.
> Los conceptos descubiertos son relaciones estadisticas aprendidas por experiencia.

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
|   |-- baby_brain.py       <- DQN con PyTorch (STATE_SIZE=18)
|   |-- trainer.py          <- Orquesta mundo <-> cerebro <-> memoria
|   |-- memory.py           <- Memorias episodicas y autobiografia
|   |-- emotions.py         <- Senales internas de control
|   |-- self_model.py       <- Modelo del yo (nivel, habilidades)
|   |-- curriculum.py       <- Niveles 0-6; senaliza cambios de laberinto (0.2.1)
|   |-- metrics.py          <- Estadisticas persistentes + por nivel (0.2.1)
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
|-- tests/                  <- 110 tests con pytest
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

## Que queda para 0.3

- Multiples objetivos por episodio
- Relaciones mas complejas entre objetos
- Texto generado simple basado en conceptos

Ver: [docs/evolucion.md](docs/evolucion.md)
