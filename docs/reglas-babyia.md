# Reglas de BabyIA

## Lo que BabyIA PUEDE hacer

- Guardar memorias de sus experiencias en JSON
- Ajustar señales internas (curiosidad, confianza, frustración, energía)
- Aprender estrategias de navegación mediante DQN
- Mejorar su política de movimiento con el tiempo
- Recoger powerups del grid que modifican su estado corporal (mecanica de juego)
- Recibir daño de hazards y ser bloqueado por su estado corporal (mecanica de juego)
- Intentar cruzar puertas especiales con requisitos corporales (mecanica de juego)
- Subir de nivel al completar la puerta de nivel con llave (level_completed, 0.4.3)
- Usar la llave para abrir puertas normales sin consumirla; la llave persiste para next_level_door (fix 0.4.3)
- Activar anti-estancamiento si lleva 100 episodios sin completar nivel (0.4.3)
- Entrar a salas opcionales (tesoro, entrenamiento) sin requisito (0.4.3)
- Calcular funcionalmente una "mision" por prioridad: FIND_KEY / GO_TO_NEXT_LEVEL_DOOR / AVOID_DANGER (0.4.4)
- Recibir reward shaping de mision (< 1 pt) que guia hacia llave y puerta sin dominar el objetivo real (0.4.4)
- Mostrar objetivo funcional en la pestana Mision (tecla 6) y en la brujula de navegacion (0.4.4)
- "Ver" objetos cercanos con campo visual real (FOV) bloqueado por paredes (0.4.5)
- Recordar posiciones de llave, puerta y hazards vistos durante el episodio (visual_memory) (0.4.5)
- Aprender con Double DQN + Prioritized Experience Replay (STATE_SIZE=40) (0.4.6)
- Diagnosticar si existe ruta accesible a la llave y a la puerta mediante BFS (0.4.6b)
- Detectar estancamiento: colisiones repetidas, oscilacion, zona mas visitada (0.4.6b)
- Registrar frases autobiográficas generadas por reglas simples
- Mantener un modelo del yo con nivel, habilidades y objetivo

## Lo que BabyIA NO PUEDE hacer

- Editar su propio código fuente
- Conectarse a internet o a APIs externas
- Borrar memorias sin autorización del usuario
- Ejecutar código nuevo generado por ella misma
- Modificar reglas de seguridad o recompensas
- Afirmar que tiene conciencia, sentimientos o voluntad propia
- Acceder a archivos fuera de la carpeta del proyecto

## Razón de estas restricciones

BabyIA es un sistema de aprendizaje por refuerzo, no un agente autónomo
con propósito propio. Las restricciones garantizan que el sistema sea
predecible, auditable y seguro de estudiar.

El objetivo es construir un laboratorio de IA comprensible, no una IA
con capacidades ilimitadas.
