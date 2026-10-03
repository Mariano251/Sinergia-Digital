"""Los estadisticos tienen que reproducir los valores publicados de la Ronda 2."""
import csv
import os

import pytest

from estadistica import (resumen_latencias, matriz_confusion, kappa_cohen, landis,
                         icc2, f_cuantil, descriptivos, fleiss)

V = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CRITERIOS = ["Relevancia (1-5)", "Precision factual (1-5)", "Persuasion (1-5)",
             "Uso de contexto (1-5)", "Claridad (1-5)"]
COL = "PRIORIDAD ASIGNADA (Alta/Media/Baja)"


# Todos los archivos que lee esta suite son de la Ronda 2, que vive en
# validacion/historico/ desde que se ordenaron las rondas cerradas.
HISTORICO = os.path.join(V, "historico")


def leer(nombre):
    with open(os.path.join(HISTORICO, nombre), encoding="utf-8") as f:
        return list(csv.DictReader(f))


def por_escenario(planilla, clave, col=COL):
    v = {r["Sesion"]: r[col].strip().upper() for r in leer(planilla)}
    return {r["Escenario"]: v[r["Sesion"]] for r in leer(clave)}


def r2_rubricas():
    return [leer(p) for p in ("R2-H3-rubrica-evaluador-A_completada.csv",
                              "R2-H3-rubrica-evaluador-B-completada.csv",
                              "R2-H3-rubrica-evaluador-C-completa.csv")]


# ── H1 ─────────────────────────────────────────────────────────────────────
def test_h1_reproduce_la_ronda_2():
    lat = [float(f["Latencia (ms)"]) / 1000 for f in leer("datos-crudos-ronda2-55-sesiones.csv")]
    r = resumen_latencias(lat, umbral=300)
    assert (r["n"], round(r["min"], 2), round(r["q1"], 2), round(r["mediana"], 2)) == (55, 2.64, 3.06, 3.36)
    assert (round(r["media"], 2), round(r["q3"], 2), round(r["max"], 2), round(r["desvio"], 2)) == (3.45, 3.82, 5.38, 0.54)
    assert r["bajo_umbral"] == 55
    # el informe publico [1,93 , 4,95]; con cuartiles sin redondear da [1,924 , 4,956]
    assert round(r["iqr"], 2) == 0.76
    assert r["bigote_inf"] == pytest.approx(1.93, abs=0.01)
    assert r["bigote_sup"] == pytest.approx(4.95, abs=0.01)
    assert [round(x, 2) for x in r["atipicos"]] == [5.38]


def test_h1_detecta_atipicos_por_arriba_y_por_abajo():
    r = resumen_latencias([1, 10, 10, 10, 10, 10, 10, 10, 30], umbral=20)
    assert r["atipicos"] == [1, 30]
    assert r["bajo_umbral"] == 8


# ── H2 ─────────────────────────────────────────────────────────────────────
def test_kappa_perfecto_y_azar():
    assert kappa_cohen([("ALTA", "ALTA"), ("BAJA", "BAJA"), ("MEDIA", "MEDIA")])["kappa"] == 1
    k = kappa_cohen([("ALTA", "ALTA"), ("ALTA", "BAJA"), ("BAJA", "ALTA"), ("BAJA", "BAJA")])
    assert k["kappa"] == 0 and k["coincidencias"] == 2


def test_h2_algoritmo_contra_experto_2_ronda_2():
    e2 = por_escenario("R2-H2-experto2-planilla-completa.csv", "R2-H2-clave-NO-MOSTRAR.csv")
    alg = {r["Escenario"]: r["Prioridad algoritmo"] for r in leer("R2-H2-clave-NO-MOSTRAR.csv")}
    pares = [(alg[e], e2[e]) for e in sorted(alg)]
    k = kappa_cohen(pares)
    assert (k["coincidencias"], round(k["po"], 3), round(k["pe"], 3), round(k["kappa"], 3)) == (35, 0.636, 0.362, 0.430)
    assert landis(k["kappa"]) == "Moderado"
    m = matriz_confusion(pares)
    assert m["ALTA"] == {"ALTA": 9, "MEDIA": 1, "BAJA": 0}
    assert m["MEDIA"] == {"ALTA": 6, "MEDIA": 16, "BAJA": 5}
    assert m["BAJA"] == {"ALTA": 0, "MEDIA": 8, "BAJA": 10}


def test_h2_experto_2_contra_experto_3_ronda_2():
    e2 = por_escenario("R2-H2-experto2-planilla-completa.csv", "R2-H2-clave-NO-MOSTRAR.csv")
    e3 = por_escenario("R3-H2-experto3-planilla-completa.csv", "R3-H2-clave-NO-MOSTRAR.csv")
    k = kappa_cohen([(e2[e], e3[e]) for e in sorted(e2)])
    assert (k["coincidencias"], round(k["kappa"], 3)) == (49, 0.829)
    assert landis(k["kappa"]) == "Casi perfecto"


def test_fleiss_con_dos_observadores_identicos_es_1_y_conocido_con_tres():
    assert fleiss([("ALTA", "ALTA"), ("BAJA", "BAJA"), ("MEDIA", "MEDIA")]) == pytest.approx(1)
    # ejemplo manual: 2 sujetos, 3 observadores; P1=1, P2=1/3 -> Pbar=2/3; p=(4/6,2/6) -> Pe=5/9
    assert fleiss([("A", "A", "A"), ("A", "B", "B")], categorias=["A", "B"]) == pytest.approx((2/3 - 5/9) / (1 - 5/9))


# ── H3 ─────────────────────────────────────────────────────────────────────
def test_cuantil_f_contra_tablas():
    assert f_cuantil(0.975, 10, 20) == pytest.approx(2.7737, abs=1e-3)
    assert f_cuantil(0.95, 5, 5) == pytest.approx(5.0503, abs=1e-3)


def test_cci_ejemplo_de_shrout_y_fleiss_1979():
    # valores de referencia de psych::ICC en R para este conjunto clasico
    X = [[9, 2, 5, 8], [6, 1, 3, 2], [8, 4, 6, 8], [7, 1, 2, 6], [10, 5, 6, 9], [6, 2, 4, 7]]
    r = icc2(X)
    assert (round(r["icc_1"], 2), round(r["ic_1"][0], 3), round(r["ic_1"][1], 2)) == (0.29, 0.019, 0.76)
    assert (round(r["icc_k"], 2), round(r["ic_k"][0], 3), round(r["ic_k"][1], 2)) == (0.62, 0.071, 0.93)


def test_cci_sin_varianza_queda_indefinido_en_vez_de_romper():
    r = icc2([[5, 4, 5]] * 10)   # todos los mensajes iguales: no hay varianza entre sujetos
    assert r["icc_k"] is None and r["ic_k"] is None and r["icc_1"] is None


def test_h3_cci_ronda_2():
    R = r2_rubricas()
    X = [[sum(float(R[j][i][c]) for c in CRITERIOS) / 5 for j in range(3)] for i in range(55)]
    r = icc2(X)
    assert (round(r["msr"], 4), round(r["msc"], 4), round(r["mse"], 4)) == (0.0815, 0.1035, 0.0139)
    assert (round(r["icc_k"], 3), round(r["icc_1"], 3)) == (0.813, 0.592)
    # El informe de la Ronda 2 publico gl=72,9 e IC [0,698 , 0,887]: habia puesto el
    # CCI(2,k) en la formula de Satterthwaite. McGraw y Wong usan el CCI(2,1), como
    # psych::ICC (verificado arriba): gl=79,7 e IC [0,702 , 0,886]
    assert round(r["gl"], 1) == 79.7
    assert (round(r["ic_k"][0], 3), round(r["ic_k"][1], 3)) == (0.702, 0.886)


def test_h3_tabla_3_criterios_ronda_2():
    R = r2_rubricas()
    valores = [int(R[j][i]["Persuasion (1-5)"]) for j in range(3) for i in range(55)]
    d = descriptivos(valores)
    assert (d["n"], round(d["media"], 2), round(d["desvio_poblacional"], 2),
            round(d["desvio_muestral"], 2), d["minimo"], d["maximo"]) == (165, 4.34, 0.77, 0.78, 3, 5)
