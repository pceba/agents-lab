"""
Semana 1 · Medir un LLM por dentro: tokens, latencia y structured outputs.

Funciona 100 % en local con Ollama (gratis, sin API keys).
Solo usa la librería estándar de Python: no hay que instalar nada con pip.

Uso:
    python llm_metrics.py                      # las dos pruebas con el modelo por defecto
    python llm_metrics.py --model qwen3.5:9b   # otro modelo
    python llm_metrics.py --pensar si          # con modo de razonamiento (más lento)
    python llm_metrics.py --runs 5             # más repeticiones para medias más fiables
    python llm_metrics.py --solo texto         # solo la prueba de texto libre
    python llm_metrics.py --solo json          # solo la prueba de structured outputs

Qué mide:
    - Tokens de entrada (prompt) y de salida (respuesta)
    - Tiempo hasta el primer token (TTFT): lo que el usuario percibe como "tarda en empezar"
    - Latencia total y velocidad de generación (tokens/segundo)
    - Si la salida estructurada cumple el JSON schema pedido
    - Coste equivalente opcional: con --precio-in / --precio-out (USD por millón de tokens)
      puedes estimar cuánto costaría la misma carga en un proveedor de pago. En local es 0.
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path

HOST_POR_DEFECTO = "http://localhost:11434"
MODELO_POR_DEFECTO = "qwen3.5:4b"

PROMPT_TEXTO = (
    "Explica en 5 frases, para alguien de negocio, qué es la ventana de contexto "
    "de un LLM y por qué importa al diseñar un agente."
)

# Caso de consultoría: extraer datos estructurados de un texto libre.
TEXTO_EMPRESA = (
    "Lácteos del Norte S.L. es una cooperativa asturiana fundada en 1987. "
    "En 2025 facturó 142 millones de euros, un 6 % más que el año anterior, "
    "con 410 empleados. Su director general, Marta Iglesias, quiere entrar en "
    "bebidas vegetales, pero le preocupan la subida del precio de la leche, "
    "la presión de las marcas blancas y la falta de perfiles digitales."
)

SCHEMA_EMPRESA = {
    "type": "object",
    "properties": {
        "empresa": {"type": "string"},
        "sector": {"type": "string"},
        "anio_fundacion": {"type": "integer"},
        "facturacion_millones_eur": {"type": "number"},
        "crecimiento_pct": {"type": "number"},
        "empleados": {"type": "integer"},
        "riesgos": {"type": "array", "items": {"type": "string"}},
        "oportunidad": {"type": "string"},
    },
    "required": [
        "empresa",
        "sector",
        "anio_fundacion",
        "facturacion_millones_eur",
        "crecimiento_pct",
        "empleados",
        "riesgos",
        "oportunidad",
    ],
}

# Respuesta "correcta" para comprobar si el modelo acierta (tu primera mini-eval).
ESPERADO_EMPRESA = {
    "anio_fundacion": 1987,
    "facturacion_millones_eur": 142,
    "crecimiento_pct": 6,
    "empleados": 410,
}


# --------------------------------------------------------------------------- #
# Cliente mínimo de Ollama (API nativa /api/chat, con streaming)
# --------------------------------------------------------------------------- #

def comprobar_ollama(host: str, modelo: str) -> None:
    """Falla con un mensaje claro si Ollama no está arrancado o falta el modelo."""
    try:
        with urllib.request.urlopen(f"{host}/api/tags", timeout=5) as r:
            modelos = [m["name"] for m in json.load(r).get("models", [])]
    except (urllib.error.URLError, ConnectionError, TimeoutError):
        sys.exit(
            f"No encuentro Ollama en {host}.\n"
            "1) Instálalo desde https://ollama.com\n"
            "2) Arráncalo (en Windows se queda en la bandeja del sistema)\n"
            f"3) Descarga el modelo: ollama pull {modelo}"
        )
    if not any(m == modelo or m.split(":")[0] == modelo for m in modelos):
        sys.exit(
            f"El modelo '{modelo}' no está descargado. Ejecuta: ollama pull {modelo}\n"
            f"Modelos que tienes: {', '.join(modelos) or '(ninguno)'}"
        )


# Modo de razonamiento ("thinking"). Los modelos como qwen3.5 piensan antes de
# responder; en modelos pequeños ese razonamiento puede alargarse muchísimo o
# entrar en bucle. Por defecto lo apagamos: se cambia con --pensar.
PENSAR: bool | None = False

# Tope de tokens generados por respuesta: un seguro contra bucles infinitos.
MAX_TOKENS = 1024


def _abrir(host: str, cuerpo: dict):
    peticion = urllib.request.Request(
        f"{host}/api/chat",
        data=json.dumps(cuerpo).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    return urllib.request.urlopen(peticion, timeout=600)


def chat(host: str, modelo: str, mensajes: list[dict], formato: dict | None = None,
         temperatura: float = 0.0) -> dict:
    """Llama a /api/chat en streaming y devuelve texto + métricas."""
    cuerpo = {
        "model": modelo,
        "messages": mensajes,
        "stream": True,
        "options": {"temperature": temperatura, "num_predict": MAX_TOKENS},
    }
    if formato is not None:
        cuerpo["format"] = formato  # structured outputs: Ollama acepta un JSON schema
    if PENSAR is not None:
        cuerpo["think"] = PENSAR

    inicio = time.perf_counter()
    ttft = None
    partes: list[str] = []
    pensamiento: list[str] = []
    final: dict = {}

    try:
        respuesta = _abrir(host, cuerpo)
    except urllib.error.HTTPError as e:
        # Modelos sin modo de razonamiento pueden rechazar el campo "think": reintentamos sin él.
        if e.code == 400 and "think" in cuerpo:
            cuerpo.pop("think")
            inicio = time.perf_counter()
            respuesta = _abrir(host, cuerpo)
        else:
            raise

    with respuesta as r:
        for linea in r:
            if not linea.strip():
                continue
            trozo = json.loads(linea)
            mensaje = trozo.get("message", {})
            pensamiento.append(mensaje.get("thinking", ""))
            contenido = mensaje.get("content", "")
            if contenido and ttft is None:
                ttft = time.perf_counter() - inicio
            partes.append(contenido)
            if trozo.get("done"):
                final = trozo
                break

    total = time.perf_counter() - inicio
    tokens_out = final.get("eval_count", 0)
    eval_s = final.get("eval_duration", 0) / 1e9

    return {
        "texto": "".join(partes),
        "chars_pensamiento": len("".join(pensamiento)),
        "cortado_por_tope": final.get("done_reason") == "length",
        "tokens_in": final.get("prompt_eval_count", 0),
        "tokens_out": tokens_out,
        "ttft_s": ttft if ttft is not None else total,
        "latencia_s": total,
        "carga_modelo_s": final.get("load_duration", 0) / 1e9,
        "tokens_por_s": tokens_out / eval_s if eval_s > 0 else 0.0,
    }


# --------------------------------------------------------------------------- #
# Pruebas
# --------------------------------------------------------------------------- #

def prueba_texto(host: str, modelo: str) -> dict:
    r = chat(host, modelo, [{"role": "user", "content": PROMPT_TEXTO}], temperatura=0.7)
    r["prueba"] = "texto"
    return r


def prueba_json(host: str, modelo: str) -> dict:
    mensajes = [
        {
            "role": "system",
            "content": "Eres un analista de consultoría. Extrae los datos del texto. "
                       "Responde solo con JSON que cumpla el schema.",
        },
        {"role": "user", "content": TEXTO_EMPRESA},
    ]
    r = chat(host, modelo, mensajes, formato=SCHEMA_EMPRESA)
    r["prueba"] = "json"

    try:
        datos = json.loads(r["texto"])
        faltan = [k for k in SCHEMA_EMPRESA["required"] if k not in datos]
        aciertos = sum(
            1 for k, v in ESPERADO_EMPRESA.items()
            if isinstance(datos.get(k), (int, float)) and abs(datos[k] - v) < 1e-6
        )
        r["json_valido"] = not faltan
        r["campos_faltan"] = faltan
        r["aciertos"] = f"{aciertos}/{len(ESPERADO_EMPRESA)}"
    except json.JSONDecodeError:
        r["json_valido"] = False
        r["campos_faltan"] = SCHEMA_EMPRESA["required"]
        r["aciertos"] = f"0/{len(ESPERADO_EMPRESA)}"
    return r


# --------------------------------------------------------------------------- #
# Informe
# --------------------------------------------------------------------------- #

def coste_equivalente(r: dict, precio_in: float, precio_out: float) -> float:
    return (r["tokens_in"] * precio_in + r["tokens_out"] * precio_out) / 1_000_000


def resumen(resultados: list[dict], precio_in: float, precio_out: float) -> None:
    for prueba in ("texto", "json"):
        filas = [r for r in resultados if r["prueba"] == prueba]
        if not filas:
            continue
        # La primera ejecución incluye la carga del modelo en memoria: se reporta aparte.
        calientes = filas[1:] or filas
        med = lambda k: statistics.median(r[k] for r in calientes)  # noqa: E731

        print(f"\n=== Prueba: {prueba} · {len(filas)} ejecuciones ===")
        print(f"Tokens entrada (mediana) : {med('tokens_in'):.0f}")
        print(f"Tokens salida  (mediana) : {med('tokens_out'):.0f}")
        print(f"TTFT           (mediana) : {med('ttft_s'):.2f} s")
        print(f"Latencia total (mediana) : {med('latencia_s'):.2f} s")
        print(f"Velocidad      (mediana) : {med('tokens_por_s'):.1f} tokens/s")
        print(f"Carga del modelo (1.ª)   : {filas[0]['carga_modelo_s']:.2f} s")
        print(f"Pensamiento (mediana)    : {med('chars_pensamiento'):.0f} caracteres")
        cortadas = sum(r["cortado_por_tope"] for r in filas)
        if cortadas:
            print(f"Cortadas por el tope     : {cortadas}/{len(filas)} (subir --max-tokens o apagar --pensar)")
        print("Coste real en local      : 0,00 USD")
        if precio_in or precio_out:
            c = statistics.median(coste_equivalente(r, precio_in, precio_out) for r in calientes)
            print(f"Coste equivalente/llamada: {c:.6f} USD (con tus precios de referencia)")
        if prueba == "json":
            validos = sum(r["json_valido"] for r in filas)
            print(f"JSON válido              : {validos}/{len(filas)}")
            print(f"Aciertos numéricos       : {', '.join(r['aciertos'] for r in filas)}")

    ultima_json = next((r for r in reversed(resultados) if r["prueba"] == "json"), None)
    if ultima_json:
        print("\nÚltima salida estructurada:")
        print(ultima_json["texto"])


def main() -> None:
    p = argparse.ArgumentParser(description="Mide tokens, latencia y structured outputs de un LLM local.")
    p.add_argument("--model", default=MODELO_POR_DEFECTO)
    p.add_argument("--host", default=HOST_POR_DEFECTO)
    p.add_argument("--runs", type=int, default=3)
    p.add_argument("--solo", choices=["texto", "json"])
    p.add_argument("--precio-in", type=float, default=0.0, help="USD por millón de tokens de entrada (referencia)")
    p.add_argument("--precio-out", type=float, default=0.0, help="USD por millón de tokens de salida (referencia)")
    p.add_argument("--pensar", choices=["no", "si", "defecto"], default="no",
                   help="Modo de razonamiento del modelo (por defecto apagado)")
    p.add_argument("--max-tokens", type=int, default=1024, help="Tope de tokens por respuesta")
    a = p.parse_args()

    global PENSAR, MAX_TOKENS
    PENSAR = {"no": False, "si": True, "defecto": None}[a.pensar]
    MAX_TOKENS = a.max_tokens

    comprobar_ollama(a.host, a.model)
    pruebas = [prueba_texto, prueba_json]
    if a.solo:
        pruebas = [prueba_texto] if a.solo == "texto" else [prueba_json]

    resultados = []
    for prueba in pruebas:
        for i in range(a.runs):
            print(f"{prueba.__name__} · ejecución {i + 1}/{a.runs}...", flush=True)
            r = prueba(a.host, a.model)
            r.update({"modelo": a.model, "ejecucion": i + 1})
            resultados.append(r)

    resumen(resultados, a.precio_in, a.precio_out)

    carpeta = Path(__file__).parent / "resultados"
    carpeta.mkdir(exist_ok=True)
    fichero = carpeta / f"metricas-{a.model.replace(':', '_')}-{datetime.now():%Y%m%d-%H%M%S}.jsonl"
    with fichero.open("w", encoding="utf-8") as f:
        for r in resultados:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"\nResultados guardados en {fichero}")


if __name__ == "__main__":
    main()
