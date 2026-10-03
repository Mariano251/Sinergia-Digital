"""
Estadisticos de H1, H2 y H3, sin scipy. Son los mismos metodos que produjeron el
informe de la Ronda 2 (test_estadistica.py reproduce esos valores publicados):

  H1  cuartiles inclusivos, desvio muestral, atipicos de Tukey (1,5 x IQR)
  H2  matriz de confusion 3x3, Kappa de Cohen, Kappa de Fleiss, Landis y Koch (1977)
  H3  CCI de dos vias, efectos aleatorios, acuerdo absoluto (Shrout y Fleiss 1979),
      con IC95% de McGraw y Wong (1996); cuantiles F por inversion de la beta
      incompleta regularizada
"""
import math
import statistics as st
from collections import Counter

CATEGORIAS = ["ALTA", "MEDIA", "BAJA"]


# ── H1 ─────────────────────────────────────────────────────────────────────
def resumen_latencias(valores, umbral):
    v = sorted(valores)
    q1, mediana, q3 = st.quantiles(v, n=4, method="inclusive")
    iqr = q3 - q1
    inf, sup = q1 - 1.5 * iqr, q3 + 1.5 * iqr
    return {
        "n": len(v), "min": v[0], "q1": q1, "mediana": mediana, "media": st.mean(v),
        "q3": q3, "max": v[-1], "desvio": st.stdev(v),
        "bajo_umbral": sum(1 for x in v if x < umbral),
        "iqr": iqr, "bigote_inf": inf, "bigote_sup": sup,
        "atipicos": [x for x in v if x < inf or x > sup],
    }


# ── H2 ─────────────────────────────────────────────────────────────────────
def matriz_confusion(pares, categorias=CATEGORIAS):
    """m[fila][columna]: fila = primer elemento del par, columna = segundo."""
    m = {a: {b: 0 for b in categorias} for a in categorias}
    for a, b in pares:
        m[a][b] += 1
    return m


def kappa_cohen(pares, categorias=CATEGORIAS):
    n = len(pares)
    coinc = sum(1 for a, b in pares if a == b)
    po = coinc / n
    fa = Counter(a for a, _ in pares)
    fb = Counter(b for _, b in pares)
    pe = sum((fa[c] / n) * (fb[c] / n) for c in categorias)
    kappa = 1.0 if pe == 1 else (po - pe) / (1 - pe)
    return {"n": n, "coincidencias": coinc, "po": po, "pe": pe, "kappa": kappa}


def fleiss(sujetos, categorias=CATEGORIAS):
    """sujetos: una tupla de clasificaciones por sujeto, mismo numero de observadores."""
    n, r = len(sujetos), len(sujetos[0])
    total = Counter()
    p_i = []
    for s in sujetos:
        c = Counter(s)
        total.update(c)
        p_i.append((sum(c[k] ** 2 for k in categorias) - r) / (r * (r - 1)))
    pbar = sum(p_i) / n
    pe = sum((total[k] / (n * r)) ** 2 for k in categorias)
    return (pbar - pe) / (1 - pe)


def landis(k):
    return ("Casi perfecto" if k >= .81 else "Sustancial" if k >= .61 else
            "Moderado" if k >= .41 else "Debil" if k >= .21 else
            "Pobre" if k >= 0 else "Peor que el azar")


# ── H3 ─────────────────────────────────────────────────────────────────────
def _beta_fc(a, b, x):
    """Fraccion continua de la beta incompleta (Lentz modificado)."""
    tiny = 1e-300
    c, d = 1.0, 1.0 - (a + b) * x / (a + 1)
    d = 1 / (d if abs(d) > tiny else tiny)
    h = d
    for m in range(1, 1000):
        for num in (m * (b - m) * x / ((a + 2 * m - 1) * (a + 2 * m)),
                    -(a + m) * (a + b + m) * x / ((a + 2 * m) * (a + 2 * m + 1))):
            d = 1 + num * d
            d = 1 / (d if abs(d) > tiny else tiny)
            c = 1 + num / c
            c = c if abs(c) > tiny else tiny
            h *= d * c
        if abs(d * c - 1) < 1e-15:
            break
    return h


def beta_reg(a, b, x):
    if x <= 0:
        return 0.0
    if x >= 1:
        return 1.0
    ln = math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b) + a * math.log(x) + b * math.log(1 - x)
    if x < (a + 1) / (a + b + 2):
        return math.exp(ln) * _beta_fc(a, b, x) / a
    return 1 - math.exp(ln) * _beta_fc(b, a, 1 - x) / b


def f_cdf(x, d1, d2):
    return 0.0 if x <= 0 else beta_reg(d1 / 2, d2 / 2, d1 * x / (d1 * x + d2))


def f_cuantil(p, d1, d2):
    lo, hi = 0.0, 1.0
    while f_cdf(hi, d1, d2) < p:
        hi *= 2
    while hi - lo > 1e-12 * max(1.0, hi):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if f_cdf(mid, d1, d2) < p else (lo, mid)
    return (lo + hi) / 2


def icc2(X, alfa=0.05):
    """X: n sujetos x k evaluadores. CCI(2,1) y CCI(2,k), acuerdo absoluto."""
    n, k = len(X), len(X[0])
    g = sum(map(sum, X)) / (n * k)
    filas = [sum(f) / k for f in X]
    cols = [sum(X[i][j] for i in range(n)) / n for j in range(k)]
    ssr = k * sum((m - g) ** 2 for m in filas)
    ssc = n * sum((m - g) ** 2 for m in cols)
    sst = sum((v - g) ** 2 for f in X for v in f)
    msr, msc = ssr / (n - 1), ssc / (k - 1)
    mse = (sst - ssr - ssc) / ((n - 1) * (k - 1))

    base = {"n": n, "k": k, "msr": msr, "msc": msc, "mse": mse}
    if msr == 0 or mse == 0:
        # sin varianza entre sujetos o sin error residual el CCI no esta definido
        return {**base, "gl": None, "icc_1": None, "ic_1": None, "icc_k": None, "ic_k": None}

    icc1 = (msr - mse) / (msr + (k - 1) * mse + k * (msc - mse) / n)
    icck = (msr - mse) / (msr + (msc - mse) / n)

    # McGraw y Wong (1996), caso 2A
    a = k * icc1 / (n * (1 - icc1))
    b = 1 + k * icc1 * (n - 1) / (n * (1 - icc1))
    gl = (a * msc + b * mse) ** 2 / ((a * msc) ** 2 / (k - 1) + (b * mse) ** 2 / ((n - 1) * (k - 1)))
    fl = f_cuantil(1 - alfa / 2, n - 1, gl)
    fu = f_cuantil(1 - alfa / 2, gl, n - 1)
    c = k * msc + (k * n - k - n) * mse
    l1 = n * (msr - fl * mse) / (fl * c + n * msr)
    u1 = n * (fu * msr - mse) / (c + n * fu * msr)
    a_k = lambda r: k * r / (1 + (k - 1) * r)
    return {**base, "gl": gl,
            "icc_1": icc1, "ic_1": (l1, u1), "icc_k": icck, "ic_k": (a_k(l1), a_k(u1))}


def descriptivos(valores):
    return {"n": len(valores), "media": st.mean(valores),
            "desvio_poblacional": st.pstdev(valores), "desvio_muestral": st.stdev(valores),
            "minimo": min(valores), "maximo": max(valores)}


def interpretar_cci(v):
    """Koo y Li (2016)."""
    return "Excelente" if v >= .90 else "Buena" if v >= .75 else "Moderada" if v >= .50 else "Pobre"
