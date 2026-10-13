# 2026-10-13 · Primeras mediciones con un LLM local

**Setup:** Ollama en Windows, portátil de 16 GB de RAM, 100% CPU (sin GPU), contexto de 4.096 tokens. Modelos: `qwen3.5:4b` y `qwen3.5:9b`.

## Qué he aprendido

1. **El razonamiento sin control puede no terminar.** Con el modo "thinking" activado, `qwen3.5:4b` estuvo más de 10 minutos pensando una pregunta de una frase. Con `--think=false` respondió en 30 s. Un harness necesita siempre un tope de tokens, timeouts y decidir cuándo dejar razonar al modelo.

2. **El prompt es la mayor palanca de latencia.** Mismo modelo, misma pregunta:

   | | Prompt vago | Prompt preciso |
   | --- | --- | --- |
   | Tokens generados | 223 | 26 |
   | Tiempo generando | 29,0 s | 4,5 s |
   | Respeta el formato | No | Sí |
   | Acierta | No | Sí (genérico) |

   El modelo no va más rápido: escribe menos. Menos tokens de salida = menos tiempo y menos coste.

3. **En CPU, leer contexto es caro.** Lee unos 23 tokens/s y genera unos 6 tokens/s. Un prompt de 3.000 tokens tardaría ~2 minutos solo en leerse. Para el harness: contexto corto y pocas llamadas.

4. **Arranque en frío.** Tras unos minutos sin uso, Ollama descarga el modelo y la siguiente llamada paga ~15 s de carga.

5. **"JSON válido" no mide al modelo.** Con un schema, Ollama restringe la generación y el JSON siempre sale bien formado. Lo que mide al modelo es si los valores son correctos: 4/4 aciertos, pero en un caso fácil (números literales en el texto). Un caso no es una eval.

## Resultados del script (`llm_metrics.py --runs 2`, qwen3.5:4b, sin razonamiento)

| Prueba | Tokens in | Tokens out | TTFT | Latencia | Velocidad | Calidad |
| --- | --- | --- | --- | --- | --- | --- |
| Texto | 44 | 172 | 2,5 s | 33,8 s | 5,5 tok/s | — |
| JSON | 141 | 138 | 2,3 s | 26,0 s | 5,8 tok/s | JSON 2/2, números 4/4 |

## Siguiente

- Caso de extracción difícil (cálculos, números en letra, dos empresas) y comparar 4b vs 9b.
- Convertirlo en una mini-eval de 10 casos.
