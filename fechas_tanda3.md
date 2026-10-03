# Fechas y horas de las ejecuciones de la Tanda 3

Ejecuciones **158 a 212** de n8n, que son las 55 sesiones de la Tanda 3.

**Fuentes**

| Dato | De dónde sale |
|---|---|
| `id`, `startedAt`, `stoppedAt`, estado | tabla `execution_entity` de `~/.n8n/database.sqlite` |
| `Escenario` | `validacion/_privado/tanda3-IDENTIFICABLE (2).csv`, columna `Escenario` |
| `N` de sesión | `validacion/T3-ANEXO-E-55-sesiones.csv`, orden cronológico de detección |

Los valores de `startedAt` y `stoppedAt` se transcriben **tal cual los guarda n8n**, en la hora local del
servidor donde corrió. La columna de duración es la resta de esas dos marcas.

Se verificó que los 55 escenarios del archivo identificable coincidan exactamente con los del anexo: el
cruce es completo y unívoco, sin faltantes ni duplicados.

> **Advertencia.** La columna `Timestamp` del archivo `tanda3-IDENTIFICABLE (2).csv` contiene fechas
> repartidas entre el 01/09 y el 13/09/2026 que **no corresponden a ninguna ejecución registrada**. De ese
> archivo se toma únicamente el `Escenario`. Las fechas y horas de esta tabla provienen de la base de n8n,
> que es la fuente autoritativa. Todas las demás columnas de ese archivo (valor, contador, prioridad,
> canal, latencia, estado y texto del mensaje) sí coinciden con n8n.

---

## Tabla

| id | startedAt | stoppedAt | Duración (ms) | N | Escenario |
|---:|---|---|---:|---:|---|
| 158 | 2026-09-11 20:11:45.866 | 2026-09-11 20:11:53.623 | 7757 | 1 | I-09-0 |
| 159 | 2026-09-11 20:11:46.801 | 2026-09-11 20:11:53.489 | 6688 | 2 | I-06-0 |
| 160 | 2026-09-11 20:11:47.410 | 2026-09-11 20:11:53.446 | 6036 | 3 | I-01-0 |
| 161 | 2026-09-11 20:11:48.036 | 2026-09-11 20:11:53.641 | 5605 | 4 | I-07-0 |
| 162 | 2026-09-11 20:11:48.632 | 2026-09-11 20:11:54.487 | 5855 | 5 | I-02-0 |
| 163 | 2026-09-11 20:11:49.227 | 2026-09-11 20:11:56.752 | 7525 | 6 | I-10-0 |
| 164 | 2026-09-11 20:11:49.889 | 2026-09-11 20:11:54.659 | 4770 | 7 | I-04-0 |
| 165 | 2026-09-11 20:11:50.490 | 2026-09-11 20:11:55.081 | 4591 | 8 | I-08-0 |
| 166 | 2026-09-11 20:11:51.093 | 2026-09-11 20:11:55.616 | 4523 | 9 | I-05-0 |
| 167 | 2026-09-11 20:11:51.702 | 2026-09-11 20:11:56.398 | 4696 | 10 | I-03-0 |
| 168 | 2026-09-11 20:16:45.814 | 2026-09-11 20:16:51.440 | 5626 | 11 | I-07-1 |
| 169 | 2026-09-11 20:16:46.416 | 2026-09-11 20:16:51.608 | 5192 | 12 | I-05-1 |
| 170 | 2026-09-11 20:16:47.018 | 2026-09-11 20:16:52.056 | 5038 | 13 | I-01-1 |
| 171 | 2026-09-11 20:16:47.618 | 2026-09-11 20:16:51.852 | 4234 | 14 | I-09-1 |
| 172 | 2026-09-11 20:16:48.225 | 2026-09-11 20:16:52.573 | 4348 | 15 | I-08-1 |
| 173 | 2026-09-11 20:16:48.823 | 2026-09-11 20:16:53.480 | 4657 | 16 | I-04-1 |
| 174 | 2026-09-11 20:16:49.423 | 2026-09-11 20:16:53.280 | 3857 | 17 | I-06-1 |
| 175 | 2026-09-11 20:16:50.016 | 2026-09-11 20:16:54.265 | 4249 | 18 | I-03-1 |
| 176 | 2026-09-11 20:16:50.602 | 2026-09-11 20:16:54.644 | 4042 | 19 | I-10-1 |
| 177 | 2026-09-11 20:16:51.198 | 2026-09-11 20:16:55.567 | 4369 | 20 | I-02-1 |
| 178 | 2026-09-11 20:21:45.817 | 2026-09-11 20:21:50.510 | 4693 | 21 | I-02-2 |
| 179 | 2026-09-11 20:21:46.407 | 2026-09-11 20:21:50.488 | 4081 | 22 | I-08-2 |
| 180 | 2026-09-11 20:21:46.999 | 2026-09-11 20:21:51.493 | 4494 | 23 | I-10-2 |
| 181 | 2026-09-11 20:21:47.588 | 2026-09-11 20:21:51.650 | 4062 | 24 | I-07-2 |
| 182 | 2026-09-11 20:21:48.179 | 2026-09-11 20:21:52.632 | 4453 | 25 | I-03-2 |
| 183 | 2026-09-11 20:21:48.782 | 2026-09-11 20:21:52.338 | 3556 | 26 | I-09-2 |
| 184 | 2026-09-11 20:21:49.376 | 2026-09-11 20:22:08.630 | 19254 | 27 | I-04-2 |
| 185 | 2026-09-11 20:21:49.962 | 2026-09-11 20:21:54.377 | 4415 | 28 | I-06-2 |
| 186 | 2026-09-11 20:21:50.553 | 2026-09-11 20:21:53.996 | 3443 | 29 | I-05-2 |
| 187 | 2026-09-11 20:21:51.148 | 2026-09-11 20:22:10.509 | 19361 | 30 | I-01-2 |
| 188 | 2026-09-11 20:26:45.789 | 2026-09-11 20:26:49.839 | 4050 | 31 | I-10-3 |
| 189 | 2026-09-11 20:26:46.378 | 2026-09-11 20:26:51.140 | 4762 | 32 | I-08-3 |
| 190 | 2026-09-11 20:26:46.970 | 2026-09-11 20:26:51.043 | 4073 | 33 | I-03-3 |
| 191 | 2026-09-11 20:26:47.561 | 2026-09-11 20:26:51.542 | 3981 | 34 | I-01-3 |
| 192 | 2026-09-11 20:26:48.154 | 2026-09-11 20:26:52.317 | 4163 | 35 | I-07-3 |
| 193 | 2026-09-11 20:26:48.744 | 2026-09-11 20:26:53.290 | 4546 | 36 | I-05-3 |
| 194 | 2026-09-11 20:26:49.332 | 2026-09-11 20:26:53.061 | 3729 | 37 | I-04-3 |
| 195 | 2026-09-11 20:26:49.922 | 2026-09-11 20:26:53.954 | 4032 | 38 | I-06-3 |
| 196 | 2026-09-11 20:26:50.514 | 2026-09-11 20:26:54.783 | 4269 | 39 | I-02-3 |
| 197 | 2026-09-11 20:26:51.110 | 2026-09-11 20:26:54.854 | 3744 | 40 | I-09-3 |
| 198 | 2026-09-11 20:31:45.826 | 2026-09-11 20:31:50.389 | 4563 | 41 | I-05-4 |
| 199 | 2026-09-11 20:31:46.430 | 2026-09-11 20:31:51.040 | 4610 | 42 | I-08-4 |
| 200 | 2026-09-11 20:31:47.024 | 2026-09-11 20:31:51.809 | 4785 | 43 | I-02-4 |
| 201 | 2026-09-11 20:31:47.623 | 2026-09-11 20:31:51.736 | 4113 | 44 | I-03-4 |
| 202 | 2026-09-11 20:31:48.221 | 2026-09-11 20:31:51.707 | 3486 | 45 | I-01-4 |
| 203 | 2026-09-11 20:31:48.829 | 2026-09-11 20:31:52.565 | 3736 | 46 | I-07-4 |
| 204 | 2026-09-11 20:31:49.421 | 2026-09-11 20:31:52.700 | 3279 | 47 | I-06-4 |
| 205 | 2026-09-11 20:31:50.014 | 2026-09-11 20:31:53.943 | 3929 | 48 | I-10-4 |
| 206 | 2026-09-11 20:31:50.609 | 2026-09-11 20:31:54.275 | 3666 | 49 | I-09-4 |
| 207 | 2026-09-11 20:31:51.196 | 2026-09-11 20:31:55.213 | 4017 | 50 | I-04-4 |
| 208 | 2026-09-11 20:36:45.830 | 2026-09-11 20:36:49.267 | 3437 | 51 | I-05-5 |
| 209 | 2026-09-11 20:36:46.452 | 2026-09-11 20:36:49.820 | 3368 | 52 | I-03-5 |
| 210 | 2026-09-11 20:36:47.044 | 2026-09-11 20:36:51.064 | 4019 | 53 | I-01-5 |
| 211 | 2026-09-11 20:36:47.639 | 2026-09-11 20:36:51.650 | 4011 | 54 | I-04-5 |
| 212 | 2026-09-11 20:36:48.227 | 2026-09-11 20:36:51.730 | 3503 | 55 | I-02-5 |

---

## Resumen

| | |
|---|---|
| Ejecuciones | 55, de la 158 a la 212, sin saltos |
| Primera en arrancar | 2026-09-11 20:11:45.866 (sesión N 1, escenario I-09-0) |
| Última en terminar | 2026-09-11 20:36:51.730 |
| Fecha | **todas el 11/09/2026** |
| Estado en n8n | `success` en las 55 |
| Duración mínima / mediana / máxima | 3279 ms / 4269 ms / 19361 ms |

### Los seis ciclos del job

Las 55 sesiones no se dispararon de corrido: se agrupan en seis ciclos del job de detección del backend,
separados por unos cinco minutos, que es el intervalo con el que corre ese job.

| Ciclo | Hora de inicio | Sesiones | Rango de ejecuciones |
|---:|---|---:|---|
| 1 | 20:11 | 10 | 158 a 167 |
| 2 | 20:16 | 10 | 168 a 177 |
| 3 | 20:21 | 10 | 178 a 187 |
| 4 | 20:26 | 10 | 188 a 197 |
| 5 | 20:31 | 10 | 198 a 207 |
| 6 | 20:36 | 5 | 208 a 212 |

La ventana completa va de las **20:11:45.866** a las **20:36:51.730**, es decir, **menos de 26 minutos**.

### Las dos ejecuciones más largas

Las dos que superan los 19 segundos son los valores atípicos de H1, y las dos por la misma causa: el nodo
de envío por Telegram tardó unos 15,9 s en responder. La generación con IA tardó menos de 2 s en ambas y el
scoring, 5 y 8 milisegundos. Pertenecen al mismo ciclo, el de las 20:21, de modo que fue un episodio
puntual de la API y no una degradación del sistema. El desglose nodo por nodo está en
`validacion/T3-FIGURA-nodos-exec-184-187.png`.

| id | N | Escenario | Duración (ms) |
|---:|---:|---|---:|
| 187 | 30 | I-01-2 | 19361 |
| 184 | 27 | I-04-2 | 19254 |

---

## Por qué la ventana es de 26 minutos

La duración total no es una corrida apurada ni una limitación de recursos: **es el mínimo que el diseño
permite**, y se deduce de dos parámetros del sistema.

La Tanda 3 existe para probar una cosa concreta: que el contador de abandonos lo incremente el backend, como
en producción, en lugar de fijarse a mano antes de cada escenario. Para eso cada cuenta tiene que abandonar
varias veces **en secuencia**: la misma cuenta pasa por contador 0, después 1, después 2, y así. Un nivel del
contador no puede medirse hasta que el anterior se haya notificado y el backend haya sumado uno.

Eso obliga a seis ciclos consecutivos, y el ritmo lo impone el job de detección del backend:

| Parámetro | Valor | Dónde está |
|---|---|---|
| Intervalo del job de detección | **5 minutos** | `abandonedCartService.js`, `INTERVAL_MS = 5 * 60 * 1000` |
| Inactividad exigida para considerar abandono | **2 minutos** | `abandonedCartService.js`, `INTERVAL '2 minutes'` |
| Ciclos necesarios | **6** | contador 0 a 5, según `plan-tanda3.json` |

Cinco intervalos de cinco minutos entre seis ciclos dan **25 minutos**. La corrida duró 25 min 06 s. Es decir
que la ventana observada **coincide con el piso teórico del diseño**: no había forma de hacerla más corta, y
alargarla no habría aportado nada, porque la variable bajo estudio es el contador, no el tiempo transcurrido.

La correspondencia entre ciclo y nivel del contador es exacta:

| Ciclo | Hora de inicio | Separación | Sesiones | Nivel del contador |
|---:|---|---|---:|---:|
| 1 | 20:11:45 | — | 10 | 0 |
| 2 | 20:16:45 | 5,0 min | 10 | 1 |
| 3 | 20:21:45 | 5,0 min | 10 | 2 |
| 4 | 20:26:45 | 5,0 min | 10 | 3 |
| 5 | 20:31:45 | 5,0 min | 10 | 4 |
| 6 | 20:36:45 | 5,0 min | 5 | 5 |

Cada ciclo contiene **un único nivel de contador**, sin mezcla. El sexto tiene cinco sesiones y no diez porque
solo las cuentas 1 a 5 llegan al contador 5; las cuentas 6 a 10 abandonan cinco veces y terminan en 4. Las
separaciones son de 5,0 minutos exactos en los cinco saltos, que es el intervalo del job: **el ritmo lo marcó
el sistema, no el script**. El script solo montaba los carritos y esperaba.

---

## Qué no queda afectado por la ventana corta

Las tres hipótesis se miden **por sesión**, y ninguna tiene un componente temporal entre sesiones:

| Hipótesis | Qué mide | ¿Depende de cuándo ocurrió la sesión? |
|---|---|---|
| **H1** | Latencia desde la detección hasta el registro de auditoría, dentro de cada ejecución | **No.** Cada sesión aporta su propio intervalo, medido de punta a punta |
| **H2** | Concordancia entre el scoring del algoritmo y la clasificación del experto | **No.** El scoring es función del valor del carrito y del contador |
| **H3** | Calidad del mensaje según la rúbrica de cinco criterios | **No.** Depende del prompt y del contenido del carrito |

Que las 55 sesiones ocurran en 26 minutos o en 26 días no cambia ninguno de esos tres valores.

---

## Qué sí limita, y conviene declararlo

Hay que ser preciso también con lo que la ventana corta **no** permite afirmar:

1. **No se muestreó variabilidad temporal.** Las 55 sesiones corrieron bajo las mismas condiciones de red, de
   carga del servidor y de disponibilidad de las APIs externas. Una corrida repartida en días habría
   capturado franjas horarias y estados de servicio distintos.
2. **Los valores atípicos lo demuestran.** Las dos ejecuciones de ~19 s cayeron en el **mismo ciclo**, el de
   las 20:21, porque la API de Telegram tuvo un episodio puntual. En una ventana de 26 minutos, un incidente
   de la API afecta a un ciclo entero y no se compensa; en una ventana larga, se diluye. Dicho al revés: la
   medición de latencia es sensible a condiciones externas que esta tanda no muestreó.
3. **No representa una distribución realista de abandonos.** En producción los abandonos llegan dispersos a
   lo largo del día. Acá llegan en lotes de diez, cada cinco minutos. Lo que se validó es el pipeline, no el
   patrón temporal de la demanda.

Nada de esto invalida H1, H2 ni H3. Son limitaciones de validez externa, y se declaran como tales.

---

## Redacción sugerida para la tesis

> *Las 55 sesiones de la tercera tanda se ejecutaron el 11 de septiembre de 2026 entre las 20:11 y las 20:36,
> en una ventana de 25 minutos. Esa duración responde al diseño y no a una restricción operativa: la tanda
> evalúa el incremento del contador de abandonos por parte del backend, lo que exige que cada cuenta abandone
> de forma secuencial, un nivel de contador por ciclo. Con un job de detección que se ejecuta cada cinco
> minutos, los seis ciclos necesarios para recorrer los niveles 0 a 5 ocupan un mínimo de veinticinco
> minutos, que es exactamente lo que se observa. Las separaciones entre ciclos fueron de 5,0 minutos en los
> cinco saltos, marcadas por el propio job y no por el script de ejecución.*
>
> *Las tres hipótesis se miden por sesión y carecen de componente temporal entre sesiones, de modo que la
> compresión de la ventana no afecta sus resultados. Sí constituye una limitación de validez externa: las 55
> sesiones comparten condiciones de red, carga y disponibilidad de las APIs externas. Los dos valores
> atípicos de latencia, ambos del mismo ciclo y atribuibles a un episodio puntual de la API de mensajería,
> ilustran esa sensibilidad. Una replicación distribuida en el tiempo permitiría caracterizar esa
> variabilidad.*

---

## Verificación

Todo lo afirmado en esta sección es reproducible:

| Afirmación | Cómo verificarla |
|---|---|
| Las 55 ejecuciones y sus marcas de tiempo | `execution_entity` de `~/.n8n/database.sqlite`, ids 158 a 212 |
| Intervalo del job y umbral de inactividad | `technova-backend/src/services/abandonedCartService.js` |
| Seis ciclos y el nivel de contador de cada uno | `validacion/tanda3-incremental/plan-tanda3.json`, campos `ciclo` y `ab_esperado` |
| Que el contador lo incrementó el backend | `run_validacion_tanda3.js` escribe el contador una sola vez, en 0; después solo verifica |
| Registro de la corrida | `validacion/tanda3-incremental/run-tanda3-resultados.json` |
