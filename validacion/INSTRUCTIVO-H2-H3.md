# Instrumentos de validación — H2 y H3

**Muestra: 55 sesiones.** Datos crudos seudonimizados: `datos-crudos-55-sesiones.csv`

---

## De dónde salen las 55

No es un número elegido: sale de dos diseños independientes que se reportan por separado.

| Subconjunto | n | Diseño | Vía de disparo |
|---|---|---|---|
| `F-01` … `F-25` | 25 | Factorial 5×5: valor de carrito (40k/80k/120k/160k/200k) × abandonos previos (0/1/2/3/5) | Manual (detección sincrónica) |
| `B40-01` … `B40-05` | 5 | Casos de frontera en torno al umbral 40 (abandonos = 2) | Manual |
| `B70-01` … `B70-05` | 5 | Casos de frontera en torno al umbral 70 (abandonos = 5) | Manual |
| `exec-82` … `exec-101` | 20 | 10 usuarios × 2 ciclos de detección | **Automática (job periódico)** |

Reparto obtenido: **12 ALTA · 30 MEDIA · 13 BAJA** — 12 por Telegram, 43 por Email.

> **Nota metodológica obligatoria.** Las 55 son sesiones controladas con perfiles
> sintéticos, no tráfico orgánico. Redactar así:
>
> *"Se ejecutaron 55 sesiones controladas con perfiles sintéticos: 35 mediante
> un diseño factorial 5×5 más 10 casos de frontera en torno a los umbrales de
> clasificación, disparadas de forma sincrónica; y 20 mediante el job de
> detección periódica, con 10 perfiles en dos ciclos."*

### Advertencia sobre el subconjunto automático

9 de las 20 sesiones automáticas **no quedaron registradas en la planilla** por
una condición de carrera en la escritura concurrente: el orquestador reportó
éxito en las 20, pero varias escrituras simultáneas se pisaron entre sí. Los
datos se **recuperaron del almacén de ejecuciones del orquestador** y se
verificaron uno a uno contra el diseño (9/9 coincidentes en puntuación y
prioridad). Esto debe declararse en el capítulo de limitaciones.

---

## H2 — Concordancia del scoring

**Objetivo.** Comparar la prioridad que asigna el algoritmo contra la que asigna
un especialista humano, sobre las mismas 55 sesiones.

**Instrumento:** `H2-experto-planilla-ciega.csv`
**Quién:** un (1) experto en marketing digital con experiencia en e-commerce.

### Condiciones de aplicación

1. Recibe **únicamente** la planilla ciega. No ve `Scoring`, `Puntuacion` ni el
   canal por el que se envió el mensaje.
2. No conoce la fórmula del Anexo A, ni los pesos, ni los umbrales.
3. El orden está **aleatorizado con semilla `20260903`**, de modo que ni la
   estructura factorial ni la separación entre tandas sean inferibles.
4. Clasifica cada sesión en **Alta**, **Media** o **Baja**.
5. Completa las 55 de corrido, sin volver atrás.

> `H2-clave-NO-MOSTRAR-AL-EXPERTO.csv` vincula cada `S-xx` con su escenario, su
> tanda y la respuesta del algoritmo. **Es para el análisis, no para el experto.**

### Criterio que se le explica (lo único)

> "Prioridad de recuperación" = cuánta urgencia y cuántos recursos amerita este
> carrito abandonado. Alta = contactar ya y por el canal más directo.
> Media = contactar, sin urgencia. Baja = contacto de bajo costo o nada.

Ninguna regla numérica. Se busca juicio profesional, no reconstrucción de la fórmula.

### Análisis

- **Concordancia simple** = coincidencias / 55
- **Kappa de Cohen (κ)** sobre la matriz de confusión 3×3

| κ | Acuerdo (Landis & Koch, 1977) |
|---|---|
| < 0,20 | Pobre |
| 0,21 – 0,40 | Débil |
| 0,41 – 0,60 | Moderado |
| 0,61 – 0,80 | Sustancial |
| 0,81 – 1,00 | Casi perfecto |

**Reportar las dos cifras.** Con tres categorías el azar ya produce ~33% de
acuerdo, así que la concordancia simple sola sobreestima.

### Desagregaciones obligatorias

1. **Casos claros vs. casos de frontera.** 10 de las 55 (`B40-*`, `B70-*`) están
   a uno o dos puntos de un umbral. Es esperable —y deseable— que el desacuerdo
   se concentre ahí. Un acuerdo alto solo en lo obvio no valida nada.
2. **Tanda manual vs. automática.** Ambas usan el mismo algoritmo, así que no
   debería haber diferencia. Si la hay, es una señal a investigar.

---

## H3 — Calidad de los mensajes generados

**Objetivo.** Evaluar los 55 mensajes en cinco dimensiones, con tres evaluadores
independientes.

**Instrumento:** `H3-rubrica-evaluador-A.csv` / `-B.csv` / `-C.csv` (idénticos).

### Condiciones de aplicación

1. Los tres puntúan **de forma independiente**. No se consultan ni comparan hasta
   que los tres terminen. *Si se consultan, el CCI mide conversación, no acuerdo.*
2. **Cada uno recibe su propia planilla.** Nunca un documento compartido.
3. No ven prioridad ni canal: anclaría el juicio.
4. Orden aleatorizado con semilla `20260904`, distinto al de H2.
5. Escala **1 a 5**, enteros. Sin decimales ni casillas vacías.
6. Ven el valor y los productos del carrito, necesarios para juzgar precisión
   factual y uso de contexto.

---

## Definiciones operativas de los 5 criterios

> Estas anclas son lo que hace que tres personas puntúen parecido. Sin
> definiciones explícitas el CCI se desploma, y no es culpa de los evaluadores:
> es culpa del instrumento.

### 1. Relevancia
*¿El mensaje se dirige a esta situación concreta, o serviría para cualquiera?*

| | |
|---|---|
| **1** | Genérico. Se enviaría igual a cualquier cliente sin cambiar una palabra. |
| **3** | Menciona que hay un carrito pendiente, pero sin particularizar. |
| **5** | Se refiere a este carrito y esta situación. Cambiarle los datos lo dejaría sin sentido. |

### 2. Precisión factual
*¿Todo lo que afirma es verdadero según la base de conocimientos y el carrito real?*

Datos verificables — **base de conocimientos real del sistema**, verificada
contra los prompts en producción:

- Envíos: 48hs a todo el país. Gratis en compras superiores a **$30.000**.
- Pagos: 3 cuotas sin interés en compras superiores a $500. Hasta 12 cuotas con interés.
- Garantía: 12 meses oficial.
- Devoluciones: 30 días sin preguntas.
- Descuentos: hasta 5% si el cliente lo pide. Nunca superar el 10%.

> **Corrección respecto de la versión anterior de este instructivo.** La primera
> ronda de evaluación se aplicó con una base tomada de una versión antigua del
> workflow (envío gratis > $50.000, costo $3.500, 3-5 días hábiles). Impacto
> medido: bajo — solo 11 de 55 mensajes mencionan envío gratis, de los cuales uno
> cita $30.000 y uno $50.000, y ese grupo puntuó **por encima** del resto en
> precisión factual (3,76 vs 3,32). Aun así debe declararse como salvedad de la
> primera ronda.

| | |
|---|---|
| **1** | Inventa datos, o contradice el carrito (productos o montos inexistentes). |
| **3** | Todo correcto, pero impreciso o incompleto en algún punto. |
| **5** | Cada afirmación es verificable y coincide con el carrito y la base. Cero invención. |

> **Regla dura:** una sola afirmación falsa —un precio, un plazo, un producto que
> no está en el carrito— fuerza puntaje **1 o 2**, por bueno que sea el resto.
> La alucinación es el riesgo central de estos sistemas y la rúbrica debe
> castigarla, no promediarla.

### 3. Persuasión
*¿Genera motivación real para completar la compra, sin presionar?*

| | |
|---|---|
| **1** | No invita a la acción, o presiona de forma invasiva o manipuladora. |
| **3** | Invita a comprar, pero sin argumento propio: solo repite el link. |
| **5** | Construye una razón concreta para volver, con tono cordial y cierre claro. |

### 4. Uso de contexto
*¿Aprovecha lo que el sistema sabe del cliente?*

Disponible: nombre, productos, cantidades, valor total, link de checkout.

| | |
|---|---|
| **1** | No usa ninguno. |
| **3** | Usa uno o dos (típicamente el nombre y el link). |
| **5** | Integra la mayoría de forma natural, no como una lista pegada. |

### 5. Claridad
*¿Se entiende en una sola lectura?*

| | |
|---|---|
| **1** | Confuso, ambiguo, con errores de redacción o formato roto. |
| **3** | Se entiende, pero es largo, repetitivo o desordenado. |
| **5** | Directo y bien redactado. Sin errores. Extensión adecuada al canal. |

---

## Análisis de H3

- **Promedio por mensaje** = media de los 15 puntajes (5 criterios × 3 evaluadores)
- **Promedio global** = media de los 55 promedios
- **Promedio por criterio** = para identificar dónde el sistema es más débil
- **CCI** = acuerdo entre evaluadores

Para el CCI usar **efectos aleatorios de dos vías, acuerdo absoluto, medidas
promedio — ICC(2,k)**: es el que corresponde cuando los mismos tres evaluadores
puntúan a todos los sujetos y se reporta la media.

| CCI | Fiabilidad (Koo & Li, 2016) |
|---|---|
| < 0,50 | Pobre |
| 0,50 – 0,75 | Moderada |
| 0,75 – 0,90 | Buena |
| > 0,90 | Excelente |

**Desagregar además por canal** (Telegram vs Email): los prompts de sistema son
distintos, así que la calidad podría no ser homogénea. Es una comparación que
el diseño permite hacer y conviene reportar.

---

## Qué hay que reportar sí o sí

1. **Los datos crudos**, no solo los agregados: las 55 clasificaciones del
   experto y los 825 puntajes individuales (55 × 5 × 3) van al anexo.
2. **Las semillas de aleatorización** (`20260903` para H2, `20260904` para H3).
3. **El perfil de los evaluadores** (formación, experiencia) sin identificarlos.
4. **Que las sesiones son controladas**, con la redacción del inicio de este
   documento.
5. **La recuperación de las 9 filas perdidas** y su causa.

---
---

# SEGUNDA RONDA — protocolo de re-validación

> Esta sección aplica **después** de implementar el rediseño del scoring
> (`REDISENO-SCORING-H2.md`) y los prompts corregidos (`PROMPTS-MEJORADOS-H3.md`).

## Por qué hace falta una segunda ronda

La primera ronda refutó las dos hipótesis y permitió identificar las causas.
Las correcciones se derivaron **observando esos mismos datos**, así que no
pueden validarse con ellos: sería ajustar al conjunto de prueba.

La segunda ronda usa **sesiones nuevas** y, en H2, **un evaluador distinto**.

---

## H2 — segundo experto, obligatorio

**El experto de la primera ronda NO puede validar el rediseño.**

La regla implementada (tramos de valor + castigo por abandono ≥ 4) se dedujo de
sus propias respuestas. Medir concordancia contra él sería tautológico: se
estaría comprobando que una copia se parece al original.

| | Experto 1 | Experto 2 |
|---|---|---|
| Rol | Derivación de la regla (exploratorio) | **Validación (confirmatorio)** |
| Datos | Las 55 sesiones de la primera ronda | Sesiones nuevas |
| Qué mide | Diagnóstico del desacuerdo | Generalización entre profesionales |

Con el experto 2, la concordancia mide algo real: si el heurístico que se
formalizó es compartido por otros profesionales del rubro, o era idiosincrásico
del primero.

**Condiciones idénticas a la primera ronda:** planilla ciega, sin ver la
respuesta del algoritmo, orden aleatorizado, sin conocer la fórmula.

### Cómo reportarlo

> *"El rediseño del algoritmo se derivó del análisis exploratorio de las
> clasificaciones del primer experto. Su validación se realizó sobre un conjunto
> de sesiones independiente, evaluado por un segundo experto que no participó en
> la fase exploratoria."*

Esa frase es lo que separa un hallazgo de un ajuste.

---

## H3 — evaluación ciega a la versión

**No mandar los mensajes nuevos diciendo "esta es la versión mejorada".**
Los evaluadores puntúan más alto por expectativa, aunque no haya mejora. El
sesgo es fuerte y conocido.

### Diseño correcto

```
55 mensajes de la primera ronda  +  55 mensajes nuevos
              ↓
     mezclados aleatoriamente
              ↓
    110 ítems sin etiqueta de versión
```

Los mismos tres evaluadores puntúan los 110 sin saber cuál es cuál.

**Ventajas:**

1. La comparación antes/después queda **libre de sesgo de expectativa**
2. Se obtiene un **re-test de fiabilidad**: los 55 viejos ya fueron puntuados,
   así que se puede medir la estabilidad de cada evaluador consigo mismo
3. Cualquier deriva en la severidad de los evaluadores queda controlada, porque
   ambas versiones se puntúan en la misma sesión de trabajo

**Costo:** unas 2 horas por evaluador en vez de 1. Es el precio de poder
afirmar que la mejora es real y no expectativa.

### Análisis de la segunda ronda

- Promedio global de cada versión, y la diferencia
- Diferencia **por criterio** — se espera mayor mejora en precisión factual y
  persuasión, que son los que las correcciones apuntan
- Diferencia **por prompt** (Alta / Media / Baja) — se espera la mayor mejora en
  Baja, que era el que no tenía base de conocimientos
- CCI de la segunda ronda, y estabilidad intra-evaluador sobre los 55 repetidos

---

## Interacción entre los dos cambios — no perderla de vista

El rediseño del scoring **degrada a Baja** las sesiones con 4 o más abandonos.
Eso hace que **más mensajes se generen con el prompt de Baja**, que era el peor
de los tres.

Por eso el orden importa: **corregir el prompt de Baja antes de correr la tanda
nueva.** Si se cambia el scoring sin corregir ese prompt, el promedio de H3
puede empeorar aunque el scoring haya mejorado.

---

## Orden de ejecución

1. Aplicar el rediseño del scoring en el nodo `Scoring - Clasificar Lead`
2. Aplicar los tres prompts corregidos en los nodos `AI Agent - ...`
3. Re-exportar el workflow al repositorio, para que el artefacto publicado sea
   el que generó los datos
4. Correr la tanda nueva de sesiones
5. Generar los instrumentos: planilla ciega para el **experto 2** y las tres
   rúbricas con los 110 mensajes mezclados
6. Recolectar, analizar y comparar contra la primera ronda
