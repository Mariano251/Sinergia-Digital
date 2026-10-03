"""Tests del armado de la Tanda 3. Correr con: python -m pytest -q"""
import copy
import csv
import json
import os

import pytest

from armar_tanda3 import (unir_con_plan, productos_de, planilla_experto, planillas_expertos,
                          rubricas_evaluadores, SEMILLA_H3,
                          escribir_tabla, leer_tabla, ErrorDeIntegridad)
from extraer_n8n import seudonimizar

AQUI = os.path.dirname(os.path.abspath(__file__))
VALIDACION = os.path.dirname(AQUI)
PLAN = json.load(open(os.path.join(AQUI, "plan-tanda3.json"), encoding="utf-8"))["sesiones"]


# Las planillas de la Ronda 2 que se usan como referencia de formato viven en
# validacion/historico/ desde que se ordenaron las rondas cerradas.
HISTORICO = os.path.join(VALIDACION, "historico")


def _cabecera(nombre):
    with open(os.path.join(HISTORICO, nombre), encoding="utf-8") as f:
        return next(csv.reader(f))


def filas_simuladas(plan=PLAN):
    """Filas como las devolveria extraer_n8n para una corrida perfecta (modo job)."""
    filas = []
    for s in plan:
        filas.append({
            "Timestamp": f"2026-09-12T10:{s['ciclo']:02d}:{s['u']:02d}.000Z",
            "Customer ID": str(s["u"]), "Nombre": f"Nombre{s['u']} Apellido",
            "Email": f"real{s['u']}@mail.com", "Cart Value": str(s["cv"]),
            "Scoring": s["prioridad_esperada"],
            "Canal": "Telegram" if s["prioridad_esperada"] == "ALTA" else "Email",
            "Status": "Enviado", "Conversión Proxy": "Pendiente",
            "Checkout URL": "http://localhost:5173/checkout",
            "Puntuacion": str(s["puntuacion_esperada"]), "Cart Stage": "cart",
            "Abandonos Previos": str(s["ab_esperado"]),
            "Mensaje IA": f"Hola Nombre{s['u']}, mensaje de {s['id']}",
            "Latencia (ms)": "3000", "Escenario": f"exec-{1000 + len(filas)}",
            "_productos": "", "_exec": 1000 + len(filas),
        })
    return filas


def tabla_simulada():
    return [seudonimizar(f) for f in unir_con_plan(filas_simuladas(), PLAN)]


# ── cruce con el plan ────────────────────────────────────────────────────────

def test_corrida_perfecta_asigna_el_escenario_del_plan():
    filas = unir_con_plan(filas_simuladas(), PLAN)
    assert len(filas) == 55
    assert {f["Escenario"] for f in filas} == {s["id"] for s in PLAN}
    f = next(x for x in filas if x["Escenario"] == "I-03-2")
    assert f["Abandonos Previos"] == "2" and f["Customer ID"] == "3"


def test_el_orden_por_cliente_sale_del_timestamp_no_del_orden_de_entrada():
    filas = filas_simuladas()
    filas.reverse()
    assert {f["Escenario"] for f in unir_con_plan(filas, PLAN)} == {s["id"] for s in PLAN}


def test_contador_que_no_coincide_con_la_secuencia_es_error():
    filas = filas_simuladas()
    next(f for f in filas if f["Customer ID"] == "4" and f["Abandonos Previos"] == "2")["Abandonos Previos"] = "3"
    with pytest.raises(ErrorDeIntegridad, match="contador"):
        unir_con_plan(filas, PLAN)


def test_valor_de_carrito_distinto_al_plan_es_error():
    filas = filas_simuladas()
    filas[0]["Cart Value"] = "1"
    with pytest.raises(ErrorDeIntegridad, match="carrito"):
        unir_con_plan(filas, PLAN)


def test_sesion_faltante_es_error():
    with pytest.raises(ErrorDeIntegridad, match="cliente 7"):
        unir_con_plan([f for f in filas_simuladas() if f["Escenario"] != "exec-1016"], PLAN)


def test_ejecucion_duplicada_es_error():
    filas = filas_simuladas()
    filas.append(copy.deepcopy(filas[3]))
    with pytest.raises(ErrorDeIntegridad):
        unir_con_plan(filas, PLAN)


def test_etiqueta_manual_que_no_coincide_con_el_plan_es_error():
    filas = filas_simuladas()
    filas[0]["Escenario"] = "I-09-9"
    with pytest.raises(ErrorDeIntegridad, match="etiqueta"):
        unir_con_plan(filas, PLAN)


# ── productos ────────────────────────────────────────────────────────────────

def test_productos_con_los_nombres_de_las_planillas_anteriores():
    assert productos_de([[3, 1], [6, 1]]) == "1x Auriculares Bluetooth Pro, 1x Webcam 1080p"
    assert productos_de([[5, 1], [1, 1], [2, 1]]) == "1x SSD 1TB NVMe, 1x Teclado Mecanico RGB, 1x Mouse Pad XL"
    assert productos_de([[2, 2]]) == "2x Mouse Pad XL"


def test_productos_reproducen_la_planilla_del_experto_2():
    from generar_plan import COMPOSICION
    with open(os.path.join(HISTORICO, "R2-H2-experto2-planilla-ciega.csv"), encoding="utf-8") as f:
        for r in csv.DictReader(f):
            assert productos_de(COMPOSICION[int(r["Valor del carrito (ARS)"])]) == r["Productos en el carrito"]


# ── planilla ciega del experto (H2) ──────────────────────────────────────────

def test_planilla_experto_misma_estructura_que_la_ronda_2_y_sin_fuga():
    filas = tabla_simulada()
    ciega, clave = planilla_experto(filas, PLAN, semilla=1)
    assert list(ciega[0].keys()) == _cabecera("R2-H2-experto2-planilla-ciega.csv")
    assert list(clave[0].keys()) == _cabecera("R2-H2-clave-NO-MOSTRAR.csv")
    assert [r["Sesion"] for r in ciega] == [f"S-{i:02d}" for i in range(1, 56)]
    assert all(r["PRIORIDAD ASIGNADA (Alta/Media/Baja)"] == "" for r in ciega)
    texto = json.dumps(ciega)
    for fuga in ("ALTA", "MEDIA", "BAJA", "Telegram", "I-0", "I-1"):
        assert fuga not in texto


def test_planilla_experto_clave_une_cada_sesion_con_su_escenario():
    filas = tabla_simulada()
    ciega, clave = planilla_experto(filas, PLAN, semilla=1)
    por_id = {f["Escenario"]: f for f in filas}
    for c, k in zip(ciega, clave):
        assert c["Sesion"] == k["Sesion"]
        f = por_id[k["Escenario"]]
        assert c["Valor del carrito (ARS)"] == f["Cart Value"] == k["Cart Value"]
        assert c["Abandonos previos del cliente"] == f["Abandonos Previos"] == k["Abandonos Previos"]
        assert k["Prioridad algoritmo"] == f["Scoring"]


def test_planilla_experto_orden_aleatorio_y_reproducible():
    filas = tabla_simulada()
    a = planilla_experto(filas, PLAN, semilla=1)[1]
    b = planilla_experto(filas, PLAN, semilla=1)[1]
    c = planilla_experto(filas, PLAN, semilla=2)[1]
    assert a == b and a != c
    assert [k["Escenario"] for k in a] != [s["id"] for s in PLAN]


# ── rubricas de los evaluadores (H3) ─────────────────────────────────────────

def test_rubricas_misma_estructura_que_la_ronda_2_y_mismo_orden_para_los_tres():
    filas = tabla_simulada()
    rubricas, clave = rubricas_evaluadores(filas, PLAN, semilla=1)
    assert set(rubricas) == {"A", "B", "C"}
    assert list(rubricas["A"][0].keys()) == _cabecera("R2-H3-rubrica-evaluador-A.csv")
    assert list(clave[0].keys()) == _cabecera("R2-H3-clave-NO-MOSTRAR.csv")
    assert rubricas["A"] == rubricas["B"] == rubricas["C"]
    assert [r["Mensaje"] for r in rubricas["A"]] == [f"M-{i:02d}" for i in range(1, 56)]
    criterios = [k for k in rubricas["A"][0] if "(1-5)" in k] + ["Observaciones"]
    assert all(r[k] == "" for r in rubricas["A"] for k in criterios)


def test_rubricas_seudonimizadas_y_sin_prioridad_ni_canal():
    filas = tabla_simulada()
    rubricas, clave = rubricas_evaluadores(filas, PLAN, semilla=1)
    texto = json.dumps(rubricas["A"])
    assert "Nombre" not in texto and "real" not in texto
    assert "Cliente 03" in texto
    for fuga in ("ALTA", "MEDIA", "BAJA", "Telegram"):
        assert fuga not in texto
    por_id = {f["Escenario"]: f for f in filas}
    for r, k in zip(rubricas["A"], clave):
        assert r["Mensaje"] == k["Mensaje"]
        assert k["Prioridad"] == por_id[k["Escenario"]]["Scoring"]
        assert k["Escenario"] in r["Mensaje generado"]  # el mensaje simulado lleva su id


def test_rubricas_y_planilla_experto_no_comparten_orden():
    filas = tabla_simulada()
    _, clave_h2 = planilla_experto(filas, PLAN, semilla=20260912)
    _, clave_h3 = rubricas_evaluadores(filas, PLAN, semilla=20260913)
    assert [k["Escenario"] for k in clave_h2] != [k["Escenario"] for k in clave_h3]


# ── tabla en disco: las planillas salen del archivo guardado ─────────────────

def test_tabla_guardada_y_releida_da_las_mismas_planillas(tmp_path):
    ruta = tmp_path / "datos-crudos-tanda3-55-sesiones.csv"
    escribir_tabla(tabla_simulada(), ruta)
    releida = leer_tabla(ruta, PLAN)
    assert planilla_experto(releida, PLAN) == planilla_experto(tabla_simulada(), PLAN)
    assert rubricas_evaluadores(releida, PLAN) == rubricas_evaluadores(tabla_simulada(), PLAN)


def test_tabla_guardada_tiene_las_16_columnas_de_la_ronda_2(tmp_path):
    ruta = tmp_path / "t.csv"
    escribir_tabla(tabla_simulada(), ruta)
    with open(ruta, encoding="utf-8") as f:
        assert next(csv.reader(f)) == _cabecera("datos-crudos-ronda2-55-sesiones.csv")


def test_leer_tabla_rechaza_una_tabla_que_no_coincide_con_el_plan(tmp_path):
    tabla = tabla_simulada()
    tabla[5]["Abandonos Previos"] = "4"
    ruta = tmp_path / "t.csv"
    escribir_tabla(tabla, ruta)
    with pytest.raises(ErrorDeIntegridad, match="contador"):
        leer_tabla(ruta, PLAN)


def test_leer_tabla_rechaza_una_tabla_incompleta(tmp_path):
    ruta = tmp_path / "t.csv"
    escribir_tabla(tabla_simulada()[:54], ruta)
    with pytest.raises(ErrorDeIntegridad, match="54"):
        leer_tabla(ruta, PLAN)


def test_leer_tabla_rechaza_una_tabla_sin_seudonimizar(tmp_path):
    ruta = tmp_path / "t.csv"
    escribir_tabla(unir_con_plan(filas_simuladas(), PLAN), ruta)
    with pytest.raises(ErrorDeIntegridad, match="seudonim"):
        leer_tabla(ruta, PLAN)


# ── dos expertos (H2) ────────────────────────────────────────────────────────

def test_dos_planillas_de_experto_con_su_propia_clave():
    tabla = tabla_simulada()
    planillas = planillas_expertos(tabla, PLAN)
    assert set(planillas) == {"A", "B"}
    por_id = {f["Escenario"]: f for f in tabla}
    for ciega, clave in planillas.values():
        assert list(ciega[0].keys()) == _cabecera("R2-H2-experto2-planilla-ciega.csv")
        assert sorted(k["Escenario"] for k in clave) == sorted(por_id)
        for c, k in zip(ciega, clave):
            assert c["Sesion"] == k["Sesion"]
            assert c["Valor del carrito (ARS)"] == por_id[k["Escenario"]]["Cart Value"]


def test_los_dos_expertos_no_comparten_ninguna_posicion():
    (_, clave_a), (_, clave_b) = planillas_expertos(tabla_simulada(), PLAN).values()
    iguales = [a["Sesion"] for a, b in zip(clave_a, clave_b) if a["Escenario"] == b["Escenario"]]
    assert iguales == []


def test_ninguna_planilla_de_experto_repite_el_orden_de_las_rubricas():
    tabla = tabla_simulada()
    _, clave_h3 = rubricas_evaluadores(tabla, PLAN, semilla=SEMILLA_H3)
    for _, clave in planillas_expertos(tabla, PLAN).values():
        assert [k["Escenario"] for k in clave] != [k["Escenario"] for k in clave_h3]


def _fila(nombre, mensaje, n=5):
    return {"Customer ID": str(n), "Nombre": nombre, "Email": "x@y.com", "Mensaje IA": mensaje}


def test_seudonimizar_reemplaza_el_nombre_aunque_el_modelo_le_agregue_tilde():
    # Caso real de la tanda 3: el modelo escribio el nombre con tilde y en la base
    # figura sin tilde. Los nombres de estas pruebas son ficticios.
    out = seudonimizar(_fila("Martin Ramirez", "**Asunto:** Martín, tus Auriculares\n\nHola Martín,"))
    assert out["Mensaje IA"] == "**Asunto:** Cliente 05, tus Auriculares\n\nHola Cliente 05,"


def test_seudonimizar_reemplaza_nombre_completo_con_tilde_y_en_mayusculas():
    out = seudonimizar(_fila("Adrian Paredes", "Hola ADRIÁN PAREDES y adrián", n=8))
    assert out["Mensaje IA"] == "Hola Cliente 08 y Cliente 08"


def test_seudonimizar_no_toca_palabras_que_contienen_el_nombre():
    out = seudonimizar(_fila("Mora Firme", "Hola Mora, conexion firme y moravia", n=9))
    assert out["Mensaje IA"] == "Hola Cliente 09, conexion firme y moravia"
