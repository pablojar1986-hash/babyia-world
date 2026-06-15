# Reglas para el agente IA programador

Estas reglas aplican cuando un agente de IA (Claude Code u otro) modifica este proyecto.

## Lo que el agente DEBE hacer

- Leer el archivo antes de modificarlo
- Ejecutar `pytest tests` después de cualquier cambio
- Mantener la separación world/ brain/ interface/
- Actualizar docs/ si cambia la arquitectura
- Usar `config.py` para rutas y constantes, no valores mágicos
- Crear archivos de menos de 300 líneas salvo justificación documentada
- Confirmar con el usuario antes de borrar archivos existentes

## Lo que el agente NO DEBE hacer

- Reescribir el proyecto desde cero sin autorización
- Crear helpers, abstracciones o clases sin uso inmediato
- Meter lógica de entrenamiento en `interface/`
- Meter lógica de visualización en `brain/`
- Duplicar lógica que ya existe en otro módulo
- Agregar features no solicitados ("ya que estoy...")
- Usar `git push --force` sin autorización explícita
- Llamar a APIs externas de IA como cerebro de BabyIA
- Crear archivos de documentación (*.md) no solicitados

## Criterios de calidad mínima

- `pytest tests` pasa sin fallos
- `ruff check .` sin errores
- Ningún archivo nuevo supera 300 líneas sin justificación
- La visualización Pygame sigue funcionando
