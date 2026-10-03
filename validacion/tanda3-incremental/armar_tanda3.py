"""
Arma la Tanda 3 despues de correr run_validacion_tanda3.js. Son dos pasos y el
segundo lee SOLO lo que el primero dejo en disco:

  datos         Extrae de n8n las ejecuciones posteriores a la tanda 2 (exec > 157)
                y las une con el plan: por cada cliente, sus sesiones en orden
                cronologico tienen que coincidir una a una con el plan (valor de
                carrito) y el contador que viajo en el payload tiene que ser 0, 1, 2...
                Esa es la prueba de que el incremento lo hizo el backend.
                Escribe validacion/datos-crudos-tanda3-55-sesiones.csv (seudonimizada)
                y validacion/_privado/tanda3-IDENTIFICABLE.csv.

  instrumentos  Lee validacion/datos-crudos-tanda3-55-sesiones.csv, la vuelve a
                verificar contra el plan y genera en validacion/:
                  - dos planillas ciegas de experto (H2), A y B, cada una con su
                    orden (semillas 20260912 y 20260919) y su propia clave
                  - rubricas de los evaluadores A, B y C (H3), semilla 20260913
                Mismas columnas que los instrumentos de la Ronda 2.

Uso:  python armar_tanda3.py [datos|instrumentos] [--desde 158]     (sin paso: los dos)
"""
import csv
import json
import os
import random
import sys
from collections import defaultdict

from extraer_n8n import COLUMNAS, extraer, seudonimizar

AQUI = os.path.dirname(os.path.abspath(__file__))
VALIDACION = os.path.dirname(AQUI)
PRIVADO = os.path.join(VALIDACION, "_privado")
TABLA = os.path.join(VALIDACION, "datos-crudos-tanda3-55-sesiones.csv")

SEMILLA_H2 = 20260912
# B: primera semilla desde 20260914 sin ninguna posicion en comun con A ni con las rubricas
SEMILLAS_EXPERTOS = {"A": 20260912, "B": 20260919}
SEMILLA_H3 = 20260913

# Nombres de producto normalizados, tal como figuran en las planillas de la Ronda 2
NOMBRES = {
    8: "Cable USB-C 2m", 2: "Mouse Pad XL", 6: "Webcam 1080p", 3: "Auriculares Bluetooth Pro",
    1: "Teclado Mecanico RGB", 7: "Headset Gamer 7.1", 5: "SSD 1TB NVMe", 4: "Monitor 27 pulgadas Full HD",
}

CRITERIOS = ["Relevancia (1-5)", "Precision factual (1-5)", "Persuasion (1-5)",
             "Uso de contexto (1-5)", "Claridad (1-5)"]


class ErrorDeIntegridad(Exception):
    pass


def productos_de(items):
    return ", ".join(f"{q}x {NOMBRES[pid]}" for pid, q in items)


def unir_con_plan(filas, plan):
    """Asigna a cada fila su sesion del plan y verifica la secuencia del contador."""
    por_cliente = defaultdict(list)
    for f in filas:
        por_cliente[int(f["Customer ID"])].append(f)
    plan_cliente = defaultdict(list)
    for s in plan:
        plan_cliente[s["u"]].append(s)

    errores, unidas = [], []
    for u in sorted(plan_cliente):
        esperadas = sorted(plan_cliente[u], key=lambda s: s["ciclo"])
        reales = sorted(por_cliente.get(u, []), key=lambda f: f["Timestamp"])
        if len(reales) != len(esperadas):
            errores.append(f"cliente {u}: {len(reales)} ejecuciones, el plan tiene {len(esperadas)}")
            continue
        for f, s in zip(reales, esperadas):
            if int(float(f["Cart Value"])) != s["cv"]:
                errores.append(f"{s['id']}: carrito {f['Cart Value']}, el plan dice {s['cv']}")
            if int(f["Abandonos Previos"]) != s["ab_esperado"]:
                errores.append(f"{s['id']}: contador {f['Abandonos Previos']}, "
                               f"la secuencia pide {s['ab_esperado']}")
            if not f["Escenario"].startswith("exec-") and f["Escenario"] != s["id"]:
                errores.append(f"{s['id']}: etiqueta {f['Escenario']} no coincide con el plan")
            unidas.append({**f, "Escenario": s["id"]})
    extra = sorted(set(por_cliente) - set(plan_cliente))
    if extra:
        errores.append(f"clientes fuera del plan: {extra}")
    if errores:
        raise ErrorDeIntegridad("; ".join(errores))
    orden = {s["id"]: i for i, s in enumerate(plan)}
    return sorted(unidas, key=lambda f: orden[f["Escenario"]])


def _mezclar(filas, semilla):
    filas = list(filas)
    random.Random(semilla).shuffle(filas)
    return filas


def planilla_experto(filas, plan, semilla=SEMILLA_H2):
    items = {s["id"]: s["items"] for s in plan}
    ciega, clave = [], []
    for i, f in enumerate(_mezclar(filas, semilla), 1):
        sid = f"S-{i:02d}"
        ciega.append({
            "Sesion": sid,
            "Valor del carrito (ARS)": f["Cart Value"],
            "Etapa alcanzada": f["Cart Stage"],
            "Abandonos previos del cliente": f["Abandonos Previos"],
            "Productos en el carrito": productos_de(items[f["Escenario"]]),
            "PRIORIDAD ASIGNADA (Alta/Media/Baja)": "",
        })
        clave.append({
            "Sesion": sid, "Escenario": f["Escenario"], "Cart Value": f["Cart Value"],
            "Abandonos Previos": f["Abandonos Previos"], "Puntuacion algoritmo": f["Puntuacion"],
            "Prioridad algoritmo": f["Scoring"],
        })
    return ciega, clave


def planillas_expertos(filas, plan, semillas=SEMILLAS_EXPERTOS):
    """Una planilla ciega y una clave por experto, cada una con su propio orden."""
    return {e: planilla_experto(filas, plan, semilla) for e, semilla in semillas.items()}


def rubricas_evaluadores(filas, plan, semilla=SEMILLA_H3):
    """Las filas llegan de la tabla seudonimizada (leer_tabla)."""
    items = {s["id"]: s["items"] for s in plan}
    rubrica, clave = [], []
    for i, f in enumerate(_mezclar(filas, semilla), 1):
        mid = f"M-{i:02d}"
        rubrica.append({
            "Mensaje": mid,
            "Valor del carrito (ARS)": f["Cart Value"],
            "Productos en el carrito": productos_de(items[f["Escenario"]]),
            "Mensaje generado": f["Mensaje IA"],
            **{c: "" for c in CRITERIOS},
            "Observaciones": "",
        })
        clave.append({
            "Mensaje": mid, "Escenario": f["Escenario"], "Prioridad": f["Scoring"],
            "Canal": f["Canal"], "Cart Value": f["Cart Value"], "Latencia (ms)": f["Latencia (ms)"],
        })
    return {e: [dict(r) for r in rubrica] for e in "ABC"}, clave


def escribir_tabla(filas, ruta):
    _escribir(filas, ruta, COLUMNAS)


def leer_tabla(ruta, plan):
    """Lee la tabla seudonimizada y la vuelve a verificar contra el plan."""
    with open(ruta, encoding="utf-8") as f:
        filas = list(csv.DictReader(f))
    if len(filas) != len(plan):
        raise ErrorDeIntegridad(f"la tabla tiene {len(filas)} filas, el plan tiene {len(plan)}")
    por_id = {s["id"]: s for s in plan}
    if {f["Escenario"] for f in filas} != set(por_id):
        raise ErrorDeIntegridad("los escenarios de la tabla no coinciden con los del plan")
    errores = []
    for f in filas:
        s = por_id[f["Escenario"]]
        n = int(f["Customer ID"])
        if n != s["u"] or int(float(f["Cart Value"])) != s["cv"]:
            errores.append(f"{s['id']}: cuenta o carrito distinto al plan")
        if int(f["Abandonos Previos"]) != s["ab_esperado"]:
            errores.append(f"{s['id']}: contador {f['Abandonos Previos']}, la secuencia pide {s['ab_esperado']}")
        if f["Nombre"] != f"Cliente {n:02d}" or f["Email"] != f"cliente{n:02d}@ejemplo.test":
            errores.append(f"{s['id']}: fila sin seudonimizar")
    if errores:
        raise ErrorDeIntegridad("; ".join(errores))
    orden = {s["id"]: i for i, s in enumerate(plan)}
    return sorted(filas, key=lambda f: orden[f["Escenario"]])


def _escribir(filas, ruta, columnas=None):
    with open(ruta, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=columnas or list(filas[0].keys()),
                           extrasaction="ignore", lineterminator="\n")
        w.writeheader()
        w.writerows(filas)


def _cargar_plan():
    return json.load(open(os.path.join(AQUI, "plan-tanda3.json"), encoding="utf-8"))["sesiones"]


def paso_datos(desde):
    plan = _cargar_plan()
    filas, avisos = extraer(desde, 10 ** 9)
    for a in avisos:
        print("AVISO:", a)
    unidas = unir_con_plan(filas, plan)
    execs = sorted(f["_exec"] for f in unidas)
    print(f"cruce con el plan OK: {len(unidas)} sesiones (exec {execs[0]}..{execs[-1]}), "
          f"contador 0..k en las 10 cuentas")

    distintas = [f["Escenario"] for f, s in zip(unidas, plan) if f["Scoring"] != s["prioridad_esperada"]]
    if distintas:
        print(f"AVISO: el scoring de n8n difiere de la regla esperada en {distintas}")

    escribir_tabla(unidas, os.path.join(PRIVADO, "tanda3-IDENTIFICABLE.csv"))
    escribir_tabla([seudonimizar(f) for f in unidas], TABLA)
    print(f"tabla -> {TABLA}")


def paso_instrumentos():
    plan = _cargar_plan()
    tabla = leer_tabla(TABLA, plan)
    print(f"tabla leida y verificada contra el plan: {len(tabla)} filas")

    for e, (ciega, clave) in planillas_expertos(tabla, plan).items():
        _escribir(ciega, os.path.join(VALIDACION, f"T3-H2-experto-{e}-planilla-ciega.csv"))
        _escribir(clave, os.path.join(VALIDACION, f"T3-H2-experto-{e}-clave-NO-MOSTRAR.csv"))

    rubricas, clave = rubricas_evaluadores(tabla, plan)
    for e, r in rubricas.items():
        _escribir(r, os.path.join(VALIDACION, f"T3-H3-rubrica-evaluador-{e}.csv"))
    _escribir(clave, os.path.join(VALIDACION, "T3-H3-clave-NO-MOSTRAR.csv"))
    print(f"instrumentos T3-* -> {VALIDACION}")


if __name__ == "__main__":
    args = sys.argv[1:]
    desde = int(args[args.index("--desde") + 1]) if "--desde" in args else 158
    if "instrumentos" not in args:
        paso_datos(desde)
    if "datos" not in args:
        paso_instrumentos()
