"""Cotejo de la latencia de la Tabla E1 con la exportación de n8n (ejecuciones 158 a 212).
Uso, desde la raíz del repositorio:
    python validacion/tanda3-incremental/cotejo_latencias.py
"""
import csv, os, numpy as np
RAIZ = 'validacion'
BASE = os.path.join(RAIZ, 'tanda3-incremental', 'ejecuciones-158-212')
CRUDOS = os.path.join(RAIZ, 'datos-crudos-tanda3-55-sesiones.csv')  # latencia en ms, como la Tabla E1

ex = {int(r['N_sesion']): r for r in csv.DictReader(open(os.path.join(BASE, 'ejecuciones.csv'), encoding='utf-8'))}
nod = list(csv.DictReader(open(os.path.join(BASE, 'nodos.csv'), encoding='utf-8')))
aud = {int(r['exec_id']): int(r['inicio_relativo_ms']) for r in nod if 'Auditor' in r['nodo']}
por_esc = {r['Escenario']: int(r['Latencia (ms)']) / 1000
           for r in csv.DictReader(open(CRUDOS, encoding='utf-8'))}
lat = {n: (e['escenario'], por_esc[e['escenario']]) for n, e in ex.items() if e['escenario'] in por_esc}

ns = sorted(lat)
print('Sesiones cotejadas por escenario:', len(ns), 'de', len(ex))
L = np.array([lat[n][1] for n in ns])
D = np.array([int(ex[n]['duracion_ms']) / 1000 for n in ns])
A = np.array([aud[int(ex[n]['id'])] / 1000 for n in ns])
print('r(latencia, duración de la ejecución) = %.3f' % np.corrcoef(L, D)[0, 1])
print('r(latencia, inicio del nodo de auditoría) = %.3f' % np.corrcoef(L, A)[0, 1])
d = L - D
print('latencia - duración: mínimo %.2f s, máximo %.2f s, mediana %.2f s' % (d.min(), d.max(), np.median(d)))
for n in (27, 30):
    print('sesión %d: latencia %.3f s, ejecución %s ms' % (n, lat[n][1], ex[n]['duracion_ms']))
