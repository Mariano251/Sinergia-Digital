"""
Plan de la Tanda 3 (contador de abandonos INCREMENTAL).

Diseno:
- Las mismas 10 cuentas de las tandas 1 y 2 (user_id 1..10).
- El contador previous_abandonment_count se pone en 0 UNA sola vez, al inicio.
  Despues nadie lo toca: lo incrementa el backend (+1 por cada abandono notificado),
  igual que en produccion.
- 55 sesiones = 5,5 ciclos: las cuentas 1-5 abandonan 6 veces (contador 0..5)
  y las cuentas 6-10 abandonan 5 veces (contador 0..4).
- Se reutilizan los MISMOS 55 valores de carrito de las tandas 1 y 2, con las mismas
  composiciones de productos. Lo unico que cambia es de donde sale el contador.
- Asignacion estratificada: se ordenan los 55 valores, se cortan en 5 bloques de 11
  y en cada bloque se reparten al azar 2 valores a cada nivel de contador 0..4 y 1 al
  nivel 5. Asi cada nivel de contador recibe carritos de todo el rango de valor y el
  contador no queda confundido con el valor. Dentro de cada nivel, el valor se asigna
  a una cuenta al azar. Semilla fija: 20260911.

Salida: plan-tanda3.json (lo consume run_tanda3.js).
"""
import json
import random
from collections import Counter

SEMILLA = 20260911

# 8=Cable 4000 · 2=MousePad 20000 · 6=Webcam 35000 · 3=Auriculares 45000
# 1=Teclado 55000 · 7=Headset 65000 · 5=SSD 85000 · 4=Monitor 180000
PRECIOS = {8: 4000, 2: 20000, 6: 35000, 3: 45000, 1: 55000, 7: 65000, 5: 85000, 4: 180000}

# Composiciones de run_validacion.js (CARRITOS) y run_validacion_cron.js (CICLO_1/2)
COMPOSICION = {
    24000: [[2, 1], [8, 1]],
    40000: [[2, 2]],
    49000: [[3, 1], [8, 1]],
    55000: [[1, 1]],
    59000: [[1, 1], [8, 1]],
    64000: [[2, 3], [8, 1]],
    68000: [[2, 3], [8, 2]],
    69000: [[7, 1], [8, 1]],
    72000: [[2, 3], [8, 3]],
    76000: [[2, 3], [8, 4]],
    80000: [[3, 1], [6, 1]],
    85000: [[5, 1]],
    90000: [[3, 2]],
    100000: [[3, 1], [1, 1]],
    105000: [[5, 1], [2, 1]],
    110000: [[3, 1], [7, 1]],
    112000: [[6, 1], [3, 1], [2, 1], [8, 3]],
    116000: [[6, 1], [3, 1], [2, 1], [8, 4]],
    120000: [[5, 1], [6, 1]],
    124000: [[5, 1], [6, 1], [8, 1]],
    128000: [[5, 1], [6, 1], [8, 2]],
    130000: [[5, 1], [3, 1]],
    140000: [[5, 1], [1, 1]],
    150000: [[5, 1], [7, 1]],
    160000: [[5, 1], [1, 1], [2, 1]],
    180000: [[4, 1]],
    200000: [[4, 1], [2, 1]],
}

# Los 55 valores de carrito de las tandas 1 y 2
VALORES = (
    [v for v in (40000, 80000, 120000, 160000, 200000) for _ in range(5)]      # F-01..F-25
    + [64000, 68000, 72000, 76000, 80000]                                    # B40
    + [112000, 116000, 120000, 124000, 128000]                               # B70
    + [40000, 64000, 90000, 110000, 140000, 55000, 180000, 200000, 69000, 130000]   # ciclo 1 job
    + [160000, 49000, 100000, 24000, 200000, 85000, 120000, 59000, 150000, 105000]  # ciclo 2 job
)


def prioridad_esperada(cv, ab):
    """Regla vigente (tanda 2): tramos de valor + castigo por abandono recurrente."""
    p = round(min(cv / 200000, 1) * 100 * 100) / 100
    nivel = 2 if p >= 70 else 1 if p >= 30 else 0
    if ab >= 4:
        nivel = max(0, nivel - 1)
    return p, ["BAJA", "MEDIA", "ALTA"][nivel]


def generar():
    rng = random.Random(SEMILLA)
    ordenados = sorted(VALORES)
    por_nivel = {k: [] for k in range(6)}
    for b in range(5):
        bloque = ordenados[b * 11:(b + 1) * 11]
        niveles = [k for k in range(5) for _ in range(2)] + [5]
        rng.shuffle(niveles)
        for v, k in zip(bloque, niveles):
            por_nivel[k].append(v)

    sesiones = []
    for k in range(6):
        cuentas = list(range(1, 6)) if k == 5 else list(range(1, 11))
        valores = por_nivel[k][:]
        rng.shuffle(valores)
        for u, cv in zip(cuentas, valores):
            p, prio = prioridad_esperada(cv, k)
            sesiones.append({
                "id": f"I-{u:02d}-{k}",
                "ciclo": k + 1,
                "u": u,
                "ab_esperado": k,
                "cv": cv,
                "items": COMPOSICION[cv],
                "puntuacion_esperada": p,
                "prioridad_esperada": prio,
            })
    return sesiones


if __name__ == "__main__":
    sesiones = generar()
    for s in sesiones:
        assert sum(PRECIOS[pid] * q for pid, q in s["items"]) == s["cv"], s
    assert Counter(s["cv"] for s in sesiones) == Counter(VALORES)
    with open("plan-tanda3.json", "w", encoding="utf-8") as f:
        json.dump({"semilla": SEMILLA, "sesiones": sesiones}, f, indent=2, ensure_ascii=False)

    print(f"{len(sesiones)} sesiones -> plan-tanda3.json")
    print("\nprioridad esperada x contador de abandonos:")
    print("  ab   ALTA MEDIA BAJA  | valor min-max")
    for k in range(6):
        ss = [s for s in sesiones if s["ab_esperado"] == k]
        c = Counter(s["prioridad_esperada"] for s in ss)
        print(f"  {k}   {c['ALTA']:4d} {c['MEDIA']:5d} {c['BAJA']:4d}  | "
              f"${min(s['cv'] for s in ss):,} - ${max(s['cv'] for s in ss):,}")
    c = Counter(s["prioridad_esperada"] for s in sesiones)
    print(f"  tot {c['ALTA']:4d} {c['MEDIA']:5d} {c['BAJA']:4d}")
    print("\ncuenta: valores en orden de abandono")
    for u in range(1, 11):
        print(f"  {u:2d}: " + "  ".join(f"{s['cv']//1000}k" for s in sesiones if s["u"] == u))
