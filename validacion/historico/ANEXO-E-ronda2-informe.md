# Evidencia primaria - Ronda 2 (55 sesiones)

**Alcance:** exclusivamente las ejecuciones **102 a 157** de n8n, del 03/09/2026
entre 17:36:09 y 17:51:59. **No se mezcla con la tanda 1** (ejecuciones 47-101).

**Fuente:** `execution_data` de n8n. Ningun dato fue reconstruido de memoria ni
exportado de la planilla de auditoria.

| | |
|---|---|
| Ejecuciones en el rango | 56 |
| Con estado `success` | 55 |
| Con estado `error` | 1 (exec 117) |
| Filas de la tabla | **55** |

> **Sobre la ejecucion 117.** Corresponde al escenario `F-16`.
> Fallo por *timeout* de la API de Telegram tras 21,15 s en el nodo de envio, y su
> nodo de auditoria no llego a ejecutarse. Se reenvio como ejecucion **137**, que es
> la que integra la tabla. La 117 queda excluida por no haber producido datos.

---

# 1. Tabla Anexo E

Archivo: **`ANEXO-E-ronda2-55-sesiones.csv`** (55 filas, 12 columnas, ordenado por N).

Columnas: `N`, `fecha`, `id_anonimizado`, `valor_carrito`, `etapa`,
`abandonos_previos`, `prioridad_algoritmo`, `prioridad_experto2`, `latencia_seg`,
`rubrica_promedio`, `canal`, `estado`.

Notas sobre dos columnas:

- **`estado`** proviene de `execution_entity.status` de n8n, es decir el resultado
  real de la ejecucion. **No** se uso la columna `Status` de la planilla de auditoria:
  esa columna es un literal fijo `"Enviado"` en el nodo de Google Sheets, escrito
  igual en toda fila con independencia de lo ocurrido, y por lo tanto no informa nada.
  Lo mismo aplica a `Conversion Proxy`, literal fijo `"Pendiente"`.
- **`prioridad_experto1` fue excluida deliberadamente.** El algoritmo de la Ronda 2
  implementa la regla derivada de las clasificaciones del experto 1, a las que
  reproduce con Kappa = 1,000. Compararlos seria circular.

---

# 2 a 4, 6. Resultados calculados

Salida literal del script de analisis (`r2_analisis.py`):

```

====================================================================================================
2. H1 — LATENCIA (n=55, solo Ronda 2)
====================================================================================================
  n                 :       55 
  minimo            :     2.64 s
  Q1                :     3.06 s
  mediana           :     3.36 s
  media             :     3.45 s
  Q3                :     3.82 s
  maximo            :     5.38 s
  desvio estandar   :     0.54 s
  < 300 s           :       55 / 55  = 100.0 %

  IQR = 0.76 s | bigotes de Tukey: [1.93 , 4.95]
  outliers por 1.5*IQR: 1
    N7 F-07 exec 108: 5.38 s

====================================================================================================
3. H2 — ALGORITMO vs EXPERTO 2 (n=55, solo Ronda 2)
====================================================================================================

              Alta   Media    Baja   total   <- EXPERTO 2
  Alta           9       1       0      10
  Media          6      16       5      27
  Baja           0       8      10      18
  total         15      25      15      55
  ^ ALGORITMO

  coincidencias        : 35/55
  concordancia simple  : 63.6 %
  acuerdo esperado azar: 36.2 %
  Kappa de Cohen       : 0.430
  Landis y Koch (1977) : Moderado

====================================================================================================
4. H3 — CALIDAD DE MENSAJES (n=55 sesiones, 825 puntajes)
====================================================================================================

  promedio global: 4.79 / 5,00

  por criterio:
    Relevancia (1-5)          : 5.00
    Precision factual (1-5)   : 4.96
    Persuasion (1-5)          : 4.34
    Uso de contexto (1-5)     : 4.72
    Claridad (1-5)            : 4.94

  por canal:
    Telegram  (n=10 mensajes): 4.91
    Email     (n=45 mensajes): 4.76

  por evaluador (severidad):
    Evaluador A: 4.84
    Evaluador B: 4.78
    Evaluador C: 4.76

  mensajes con promedio >= 4,0: 55/55 = 100.0 %

  CCI(2,k) medidas promedio : 0.813   IC95% [0.698 , 0.887]   (Buena)
  CCI(2,1) medida individual: 0.592
  (dos vias, efectos aleatorios, acuerdo absoluto | MSR=0.0815 MSC=0.1035 MSE=0.0139 gl=72.9)

====================================================================================================
6. DISTRIBUCION Y CORRESPONDENCIA PRIORIDAD -> CANAL
====================================================================================================

  prioridad_algoritmo: {'Alta': 10, 'Media': 27, 'Baja': 18}
  prioridad_experto2 : {'Alta': 15, 'Media': 25, 'Baja': 15}

  cruce prioridad_algoritmo x canal:
    Alta   -> Telegram : 10
    Media  -> Email    : 27
    Baja   -> Email    : 18

  regla Alta->Telegram y Media/Baja->Email se cumple en las 55: True

  filas escritas: 55 -> ANEXO-E-ronda2-55-sesiones.csv
```

---

## Precisiones sobre H1

El unico valor atipico segun el criterio de Tukey (1,5xIQR) es **N7, escenario
`F-07`, ejecucion 108: 5,38 s**. Su descomposicion, tomada del registro de eventos:

```
+       9 ms   scoring completo
+   3.088 ms   generacion con Claude terminada     (3,07 s)
+   4.734 ms   Gmail confirmado                    (1,64 s)
+   6.009 ms   fila de auditoria escrita
```

Contra las distribuciones de la propia tanda: la generacion con IA tuvo mediana de
**2,22 s** (maximo 3,64 s) y el envio mediana de **0,45 s** (maximo 1,64 s, que es
justamente este caso). **La causa del atipico es el envio por Gmail, 3,6 veces por
encima de la mediana, sumado a una generacion algo mas lenta que la mediana.** No hubo
reintentos ni arranque en frio: los nodos previos corrieron en 9 ms.

Ningun valor se acerca al umbral de 300 s: el maximo de la tanda es 1,8 % de ese umbral.

## Precisiones sobre H3

El **CCI(2,k) = 0,813 con IC95% [0,698 , 0,887]** se calculo con el modelo de dos
vias, efectos aleatorios, acuerdo absoluto, medidas promedio. El intervalo se obtuvo
con la formulacion de McGraw y Wong (1996) y los cuantiles de la distribucion F
calculados por inversion numerica de la funcion beta incompleta regularizada
(scipy no estaba disponible en el entorno; la implementacion se verifico por
bisección con tolerancia 1e-12).

El limite inferior del intervalo (0,698) cae en la franja "moderada", de modo que
**corresponde reportar el intervalo y no solo el estimador puntual**.

Observacion: el CCI es menor que el de la tanda 1 pese a que los puntajes son mas
altos. No es una contradiccion: con casi todos los valores concentrados en 5, la
varianza entre sujetos se reduce, y el CCI mide precisamente la proporcion de
varianza atribuible a diferencias entre sujetos. Con poco rango, el coeficiente baja
aunque el acuerdo absoluto sea alto.

---

# 5. Origen de la columna `prioridad_experto2`

**Declaracion honesta y literal de lo que se puede verificar:**

1. Se genero el instrumento ciego `R2-H2-experto2-planilla-ciega.csv` con las 55
   sesiones en orden aleatorizado (semilla 20260905), sin las columnas `Scoring`,
   `Puntuacion` ni `Canal`.
2. El archivo fue entregado al tesista para su aplicacion.
3. El tesista devolvio `R2-H2-experto2-planilla-completa.csv` con las 55
   clasificaciones completas.

**No se dispone de evidencia tecnica sobre quien o que produjo esas clasificaciones.**
El proceso de aplicacion ocurrio fuera del entorno auditable: no hay registro de
sesion, marca temporal por item, ni identificacion del respondente. El tesista habia
manifestado que conseguiria un segundo experto humano, pero **eso no puede
verificarse desde los datos.**

Lo unico que puede afirmarse con evidencia son propiedades analiticas de las respuestas:

| Observacion | Valor |
|---|---|
| Distribucion asignada | Alta 15, Media 25, Baja 15 |
| Ajuste a una regla de 3 parametros (tramos de valor + castigo por abandono) | 89,1 % (Kappa 0,834) |
| Regla implicita que mejor ajusta | ALTA >= $112.000, MEDIA >= $80.000, castigo si abandonos >= 5 |
| Coherencia con el valor del carrito | monotonica: Alta $167.333, Media $111.520, Baja $52.800 de promedio |
| Casillas vacias o fuera de rango | ninguna |

El ajuste del 89,1 % indica un criterio consistente pero **no perfectamente**
mecanico, a diferencia del experto 1, cuyas respuestas se reproducen al 100 %.

**Para la tesis:** corresponde declarar el rol tal como se aplico y, si se afirma que
fue un profesional humano, respaldarlo con documentacion del propio tesista (perfil,
fecha y condiciones de aplicacion). **Este informe no puede sustentar esa afirmacion.**

---

# 7. Algoritmo de scoring de la Ronda 2

Version exacta que corrio en las ejecuciones 102-157, extraida del snapshot
`execution_data.workflowData` de la ejecucion 110:

```javascript
// ═══════════════════════════════════════════════════════════════
// SCORING POR TRAMOS DE VALOR CON CASTIGO POR ABANDONO RECURRENTE
//   puntuacion = 100 · min(cart_value / 200000, 1)
//   ALTA  ≥ 70  (equivale a $140.000)
//   MEDIA ≥ 30  (equivale a  $60.000)
//   BAJA  < 30
//   si previous_abandonment_count ≥ 4 → baja un nivel
//
// Cambios respecto de la version anterior:
//   - el abandono deja de sumar linealmente y pasa a ser castigo por umbral
//   - se elimina cart_stage del calculo: el backend siempre manda 'cart',
//     con lo cual sus 20 puntos eran una constante que no discriminaba nada
//   - umbral MEDIA de 40 a 30, para eliminar la zona en la que ALTA era
//     inalcanzable con cualquier carrito
// ═══════════════════════════════════════════════════════════════
const body = $input.first().json.body;

// --- Entradas ---
const cartValue = parseFloat(body.cart_value) || 0;
const abandonos = parseInt(body.previous_abandonment_count) || 0;
// cart_stage se conserva solo para el registro de auditoria: NO entra en el calculo
const cartStage = (body.cart_stage || 'browsing').toString().toLowerCase();

// --- Constantes ---
const CART_VALUE_MAX = 200000;
const U_ALTA         = 70;   // equivale a $140.000
const U_MEDIA        = 30;   // equivale a  $60.000
const AB_CASTIGO     = 4;    // a partir de aqui se degrada un nivel

// --- Puntuacion (0-100), solo por valor de carrito ---
const valorNorm  = Math.min(cartValue / CART_VALUE_MAX, 1);
const puntuacion = Math.round(valorNorm * 100 * 100) / 100;

// --- Clasificacion por tramos ---
const NIVELES = ['BAJA', 'MEDIA', 'ALTA'];
let nivel = puntuacion >= U_ALTA ? 2 : puntuacion >= U_MEDIA ? 1 : 0;

// --- Castigo por abandono recurrente ---
const degradado = abandonos >= AB_CASTIGO;
if (degradado) nivel = Math.max(0, nivel - 1);

const prioridad = NIVELES[nivel];

// --- Resumen de items ---
const items = body.cart?.items || [];
const itemsResumen = items.map(i => `${i.name} (x${i.quantity}) - $${i.price}`).join(', ');

// --- Timestamps para latencia ---
// timestamp_evento: cuándo el backend detectó el abandono (viene en el payload)
// timestamp_procesado: cuándo n8n procesa el scoring (ahora)
const tsEvento = body.timestamp || body.detected_at || new Date().toISOString();
const tsProcesado = new Date().toISOString();

return [{
  json: {
    customer_id:              body.customer_id           || body.customer?.customer_id || 'sin-id',
    name:                     body.name                  || body.customer?.name        || 'Cliente',
    email:                    body.email                 || body.customer?.email       || '',
    phone:                    body.phone                 || body.customer?.phone       || '',
    telegram_chat_id:         body.telegram_chat_id      || '',
    cart_value:               cartValue,
    cart_id:                  body.cart?.cart_id         || body.cart_id               || '',
    checkout_url:             body.cart?.checkout_url    || body.checkout_url          || '',
    cart_value:               cartValue,
    cart_id:                  body.cart?.cart_id         || body.cart_id               || '',
    checkout_url:             body.cart?.checkout_url    || body.checkout_url          || '',
    items_resumen:            itemsResumen               || body.producto              || 'productos seleccionados',
    is_returning:             body.customer?.is_returning_customer || false,
    // --- campos del scoring ---
    cart_stage:               cartStage,
    previous_abandonment_count: abandonos,
    puntuacion:               puntuacion,
    prioridad:                prioridad,
    degradado:                degradado,
    // --- timestamps ---
    timestamp_evento:         tsEvento,
    timestamp_procesado:      tsProcesado
  }
}];
```

## Comportamiento verificado sobre las 55

| | |
|---|---|
| `puntuacion` | `100 x min(cart_value / 200000, 1)` |
| Umbral ALTA | >= 70 (equivale a $140.000) |
| Umbral MEDIA | >= 30 (equivale a $60.000) |
| Castigo | si `previous_abandonment_count >= 4`, baja un nivel |
| `cart_stage` | no participa del calculo; se conserva en la salida |
| Campo `degradado` | booleano, registra si se aplico el castigo |

> **Defecto de codigo, sin efecto funcional.** En el objeto `return`, las claves
> `cart_value`, `cart_id` y `checkout_url` estan duplicadas. En JavaScript prevalece
> la ultima definicion y los valores duplicados son identicos a los primeros, de modo
> que la salida del nodo no se altera. Se documenta por exactitud.
