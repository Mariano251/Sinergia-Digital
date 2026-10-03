# Rondas de validación cerradas

Esta carpeta agrupa los datos e instrumentos de las **rondas 1 y 2**, que ya están cerradas. Los archivos se
movieron acá con `git mv`, sin tocar una sola línea de su contenido: git los registra como renombres puros
(`R100`), es decir, byte a byte idénticos a como estaban en `validacion/`.

Los datos de la **Tanda 3**, que es la ronda vigente, siguen en `validacion/`.

---

## Qué ronda fue cada una

| Ronda | Fecha | Ejecuciones de n8n | Sesiones | Infraestructura | Algoritmo de scoring |
|---|---|---|---|---|---|
| **v21 (sobre Render)** | abril a julio de 2026 | fuera del rango conservado | 55 | **Render**, plan gratuito | el que estuviera vigente entonces |
| **Ronda 1** | 02 y 03/09/2026 | 47 a 101 | 55 | local | ponderado 50 % valor + 30 % abandono + 20 % etapa |
| **Ronda 2** | 03/09/2026 | 102 a 157 | 55 | local | por tramos de valor, con castigo por abandono |
| *(Tanda 3, vigente)* | 11/09/2026 | 158 a 212 | 55 | local | por tramos de valor, con castigo por abandono |

> **De la v21 no hay archivos en este repositorio.** Sus 55 sesiones (identificadores U01 a U20, latencia
> mediana de 94 s, cuatro valores atípicos por arranque en frío del servidor de Render) provienen de una
> exportación del panel de auditoría de Google Sheets que nunca se commiteó, y figuran únicamente dentro del
> documento de la tesis. La fila queda en esta tabla para dejar constancia de que esa ronda existió y de que
> sus latencias **no son comparables** con las de las rondas 1, 2 y 3, que corrieron en local.

---

## Ronda 1 — 02 y 03/09/2026

Diseño: 35 sesiones por disparo manual (factorial 5×5 sobre valor de carrito y abandonos previos, más 10
casos de frontera en torno a los umbrales) y 20 por el job automático de detección.

| Archivo | Filas | Qué es |
|---|---:|---|
| `datos-crudos-55-sesiones.csv` | 55 | Tabla seudonimizada de la ronda |
| `H2-experto-planilla-ciega.csv` | 55 | Instrumento ciego entregado al experto 1 |
| `H2-clave-NO-MOSTRAR-AL-EXPERTO.csv` | 55 | Clave de descifrado de ese instrumento |
| `Evaluación_H2_COMPLETO.csv` | 55 | Respuestas devueltas por el experto 1 |
| `H3-rubrica-evaluador-A.csv` | 55 | Rúbrica entregada al evaluador A |
| `H3-rubrica-evaluador-B.csv` | 55 | Rúbrica entregada al evaluador B |
| `H3-rubrica-evaluador-C.csv` | 55 | Rúbrica entregada al evaluador C |
| `H3-clave-NO-MOSTRAR-A-EVALUADORES.csv` | 55 | Clave de descifrado de las rúbricas |
| `Evaluador_A_H3_COMPLETO.csv` | 55 | Puntajes devueltos por el evaluador A |
| `Evaluador_B_H3_COMPLETO.csv` | 55 | Puntajes devueltos por el evaluador B |
| `Evaluador_C_H3_COMPLETO.csv` | 55 | Puntajes devueltos por el evaluador C |

Resultados: H1 mediana 3,62 s y 55/55 bajo el umbral; **H2 24/55 = 43,6 % con Kappa de Cohen 0,084**, que es
prácticamente acuerdo por azar; **H3 promedio global 3,55 / 5** con CCI(2,k) 0,914.

Esos dos incumplimientos son los que motivaron el rediseño documentado en `../REDISENO-SCORING-H2.md` y
`../PROMPTS-MEJORADOS-H3.md`, y el paso a la Ronda 2.

---

## Ronda 2 — 03/09/2026

Se repitieron **los mismos 55 escenarios** de la Ronda 1 con el scoring y los prompts corregidos, de modo que
la comparación antes/después fuera lo más limpia posible.

### Datos e instrumentos

| Archivo | Filas | Qué es |
|---|---:|---|
| `datos-crudos-ronda2-55-sesiones.csv` | 55 | Tabla seudonimizada de la ronda |
| `R2-H2-experto2-planilla-ciega.csv` | 55 | Instrumento ciego del experto 2 (semilla 20260905) |
| `R2-H2-experto2-planilla-completa.csv` | 55 | Respuestas devueltas por el experto 2 |
| `R2-H2-clave-NO-MOSTRAR.csv` | 55 | Clave del instrumento del experto 2 |
| `R3-H2-experto3-planilla-ciega.csv` | 55 | Instrumento ciego del experto 3 (semilla 20260908) |
| `R3-H2-experto3-planilla-completa.csv` | 55 | Respuestas devueltas por el experto 3 |
| `R3-H2-clave-NO-MOSTRAR.csv` | 55 | Clave del instrumento del experto 3 |
| `R2-H3-rubrica-evaluador-A.csv` | 55 | Rúbrica entregada al evaluador A |
| `R2-H3-rubrica-evaluador-B.csv` | 55 | Rúbrica entregada al evaluador B |
| `R2-H3-rubrica-evaluador-C.csv` | 55 | Rúbrica entregada al evaluador C |
| `R2-H3-rubrica-evaluador-A_completada.csv` | 55 | Puntajes devueltos por el evaluador A |
| `R2-H3-rubrica-evaluador-B-completada.csv` | 55 | Puntajes devueltos por el evaluador B |
| `R2-H3-rubrica-evaluador-C-completa.csv` | 55 | Puntajes devueltos por el evaluador C |
| `R2-H3-clave-NO-MOSTRAR.csv` | 55 | Clave de las rúbricas |

### Anexos y análisis

| Archivo | Filas | Qué es |
|---|---:|---|
| `ANEXO-E-ronda2-55-sesiones.csv` | 55 | Tabla del Anexo E de la ronda |
| `ANEXO-E-ronda2-informe.md` | — | Informe de evidencia primaria, con la salida literal del análisis |
| `ANEXO-tabla-55-sesiones-ronda2.csv` | 55 | Tabla de las 55 sesiones para el documento |
| `ANEXO-E-H1-latencias-ronda2.csv` | 55 | Latencia de cada sesión |
| `ANEXO-E-H2-experto2-ronda2.csv` | 55 | Clasificación individual del experto 2 |
| `ANEXO-E-H2-experto3-ronda2.csv` | 55 | Clasificación individual del experto 3 |
| `ANEXO-E-H2-experto2-vs-experto3.csv` | 55 | Acuerdo entre los dos expertos, con matriz de confusión |
| `ANEXO-E-H3-rubrica-ronda2.csv` | 55 | Promedio de rúbrica por sesión |
| `ANEXO-E-H3-rubrica-detalle-ronda2.csv` | 55 | Promedio por criterio y por sesión |
| `ANEXO-E-bis-H3-por-sesion.csv` | 55 | Anexo E-bis: desglose de H3 por sesión y criterio |
| `ANEXO-E-H3-tabla3-criterios.csv` | 5 | Estadísticos por criterio (Tabla 3) |
| `analisis_fleiss_3expertos.py` | — | Kappa de Fleiss entre los tres expertos y los Kappa por pares |

Resultados: H1 mediana 3,36 s y 55/55 bajo el umbral; H2 **35/55 = 63,6 % (κ 0,430)** contra el experto 2 y
**39/55 = 70,9 % (κ 0,532)** contra el experto 3, los dos por debajo del umbral del 85 %; acuerdo entre
expertos 49/55 = 89,1 % (κ 0,829); H3 promedio global **4,79 / 5** con CCI(2,k) 0,813.

> **Corrección sobre el CCI.** El intervalo publicado en `ANEXO-E-ronda2-informe.md` es [0,698 , 0,887] con
> 72,9 grados de libertad. El valor correcto es **[0,702 , 0,886] con 79,7 grados de libertad**: la fórmula
> de Satterthwaite de McGraw y Wong usa el CCI(2,1) y en el informe se había usado el CCI(2,k). El estimador
> puntual (0,813) no cambia y la conclusión tampoco. La implementación corregida está en
> `../tanda3-incremental/estadistica.py`, verificada contra el ejemplo de referencia de Shrout y Fleiss
> (1979). **El archivo del informe se conserva tal como se publicó**; esta nota documenta la diferencia.

> **Sobre el origen del código de scoring.** El informe afirma que el algoritmo se extrajo del snapshot
> `execution_data.workflowData` de la ejecución 110. Ese campo **no existe** en la base de n8n: las claves de
> `execution_data` son `version`, `startData`, `resultData`, `executionData` y `resumeToken`. La verificación
> que sí es reproducible consiste en aplicar las dos fórmulas candidatas a los datos de cada ronda: la
> ponderada reproduce 55/55 de la Ronda 1 y la de tramos reproduce 55/55 de las Rondas 2 y 3.

---

## Instrumento ciego combinado (Rondas 1 y 2)

| Archivo | Filas | Qué es |
|---|---:|---|
| `CIEGO110-H3-rubrica-evaluador-A.csv` | 110 | Los 55 mensajes de cada ronda mezclados, sin etiqueta de versión |
| `CIEGO110-H3-rubrica-evaluador-B.csv` | 110 | Ídem, para el evaluador B |
| `CIEGO110-H3-rubrica-evaluador-C.csv` | 110 | Ídem, para el evaluador C |
| `CIEGO110-H3-clave-NO-MOSTRAR.csv` | 110 | Clave de descifrado |

Generados con semilla 20260907 como alternativa excluyente a las rúbricas `R2-H3-*`: si los evaluadores veían
primero los 55 mensajes nuevos, al recibir los 110 reconocían cuáles eran y la ceguera se perdía. **Se aplicó
el formato de 55**, de modo que estos instrumentos quedaron sin usar.

---

## Qué quedó en `validacion/`

No se movieron los documentos que se siguen usando o que son transversales a todas las rondas:

| Archivo | Por qué queda |
|---|---|
| `INSTRUCTIVO-H2-H3.md` | Instructivo de aplicación, reutilizado sin cambios en la Tanda 3 |
| `PARA-EXPERTO-criterio.md` | Consigna entregada a los expertos, reutilizada en la Tanda 3 |
| `PARA-EVALUADORES-rubrica.md` | Consigna entregada a los evaluadores, reutilizada en la Tanda 3 |
| `MENSAJES-PARA-ENVIAR.md` | Guía de qué archivo recibe cada participante y cuál nunca |
| `REDISENO-SCORING-H2.md` | Explica el scoring hoy vigente, nacido del fracaso de H2 en la Ronda 1 |
| `PROMPTS-MEJORADOS-H3.md` | Explica los prompts hoy vigentes |
| `ANEXO-cambios-entre-tandas.md` | Anexo auditable de los cambios entre rondas; es transversal |

---

## Referencias desde el código

Al mover los archivos hubo que actualizar dos suites de pruebas, que usan planillas de la Ronda 2 como
referencia de formato y como banco de prueba de los estadísticos:

- `../tanda3-incremental/test_armar_tanda3.py` y `../tanda3-incremental/test_estadistica.py` ahora resuelven
  esas rutas contra `validacion/historico/`.
- `analisis_fleiss_3expertos.py` **no necesitó cambios**: resuelve sus rutas contra su propio directorio, y se
  movió junto con los archivos que lee.

Verificado después del movimiento: las 56 pruebas de `pytest` pasan, y el script de Fleiss sigue devolviendo
los mismos valores (Kappa de Fleiss 0,597; pares 0,430 / 0,532 / 0,829).

---

## Datos identificables

Ninguno de los archivos de esta carpeta contiene nombres reales, direcciones de correo ni identificadores de
mensajería: están seudonimizados como `Cliente NN` y `clienteNN@ejemplo.test`, también dentro del texto de los
mensajes generados. Los originales identificables viven en `validacion/_privado/`, que está excluida del
repositorio por `.gitignore`.
