"""
Analisis de H1, H2 y H3 de la Tanda 3, con los mismos metodos que la Ronda 2
(ver estadistica.py y test_estadistica.py).

  H1  se calcula ya: sale de datos-crudos-tanda3-55-sesiones.csv y, si esta la base
      de n8n, del tiempo de cada nodo (generacion con IA y envio).
  H2  cuando vuelvan las planillas de los expertos:
        validacion/T3-H2-experto-A-planilla-completa.csv
        validacion/T3-H2-experto-B-planilla-completa.csv
      Alcanza con una; con las dos se agrega el acuerdo entre expertos.
  H3  cuando vuelvan las tres rubricas:
        validacion/T3-H3-rubrica-evaluador-{A,B,C}-completa.csv

Antes de calcular, cada planilla devuelta se compara con la que se entrego: mismas
sesiones, mismos datos, respuestas completas y dentro de la escala. Si algo no
cierra, se detiene y dice donde.

Salidas en validacion/: T3-ANEXO-E-*.csv y T3-ANEXO-E-informe.md
Uso:  python analisis_tanda3.py
"""
import csv
import glob
import io
import os
import sqlite3
import statistics as st
from collections import Counter
from contextlib import redirect_stdout

from armar_tanda3 import (ErrorDeIntegridad, CRITERIOS, VALIDACION, TABLA, leer_tabla, _cargar_plan,
                          _escribir)
from estadistica import (CATEGORIAS, resumen_latencias, matriz_confusion, kappa_cohen, landis,
                         icc2, descriptivos, interpretar_cci)

COL = "PRIORIDAD ASIGNADA (Alta/Media/Baja)"
UMBRAL_H1_S = 300
UMBRAL_H2 = 0.85
UMBRAL_H3 = 4.0
UMBRALES_VALOR = (60000, 140000)   # ALTA >= 70 pts y MEDIA >= 30 pts sobre $200.000
MARGEN_FRONTERA = 10000
AB_CASTIGO = 4
ORDEN_ANEXO_BIS = [("claridad", "Claridad (1-5)"), ("relevancia", "Relevancia (1-5)"),
                   ("precision", "Precision factual (1-5)"), ("uso_contexto", "Uso de contexto (1-5)"),
                   ("persuasion", "Persuasion (1-5)")]
EXEC_DESDE = 158
# Son los mismos expertos de la Ronda 2 (confirmado por el tesista): A = experto 2, B = experto 3
NUMERO_EXPERTO = {"A": "2", "B": "3"}


def nombre_experto(e):
    return f"{e} (experto {NUMERO_EXPERTO[e]})"
BARRA = "=" * 100


def ruta(nombre):
    return os.path.join(VALIDACION, nombre)


def leer_csv(p):
    with open(p, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def es_frontera_valor(cv):
    return any(abs(cv - u) <= MARGEN_FRONTERA for u in UMBRALES_VALOR)


def ordenar_cronologico(tabla):
    return sorted(tabla, key=lambda f: f["Timestamp"])


# ── validacion de lo devuelto ──────────────────────────────────────────────
def _mismos_datos(llena, entregada, id_col, respuestas):
    if len(llena) != len(entregada):
        raise ErrorDeIntegridad(f"tiene {len(llena)} filas, se entregaron {len(entregada)}")
    errores = []
    for f, g in zip(llena, entregada):
        alteradas = [c for c in g if c not in respuestas and f.get(c, "").strip() != g[c].strip()]
        if f.get(id_col) != g[id_col] or alteradas:
            errores.append(f"{g[id_col]}: datos alterados {alteradas or [id_col]}")
    return errores


def validar_planilla_experto(llena, entregada):
    """Devuelve {Sesion: ALTA|MEDIA|BAJA}."""
    errores = _mismos_datos(llena, entregada, "Sesion", {COL})
    out = {}
    for f in llena:
        v = f.get(COL, "").strip().upper()
        if not v:
            errores.append(f"{f['Sesion']}: sin respuesta")
        elif v not in CATEGORIAS:
            errores.append(f"{f['Sesion']}: valor {f[COL].strip()!r} fuera de Alta/Media/Baja")
        out[f["Sesion"]] = v
    if errores:
        raise ErrorDeIntegridad("; ".join(errores))
    return out


def validar_rubrica(llena, entregada):
    """Devuelve {Mensaje: {criterio: int}}."""
    errores = _mismos_datos(llena, entregada, "Mensaje", set(CRITERIOS) | {"Observaciones"})
    out = {}
    for f in llena:
        punt = {}
        for c in CRITERIOS:
            v = f.get(c, "").strip()
            if v not in {"1", "2", "3", "4", "5"}:
                errores.append(f"{f['Mensaje']}: {c} = {v!r}")
            else:
                punt[c] = int(v)
        out[f["Mensaje"]] = punt
    if errores:
        raise ErrorDeIntegridad("; ".join(errores))
    return out


def respuestas_por_escenario(por_sesion, clave):
    return {k["Escenario"]: por_sesion[k["Sesion"]] for k in clave}


def puntajes_por_escenario(por_mensaje, clave):
    return {k["Escenario"]: por_mensaje[k["Mensaje"]] for k in clave}


# ── H1 ─────────────────────────────────────────────────────────────────────
def analizar_h1(tabla, desglose=None):
    lat = {f["Escenario"]: float(f["Latencia (ms)"]) / 1000 for f in tabla}
    canales = sorted({f["Canal"] for f in tabla})
    r = {"general": resumen_latencias(list(lat.values()), UMBRAL_H1_S),
         "por_canal": {c: resumen_latencias([lat[f["Escenario"]] for f in tabla if f["Canal"] == c],
                                            UMBRAL_H1_S) for c in canales},
         "latencias": lat, "desglose": desglose or {}}
    atip = set(r["general"]["atipicos"])
    r["atipicos"] = [f for f in tabla if lat[f["Escenario"]] in atip]
    return r


def desglose_n8n(tabla, desde=EXEC_DESDE):
    """{escenario: {exec, estado, ia_s, envio_s, nodo_envio}} desde la base de n8n."""
    from extraer_n8n import DB, extraer, parse_flatted
    if not os.path.exists(DB):
        return None
    filas, _ = extraer(desde, 10 ** 9)
    # en n8n el Customer ID es numero; en la tabla leida del CSV, texto
    por_clave = {(str(f["Customer ID"]), f["Timestamp"]): f["_exec"] for f in filas}
    con = sqlite3.connect(DB)
    out = {}
    for f in tabla:
        ex = por_clave.get((f["Customer ID"], f["Timestamp"]))
        if ex is None:
            raise ErrorDeIntegridad(f"{f['Escenario']}: no se encontro su ejecucion en n8n")
        estado, data = con.execute("""SELECT e.status, d.data FROM execution_entity e
                                      JOIN execution_data d ON d.executionId = e.id WHERE e.id = ?""",
                                   (ex,)).fetchone()
        rd = parse_flatted(data)["resultData"]["runData"]
        ia = next(v[0]["executionTime"] for k, v in rd.items() if k.startswith("AI Agent"))
        envio = next((k, v[0]["executionTime"]) for k, v in rd.items()
                     if k.startswith("Telegram") or k.startswith("Gmail"))
        out[f["Escenario"]] = {"exec": ex, "estado": estado, "ia_s": ia / 1000,
                               "envio_s": envio[1] / 1000, "nodo_envio": envio[0]}
    con.close()
    return out


# ── H2 ─────────────────────────────────────────────────────────────────────
def _desagregar(tabla, resp, grupos):
    out = {}
    for nombre, criterio in grupos.items():
        g = {}
        for f in tabla:
            etiqueta = criterio(f)
            d = g.setdefault(etiqueta, {"n": 0, "coinciden": 0})
            d["n"] += 1
            d["coinciden"] += resp[f["Escenario"]] == f["Scoring"]
        out[nombre] = dict(sorted(g.items()))
    return out


GRUPOS_H2 = {
    "frontera de valor (+-$10.000 de $60.000 o $140.000)":
        lambda f: "frontera" if es_frontera_valor(int(float(f["Cart Value"]))) else "clara",
    "castigo por abandono (contador >= 4)":
        lambda f: "con castigo" if int(f["Abandonos Previos"]) >= AB_CASTIGO else "sin castigo",
    "nivel del contador": lambda f: f"contador {f['Abandonos Previos']}",
    "prioridad del algoritmo": lambda f: f["Scoring"],
}


def analizar_h2(tabla, respuestas):
    alg = {f["Escenario"]: f["Scoring"] for f in tabla}
    escs = sorted(alg)
    r = {"algoritmo": Counter(alg.values()), "vs_algoritmo": {}, "entre_expertos": None}
    for e, resp in respuestas.items():
        pares = [(alg[s], resp[s]) for s in escs]
        r["vs_algoritmo"][e] = {
            "distribucion": Counter(resp.values()),
            "matriz": matriz_confusion(pares), "kappa": kappa_cohen(pares),
            "desagregaciones": _desagregar(tabla, resp, GRUPOS_H2),
            "discordancias": [(f, resp[f["Escenario"]]) for f in tabla if resp[f["Escenario"]] != f["Scoring"]],
        }
    if len(respuestas) >= 2:
        (na, a), (nb, b) = list(respuestas.items())[:2]
        pares = [(a[s], b[s]) for s in escs]
        nivel = {"BAJA": 0, "MEDIA": 1, "ALTA": 2}
        consenso = [s for s in escs if a[s] == b[s]]
        r["entre_expertos"] = {
            "nombres": (na, nb), "matriz": matriz_confusion(pares), "kappa": kappa_cohen(pares),
            "direccion": {f"{na} mas alto": sum(nivel[a[s]] > nivel[b[s]] for s in escs),
                          f"{nb} mas alto": sum(nivel[b[s]] > nivel[a[s]] for s in escs)},
            "saltos_de_dos": sum(abs(nivel[a[s]] - nivel[b[s]]) == 2 for s in escs),
            "consenso_n": len(consenso),
            "algoritmo_en_consenso": sum(alg[s] == a[s] for s in consenso),
        }
    return r


# ── H3 ─────────────────────────────────────────────────────────────────────
def analizar_h3(tabla, puntajes):
    """puntajes: {evaluador: {escenario: {criterio: int}}}"""
    evs = list(puntajes)
    escs = [f["Escenario"] for f in tabla]
    prom = lambda d: sum(d[c] for c in CRITERIOS) / len(CRITERIOS)
    por_sesion = {}
    for s in escs:
        crit = {c: st.mean(puntajes[e][s][c] for e in evs) for c in CRITERIOS}
        por_sesion[s] = {**crit, "promedio": st.mean(crit.values())}
    matriz = [[prom(puntajes[e][s]) for e in evs] for s in escs]

    def media_de(filtro):
        sel = [s for s in escs if filtro(s)]
        return {"n": len(sel), "media": st.mean(por_sesion[s]["promedio"] for s in sel)}

    fila = {f["Escenario"]: f for f in tabla}
    return {
        "global": st.mean(v["promedio"] for v in por_sesion.values()),
        "por_criterio": {c: descriptivos([puntajes[e][s][c] for e in evs for s in escs]) for c in CRITERIOS},
        "por_criterio_sesion": {c: descriptivos([por_sesion[s][c] for s in escs]) for c in CRITERIOS},
        "por_evaluador": {e: st.mean(prom(puntajes[e][s]) for s in escs) for e in evs},
        "por_canal": {c: media_de(lambda s, c=c: fila[s]["Canal"] == c) for c in sorted({f["Canal"] for f in tabla})},
        "por_prioridad": {p: media_de(lambda s, p=p: fila[s]["Scoring"] == p) for p in CATEGORIAS},
        "por_contador": {k: media_de(lambda s, k=k: fila[s]["Abandonos Previos"] == k)
                         for k in sorted({f["Abandonos Previos"] for f in tabla})},
        "mensajes_4_o_mas": sum(1 for v in por_sesion.values() if v["promedio"] >= UMBRAL_H3),
        "por_sesion": por_sesion,
        "cci": icc2(matriz) if len(evs) >= 2 else None,
    }


# ── carga de lo devuelto ───────────────────────────────────────────────────
def _buscar_completa(patron):
    hallados = sorted(glob.glob(ruta(patron)))
    return hallados[0] if hallados else None


def cargar_expertos():
    resp, faltan = {}, []
    for e in ("A", "B"):
        p = _buscar_completa(f"T3-H2-experto-{e}-planilla-complet*.csv")
        if not p:
            faltan.append(f"T3-H2-experto-{e}-planilla-completa.csv")
            continue
        try:
            por_sesion = validar_planilla_experto(leer_csv(p), leer_csv(ruta(f"T3-H2-experto-{e}-planilla-ciega.csv")))
        except ErrorDeIntegridad as err:
            raise ErrorDeIntegridad(f"{os.path.basename(p)}: {err}")
        resp[e] = respuestas_por_escenario(por_sesion, leer_csv(ruta(f"T3-H2-experto-{e}-clave-NO-MOSTRAR.csv")))
    return resp, faltan


def cargar_evaluadores():
    punt, faltan = {}, []
    clave = leer_csv(ruta("T3-H3-clave-NO-MOSTRAR.csv"))
    for e in "ABC":
        p = _buscar_completa(f"T3-H3-rubrica-evaluador-{e}-complet*.csv")
        if not p:
            faltan.append(f"T3-H3-rubrica-evaluador-{e}-completa.csv")
            continue
        try:
            por_msj = validar_rubrica(leer_csv(p), leer_csv(ruta(f"T3-H3-rubrica-evaluador-{e}.csv")))
        except ErrorDeIntegridad as err:
            raise ErrorDeIntegridad(f"{os.path.basename(p)}: {err}")
        punt[e] = puntajes_por_escenario(por_msj, clave)
    return punt, faltan


# ── impresion ──────────────────────────────────────────────────────────────
def pct(a, b):
    return f"{a}/{b} = {100 * a / b:5.1f} %"


def imprimir_resumen(r, sangria="  "):
    print(f"{sangria}n                 : {r['n']:8d}")
    for k, nombre in [("min", "minimo"), ("q1", "Q1"), ("mediana", "mediana"), ("media", "media"),
                      ("q3", "Q3"), ("max", "maximo"), ("desvio", "desvio estandar")]:
        print(f"{sangria}{nombre:18s}: {r[k]:8.2f} s")
    print(f"{sangria}< {UMBRAL_H1_S} s           : {pct(r['bajo_umbral'], r['n'])}")


def imprimir_h1(r, n_de):
    g = r["general"]
    print(BARRA + "\nH1 - LATENCIA DETECCION -> ENVIO (n=%d, Tanda 3)\n" % g["n"] + BARRA)
    imprimir_resumen(g)
    print(f"\n  IQR = {g['iqr']:.2f} s | bigotes de Tukey: [{g['bigote_inf']:.2f} , {g['bigote_sup']:.2f}]")
    print(f"  atipicos por 1.5*IQR: {len(r['atipicos'])}")
    for f in sorted(r["atipicos"], key=lambda f: -r["latencias"][f["Escenario"]]):
        d = r["desglose"].get(f["Escenario"])
        extra = (f" | exec {d['exec']}: IA {d['ia_s']:.2f} s, envio {d['envio_s']:.2f} s ({d['nodo_envio']})"
                 if d else "")
        print(f"    N{n_de[f['Escenario']]} {f['Escenario']} {f['Canal']:8s} {r['latencias'][f['Escenario']]:.2f} s{extra}")
    print("\n  por canal:")
    for c, rc in r["por_canal"].items():
        print(f"    {c:9s} n={rc['n']:2d}  mediana {rc['mediana']:.2f} s  media {rc['media']:.2f} s  max {rc['max']:.2f} s")
    if r["desglose"]:
        d = r["desglose"].values()
        ia = [x["ia_s"] for x in d]
        print("\n  componentes (tiempo de nodo en n8n):")
        print(f"    generacion con IA   : mediana {st.median(ia):.2f} s  max {max(ia):.2f} s")
        for nodo in sorted({x["nodo_envio"] for x in d}):
            env = [x["envio_s"] for x in d if x["nodo_envio"] == nodo]
            print(f"    {nodo[:20]:20s}: mediana {st.median(env):.2f} s  max {max(env):.2f} s  (n={len(env)})")
        estados = Counter(x["estado"] for x in d)
        print(f"    estado de las ejecuciones: {dict(estados)}")
    print(f"\n  H1 (100 % bajo {UMBRAL_H1_S} s): {'SE CUMPLE' if g['bajo_umbral'] == g['n'] else 'NO SE CUMPLE'}")


def imprimir_matriz(m, fila, columna):
    print(f"\n  {'':10s}" + "".join(f"{c.title():>8s}" for c in CATEGORIAS) + f"{'total':>8s}   <- {columna}")
    for a in CATEGORIAS:
        print(f"  {a.title():10s}" + "".join(f"{m[a][b]:8d}" for b in CATEGORIAS) + f"{sum(m[a].values()):8d}")
    print(f"  {'total':10s}" + "".join(f"{sum(m[a][b] for a in CATEGORIAS):8d}" for b in CATEGORIAS)
          + f"{sum(sum(x.values()) for x in m.values()):8d}")
    print(f"  ^ {fila}")


def imprimir_h2(r, faltan):
    print(BARRA + "\nH2 - ALGORITMO vs EXPERTOS (Tanda 3)\n" + BARRA)
    if faltan:
        print("  PENDIENTE: faltan " + ", ".join(faltan))
    if not r:
        return
    print("  algoritmo: " + ", ".join(f"{c.title()} {r['algoritmo'][c]}" for c in CATEGORIAS))
    for e, x in r["vs_algoritmo"].items():
        k = x["kappa"]
        print(f"\n  --- ALGORITMO vs EXPERTO {nombre_experto(e)} ---")
        print(f"  experto {nombre_experto(e)}: " + ", ".join(f"{c.title()} {x['distribucion'][c]}" for c in CATEGORIAS))
        imprimir_matriz(x["matriz"], "ALGORITMO", f"EXPERTO {nombre_experto(e)}")
        print(f"\n  coincidencias        : {k['coincidencias']}/{k['n']}")
        print(f"  concordancia simple  : {100 * k['po']:.1f} %   (umbral H2: {100 * UMBRAL_H2:.0f} %)")
        print(f"  acuerdo esperado azar: {100 * k['pe']:.1f} %")
        print(f"  Kappa de Cohen       : {k['kappa']:.3f}   Landis y Koch (1977): {landis(k['kappa'])}")
        for nombre, grupos in x["desagregaciones"].items():
            print(f"  {nombre}:")
            for g, d in grupos.items():
                print(f"    {g:14s}: {pct(d['coinciden'], d['n'])}")
        print("  discordancias (escenario, carrito, contador, algoritmo -> experto):")
        for f, experto in x["discordancias"]:
            print(f"    {f['Escenario']}  ${int(float(f['Cart Value'])):>7,}  ab={f['Abandonos Previos']}  "
                  f"{f['Scoring'].title():5s} -> {experto.title()}".replace(",", "."))
    ee = r["entre_expertos"]
    if ee:
        na, nb = ee["nombres"]
        k = ee["kappa"]
        print(f"\n  --- EXPERTO {nombre_experto(na)} vs EXPERTO {nombre_experto(nb)} (fiabilidad inter-observador) ---")
        imprimir_matriz(ee["matriz"], f"EXPERTO {nombre_experto(na)}", f"EXPERTO {nombre_experto(nb)}")
        print(f"\n  coincidencias        : {pct(k['coincidencias'], k['n'])}")
        print(f"  Kappa de Cohen       : {k['kappa']:.3f}   ({landis(k['kappa'])})")
        print(f"  discordancias        : {ee['direccion']}, de dos escalones: {ee['saltos_de_dos']}")
        print(f"  algoritmo en las {ee['consenso_n']} sesiones con consenso de ambos: "
              f"{pct(ee['algoritmo_en_consenso'], ee['consenso_n'])}")


def imprimir_h3(r, faltan):
    print(BARRA + "\nH3 - CALIDAD DE LOS MENSAJES (Tanda 3)\n" + BARRA)
    if faltan:
        print("  PENDIENTE: faltan " + ", ".join(faltan))
    if not r:
        return
    n = len(r["por_sesion"])
    print(f"\n  promedio global: {r['global']:.2f} / 5,00   (umbral H3: {UMBRAL_H3:.1f})")
    print("\n  por criterio (evaluaciones individuales):")
    for c, d in r["por_criterio"].items():
        print(f"    {c:26s}: media {d['media']:.2f}  desvio {d['desvio_muestral']:.2f}  [{d['minimo']}-{d['maximo']}]  n={d['n']}")
    print("\n  por canal:")
    for c, d in r["por_canal"].items():
        print(f"    {c:9s} (n={d['n']:2d} mensajes): {d['media']:.2f}")
    print("\n  por prioridad del algoritmo:")
    for c, d in r["por_prioridad"].items():
        print(f"    {c.title():6s} (n={d['n']:2d}): {d['media']:.2f}")
    print("\n  por nivel del contador de abandonos:")
    for c, d in r["por_contador"].items():
        print(f"    contador {c} (n={d['n']:2d}): {d['media']:.2f}")
    print("\n  por evaluador (severidad):")
    for e, v in r["por_evaluador"].items():
        print(f"    Evaluador {e}: {v:.2f}")
    print(f"\n  mensajes con promedio >= 4,0: {pct(r['mensajes_4_o_mas'], n)}")
    c = r["cci"]
    if c and c["icc_k"] is None:
        print("\n  CCI: no definido (sin varianza entre mensajes o sin error residual)")
    elif c:
        print(f"\n  CCI(2,k) medidas promedio : {c['icc_k']:.3f}   IC95% [{c['ic_k'][0]:.3f} , {c['ic_k'][1]:.3f}]   "
              f"({interpretar_cci(c['icc_k'])}, Koo y Li 2016)")
        print(f"  CCI(2,1) medida individual: {c['icc_1']:.3f}   IC95% [{c['ic_1'][0]:.3f} , {c['ic_1'][1]:.3f}]")
        print(f"  (dos vias, efectos aleatorios, acuerdo absoluto | MSR={c['msr']:.4f} MSC={c['msc']:.4f} "
              f"MSE={c['mse']:.4f} gl={c['gl']:.1f})")
    print(f"\n  H3 (promedio global >= {UMBRAL_H3:.1f}): {'SE CUMPLE' if r['global'] >= UMBRAL_H3 else 'NO SE CUMPLE'}")


# ── anexos ─────────────────────────────────────────────────────────────────
def escribir_anexos(tabla, n_de, h1, h2r, resp, h3r):
    f2 = lambda x: f"{x:.2f}"
    filas = []
    for f in tabla:
        s = f["Escenario"]
        d = h1["desglose"].get(s, {})
        filas.append({
            "N": n_de[s], "escenario": s, "fecha": f["Timestamp"][:10],
            "id_anonimizado": f"U{int(f['Customer ID']):02d}", "valor_carrito": int(float(f["Cart Value"])),
            "etapa": f["Cart Stage"], "abandonos_previos": f["Abandonos Previos"],
            "prioridad_algoritmo": f["Scoring"].title(),
            **{f"prioridad_experto{NUMERO_EXPERTO[e]}": resp.get(e, {}).get(s, "").title() for e in "AB"},
            "latencia_seg": f2(h1["latencias"][s]),
            "rubrica_promedio": f2(h3r["por_sesion"][s]["promedio"]) if h3r else "",
            "canal": f["Canal"], "estado": d.get("estado", ""),
        })
    _escribir(filas, ruta("T3-ANEXO-E-55-sesiones.csv"))

    _escribir([{"N": n_de[f["Escenario"]], "escenario": f["Escenario"],
                "exec_id": h1["desglose"].get(f["Escenario"], {}).get("exec", ""), "canal": f["Canal"],
                "latencia_seg": f2(h1["latencias"][f["Escenario"]]),
                "ia_seg": f2(h1["desglose"][f["Escenario"]]["ia_s"]) if h1["desglose"] else "",
                "envio_seg": f2(h1["desglose"][f["Escenario"]]["envio_s"]) if h1["desglose"] else ""}
               for f in tabla], ruta("T3-ANEXO-E-H1-latencias.csv"))

    if h2r:
        _escribir([{"N": n_de[f["Escenario"]], "escenario": f["Escenario"],
                    "valor_carrito": int(float(f["Cart Value"])), "abandonos_previos": f["Abandonos Previos"],
                    "prioridad_algoritmo": f["Scoring"].title(),
                    **{f"prioridad_experto{NUMERO_EXPERTO[e]}": resp[e][f["Escenario"]].title() for e in resp},
                    **{f"experto{NUMERO_EXPERTO[e]}_coincide_algoritmo":
                       "SI" if resp[e][f["Escenario"]] == f["Scoring"] else "NO" for e in resp},
                    **({"experto2_coincide_experto3": "SI" if resp["A"][f["Escenario"]] == resp["B"][f["Escenario"]]
                        else "NO"} if len(resp) == 2 else {})}
                   for f in tabla], ruta("T3-ANEXO-E-H2-expertos.csv"))

    if h3r:
        _escribir([{"N": n_de[f["Escenario"]],
                    **{k: f2(h3r["por_sesion"][f["Escenario"]][c]) for k, c in ORDEN_ANEXO_BIS},
                    "promedio": f2(h3r["por_sesion"][f["Escenario"]]["promedio"])}
                   for f in tabla], ruta("T3-ANEXO-E-bis-H3-por-sesion.csv"))
        nombres = {c: c.replace(" (1-5)", "") for c in CRITERIOS}
        _escribir([{"criterio": nombres[c], "n": d["n"], "media": f2(d["media"]),
                    "desvio_poblacional": f2(d["desvio_poblacional"]), "desvio_muestral": f2(d["desvio_muestral"]),
                    "minimo": d["minimo"], "maximo": d["maximo"]}
                   for c, d in ((c, h3r["por_criterio"][c]) for _, c in ORDEN_ANEXO_BIS)],
                  ruta("T3-ANEXO-E-H3-tabla3-criterios.csv"))


def main():
    plan = _cargar_plan()
    tabla = ordenar_cronologico(leer_tabla(TABLA, plan))
    n_de = {f["Escenario"]: i for i, f in enumerate(tabla, 1)}

    desglose = desglose_n8n(tabla)
    if desglose is None:
        previo = ruta("T3-ANEXO-E-H1-latencias.csv")
        desglose = ({r["escenario"]: {"exec": r["exec_id"], "estado": "", "ia_s": float(r["ia_seg"]),
                                      "envio_s": float(r["envio_seg"]), "nodo_envio": r["canal"]}
                     for r in leer_csv(previo)} if os.path.exists(previo) else {})
    h1 = analizar_h1(tabla, desglose)

    resp, faltan_h2 = cargar_expertos()
    h2r = analizar_h2(tabla, resp) if resp else None

    # con rubricas parciales no se calcula: los promedios y el CCI necesitan a los tres
    punt, faltan_h3 = cargar_evaluadores()
    h3r = analizar_h3(tabla, punt) if len(punt) == 3 else None

    salida = io.StringIO()
    with redirect_stdout(salida):
        imprimir_h1(h1, n_de)
        print()
        imprimir_h2(h2r, faltan_h2)
        print()
        imprimir_h3(h3r, faltan_h3)
    texto = salida.getvalue()
    print(texto)

    escribir_anexos(tabla, n_de, h1, h2r, resp, h3r)
    with open(ruta("T3-ANEXO-E-informe.md"), "w", encoding="utf-8") as f:
        f.write("# Evidencia primaria - Tanda 3 (55 sesiones, contador incremental)\n\n")
        f.write(f"Ejecuciones de n8n desde la {EXEC_DESDE}. N sigue el orden cronologico de deteccion.\n")
        f.write("Salida literal de `tanda3-incremental/analisis_tanda3.py`:\n\n```\n" + texto + "```\n")
    print("anexos T3-ANEXO-E-* e informe escritos en", VALIDACION)


if __name__ == "__main__":
    main()
