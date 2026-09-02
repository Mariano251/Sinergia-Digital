# Instrumentos de validación — H2 y H3

Corrida de referencia: **35 sesiones**, 2026-09-02.
Datos crudos: `datos-crudos-tanda-2026-09-02.csv`

---

## H2 — Concordancia del scoring

**Objetivo.** Comparar la prioridad que asigna el algoritmo contra la que asigna
un especialista humano, sobre las mismas 35 sesiones.

**Instrumento.** `H2-experto-planilla-ciega.csv`

**Quién.** Un (1) experto en marketing digital con experiencia en e-commerce.

### Condiciones de aplicación

1. El experto recibe **únicamente** la planilla ciega. No ve la columna `Scoring`
   ni `Puntuacion`, ni el canal por el que se envió el mensaje.
2. No conoce la fórmula del Anexo A, ni los pesos, ni los umbrales.
3. El orden de las sesiones está **aleatorizado** (semilla fija `20260902`), de
   modo que la estructura factorial del diseño no sea inferible.
4. Clasifica cada sesión en **Alta**, **Media** o **Baja** prioridad de
   recuperación, según su criterio profesional.
5. Completa las 35 sin volver atrás a revisar las anteriores.

> La clave `H2-clave-NO-MOSTRAR-AL-EXPERTO.csv` vincula cada `S-xx` con su
> escenario y con la respuesta del algoritmo. **Es para el análisis posterior,
> no para el experto.**

### Criterio de prioridad (lo único que se le explica)

> "Prioridad de recuperación" = cuánta urgencia y cuántos recursos amerita este
> carrito abandonado. Alta = contactar ya y por el canal más directo.
> Media = contactar, sin urgencia. Baja = contacto de bajo costo o nada.

No se le da ninguna regla numérica. El juicio tiene que ser profesional, no
una reconstrucción de la fórmula.

### Análisis

- **Concordancia simple** = coincidencias / 35
- **Kappa de Cohen (κ)** sobre la matriz de confusión 3×3

Interpretación de κ (Landis & Koch, 1977):

| κ | Acuerdo |
|---|---|
| < 0,20 | Pobre |
| 0,21 – 0,40 | Débil |
| 0,41 – 0,60 | Moderado |
| 0,61 – 0,80 | Sustancial |
| 0,81 – 1,00 | Casi perfecto |

**Reportar siempre las dos cifras.** La concordancia simple sola sobreestima:
con tres categorías, el azar ya produce ~33% de acuerdo.

### Nota sobre los casos de frontera

10 de las 35 sesiones (`B40-*` y `B70-*`) fueron diseñadas a 1–2 puntos de un
umbral. Es esperable —y **metodológicamente deseable**— que ahí se concentre
el desacuerdo. Reportar la concordancia **desagregada**: casos claros vs.
casos de frontera. Un acuerdo alto solo en los casos obvios no valida nada.

---

## H3 — Calidad de los mensajes generados

**Objetivo.** Evaluar la calidad de los 35 mensajes producidos por la IA en
cinco dimensiones, con tres evaluadores independientes.

**Instrumento.** `H3-rubrica-evaluador-A.csv` / `-B.csv` / `-C.csv`
(idénticos; uno por evaluador)

### Condiciones de aplicación

1. Los tres evaluadores puntúan **de forma independiente**. No se consultan
   entre sí ni comparan resultados hasta que los tres hayan terminado.
   *Si se consultan, el CCI mide conversación, no acuerdo.*
2. No ven la prioridad asignada ni el canal de envío: eso anclaría el juicio.
3. Orden aleatorizado, distinto al de H2.
4. Escala **1 a 5**, enteros. No se permiten decimales ni casillas vacías.
5. Cada evaluador ve el valor y los productos del carrito, porque los necesita
   para juzgar precisión factual y uso de contexto.

---

## Definiciones operativas de los 5 criterios

> Estas definiciones son lo que hace que tres personas distintas puntúen
> parecido. Sin anclas explícitas, el CCI se desploma y no es culpa de los
> evaluadores: es culpa del instrumento.

### 1. Relevancia
*¿El mensaje se dirige a esta situación concreta, o serviría para cualquiera?*

| | |
|---|---|
| **1** | Genérico. Podría enviarse a cualquier cliente sin cambiar una palabra. |
| **3** | Menciona que hay un carrito pendiente, pero sin particularizar. |
| **5** | Se refiere específicamente a este carrito y a esta situación. Reemplazar los datos por los de otro cliente lo dejaría sin sentido. |

### 2. Precisión factual
*¿Todo lo que afirma es verdadero según la base de conocimientos y el carrito real?*

Datos verificables: envío gratis > $50.000 · costo $3.500 · 48hs a 3-5 días
hábiles · 3 a 12 cuotas · garantía 12 meses · devolución 30 días.

| | |
|---|---|
| **1** | Inventa datos, o contradice el carrito (productos o montos que no existen). |
| **3** | Todo correcto pero impreciso o incompleto en algún punto. |
| **5** | Cada afirmación es verificable y coincide con el carrito y la base. Cero invención. |

> Una sola afirmación falsa —un precio, un plazo, un producto que no está en el
> carrito— fuerza puntaje **1 o 2**, por bueno que sea el resto. La alucinación
> es el riesgo central de estos sistemas y la rúbrica tiene que castigarla.

### 3. Persuasión
*¿Genera motivación real para completar la compra, sin presionar?*

| | |
|---|---|
| **1** | No invita a la acción, o presiona de forma invasiva o manipuladora. |
| **3** | Invita a comprar, pero sin argumento propio: solo repite el link. |
| **5** | Construye una razón concreta para volver, con tono cordial y sin presión. Cierre claro. |

### 4. Uso de contexto
*¿Aprovecha lo que el sistema sabe del cliente?*

Elementos disponibles: nombre, productos, cantidades, valor total, link de checkout.

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
- **Promedio global** = media de los 35 promedios
- **Promedio por criterio** = para identificar dónde el sistema es más débil
- **CCI** (coeficiente de correlación intraclase) → acuerdo entre evaluadores

Para el CCI, usar el modelo de **efectos aleatorios de dos vías, acuerdo
absoluto, medidas promedio — ICC(2,k)**. Es el que corresponde cuando los mismos
tres evaluadores puntúan a todos los sujetos y se reporta la media.

Interpretación (Koo & Li, 2016):

| CCI | Fiabilidad |
|---|---|
| < 0,50 | Pobre |
| 0,50 – 0,75 | Moderada |
| 0,75 – 0,90 | Buena |
| > 0,90 | Excelente |

---

## Lo que hay que reportar sí o sí

1. **Los datos crudos**, no solo los agregados. Las 35 clasificaciones del
   experto y los 525 puntajes individuales van al anexo.
2. **La semilla de aleatorización** (`20260902`) y el procedimiento, para que
   el orden sea reproducible.
3. **El perfil de los evaluadores** (formación, experiencia) sin identificarlos.
4. **Que las sesiones son controladas**, no tráfico orgánico:

> "Se ejecutaron 35 sesiones controladas con perfiles sintéticos, diseñadas
> mediante un factorial 5×5 sobre valor de carrito y abandonos previos, más
> 10 casos de frontera en torno a los umbrales de clasificación."

Esa frase es la diferencia entre una validación técnica honesta y un dato
que no podés defender.
