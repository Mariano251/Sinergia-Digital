import copy

import pytest

from armar_tanda3 import ErrorDeIntegridad, planilla_experto, rubricas_evaluadores, CRITERIOS
from analisis_tanda3 import (es_frontera_valor, validar_planilla_experto, validar_rubrica,
                             analizar_h1, analizar_h2, analizar_h3, respuestas_por_escenario,
                             puntajes_por_escenario, ordenar_cronologico)
from test_armar_tanda3 import tabla_simulada, PLAN

COL = "PRIORIDAD ASIGNADA (Alta/Media/Baja)"


def completar_experto(ciega, clave, criterio):
    """criterio(escenario_de_la_clave) -> 'Alta' | 'Media' | 'Baja'"""
    llena = copy.deepcopy(ciega)
    for f, k in zip(llena, clave):
        f[COL] = criterio(k)
    return llena


def completar_rubrica(rubrica, puntaje):
    llena = copy.deepcopy(rubrica)
    for f in llena:
        for c in CRITERIOS:
            f[c] = str(puntaje(f, c))
    return llena


# ── frontera ───────────────────────────────────────────────────────────────
@pytest.mark.parametrize("cv,esperado", [(50000, True), (60000, True), (70000, True), (49000, False),
                                         (71000, False), (130000, True), (150000, True),
                                         (120000, False), (200000, False)])
def test_frontera_de_valor_a_10000_de_un_umbral(cv, esperado):
    assert es_frontera_valor(cv) is esperado


# ── validacion de lo que devuelven expertos y evaluadores ──────────────────
def test_planilla_experto_valida_normaliza_mayusculas_y_espacios():
    ciega, clave = planilla_experto(tabla_simulada(), PLAN)
    llena = completar_experto(ciega, clave, lambda k: " alta" if k["Prioridad algoritmo"] == "ALTA" else "Media ")
    r = validar_planilla_experto(llena, ciega)
    assert set(r.values()) <= {"ALTA", "MEDIA"} and len(r) == 55


def test_planilla_experto_con_respuesta_vacia_es_error():
    ciega, clave = planilla_experto(tabla_simulada(), PLAN)
    llena = completar_experto(ciega, clave, lambda k: "Alta")
    llena[7][COL] = ""
    with pytest.raises(ErrorDeIntegridad, match="S-08"):
        validar_planilla_experto(llena, ciega)


def test_planilla_experto_con_valor_fuera_de_escala_es_error():
    ciega, clave = planilla_experto(tabla_simulada(), PLAN)
    llena = completar_experto(ciega, clave, lambda k: "Alta")
    llena[0][COL] = "Urgente"
    with pytest.raises(ErrorDeIntegridad, match="Urgente"):
        validar_planilla_experto(llena, ciega)


def test_planilla_experto_con_datos_de_la_sesion_alterados_es_error():
    ciega, clave = planilla_experto(tabla_simulada(), PLAN)
    llena = completar_experto(ciega, clave, lambda k: "Alta")
    llena[3]["Abandonos previos del cliente"] = "9"
    with pytest.raises(ErrorDeIntegridad, match="S-04"):
        validar_planilla_experto(llena, ciega)


def test_rubrica_fuera_de_1_a_5_o_vacia_es_error():
    rubricas, _ = rubricas_evaluadores(tabla_simulada(), PLAN)
    llena = completar_rubrica(rubricas["A"], lambda f, c: 5)
    llena[2]["Claridad (1-5)"] = "6"
    with pytest.raises(ErrorDeIntegridad, match="M-03"):
        validar_rubrica(llena, rubricas["A"])
    llena[2]["Claridad (1-5)"] = ""
    with pytest.raises(ErrorDeIntegridad, match="M-03"):
        validar_rubrica(llena, rubricas["A"])


def test_rubrica_con_mensaje_alterado_es_error():
    rubricas, _ = rubricas_evaluadores(tabla_simulada(), PLAN)
    llena = completar_rubrica(rubricas["A"], lambda f, c: 4)
    llena[10]["Mensaje generado"] = "otro texto"
    with pytest.raises(ErrorDeIntegridad, match="M-11"):
        validar_rubrica(llena, rubricas["A"])


# ── H1 ─────────────────────────────────────────────────────────────────────
def test_h1_orden_cronologico_y_desglose_por_canal():
    tabla = ordenar_cronologico(tabla_simulada())
    assert [f["Timestamp"] for f in tabla] == sorted(f["Timestamp"] for f in tabla)
    r = analizar_h1(tabla)
    assert r["general"]["n"] == 55
    assert r["por_canal"]["Telegram"]["n"] + r["por_canal"]["Email"]["n"] == 55


# ── H2 ─────────────────────────────────────────────────────────────────────
def test_h2_experto_identico_al_algoritmo_da_kappa_1_y_experto_distinto_lo_baja():
    tabla = tabla_simulada()
    ciega_a, clave_a = planilla_experto(tabla, PLAN, 20260912)
    ciega_b, clave_b = planilla_experto(tabla, PLAN, 20260919)
    a = completar_experto(ciega_a, clave_a, lambda k: k["Prioridad algoritmo"].title())
    # B sube todo lo BAJA a MEDIA
    b = completar_experto(ciega_b, clave_b, lambda k: "Media" if k["Prioridad algoritmo"] == "BAJA"
                          else k["Prioridad algoritmo"].title())
    resp = {"A": respuestas_por_escenario(validar_planilla_experto(a, ciega_a), clave_a),
            "B": respuestas_por_escenario(validar_planilla_experto(b, ciega_b), clave_b)}
    r = analizar_h2(tabla, resp)
    assert r["vs_algoritmo"]["A"]["kappa"]["kappa"] == 1
    n_baja = sum(1 for f in tabla if f["Scoring"] == "BAJA")
    assert r["vs_algoritmo"]["B"]["kappa"]["coincidencias"] == 55 - n_baja
    assert r["entre_expertos"]["kappa"]["coincidencias"] == 55 - n_baja
    # todas las discordancias A-B son de un escalon, con B mas alto
    assert r["entre_expertos"]["direccion"] == {"A mas alto": 0, "B mas alto": n_baja}
    assert r["entre_expertos"]["saltos_de_dos"] == 0
    # desagregaciones suman las 55
    for d in r["vs_algoritmo"]["A"]["desagregaciones"].values():
        assert sum(g["n"] for g in d.values()) == 55


def test_h2_con_un_solo_experto_no_calcula_acuerdo_entre_expertos():
    tabla = tabla_simulada()
    ciega, clave = planilla_experto(tabla, PLAN, 20260912)
    a = completar_experto(ciega, clave, lambda k: "Media")
    r = analizar_h2(tabla, {"A": respuestas_por_escenario(validar_planilla_experto(a, ciega), clave)})
    assert r["entre_expertos"] is None


# ── H3 ─────────────────────────────────────────────────────────────────────
def test_h3_promedios_y_severidad_por_evaluador():
    tabla = tabla_simulada()
    rubricas, clave = rubricas_evaluadores(tabla, PLAN)
    llenas = {"A": completar_rubrica(rubricas["A"], lambda f, c: 5),
              "B": completar_rubrica(rubricas["B"], lambda f, c: 4),
              "C": completar_rubrica(rubricas["C"], lambda f, c: 5 if c != "Persuasion (1-5)" else 3)}
    punt = {e: puntajes_por_escenario(validar_rubrica(llenas[e], rubricas[e]), clave) for e in "ABC"}
    r = analizar_h3(tabla, punt)
    assert r["por_evaluador"] == {"A": 5.0, "B": 4.0, "C": pytest.approx(4.6)}
    assert r["global"] == pytest.approx((5 + 4 + 4.6) / 3)
    assert r["por_criterio"]["Persuasion (1-5)"]["media"] == pytest.approx(4)
    assert r["por_criterio"]["Relevancia (1-5)"]["n"] == 165
    assert r["mensajes_4_o_mas"] == 55
    assert len(r["por_sesion"]) == 55
    assert sum(g["n"] for g in r["por_canal"].values()) == 55
