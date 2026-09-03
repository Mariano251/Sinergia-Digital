# Rediseño del algoritmo de scoring — propuesta

> ## ⚠️ ESTO ES UN ANÁLISIS POST-HOC, NO UNA VALIDACIÓN
>
> La regla se derivó observando las respuestas del experto sobre las mismas
> 55 sesiones con las que después se mide. El 100% de concordancia está
> **inflado por construcción** y no puede reportarse como resultado.
>
> Es una **hipótesis**, y como tal va al capítulo de trabajo futuro. Para
> convertirla en resultado hay que aplicarla y re-validar con sesiones nuevas.

---

## El diagnóstico

Algoritmo actual: `50·valor + 30·abandonos + 20·etapa`, umbrales 70 / 40.

Concordancia con el experto: **43,6%**, Kappa **0,084** (pobre).

Tres problemas, en orden de gravedad:

### 1. El abandono está modelado al revés

El algoritmo lo suma linealmente hasta +30 puntos: más abandonos, más prioridad.
El experto hace lo contrario, pero **no de forma gradual** — es un castigo por umbral.

La prueba limpia, agrupando por mismo valor de carrito:

```
$ 40.000:  ab=0→B  ab=1→B  ab=2→B  ab=3→B  ab=5→B
$ 80.000:  ab=0→M  ab=1→M  ab=2→M  ab=3→M  ab=5→B   ←
$120.000:  ab=0→M  ab=1→M  ab=2→M  ab=3→M  ab=4→B   ←
$160.000:  ab=0→A  ab=1→A  ab=2→A  ab=3→A  ab=5→M   ←
$200.000:  ab=0→A  ab=1→A  ab=2→A  ab=3→A  ab=4→M   ←
```

El nivel se mantiene de 0 a 3 abandonos y cae un escalón a partir de 4.

**Interpretación de negocio:** el especialista lee el abandono recurrente como
señal de baja intención de compra —un cliente que mira y no compra—, no como
señal de interés acumulado. El algoritmo asume lo contrario.

> Ojo: **invertir el signo no alcanza.** Probado: `50·valor − 30·abandonos`
> da 34,5% y κ = −0,009, *peor* que el actual. La relación no es lineal
> en ninguna dirección: es un escalón.

### 2. La etapa aporta cero discriminación

`cart_stage` vale siempre `'cart'` porque el backend lo hardcodea
(`abandonedCartService.js:51`, `webhookController.js:58`). Sus 20 puntos son una
constante que se suma a todas las sesiones por igual: **no separa nada**.

O se implementa el tracking real de etapa de checkout, o se elimina del modelo.
Mantenerlo como está es documentar una variable que no existe.

### 3. La geometría de los umbrales produce zonas imposibles

Con la fórmula actual y `abandonos ≤ 1`, **ALTA es inalcanzable con cualquier
valor de carrito** (máximo posible: 60 puntos, umbral 70). Un carrito de
$200.000 de un cliente sin historial nunca puede ser Alta prioridad.

Eso no es una decisión de diseño documentada: es un efecto colateral de los pesos.

---

## Variantes evaluadas

| Variante | Concordancia | Kappa |
|---|---|---|
| Actual: `50·valor + 30·ab + 20·etapa` | 43,6% | 0,084 |
| Signo invertido: `50·valor − 30·ab + 20·etapa` | 34,5% | −0,009 |
| Sin abandono: `80·valor + 20·etapa` | 67,3% | 0,487 |
| Solo valor: `100·valor` | 63,6% | 0,438 |
| Tramos de valor solos | 74,5% | 0,595 |
| **Tramos + castigo si `ab ≥ 4`** | **100,0%** | **1,000** |

---

## La propuesta

Conserva la escala 0-100 y el umbral de ALTA en 70, para no romper la
comparabilidad con lo ya reportado.

```
puntuacion = 100 × min(cart_value / 200000, 1)

nivel:  puntuacion >= 70  → ALTA
        puntuacion >= 30  → MEDIA
        puntuacion <  30  → BAJA

si previous_abandonment_count >= 4  →  bajar un nivel
```

Equivalencias: `puntuación 70` ⟷ `$140.000` · `puntuación 30` ⟷ `$60.000`.

### Código para el nodo `Scoring - Clasificar Lead`

```javascript
// --- Normalización y puntuación (0-100) ---
const CART_VALUE_MAX = 200000;
const U_ALTA  = 70;   // equivale a $140.000
const U_MEDIA = 30;   // equivale a  $60.000
const AB_CASTIGO = 4; // a partir de aqui se degrada un nivel

const valorNorm  = Math.min(cartValue / CART_VALUE_MAX, 1);
const puntuacion = Math.round(valorNorm * 100 * 100) / 100;

// --- Clasificación por tramos ---
const NIVELES = ['BAJA', 'MEDIA', 'ALTA'];
let nivel = puntuacion >= U_ALTA ? 2 : puntuacion >= U_MEDIA ? 1 : 0;

// --- Castigo por abandono recurrente ---
const degradado = abandonos >= AB_CASTIGO;
if (degradado) nivel = Math.max(0, nivel - 1);

const prioridad = NIVELES[nivel];
```

Conviene agregar `degradado` al payload y a la planilla: deja explícito
cuándo se aplicó el castigo, sin tener que recalcularlo.

### Ejemplos del cambio

| Caso | $cart | ab | Actual | Propuesto | Experto |
|---|---|---|---|---|---|
| S-16 | 200.000 | 0 | MEDIA | **ALTA** | Alta |
| S-04 | 124.000 | 5 | ALTA | **BAJA** | Baja |
| S-27 | 128.000 | 5 | ALTA | **BAJA** | Baja |
| S-33 | 40.000 | 5 | MEDIA | **BAJA** | Baja |
| S-50 | 120.000 | 5 | ALTA | **BAJA** | Baja |

---

## Advertencia sobre el ajuste perfecto

Un modelo de **tres parámetros** (dos umbrales y un corte de abandono) reproduce
**55 juicios humanos sin un solo error**. La baja complejidad frente al número de
observaciones sugiere que el experto aplicó efectivamente ese heurístico, y no que
la regla esté sobreajustada al ruido.

Aun así, hay dos lecturas y conviene tener la respuesta preparada:

- El experto aplicó un criterio profesional muy consistente y formalizable.
  Es el escenario deseable y refuerza el aporte.
- O las respuestas no surgieron de deliberación caso por caso.

Documentar cómo se aplicó el instrumento —tiempo empleado, condiciones— cubre
esa pregunta antes de que la hagan.

---

## Cómo convertir esto en un resultado

1. Aplicar el rediseño al nodo de scoring
2. Correr una tanda de sesiones **nuevas**
3. Que el experto clasifique **esos casos nuevos**, que no vio
4. Recién ahí calcular concordancia y Kappa

Si el heurístico es real, la concordancia debería mantenerse alta sobre datos
frescos. Si baja mucho, la regla estaba sobreajustada — y eso también es un
resultado que vale la pena reportar.
