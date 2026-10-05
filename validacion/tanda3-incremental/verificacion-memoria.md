# Verificación de la memoria conversacional (hallazgo N3-02)

Documento generado el 05/10/2026 a partir de `execution_data` de `~/.n8n/database.sqlite` y del código del
nodo de memoria de la versión de n8n instalada. Todos los textos están anonimizados con la misma regla del
proyecto: el nombre real se reemplaza por `Cliente NN`.

**Conclusión, en una línea:** **Sí.** La repetición se explica íntegramente por la memoria conversacional: el
nodo cargó el intercambio anterior del mismo cliente antes de llamar al modelo, y el modelo reprodujo su
propia respuesta previa.

---

## 1. Las ejecuciones

Seis sesiones, no siete: tres repeticiones literales y una coincidencia parcial, más las dos sesiones de
origen con las que se comparan.

| N | Escenario | Ejecución | `startedAt` (UTC) | Estado | Cliente | Prioridad | Nodo de memoria | Mensajes cargados |
|---:|---|---:|---|---|---|---|---|---:|
| 1 | I-09-0 | 158 | 2026-09-11 20:11:45.866 | success | U09 | Media | `Memoria - Media` | **0** |
| 9 | I-05-0 | 166 | 2026-09-11 20:11:51.093 | success | U05 | Media | `Memoria - Media` | **0** |
| 12 | I-05-1 | 169 | 2026-09-11 20:16:46.416 | success | U05 | Media | `Memoria - Media` | **2** |
| 14 | I-09-1 | 171 | 2026-09-11 20:16:47.618 | success | U09 | Media | `Memoria - Media` | **2** |
| 29 | I-05-2 | 186 | 2026-09-11 20:21:50.553 | success | U05 | Media | `Memoria - Media` | **4** |
| 51 | I-05-5 | 208 | 2026-09-11 20:36:45.830 | success | U05 | Baja | `Memoria - Baja` | **10** |

Las dos sesiones de origen (N 1 y N 9) son las **primeras** de su cliente en toda la tanda, y su memoria
llegó **vacía**. Las cuatro restantes recibieron historial.

---

## 2. Qué historial cargó cada una

El nodo de memoria registra en `execution_data` la acción `loadMemoryVariables` con el `chatHistory` que
entrega al agente. Los mensajes alternan `HumanMessage` (el mensaje de usuario que arma el flujo) y
`AIMessage` (la respuesta que el modelo generó en esa sesión anterior).

### N 14 (I-09-1, ejecución 171) — 2 mensajes

El historial contiene **exactamente el intercambio de la sesión N 1**, del mismo cliente, cinco minutos antes:

```
[0] HumanMessage
=Hola, soy Cliente 09. Dejé productos en mi carrito: SSD 1TB NVMe (x1) - $85000,
Webcam 1080p (x1) - $35000. El valor total es $120000 ARS.

[1] AIMessage
**Asunto:** Cliente 09, tu setup de productividad está listo

Hola Cliente 09,

Vimos que dejaste en el carrito un SSD 1TB NVMe y una Webcam 1080p. Es una dupla
perfecta: almacenamiento ultrarrápido para tu PC y video cristalino para tus
videollamadas o streaming.
[...]
```

El `HumanMessage` de la sesión nueva es **idéntico** al del historial, porque el carrito de U09 no cambió
entre I-09-0 e I-09-1: mismos productos, mismo valor de $120.000. Lo único que cambió fue el contador de
abandonos, que **no forma parte del mensaje de usuario**.

### N 12 (I-05-1, ejecución 169) — 2 mensajes

Mismo patrón: el intercambio de N 9, del mismo cliente U05, con el mismo carrito de $80.000.

### N 29 (I-05-2, ejecución 186) — 4 mensajes

Dos intercambios: los de N 9 y N 12. Los dos `AIMessage` son el mismo texto, porque N 12 ya había
reproducido el de N 9.

### N 51 (I-05-5, ejecución 208) — 10 mensajes, y cruza las tres ramas

Esta es la más reveladora. La sesión es de **prioridad Baja** y su nodo es `Memoria - Baja`, pero el historial
que recibió contiene intercambios generados en **otras ramas**:

| # | Tipo | Procedencia |
|---:|---|---|
| 0-1 | Human / AI | sesión de U05, rama Media |
| 2-3 | Human / AI | sesión de U05, rama Media |
| 4-5 | Human / AI | sesión de U05, rama Media |
| 6-7 | Human / AI | **sesión I-05-3, rama Alta (Telegram)** |
| 8-9 | Human / AI | sesión I-05-4, rama Baja |

El mensaje `[7]` no lleva el prefijo `**Asunto:**` y empieza directamente con `Hola Cliente 05,`: es el
formato de Telegram, propio del agente de **Alta** prioridad. Está dentro de la memoria del agente de **Baja**.

Esto confirma que **los cuatro nodos de memoria comparten el mismo almacenamiento**, porque los cuatro están
configurados con `sessionIdType: customKey` y la misma clave:

```
sessionKey = = ={{ $json.customer_id }}
```

La propia documentación del nodo lo describe: *"Session is automatically scoped only to this memory node. To
share a session between different memory nodes, switch Session ID to 'Define below' and use the same key in
each node."* El workflow usa exactamente esa configuración, de modo que el comportamiento es el esperado
según la herramienta, aunque no fuera el buscado.

---

## 3. ¿El texto generado es idéntico al de la sesión de origen?

Comparación carácter a carácter sobre los textos publicados en
`validacion/datos-crudos-tanda3-55-sesiones.csv`:

| Comparación | ¿Idéntico? | Similitud | Longitud |
|---|---|---:|---|
| N 14 vs N 1 | **Sí** | 100,0 % | 497 y 497 caracteres |
| N 12 vs N 9 | **Sí** | 100,0 % | 527 y 527 caracteres |
| N 29 vs N 9 | **Sí** | 100,0 % | 527 y 527 caracteres |
| N 51 vs N 9 | No | **95,2 %** | 479 y 527 caracteres |

En los tres primeros casos el texto es una copia literal, sin una sola diferencia. En N 51 la coincidencia es
parcial, lo cual es coherente con su contexto: ese agente es el de **Baja** prioridad, cuyo prompt pide un
correo más breve (máximo 6 líneas contra 12), y recibió un historial más largo y heterogéneo.

Además se verificó la procedencia de cada `AIMessage` del historial contra los 55 mensajes publicados de la
tanda: todos corresponden a mensajes efectivamente generados en sesiones anteriores del mismo cliente.

---

## 4. Longitud de la ventana

El workflow **no configura** `contextWindowLength` en ninguno de los cuatro nodos de memoria, de modo que rige
el valor por defecto de la versión instalada.

| | |
|---|---|
| Versión de n8n instalada | **2.22.6** |
| Archivo | `@n8n/n8n-nodes-langchain/dist/nodes/memory/descriptions.js`, línea 51 |
| Propiedad | `contextWindowLength` |
| **Valor por defecto** | **5** |
| Descripción en el código | *"How many past interactions the model receives as context"* |

Cinco **interacciones** equivalen a **diez mensajes**, porque cada interacción es un par
`HumanMessage` + `AIMessage`. Eso coincide exactamente con lo observado: N 51 cargó 10 mensajes, que es el
tope, pese a que el cliente U05 tenía cinco sesiones previas en la tanda. La progresión 0 → 2 → 4 → 10 de las
cuatro sesiones examinadas es la de un búfer que acumula hasta su límite.

---

## 5. Conclusión

**La repetición se explica por la memoria conversacional.** La cadena causal está documentada en los registros
de ejecución y es reproducible:

1. Los cuatro nodos de memoria usan como clave de sesión únicamente el `customer_id`, sin el nivel de
   prioridad ni un identificador de sesión. Todas las notificaciones de un mismo cliente caen en la misma
   conversación, incluso entre ramas distintas.
2. El mensaje de usuario se arma con nombre, productos y valor del carrito. En la Tanda 3 el carrito de un
   mismo cliente se repite entre ciclos, de modo que el mensaje de usuario es **idéntico** al de la sesión
   anterior. El contador de abandonos, que es lo único que varía, no entra en ese mensaje.
3. Con el intercambio anterior en el contexto y un mensaje de usuario idéntico, el modelo devuelve su propia
   respuesta previa. Es el comportamiento esperable de un modelo con temperatura baja ante un contexto que ya
   contiene la respuesta a esa misma pregunta.

No hace falta recurrir a ninguna otra explicación: no hay indicios de fallo de la API, de reintento ni de
duplicación en el registro de auditoría. Las seis ejecuciones terminaron con estado `success` y cada una
generó su propia llamada al modelo, con su propio consumo de tokens.

### Qué implica para el trabajo

- Las repeticiones **no son un defecto del prompt ni del scoring**: son consecuencia de la configuración de la
  memoria.
- Afectan a H3, porque tres de los 55 mensajes evaluados no son generaciones independientes. Dos evaluadores
  lo advirtieron por su cuenta y lo anotaron en las observaciones de la rúbrica (*"Mensaje idéntico a M-02"*,
  *"Idéntico al mensaje M-18"*), asignando la misma puntuación por consistencia.
- La corrección es de configuración, no de código: incluir en `sessionKey` el nivel de prioridad y un
  identificador de sesión, o directamente desactivar la memoria para un flujo que no es conversacional. Cada
  notificación de carrito abandonado es un evento independiente y no necesita recordar la anterior.

---

## 6. Cómo reproducirlo

| Afirmación | Cómo verificarla |
|---|---|
| Ejecuciones, horas y estados | `execution_entity` de `~/.n8n/database.sqlite`, ids 158, 166, 169, 171, 186 y 208 |
| Historial cargado por la memoria | `execution_data`, nodo `Memoria - *`, campo `ai_memory` → `loadMemoryVariables` → `chatHistory` |
| Texto generado | `execution_data`, nodo `Anthropic Chat Model*`, campo `response.generations[0][0].text` |
| Clave de sesión | el export del workflow, nodos `Memoria - *`, parámetro `sessionKey` |
| Valor por defecto de la ventana | `@n8n/n8n-nodes-langchain/dist/nodes/memory/descriptions.js`, línea 51 |
| Textos publicados | `validacion/datos-crudos-tanda3-55-sesiones.csv` |
