# Qué mandarle a cada persona

## Regla de oro

| Archivo | ¿Se manda? |
|---|---|
| `H2-experto-planilla-ciega.csv` | ✅ solo al experto |
| `H3-rubrica-evaluador-A.csv` | ✅ solo al evaluador A |
| `H3-rubrica-evaluador-B.csv` | ✅ solo al evaluador B |
| `H3-rubrica-evaluador-C.csv` | ✅ solo al evaluador C |
| `PARA-EXPERTO-criterio.md` | ✅ solo al experto |
| `PARA-EVALUADORES-rubrica.md` | ✅ solo a los 3 evaluadores |
| `INSTRUCTIVO-H2-H3.md` | ❌ **NUNCA** — revela el diseño y las rondas |
| `H2-clave-NO-MOSTRAR-AL-EXPERTO.csv` | ❌ **NUNCA** |
| `H3-clave-NO-MOSTRAR-A-EVALUADORES.csv` | ❌ **NUNCA** |
| `datos-crudos-55-sesiones.csv` | ❌ **NUNCA** (trae las respuestas) |

**Cada evaluador recibe su propia planilla, no una compartida.** Si los tres
editan el mismo documento, ven los puntajes de los demás y el CCI deja de medir
acuerdo independiente: mide contagio.

---

## Cómo compartir

1. Google Drive → Nuevo → Subir archivo → el `.csv`
2. Click derecho sobre el archivo → Abrir con → Google Sheets
3. Botón **Compartir** → agregar el correo de esa persona → permiso **Editor**
4. Repetir uno por uno. **Cuatro documentos separados** (1 experto + 3 evaluadores).

---

## Mensaje para el EXPERTO (H2)

> Hola, te paso lo que hablamos para la validación de mi tesis.
>
> **Qué es:** desarrollé un sistema que detecta carritos abandonados en una
> tienda online y los clasifica por prioridad de recuperación. Necesito comparar
> lo que decide el sistema contra el criterio de alguien con experiencia real
> en el rubro. Ahí entrás vos.
>
> **Qué tenés que hacer:** en la planilla hay 55 sesiones. De cada una vas a ver
> el valor del carrito, los productos, la etapa que alcanzó el cliente y cuántas
> veces abandonó antes. Para cada una, completá la última columna con **Alta**,
> **Media** o **Baja**.
>
> **El criterio es tuyo.** "Prioridad de recuperación" = cuánta urgencia y
> cuántos recursos amerita ese carrito. Alta = contactarlo ya y por el canal más
> directo. Media = contactarlo, sin apuro. Baja = contacto barato o nada.
>
> **Tres cosas importantes:**
> - No te voy a decir qué contestó el sistema, justamente para no condicionarte.
> - No hay respuesta correcta. Quiero **tu** criterio profesional, no que
>   adivines una fórmula.
> - Completá las 55 de corrido, sin volver atrás a revisar las anteriores.
>
> Te lleva unos 30 a 40 minutos. Cuando termines avisame y listo.
>
> Gracias, en serio. Sin esto no puedo cerrar el capítulo.

---

## Mensaje para los EVALUADORES (H3) — el mismo para los tres

> Hola, te paso lo que hablamos para la validación de mi tesis.
>
> **Qué es:** desarrollé un sistema que genera automáticamente mensajes de
> recuperación de carritos abandonados. Necesito saber si esos mensajes son
> buenos, y para eso los evalúan tres personas por separado.
>
> **Qué tenés que hacer:** en la planilla hay 55 mensajes. De cada uno vas a ver
> el texto generado, el valor del carrito y qué productos había. Puntuá cada
> mensaje del **1 al 5** en cinco criterios:
>
> - **Relevancia** — ¿es para esta situación concreta o serviría para cualquiera?
> - **Precisión factual** — ¿todo lo que afirma es cierto según el carrito?
> - **Persuasión** — ¿da ganas de completar la compra, sin presionar?
> - **Uso de contexto** — ¿aprovecha el nombre, los productos, el monto?
> - **Claridad** — ¿se entiende de una sola lectura?
>
> **Te adjunto la rúbrica con las definiciones.** Leelo antes de arrancar:
> explica qué significa un 1, un 3 y un 5 en cada criterio. Es importante que
> los tres usemos la misma vara.
>
> **Cuatro reglas:**
> - Números enteros del 1 al 5. Nada de 3,5 ni casillas vacías.
> - **No lo comentes con los otros dos evaluadores hasta que los tres terminen.**
>   La medición justamente compara si coincidimos por separado.
> - Si un mensaje afirma algo falso —un precio, un plazo, un producto que no
>   está en el carrito— eso es un 1 o un 2 en Precisión factual, por bueno que
>   sea el resto.
> - La columna "Observaciones" es opcional, pero si algo te llama la atención
>   escribilo: me sirve para la discusión.
>
> Te lleva unos 60 a 80 minutos. Avisame cuando termines.
>
> Gracias, de verdad.

---

## Checklist antes de mandar

- [ ] Los tres evaluadores tienen **planillas distintas**, no una compartida
- [ ] Ninguno recibió un archivo con "CLAVE" o "NO-MOSTRAR" en el nombre
- [ ] Nadie recibió `datos-crudos-55-sesiones.csv`
- [ ] El experto **no** recibió las rúbricas de H3 (ni al revés)
- [ ] Adjuntaste `PARA-EVALUADORES-rubrica.md` a los evaluadores (sí o sí)
- [ ] Adjuntaste `PARA-EXPERTO-criterio.md` al experto
- [ ] **NADIE** recibió `INSTRUCTIVO-H2-H3.md`
- [ ] Les pediste que **no comenten entre ellos** hasta terminar

---

## Cuando vuelvan completas

Descargá las cuatro planillas como `.csv` y guardalas acá, en `validacion/`, con
estos nombres:

```
H2-experto-COMPLETADO.csv
H3-rubrica-evaluador-A-COMPLETADO.csv
H3-rubrica-evaluador-B-COMPLETADO.csv
H3-rubrica-evaluador-C-COMPLETADO.csv
```

Con eso se calcula:

- **H2** → concordancia simple, Kappa de Cohen, matriz de confusión 3×3, y el
  desglose casos claros vs. casos de frontera
- **H3** → promedio global, promedio por criterio, promedio por mensaje y
  CCI(2,k) entre los tres evaluadores

**No completes vos ninguna casilla que haya quedado vacía.** Si alguien se saltó
un mensaje, se lo pedís de nuevo. Un dato faltante se reporta como faltante —
nunca se rellena.
