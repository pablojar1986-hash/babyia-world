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
- Activar anti-estancamiento si lleva 100 episodios sin completar nivel (0.4.3)
- Entrar a salas opcionales (tesoro, entrenamiento) sin requisito (0.4.3)
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
