# Diseño NN · <nombre del sistema>

**Fecha:**
**Enunciado (como en una entrevista):** p. ej. "Diseña un asistente que responda dudas de RR. HH. a 5.000 empleados con los documentos internos".

## 1. Requisitos
- Usuarios y volumen (peticiones/día, picos):
- Qué es una respuesta "buena" y cómo se mide:
- Latencia aceptable:
- Restricciones (privacidad, datos on-premise, presupuesto):

## 2. Arquitectura
Diagrama (boxes and arrows) + una frase por componente.

## 3. Decisiones clave y trade-offs
| Decisión | Opciones | Elección | Por qué |
| --- | --- | --- | --- |
| Modelo | grande / pequeño / routing | | |
| Conocimiento | contexto largo / RAG / fine-tuning | | |
| Orquestación | workflow fijo / agente / multi-agente | | |
| Herramientas | cuáles, con qué permisos | | |

## 4. Coste y latencia (números aproximados)
- Tokens por petición (entrada / salida):
- Coste por petición y al mes:
- Caching, batching, modelo pequeño para pasos fáciles:

## 5. Fiabilidad
- Evals antes de lanzar:
- Guardrails y escalado a humano:
- Observabilidad (trazas, métricas, alertas):

## 6. Qué haría distinto con 10x usuarios
