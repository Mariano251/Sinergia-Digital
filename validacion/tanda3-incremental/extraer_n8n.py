"""
Extrae las sesiones de validacion desde la base SQLite de n8n (~/.n8n/database.sqlite).

La fuente es execution_data, no la planilla de auditoria: la escritura concurrente
del job de deteccion puede perder filas en Google Sheets sin emitir error.

De cada ejecucion se toma la fila que el nodo "Google Sheets - Auditoria" armo
(mismas 16 columnas de la planilla) y el estado real de execution_entity.

Uso:
    python extraer_n8n.py <exec_desde> <exec_hasta> <salida_identificable.csv> <salida_seudonimizada.csv>
"""
import csv
import json
import os
import re
import sqlite3
import sys

DB = os.path.expanduser("~/.n8n/database.sqlite")

COLUMNAS = ["Timestamp", "Customer ID", "Nombre", "Email", "Cart Value", "Scoring",
            "Canal", "Status", "Conversión Proxy", "Checkout URL", "Puntuacion",
            "Cart Stage", "Abandonos Previos", "Mensaje IA", "Latencia (ms)", "Escenario"]


def parse_flatted(texto):
    """n8n guarda runData en formato 'flatted': un array donde los strings
    numericos son referencias a otras posiciones del mismo array."""
    arr = json.loads(texto)
    memo = {}

    def rev(v):
        return get(int(v)) if isinstance(v, str) and v.isdigit() else v

    def get(i):
        if i in memo:
            return memo[i]
        v = arr[i]
        if isinstance(v, list):
            out = []
            memo[i] = out
            out.extend(rev(x) for x in v)
        elif isinstance(v, dict):
            out = {}
            memo[i] = out
            for k, x in v.items():
                out[k] = rev(x)
        else:
            out = v
            memo[i] = out
        return out

    return get(0)


def _nodo(run_data, prefijo):
    for nombre, runs in run_data.items():
        if nombre.startswith(prefijo):
            return runs[0]
    return None


def _salida(run):
    for rama in (run or {}).get("data", {}).get("main", []) or []:
        if rama:
            return rama[0]["json"]
    return None


def fila_de_ejecucion(exec_id, status, data_texto):
    """Devuelve (fila, motivo). fila es None si la ejecucion no produjo auditoria."""
    d = parse_flatted(data_texto)
    rd = d["resultData"]["runData"]
    fila = _salida(_nodo(rd, "Google Sheets - Auditor"))
    if fila is None:
        return None, f"exec {exec_id}: sin fila de auditoria (status={status})"
    # las claves pueden venir con la 'o' acentuada; se normaliza al nombre publicado
    fila = {("Conversión Proxy" if k.startswith("Conversi") else k): v for k, v in fila.items()}
    salida = {c: fila.get(c, "") for c in COLUMNAS}
    # productos tal como los recibio n8n en el payload del backend
    body = (_salida(_nodo(rd, "Webhook - Carrito Abandonado")) or {}).get("body", {})
    items = (body.get("cart") or {}).get("items") or []
    salida["_productos"] = ", ".join(f"{i['quantity']}x {i['name']}" for i in items)
    if not salida["Escenario"]:
        salida["Escenario"] = f"exec-{exec_id}"
    return salida, None


def extraer(desde, hasta, db=DB):
    con = sqlite3.connect(db)
    q = """SELECT e.id, e.status, d.data FROM execution_entity e
           JOIN execution_data d ON d.executionId = e.id
           WHERE e.id BETWEEN ? AND ? ORDER BY e.id"""
    filas, avisos = [], []
    for exec_id, status, data in con.execute(q, (desde, hasta)):
        fila, motivo = fila_de_ejecucion(exec_id, status, data)
        if fila is None:
            avisos.append(motivo)
            continue
        if status != "success":
            avisos.append(f"exec {exec_id}: status={status} con fila de auditoria, se excluye")
            continue
        fila["_exec"] = exec_id
        filas.append(fila)
    con.close()
    filas.sort(key=lambda r: r["Timestamp"])
    return filas, avisos


VOCALES = {"a": "aáàä", "e": "eéèë", "i": "iíìï", "o": "oóòö", "u": "uúùü"}


def _patron_nombre(texto):
    """Palabra completa, sin distinguir mayusculas ni tildes: el modelo escribe
    'Martín' aunque en la base el cliente figure como 'Martin'."""
    partes = []
    for c in texto:
        base = c.lower()
        if c.isspace():
            partes.append(r"\s+")
        elif base in VOCALES:
            partes.append(f"[{VOCALES[base]}]")
        else:
            partes.append(re.escape(c))
    return re.compile(r"\b" + "".join(partes) + r"\b", re.IGNORECASE)


def seudonimizar(fila):
    """Misma regla que la Ronda 2: nombre completo y luego nombre de pila -> 'Cliente NN'."""
    n = int(fila["Customer ID"])
    ps = f"Cliente {n:02d}"
    real = str(fila["Nombre"]).strip()
    out = dict(fila)
    msg = str(fila["Mensaje IA"])
    if real:
        msg = _patron_nombre(real).sub(ps, msg)
        msg = _patron_nombre(real.split()[0]).sub(ps, msg)
    out["Mensaje IA"] = msg
    out["Nombre"] = ps
    out["Email"] = f"cliente{n:02d}@ejemplo.test"
    return out


def escribir(filas, ruta):
    with open(ruta, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNAS, extrasaction="ignore")
        w.writeheader()
        w.writerows(filas)


if __name__ == "__main__":
    desde, hasta, ruta_priv, ruta_pub = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3], sys.argv[4]
    filas, avisos = extraer(desde, hasta)
    for a in avisos:
        print("AVISO:", a)
    escribir(filas, ruta_priv)
    escribir([seudonimizar(f) for f in filas], ruta_pub)
    print(f"{len(filas)} filas -> {ruta_pub} (identificable: {ruta_priv})")
