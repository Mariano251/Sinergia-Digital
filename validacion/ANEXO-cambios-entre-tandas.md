# Cambios del sistema entre la tanda 1 y la tanda 2

**Fuente de todo este documento:** los *snapshots* del workflow que n8n almacena
en cada ejecucion (`execution_data.workflowData`), no el repositorio ni ninguna
reconstruccion. Se comparo la ejecucion **50** (tanda 1) contra la **110** (tanda 2).

| | Rango de ejecuciones | Inicio | Fin |
|---|---|---|---|
| **Tanda 1** | 47 - 101 | 2026-09-02 23:05:07 | 2026-09-03 04:10:28 |
| **Tanda 2** | 102 - 157 | 2026-09-03 17:36:09 | 2026-09-03 17:51:59 |

Comparacion exhaustiva de los 22 nodos: **4 cambiaron, 18 quedaron identicos, y el
cableado del workflow es identico.**

```
AI Agent - Alta Prioridad          CAMBIO: parameters
AI Agent - Baja Prioridad          CAMBIO: parameters
AI Agent - Media Prioridad         CAMBIO: parameters
Scoring - Clasificar Lead          CAMBIO: parameters
AI Agent - Manejo de Objeciones    sin cambios
Anthropic Chat Model / 1 / 2 / 3   sin cambios
Gmail - Baja / Media Prioridad     sin cambios
Google Sheets - Auditoria          sin cambios
Memoria - Alta / Media / Baja / Objeciones   sin cambios
Switch - Prioridad                 sin cambios
Telegram - Enviar Mensaje          sin cambios
Telegram - Responder Objecion      sin cambios
Validar Datos                      sin cambios
Webhook - Carrito Abandonado       sin cambios
Webhook - Respuesta Telegram       sin cambios
```

---

# 1. Scoring - SI cambio

## Antes (tanda 1)

```javascript
// ═══════════════════════════════════════════════════════════════
// SCORING MULTIDIMENSIONAL — Fórmula del Anexo A
// Score = 50·(valor_norm) + 30·(abandonos_norm) + 20·(etapa_score)
//   valor_norm    = min(cart_value / 200000, 1)
//   abandonos_norm= min(previous_abandonment_count / 5, 1)
//   etapa_score   = browsing 0.25 | cart 0.50 | checkout_started 0.75 | payment_page 1.00
// Umbrales: ALTA ≥ 70 | MEDIA ≥ 40 | BAJA < 40
// ═══════════════════════════════════════════════════════════════
const body = $input.first().json.body;

// --- Entradas ---
const cartValue = parseFloat(body.cart_value) || 0;
const abandonos = parseInt(body.previous_abandonment_count) || 0;
const cartStage = (body.cart_stage || 'browsing').toString().toLowerCase();

// --- Normalizaciones (constantes del Anexo A) ---
const CART_VALUE_MAX  = 200000;
const ABANDONMENT_MAX = 5;
const STAGE_SCORES = {
  browsing:         0.25,
  cart:             0.50,
  checkout_started: 0.75,
  payment_page:     1.00
};

const valorNorm    = Math.min(cartValue / CART_VALUE_MAX, 1);
const abandonoNorm = Math.min(abandonos / ABANDONMENT_MAX, 1);
const etapaScore   = STAGE_SCORES[cartStage] !== undefined ? STAGE_SCORES[cartStage] : 0.25;

// --- Puntuación ponderada (0–100) ---
const puntuacion = Math.round(
  (50 * valorNorm + 30 * abandonoNorm + 20 * etapaScore) * 100
) / 100;

// --- Clasificación por umbrales ---
let prioridad;
if (puntuacion >= 70) {
  prioridad = 'ALTA';
} else if (puntuacion >= 40) {
  prioridad = 'MEDIA';
} else {
  prioridad = 'BAJA';
}

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
    items_resumen:            itemsResumen               || body.producto              || 'productos seleccionados',
    is_returning:             body.customer?.is_returning_customer || false,
    // --- campos del scoring multidimensional (Anexo A) ---
    cart_stage:               cartStage,
    previous_abandonment_count: abandonos,
    puntuacion:               puntuacion,
    prioridad:                prioridad,
    // --- timestamps ---
    timestamp_evento:         tsEvento,
    timestamp_procesado:      tsProcesado
  }
}];
```

## Despues (tanda 2)

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

## Que cambio, punto por punto

| | Tanda 1 | Tanda 2 |
|---|---|---|
| **Formula** | `50*valor_norm + 30*abandonos_norm + 20*etapa_score` | `100*valor_norm` |
| **previous_abandonment_count** | Suma lineal positiva, hasta **+30 puntos** (`min(ab/5,1)`) | **No entra en la puntuacion.** Actua como castigo: si `ab >= 4`, baja un nivel |
| **Signo del abandono** | **Positivo**: mas abandonos, mas prioridad | **Negativo y por umbral**: 4 o mas abandonos, menos prioridad |
| **cart_stage** | Entra con peso 20 (browsing .25 / cart .50 / checkout_started .75 / payment_page 1.00) | **Eliminado del calculo.** Se conserva solo en la salida, para el registro |
| **Normalizacion de valor** | `min(cart_value/200000, 1)`, ponderada por 50 | `min(cart_value/200000, 1)`, ponderada por 100 |
| **Umbral ALTA** | >= 70 | >= 70 (equivale a $140.000) |
| **Umbral MEDIA** | >= 40 | **>= 30** (equivale a $60.000) |
| **Campo nuevo en la salida** | -- | `degradado` (booleano): registra si se aplico el castigo |

> **Defecto de codigo detectado en la tanda 2.** En el objeto `return`, las claves
> `cart_value`, `cart_id` y `checkout_url` aparecen **duplicadas** (lineas 8-10 y 11-13).
> En JavaScript la ultima definicion prevalece; como los valores duplicados son
> identicos a los primeros, **la salida del nodo no se altera**. Se documenta por
> exactitud, no porque tenga efecto sobre los datos.

---

# 2. System Prompts - SI cambiaron los tres

| Agente | Tanda 1 | Tanda 2 |
|---|---|---|
| Alta Prioridad (Telegram) | 769 caracteres | 1.702 |
| Media Prioridad (Email) | 640 | 1.596 |
| Baja Prioridad (Email) | 406 | 1.224 |

## Agente Alta Prioridad

### Antes (tanda 1)

```
=Eres un asistente de ventas experto de "TechNova" por Telegram. Recuperá el carrito abandonado.

Cliente: {{ $json.name }}
Productos: {{ $json.items_resumen }}
Valor: ${{ $json.cart_value }} ARS
Link: {{ $json.checkout_url }}

BASE DE CONOCIMIENTOS:
• Envíos: 48hs a todo el país. Gratis en compras +$30.000.
• Pagos: 3 cuotas sin interés en compras +$500. Hasta 12 cuotas con interés.
• Garantía: 12 meses oficial.
• Devoluciones: 30 días sin preguntas.
• Descuentos: Hasta 5% si lo pide. Nunca superar el 10%.

Saludá por nombre, mencioná los productos, respondé dudas y pedile que finalice la compra. Sé breve y cálido.
RESTRICCIÓN: Solo temas de TechNova.

No uses markdown, asteriscos ni formato especial. Solo texto plano.
```

### Despues (tanda 2)

```
=Eres un asistente de ventas de "TechNova" que escribe por Telegram. Recuperá el carrito abandonado.

DATOS DE ESTE CLIENTE:
Nombre: {{ $json.name }}
Productos en el carrito: {{ $json.items_resumen }}
Valor total: ${{ $json.cart_value }} ARS
Etapa alcanzada: {{ $json.cart_stage }}
Carritos abandonados antes: {{ $json.previous_abandonment_count }}
Link de checkout: {{ $json.checkout_url }}

BASE DE CONOCIMIENTOS (única fuente de datos permitida):
- Envíos: 48hs a todo el país. Gratis en compras superiores a $30.000.
- Pagos: 3 cuotas sin interés en cualquier compra de la tienda. Hasta 12 cuotas con interés.
- Garantía: 12 meses oficial.
- Devoluciones: 30 días sin preguntas.
- Descuentos: hasta 5% si el cliente lo pide. Nunca superar el 10%.

CÓMO ESCRIBIR EL MENSAJE:
1. Saludá por su nombre.
2. Nombrá los productos concretos del carrito y conectalos con un uso real:
   para qué le van a servir juntos. No los enumeres como una factura.
3. Elegí UN SOLO beneficio de la base, el que más aplique a ESTE carrito, y explicá
   en una línea por qué le conviene. No recites la lista completa.
4. Cerrá invitando a completar la compra con el link.
5. Preguntale si tiene alguna duda.

REGLAS DURAS:
- No inventes ningún dato. Si una cifra no está en la base, no la menciones.
- No afirmes que el envío es gratis salvo que el valor del carrito supere los $30.000.
- No menciones cuántas veces abandonó antes: usalo solo para ajustar el tono
  (si abandonó varias veces, sé más directo y menos insistente).
- Máximo 8 líneas. Tono cálido y cercano, es Telegram.
- Solo texto plano: nada de markdown, asteriscos ni viñetas con símbolos.
```

## Agente Media Prioridad

### Antes (tanda 1)

```
=Eres un asistente de ventas de "TechNova". Redactá un email de recuperación de carrito.

Cliente: {{ $json.name }}
Productos: {{ $json.items_resumen }}
Valor: ${{ $json.cart_value }} ARS
Link: {{ $json.checkout_url }}

BASE DE CONOCIMIENTOS:
• Envíos: 48hs a todo el país.
• Pagos: 3 cuotas sin interés en compras +$500.
• Garantía: 12 meses oficial.
• Devoluciones: 30 días sin preguntas.

Redactá un email profesional: saludá por nombre, recordá los productos, destacá 2 beneficios e invitá a finalizar con el link. Solo texto plano.

No uses markdown, asteriscos ni formato especial. Solo texto plano.
```

### Despues (tanda 2)

```
=Eres un asistente de ventas de "TechNova". Redactá un email de recuperación de carrito.

DATOS DE ESTE CLIENTE:
Nombre: {{ $json.name }}
Productos en el carrito: {{ $json.items_resumen }}
Valor total: ${{ $json.cart_value }} ARS
Etapa alcanzada: {{ $json.cart_stage }}
Carritos abandonados antes: {{ $json.previous_abandonment_count }}
Link de checkout: {{ $json.checkout_url }}

BASE DE CONOCIMIENTOS (única fuente de datos permitida):
- Envíos: 48hs a todo el país. Gratis en compras superiores a $30.000.
- Pagos: 3 cuotas sin interés en cualquier compra de la tienda. Hasta 12 cuotas con interés.
- Garantía: 12 meses oficial.
- Devoluciones: 30 días sin preguntas.

CÓMO ESCRIBIR EL EMAIL:
1. Asunto corto que mencione el nombre del cliente o un producto concreto del carrito.
2. Saludá por su nombre.
3. Nombrá los productos y conectalos con un uso real: qué resuelve esa combinación.
   No los pegues como lista de precios.
4. Elegí UN SOLO beneficio de la base, el que más aplique a ESTE carrito, y justificá
   en una línea por qué le conviene. No enumeres todos.
5. Cerrá con el link de checkout y una invitación a escribir si tiene dudas.

REGLAS DURAS:
- No inventes ningún dato. Si una cifra no está en la base, no la menciones.
- No afirmes que el envío es gratis salvo que el valor del carrito supere los $30.000.
- No menciones cuántas veces abandonó antes: usalo solo para ajustar el tono.
- Máximo 12 líneas en total. Profesional pero cercano.
- Solo texto plano: nada de markdown, asteriscos ni viñetas con símbolos.
```

## Agente Baja Prioridad

### Antes (tanda 1)

```
=Eres un asistente de ventas de "TechNova". Redactá un email breve de recuperación de carrito.

Cliente: {{ $json.name }}
Productos: {{ $json.items_resumen }}
Valor: ${{ $json.cart_value }} ARS
Link: {{ $json.checkout_url }}

Email corto (máx 5 líneas): recordá el carrito e invitá a finalizar la compra. Solo texto plano.

No uses markdown, asteriscos ni formato especial. Solo texto plano.
```

### Despues (tanda 2)

```
=Eres un asistente de ventas de "TechNova". Redactá un email breve de recuperación de carrito.

DATOS DE ESTE CLIENTE:
Nombre: {{ $json.name }}
Productos en el carrito: {{ $json.items_resumen }}
Valor total: ${{ $json.cart_value }} ARS
Carritos abandonados antes: {{ $json.previous_abandonment_count }}
Link de checkout: {{ $json.checkout_url }}

BASE DE CONOCIMIENTOS (única fuente de datos permitida):
- Envíos: 48hs a todo el país. Gratis en compras superiores a $30.000.
- Pagos: 3 cuotas sin interés en cualquier compra de la tienda.
- Garantía: 12 meses oficial.
- Devoluciones: 30 días sin preguntas.

CÓMO ESCRIBIR EL EMAIL:
1. Asunto corto que mencione un producto concreto del carrito.
2. Saludá por su nombre y nombrá los productos que dejó.
3. Agregá UNA razón concreta para volver, tomada de la base, la que más aplique
   a este carrito.
4. Cerrá con el link.

REGLAS DURAS:
- No inventes ningún dato. Si una cifra no está en la base, no la menciones.
- No afirmes que el envío es gratis salvo que el valor del carrito supere los $30.000.
- Máximo 6 líneas. Breve y directo, sin relleno.
- Solo texto plano: nada de markdown, asteriscos ni viñetas con símbolos.
```

## Resumen de las modificaciones

1. **Base de conocimientos unificada en los tres agentes.** El de Baja Prioridad
   **no tenia ninguna** en la tanda 1: no disponia de datos sobre envios, pagos,
   garantia ni devoluciones. En la tanda 2 los tres comparten la misma base.

2. **Contexto ampliado.** Se agregaron al prompt campos que el nodo de scoring ya
   producia y no se estaban usando: `previous_abandonment_count` en los tres, y
   `cart_stage` en Alta y Media. Antes solo recibian nombre, productos, valor y link.

3. **Instrucciones anti-invencion explicitas.** Se incorporo un bloque REGLAS DURAS
   inexistente en la tanda 1: prohibicion de mencionar cifras ausentes de la base y
   condicion explicita para afirmar envio gratis (solo si el carrito supera $30.000).

4. **Cambio en la instruccion de persuasion.** La tanda 1 pedia "destaca 2 beneficios",
   lo que producia enumeracion de la lista completa. La tanda 2 pide **un solo**
   beneficio, el que mas aplique a ese carrito, con justificacion en una linea.

5. **Instruccion de relevancia nueva.** Se pide conectar los productos con un uso
   concreto (para que le sirven juntos) en lugar de enumerarlos como una factura.
   Se agrego ademas un limite de extension explicito por canal: 8, 12 y 6 lineas.

6. **Reformulacion del umbral de cuotas.** La regla de negocio no se modifico: el
   umbral sigue siendo $500. Como el producto mas barato del catalogo cuesta $4.000,
   todo carrito lo supera y la mencion no discriminaba nada. Paso de "en compras
   superiores a $500" a "en cualquier compra de la tienda".

---

# 3. Otros cambios - ninguno

Verificado por comparacion de los parametros completos de cada nodo:

| Componente | Estado |
|---|---|
| **Modelo de IA** | **Sin cambios.** `claude-haiku-4-5-20251001` en los cuatro nodos Anthropic |
| **Temperatura / max tokens** | **Sin cambios.** `options: {}` en los cuatro: no se fijo ningun parametro, ni antes ni despues |
| **Canales** | **Sin cambios.** Telegram para Alta, Gmail para Media y Baja |
| **Enrutamiento por canal** | **Sin cambios.** Canal = ALTA -> Telegram, resto -> Email |
| **Cableado del workflow** | **Sin cambios.** Comparacion byte a byte de `connections` |
| **Nodo de validacion de entrada** | **Sin cambios** |
| **Nodo de auditoria (Google Sheets)** | **Sin cambios.** Mismas 16 columnas y mismas expresiones |
| **Agente de manejo de objeciones** | **Sin cambios** |
| **Nodos de memoria** | **Sin cambios** |
| **Logica de deteccion (backend)** | **Sin cambios.** `git log` entre el fin de la tanda 1 y el inicio de la tanda 2 no registra ningun commit sobre technova-backend/src, server.js ni database/ |
| **Umbral de inactividad y sondeo** | **Sin cambios.** 2 minutos y 5 minutos |
| **Escenarios ejecutados** | **Sin cambios.** Los mismos 55: mismos valores de carrito, mismos contadores de abandono, mismo reparto entre las diez cuentas |

> Nota: la unica diferencia operativa entre tandas es que en la tanda 2 el escenario
> `F-16` debio reenviarse individualmente, porque su primer intento fallo por timeout
> de la API de Telegram y su nodo de auditoria no llego a ejecutarse. Se restablecieron
> el carrito y el contador antes del reenvio.

---

# 4. Tabla de las 55 sesiones

Archivo: `ANEXO-tabla-55-sesiones-ronda2.csv` (55 filas, 12 columnas).

---

# 5. Trazabilidad de cada columna

| Columna | Archivo de origen | Campo |
|---|---|---|
| `N` | numeracion correlativa | ordenado por escenario: F, luego B40 y B70, luego exec |
| `fecha` | `datos-crudos-ronda2-55-sesiones.csv` | `Timestamp`, truncado a fecha |
| `identificador_anonimizado` | `datos-crudos-ronda2-55-sesiones.csv` | `Customer ID`, mapeado a U01..U10 |
| `valor_carrito` | `datos-crudos-ronda2-55-sesiones.csv` | `Cart Value` |
| `etapa` | `datos-crudos-ronda2-55-sesiones.csv` | `Cart Stage` |
| `abandonos_previos` | `datos-crudos-ronda2-55-sesiones.csv` | `Abandonos Previos` |
| `prioridad_algoritmo` | `datos-crudos-ronda2-55-sesiones.csv` | `Scoring` |
| `prioridad_experto1` | `Evaluacion_H2_COMPLETO.csv` + `H2-clave-NO-MOSTRAR-AL-EXPERTO.csv` | ver nota 1 |
| `prioridad_experto2` | `R2-H2-experto2-planilla-completa.csv` + `R2-H2-clave-NO-MOSTRAR.csv` | union por `Sesion` |
| `latencia_seg` | `datos-crudos-ronda2-55-sesiones.csv` | `Latencia (ms)` dividido por 1000 |
| `puntaje_rubrica_promedio` | `R2-H3-rubrica-evaluador-{A,B,C}-*.csv` + `R2-H3-clave-NO-MOSTRAR.csv` | media de los 15 puntajes: 5 criterios x 3 evaluadores |
| `canal` | `datos-crudos-ronda2-55-sesiones.csv` | `Canal` |

## Origen del archivo de datos crudos

`datos-crudos-ronda2-55-sesiones.csv` **no** se exporto de la planilla de auditoria.
Se reconstruyo desde `execution_data` de n8n, ejecuciones 102 a 157, porque la
escritura concurrente del job de deteccion puede perder filas en la planilla sin
emitir error. Los nombres y correos estan seudonimizados; la version identificable
queda fuera del control de versiones.

## Nota 1 - sobre `prioridad_experto1`

**El experto 1 nunca evaluo las sesiones de la tanda 2.** Evaluo las 55 de la tanda 1.
El valor se traslada por coincidencia de insumos, que es licita porque **ambas tandas
ejecutaron exactamente los mismos 55 escenarios**: mismos valores de carrito y mismos
contadores de abandono.

La union se hace por la clave `(valor_carrito, abandonos_previos)`. Verificado antes
de construir la tabla:

- 50 claves distintas en la tanda 1
- **0 claves ambiguas**: ningun par de insumos identicos recibio dos respuestas
  distintas del experto 1
- **0 filas de la tanda 2 sin correspondencia**

La union es univoca. Aun asi, al citar esta columna corresponde aclarar que es un
traslado por identidad de insumos y no una evaluacion directa sobre esta tanda.

## Nota 2 - por que `prioridad_algoritmo` y `prioridad_experto1` coinciden en las 55 filas

No es un error de la tabla. El algoritmo de la tanda 2 implementa la regla derivada
del analisis exploratorio de las clasificaciones del experto 1, que reproduce sus
juicios con Kappa = 1,000. Por construccion, ambas columnas son identicas.

**Consecuencia metodologica:** la concordancia entre `prioridad_algoritmo` y
`prioridad_experto1` **no constituye validacion alguna** y no debe reportarse como
resultado. La comparacion valida es contra `prioridad_experto2`, que no participo de
la fase exploratoria.
