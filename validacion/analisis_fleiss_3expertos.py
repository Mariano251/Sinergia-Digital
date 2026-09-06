"""
Fiabilidad inter-observador entre los tres expertos (H2).

Requiere que exista `R3-H2-experto3-planilla-completa.csv` con la columna
'PRIORIDAD ASIGNADA (Alta/Media/Baja)' llena para las 55 sesiones.

Calcula:
  - Kappa de Fleiss entre los tres expertos
  - los tres Kappa de Cohen por pares
  - acuerdo unanime y por mayoria
  - concordancia del algoritmo contra cada experto

Uso:  python analisis_fleiss_3expertos.py
"""
import csv, io, os, sys
from collections import Counter

B = os.path.dirname(os.path.abspath(__file__)) + os.sep
rd = lambda p: list(csv.DictReader(io.open(B + p, encoding='utf-8')))
CAT = ['ALTA', 'MEDIA', 'BAJA']
COL = 'PRIORIDAD ASIGNADA (Alta/Media/Baja)'

# ── experto 1: evaluo la ronda 1; se cruza por (valor, abandonos) ───────────
e1v = {r['ID_Sesion']: r['Prioridad_Asignada'].strip().upper()
       for r in rd('Evaluación_H2_COMPLETO.csv')}
e1k = {}
for r in rd('H2-clave-NO-MOSTRAR-AL-EXPERTO.csv'):
    e1k[(int(float(r['Cart Value'])), int(r['Abandonos Previos']))] = e1v[r['Sesion']]

# ── expertos 2 y 3: instrumentos propios, se cruzan por escenario ───────────
def cargar(planilla, clave):
    if not os.path.exists(B + planilla):
        print('FALTA el archivo:', planilla); sys.exit(1)
    v = {r['Sesion']: r[COL].strip().upper() for r in rd(planilla)}
    vac = [s for s, x in v.items() if not x]
    if vac:
        print(f'{planilla}: {len(vac)} respuestas vacias -> {vac[:5]}'); sys.exit(1)
    return {r['Escenario']: v[r['Sesion']] for r in rd(clave)}

e2 = cargar('R2-H2-experto2-planilla-completa.csv', 'R2-H2-clave-NO-MOSTRAR.csv')
e3 = cargar('R3-H2-experto3-planilla-completa.csv', 'R3-H2-clave-NO-MOSTRAR.csv')
alg = {r['Escenario']: r['Prioridad algoritmo'].strip().upper()
       for r in rd('R2-H2-clave-NO-MOSTRAR.csv')}
crudos = {r['Escenario']: r for r in rd('datos-crudos-ronda2-55-sesiones.csv')}

escs = sorted(crudos)
J = {}
for e in escs:
    c = crudos[e]
    J[e] = (e1k[(int(float(c['Cart Value'])), int(c['Abandonos Previos']))], e2[e], e3[e])
n = len(J)

def kappa_cohen(pares):
    m = len(pares); ac = sum(1 for a, b in pares if a == b); po = ac / m
    fa = Counter(a for a, _ in pares); fb = Counter(b for _, b in pares)
    pe = sum((fa[c] / m) * (fb[c] / m) for c in CAT)
    return ac, po, (po - pe) / (1 - pe)

def landis(k):
    return ('Casi perfecto' if k >= .81 else 'Sustancial' if k >= .61 else
            'Moderado' if k >= .41 else 'Debil' if k >= .21 else
            'Pobre' if k >= 0 else 'Peor que el azar')

print('=' * 70)
print('FIABILIDAD INTER-OBSERVADOR — 3 EXPERTOS, %d SESIONES' % n)
print('=' * 70)

# ── Kappa de Fleiss ────────────────────────────────────────────────────────
k_r = 3
P_i = []
col = {c: 0 for c in CAT}
for e in escs:
    cnt = Counter(J[e])
    for c in CAT: col[c] += cnt[c]
    P_i.append((sum(cnt[c] ** 2 for c in CAT) - k_r) / (k_r * (k_r - 1)))
p_j = {c: col[c] / (n * k_r) for c in CAT}
Pbar = sum(P_i) / n
Pe = sum(p_j[c] ** 2 for c in CAT)
fleiss = (Pbar - Pe) / (1 - Pe)
print(f'\nKAPPA DE FLEISS (3 observadores) : {fleiss:.3f}   ({landis(fleiss)})')
print(f'  acuerdo observado Pbar : {Pbar:.4f}')
print(f'  acuerdo esperado Pe    : {Pe:.4f}')
print(f'  proporciones marginales: ' + ', '.join(f'{c} {p_j[c]:.3f}' for c in CAT))

# ── Kappa de Cohen por pares ───────────────────────────────────────────────
print('\nKAPPA DE COHEN POR PARES')
idx = {'Experto 1': 0, 'Experto 2': 1, 'Experto 3': 2}
nom = list(idx)
for i in range(3):
    for j in range(i + 1, 3):
        pares = [(J[e][idx[nom[i]]], J[e][idx[nom[j]]]) for e in escs]
        ac, po, k = kappa_cohen(pares)
        print(f'  {nom[i]} vs {nom[j]}: {ac}/{n} = {po*100:5.1f}%   kappa {k:.3f}   ({landis(k)})')

# ── acuerdo unanime y mayoritario ──────────────────────────────────────────
una = sum(1 for e in escs if len(set(J[e])) == 1)
may = sum(1 for e in escs if max(Counter(J[e]).values()) >= 2)
print(f'\nACUERDO ENTRE LOS TRES')
print(f'  unanime (3/3)      : {una}/{n} = {100*una/n:.1f}%')
print(f'  mayoria (>=2/3)    : {may}/{n} = {100*may/n:.1f}%')
print(f'  sin mayoria (1/1/1): {n-may}/{n}')

# ── algoritmo contra cada experto ──────────────────────────────────────────
print('\nALGORITMO CONTRA CADA EXPERTO')
for i, nm in enumerate(nom):
    pares = [(alg[e], J[e][i]) for e in escs]
    ac, po, k = kappa_cohen(pares)
    nota = '  <- circular: el algoritmo implementa su regla' if i == 0 else ''
    print(f'  vs {nm}: {ac}/{n} = {po*100:5.1f}%   kappa {k:.3f}{nota}')

print('\n' + '=' * 70)
print('Lectura: si el Kappa de Fleiss se ubica en el mismo rango que los Kappa')
print('del algoritmo contra los expertos 2 y 3, el desacuerdo es estructural de')
print('la tarea y no atribuible al algoritmo ni a un evaluador en particular.')
print('=' * 70)
