# El destinatario de Telegram en el workflow

Documento generado el 03/10/2026 a partir del historial de git y de las ejecuciones guardadas por n8n.
**No se escribe en ningún punto el número del identificador de Telegram**: es un dato personal. Donde hace
falta compararlo se usa un hash corto (`a44c2476`), que permite verificar coincidencias sin revelar el valor.

---

## 1. Qué valor tenía el `chatId` en el workflow v4

El nodo **`Telegram - Enviar Mensaje`** del workflow
`Sinergia Digital - Recuperación de Carritos v4 (Completo) (2).json` tenía el destinatario **fijo, escrito a
mano**: un identificador numérico de 10 dígitos, no una expresión.

```
"chatId": "=<identificador de 10 dígitos>"
```

Es decir, el nodo **no** leía el `telegram_chat_id` del cliente que estaba procesando, aunque ese dato sí
viajaba en el payload y el nodo de scoring lo exponía en su salida.

Para contrastar, el otro nodo de Telegram del workflow, `Telegram - Responder Objeción`, sí usa una
expresión: `={{ $json.body.message.chat.id }}`. Y los dos nodos de Gmail también:
`={{ $('Scoring - Clasificar Lead').item.json.email }}`. **El único nodo de envío con destinatario fijo era
el de Telegram.**

### ¿De quién era ese identificador?

**Era el identificador registrado para las diez cuentas de prueba.** Se verificó contra el payload que
recibió n8n en cada una de las 55 ejecuciones de la Tanda 3:

| | |
|---|---|
| Cuentas distintas | 10 (clientes 1 a 10) |
| Identificadores de Telegram distintos entre esas 10 cuentas | **1** |
| Cuentas sin identificador | 0 |
| ¿El valor fijo del nodo coincide con el de las cuentas? | **Sí** (hash `a44c2476` en los dos casos) |

Esto es importante y matiza el hallazgo: **las diez cuentas de prueba comparten un mismo identificador de
Telegram en la base de datos**, y ese identificador es exactamente el que estaba escrito a mano en el nodo.

**A quién pertenece la cuenta no consta en el repositorio.** No hay ningún archivo del proyecto que lo
registre. Lo único que se puede afirmar por el funcionamiento de Telegram es que tiene que ser una cuenta
que previamente inició conversación con el bot, porque un bot de Telegram no puede escribirle a quien no lo
contactó antes. Lo más plausible es que sea una cuenta del propio equipo de tesis, pero **eso es una
inferencia, no evidencia que surja de los datos.**

---

## 2. Desde qué versión estaba así

El destinatario fijo **no estuvo siempre**. Es una regresión introducida el 02/09/2026, un día antes de que
empezara la primera ronda de validación.

| Commit | Fecha | Valor del `chatId` |
|---|---|---|
| `80d7a0d` | 01/07/2026 | **Expresión por cliente:** `{{ $('Scoring - Clasificar Lead1').item.json.telegram_chat_id }}` |
| `5c82e18` | 02/09/2026 | **Fijo**, hash `a44c2476`, 10 dígitos |
| `554bd77` | 03/09/2026 | **Fijo**, hash `a44c2476` (sin cambios: ese commit solo tocó el scoring y los prompts) |
| `2b22f11` | 03/10/2026 | El v4 sigue fijo. El archivo nuevo **v5** vuelve a la expresión por cliente |

En la versión de julio el nodo se llamaba `Telegram - Enviar Mensaje1` y el de scoring,
`Scoring - Clasificar Lead1`. En la versión del 02/09 los dos perdieron el sufijo `1`, lo que indica que el
workflow fue rearmado o reimportado en n8n, y que en ese rearmado la expresión se perdió y quedó un valor
fijo en su lugar.

El commit que la introdujo es `5c82e18`, *"feat: instrumentar latencia deteccion->envio y SSL condicional"*,
que es el mismo en el que se preparó la instrumentación para medir H1. O sea que la regresión entró durante
la preparación de la validación, y **estuvo activa en las tres rondas**: Ronda 1 (02-03/09), Ronda 2 (03/09)
y Tanda 3 (11/09).

---

## 3. A quién le llegaron los 11 mensajes de prioridad Alta de la Tanda 3

Las once sesiones de prioridad Alta, que son las que se notifican por Telegram:

| N | Escenario | Cuenta | Prioridad | Canal |
|---:|---|---|---|---|
| 3 | I-01-0 | U01 | Alta | Telegram |
| 4 | I-07-0 | U07 | Alta | Telegram |
| 10 | I-03-0 | U03 | Alta | Telegram |
| 16 | I-04-1 | U04 | Alta | Telegram |
| 19 | I-10-1 | U10 | Alta | Telegram |
| 20 | I-02-1 | U02 | Alta | Telegram |
| 27 | I-04-2 | U04 | Alta | Telegram |
| 30 | I-01-2 | U01 | Alta | Telegram |
| 32 | I-08-3 | U08 | Alta | Telegram |
| 36 | I-05-3 | U05 | Alta | Telegram |
| 39 | I-02-3 | U02 | Alta | Telegram |

Corresponden a **ocho cuentas distintas**: U01, U02, U03, U04, U05, U07, U08 y U10.

**Los once mensajes llegaron a una sola cuenta de Telegram**, la del identificador fijo del nodo.

Ahora bien, y esto es lo que hay que decir con precisión: **ese resultado no lo causó el valor fijo del
nodo.** Como las diez cuentas de prueba comparten el mismo identificador de Telegram en la base de datos, el
destino habría sido idéntico aunque el nodo hubiera usado la expresión por cliente. El valor escrito a mano
era redundante con los datos, no contradictorio.

### Qué significa para la tesis

Hay que separar tres afirmaciones que es fácil mezclar:

1. **El enrutamiento por canal funcionó.** Las 55 sesiones salieron por el canal que les correspondía según
   el scoring: las 11 de prioridad Alta por Telegram y las 44 de Media y Baja por correo. Eso es verificable
   y se sostiene.
2. **El envío por correo sí fue individual.** Los nodos de Gmail usaron la dirección de cada cliente, y en
   la Tanda 3 hubo 10 direcciones distintas. Eso también se sostiene.
3. **El envío por Telegram no fue individual, y no podía serlo.** No por un defecto del nodo, sino porque
   las diez cuentas de prueba apuntan a un único destino de Telegram. El canal se ejercitó, el mensaje se
   entregó y la API confirmó la recepción, pero **no se demostró la entrega diferenciada a once
   destinatarios distintos**, porque esos destinatarios no existían como tales en el entorno de prueba.

Si en el documento hay una frase del tipo *"los clientes con Telegram Chat ID registrado y clasificación de
Alta Prioridad recibieron la notificación por Telegram"*, conviene reformularla. Una redacción defendible:

> *"Las once sesiones clasificadas como Alta se enrutaron por Telegram y la API confirmó la recepción en
> todos los casos. Las diez cuentas de prueba comparten un mismo identificador de Telegram, de modo que la
> validación acredita el funcionamiento del canal, no la entrega diferenciada a destinatarios distintos. La
> entrega individualizada sí quedó acreditada en el canal de correo, con diez direcciones distintas."*

### Corrección de lo que dije antes

En el mensaje anterior y en el cuerpo del commit `2b22f11` describí este hallazgo diciendo que el nodo
*"deja de usar un chat id fijo y pasa a tomar el del cliente"*, dando a entender que el valor fijo estaba
pisando datos por cliente que existían y eran distintos. **Eso no es exacto.** Los datos por cliente existen,
pero son todos iguales entre sí e iguales al valor fijo. El cambio en el v5 sigue siendo correcto y
conveniente, porque es lo que hace falta para que el sistema funcione con usuarios reales distintos, pero
**no habría cambiado el resultado de la Tanda 3**.

---

## 4. Qué conviene hacer

1. **Corregir la redacción de la integridad omnicanal** en los términos del punto anterior.
2. **Si se quiere acreditar entrega diferenciada por Telegram**, hace falta que las cuentas de prueba tengan
   identificadores distintos, lo que implica que varias personas inicien conversación con el bot. Es una
   corrida nueva, no un arreglo de código.
3. **El `chatId` fijo ya está corregido** en el archivo nuevo
   `Sinergia Digital - Recuperacion de Carritos v5 (Header Auth).json`, que vuelve a la expresión por
   cliente. El export v4 queda intacto, porque es la evidencia de qué corrió en la Tanda 3 y está apuntado
   por el tag `tfi-validacion-tanda3`.
4. **El identificador sigue publicado** dentro del export v4, que está commiteado y en GitHub desde el
   02/09/2026. Si se quiere sacarlo del repositorio hay que reescribir el historial, que es una operación
   aparte. Mientras tanto, conviene no reproducirlo en el texto de la tesis ni en los anexos.

---

## Fuentes

| Dato | Fuente |
|---|---|
| Valor del `chatId` en cada versión | `git ls-tree` + `git show` sobre los commits de `n8n-workflows/` |
| Identificador que viajó por cliente | `execution_data` de `~/.n8n/database.sqlite`, ejecuciones 158 a 212, campo `body.telegram_chat_id` del nodo Webhook |
| Canal y prioridad de cada sesión | `validacion/datos-crudos-tanda3-55-sesiones.csv` |
| Numeración N de las sesiones | `validacion/T3-ANEXO-E-55-sesiones.csv` |
| Configuración de los nodos de Gmail | el mismo export v4 |
