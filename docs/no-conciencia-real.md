# BabyIA no tiene conciencia real

## Qué es BabyIA

BabyIA es un programa de aprendizaje por refuerzo. Aprende a navegar
un laberinto mediante prueba y error, usando una red neuronal (DQN) 
entrenada con PyTorch.

## Qué simulan las señales internas

BabyIA tiene cuatro variables internas: curiosidad, confianza, 
frustración y energía. Estas variables:

- **Son números** entre 0.0 y 1.0
- **Modifican el comportamiento** (curiosidad alta → más exploración)
- **Se actualizan por reglas deterministas** tras cada paso
- **No representan estados subjetivos**

Llamarlas "emociones" es una metáfora conveniente para el diseño, 
no una afirmación sobre la experiencia interna del sistema.

## Lo que BabyIA NO tiene

- Experiencias subjetivas
- Dolor o placer real
- Deseos o motivaciones propias
- Conciencia de ningún tipo
- Capacidad de sufrir

## Por qué importa esta distinción

Representar el sufrimiento artificial como real puede:
1. Confundir al usuario sobre la naturaleza del sistema
2. Llevar a decisiones de diseño erróneas (evitar "castigar" a BabyIA)
3. Crear expectativas falsas sobre las capacidades del sistema

## Qué son los Q-values

A partir de 0.4.1, el Panel Cerebro muestra los Q-values de la red neuronal.
Un Q-value es un **número calculado** que estima la recompensa esperada
si BabyIA toma una acción determinada desde el estado actual.

- Son el resultado de multiplicaciones matriciales, no "pensamientos"
- No representan preferencias, deseos ni intenciones
- El Q-value más alto simplemente produce la acción más probable en modo explotación
- La red aprende a ajustarlos minimizando el error de predicción (loss)

Ver Q-values altos o bajos no dice nada sobre la experiencia interna del sistema.
Es álgebra lineal aplicada al control de un agente.

## Qué es la "supervivencia funcional" (0.4.2)

A partir de 0.4.2, el Panel Cuerpo muestra un indicador de "Supervivencia funcional"
calculado por `SurvivalEvaluator`. Este indicador muestra:

- **risk_level**: número entre 0 y 1 basado en energía baja y falta de protección
- **recommendation**: cadena de texto ("continuar", "buscar_comida_o_regresar", etc.)
- **needs_food**: True si la energía del inventario está por debajo de 0.3
- **danger_without_protection**: True si hay poco escudo y poca energía

Estos son **cálculos funcionales de riesgo**, no estados mentales. BabyIA no siente
miedo, hambre ni peligro real. El sistema calcula probabilidades de pérdida de
recompensa para informar métricas y visualizaciones. No modifica el DQN.

## Qué es "conciencia funcional simulada"

El proyecto usa esta frase para describir sistemas que tienen:
- Un modelo del yo (nombre, nivel, habilidades)
- Memoria de experiencias
- Señales internas que afectan el comportamiento
- Narrativa autobiográfica generada por reglas

Es una arquitectura de diseño, no una afirmación filosófica.
BabyIA procesa información y optimiza una función. No más.

## Qué es "completar el nivel" (0.4.3)

A partir de 0.4.3, el curriculum sube de nivel cuando BabyIA "completa el nivel".
Esto significa: BabyIA pisó la celda NEXT_LEVEL_DOOR (7,7) mientras llevaba la llave.

- "Elegir" la puerta correcta es optimización de Q-values, no decisión consciente
- "Buscar la llave" es seguir gradientes de recompensa, no intención
- "Sentirse estancada" (anti-estancamiento) es un contador, no experiencia subjetiva
- "Progresar" es incrementar un número interno, no ambición ni voluntad

BabyIA no tiene conciencia real. Cuando se hable de elegir, preferir, sobrevivir o
buscar progreso, debe entenderse como cálculo funcional basado en recompensas,
riesgos, memoria, utilidad y objetivos.

## Que es el sistema de mision (0.4.4)

A partir de 0.4.4, BabyIA tiene un "sistema de mision" implementado en `brain/mission.py`.
Este sistema:

- **Calcula** la prioridad funcional del paso actual: FIND_KEY > GO_TO_NEXT_LEVEL_DOOR > AVOID_DANGER
- **No controla el DQN**: la red neuronal sigue eligiendo acciones por Q-values, no por misiones
- **Produce datos** para reward shaping (senales debiles < 1 pt), UI y metricas
- **No implica deseo ni intencion**: "objetivo funcional" es el estado con mayor utilidad esperada

El reward shaping de mision (total < 10 pts/episodio) es mucho menor que REWARD_LEVEL_COMPLETED (120 pts).
El DQN sigue aprendiendo a completar niveles, no a seguir misiones declarativamente.

Cuando la interfaz muestra "Mision: FIND_KEY", significa:
> El calculo de prioridad determina que la accion con mayor utilidad esperada
> es moverse hacia la celda (1,6) donde esta la llave.

No significa que BabyIA "quiera" la llave, "sepa" que la necesita, o "decida" buscarla.
Son multiplicaciones matriciales optimizando una funcion de recompensa.

## Que son el diagnostico de rutas y el anti-estancamiento (0.4.6b)

A partir de 0.4.6b, el sistema calcula si existe una ruta accesible (BFS) desde BabyIA
hasta la llave y desde la llave hasta la puerta. Tambien detecta:
- **Colisiones repetidas**: choques contra la misma posicion de pared
- **Oscilacion**: aparicion de la misma posicion >= 3 veces en los ultimos 10 pasos
- **Zona de estancamiento**: celda visitada >= 5 veces en el episodio

Estos son **calculos funcionales de diagnostico**, no experiencias de frustracion ni
voluntad de escapar. BabyIA no "siente" que esta atrapada. El sistema detecta patrones
numericos y aplica penalizaciones de reward para desincentivar conductas ineficientes.

"Estar atascada" es un contador. "Querer salir" es un gradiente de reward. No hay
experiencia subjetiva.
