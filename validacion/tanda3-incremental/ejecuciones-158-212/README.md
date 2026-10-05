# Ejecuciones 158 a 212 de n8n — Tanda 3, anonimizadas

Exportación de los registros de ejecución de las 55 sesiones de la Tanda 3, para que el pipeline sea
auditable sin necesidad de acceder a la base de n8n.

**Fuente:** tablas `execution_entity` y `execution_data` de `~/.n8n/database.sqlite`.
**Fecha de la corrida:** 11/09/2026.
**Zona horaria: UTC.** Equivale a las 17:11–17:36 en hora de Argentina (UTC−3). La verificación está en
`../../../fechas_tanda3.md`.

## Archivos

| Archivo | Filas | Contenido |
|---|---:|---|
| `ejecuciones.csv` | 55 | Una fila por ejecución, sin el detalle de nodos |
| `nodos.csv` | 495 | Una fila por nodo ejecutado, con su tiempo de inicio y su duración |
| `ejecuciones.json` | 55 | Lo mismo, anidado: cada ejecución con su lista de nodos |

### Columnas de `ejecuciones.csv`

| Columna | Qué es |
|---|---|
| `id` | Identificador de la ejecución en n8n |
| `startedAt_utc`, `stoppedAt_utc` | Marcas de inicio y fin, en UTC, tal como las guarda n8n |
| `duracion_ms` | Diferencia entre ambas |
| `status` | Estado reportado por n8n (`success` en las 55) |
| `N_sesion` | Número de sesión del Anexo E, en orden cronológico de detección |
| `escenario` | Identificador del plan: `I-<cuenta>-<abandonos previos>` |
| `cliente` | Identificador anonimizado, `U01` a `U10` |
| `canal`, `prioridad` | Canal de notificación y clasificación del algoritmo |

### Columnas de `nodos.csv`

| Columna | Qué es |
|---|---|
| `exec_id`, `escenario`, `cliente` | Claves para cruzar con `ejecuciones.csv` |
| `nodo` | Nombre del nodo en el workflow |
| `inicio_relativo_ms` | Milisegundos desde el arranque del primer nodo de esa ejecución |
| `duracion_ms` | Tiempo que tardó el nodo |

Los tiempos de nodo son relativos y no absolutos, de modo que las ejecuciones se pueden comparar entre sí sin
depender de la hora de arranque.

## Anonimización

| Dato original | Qué se publica |
|---|---|
| Nombre del cliente | no se exporta; el cliente figura como `U01` a `U10` |
| Dirección de correo | **eliminada** |
| Identificador de Telegram | **eliminado** |
| `customer_id` | mapeado a `U01`–`U10`, con el mismo criterio del Anexo E (`customer_id` N → `U{N:02d}`) |

Esta exportación contiene **solo metadatos de ejecución**: identificadores, marcas de tiempo, estados y
tiempos por nodo. No incluye el contenido de los payloads ni el texto de los mensajes generados. Los mensajes,
ya seudonimizados, están en `../../datos-crudos-tanda3-55-sesiones.csv`.

## Para qué sirve

- Reconstruir la latencia de cada sesión y ver en qué nodo se fue el tiempo.
- Verificar que las 55 ejecuciones son del 11/09/2026 y se agrupan en seis ciclos del job separados por cinco
  minutos.
- Identificar los dos valores atípicos de H1, las ejecuciones 184 y 187, en las que el nodo de envío por
  Telegram concentra más del 80 % del tiempo total.
