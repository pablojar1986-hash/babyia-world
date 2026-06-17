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

## Qué es "conciencia funcional simulada"

El proyecto usa esta frase para describir sistemas que tienen:
- Un modelo del yo (nombre, nivel, habilidades)
- Memoria de experiencias
- Señales internas que afectan el comportamiento
- Narrativa autobiográfica generada por reglas

Es una arquitectura de diseño, no una afirmación filosófica.
BabyIA procesa información y optimiza una función. No más.
