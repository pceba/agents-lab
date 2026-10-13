# agents-lab

Mi laboratorio para aprender LLMs, agentes, harness engineering, MCP, evals y system design (oct 2026 – may 2027).

**Coste cero:** todo funciona con modelos locales vía [Ollama](https://ollama.com). Sin API keys ni tarjetas.

## Estructura

| Carpeta | Qué va aquí | Semana del plan |
| --- | --- | --- |
| `semana-01/` | Métricas de un LLM: tokens, latencia, structured outputs | 1 |
| `nanogpt/` | GPT propio entrenado en Colab o Kaggle (GPU gratis) | 2 |
| `harness/` | Mi bucle de agente desde cero: tools, contexto, permisos, sandbox | 3–4 |
| `mcp/` | Servidor MCP propio | 5 |
| `evals/` | Casos de eval, LLM-as-judge local, resultados | 6 |
| `notes/system-design/` | Un diseño de sistema LLM por semana | 7 → mayo |
| `notes/papers/` | Resumen de 5 líneas por paper o post leído | siempre |

## Puesta en marcha (Windows)

1. Instala Ollama desde https://ollama.com y ábrelo (se queda en la bandeja del sistema).
2. Descarga un modelo pequeño (unos 2 GB):
   ```
   ollama pull qwen2.5:3b
   ```
3. Ejecuta el script de la semana 1 (solo necesita Python 3.10+, sin `pip install`):
   ```
   python semana-01/llm_metrics.py
   ```

Si tu portátil va justo de RAM, prueba `qwen2.5:1.5b`. Si va sobrado, `qwen2.5:7b` o `llama3.1:8b` para comparar.

## Ejercicios de la semana 1

- [ ] Ejecuta el script con un modelo y guarda los resultados.
- [ ] Compara dos tamaños de modelo (p. ej. 1.5b vs 3b): ¿cuánto ganas en aciertos y cuánto pierdes en velocidad?
- [ ] Cambia `--runs` a 5 y fíjate en la diferencia entre la primera ejecución (carga del modelo) y las siguientes.
- [ ] Usa `--precio-in` y `--precio-out` con los precios públicos de un proveedor para estimar qué costaría la misma carga en la nube.
- [ ] Escribe 5 líneas en `notes/` sobre qué te ha sorprendido.
