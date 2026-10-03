# Tanda 3: contador de abandonos incremental (55 sesiones)

## Qué cambia respecto de las tandas 1 y 2

En las tandas 1 y 2, el script **fijaba** `previous_abandonment_count` antes de cada
escenario. En esta tanda el contador arranca en **0 una sola vez** y después lo
incrementa **el propio backend** (+1 por cada abandono notificado), igual que en
producción. El script no vuelve a escribirlo: antes y después de cada ciclo solo lo
**verifica**.

Lo demás no cambia: el workflow de n8n es el de la tanda 2, con el mismo scoring,
los mismos prompts y el mismo modelo. También se usan las mismas 10 cuentas, los
mismos 55 valores de carrito y las mismas composiciones de productos.

## Diseño

| | |
|---|---|
| Cuentas 1 a 5 | 6 abandonos cada una → contador 0, 1, 2, 3, 4, 5 |
| Cuentas 6 a 10 | 5 abandonos cada una → contador 0, 1, 2, 3, 4 |
| Ciclos | 6: en el ciclo *k* cada cuenta abandona por *k*-ésima vez |
| Asignación de valores | estratificada por quintil de valor, al azar dentro del estrato, semilla 20260911 |
| Detección | job automático del backend (modo por defecto); alternativa: `--modo manual` |
| Reparto esperado | ALTA 11, MEDIA 26, BAJA 18 (tanda 2: 10 / 27 / 18) |

Con la asignación estratificada, cada nivel del contador recibe carritos de todo el
rango de valor ($24.000 a $200.000). Así el contador no queda confundido con el valor.
El detalle está en `plan-tanda3.json` (`python generar_plan.py`).

## Cómo correrla

1. **n8n**, con el workflow *Sinergia Digital - Recuperación de Carritos v4* activo:
   ```
   n8n start
   ```
2. **Backend** (en otra terminal):
   ```
   cd technova-backend
   npm start
   ```
3. **Chequeo previo**, que no escribe nada:
   ```
   cd technova-backend
   node run_validacion_tanda3.js --dry
   ```
4. **Corrida** (unos 30 a 40 minutos en modo job):
   ```
   node run_validacion_tanda3.js
   ```
   Mientras corre, no uses la tienda con esas 10 cuentas y no reinicies el backend.
   Si algo no cierra, el script se detiene solo y lo deja registrado en
   `run-tanda3-resultados.json`.
5. **Armado**, en dos pasos. El segundo lee **solo** la tabla que dejó el primero:
   ```
   cd validacion/tanda3-incremental
   python armar_tanda3.py datos          # n8n -> validacion/datos-crudos-tanda3-55-sesiones.csv
   python armar_tanda3.py instrumentos   # esa tabla -> planillas T3-* en validacion/
   ```
   Si corrés `python armar_tanda3.py` sin argumentos, hace los dos pasos seguidos.

## Qué genera el armado

Todo queda en `validacion/`, junto a los archivos de la Ronda 2:

| Archivo | Sale de | Para quién |
|---|---|---|
| `datos-crudos-tanda3-55-sesiones.csv` | `execution_data` de n8n + plan | la tabla de la tanda (seudonimizada) |
| `_privado/tanda3-IDENTIFICABLE.csv` | ídem | fuera del repositorio |
| `T3-H2-experto-A-planilla-ciega.csv` | la tabla | **experto A** (con `PARA-EXPERTO-criterio.md`) |
| `T3-H2-experto-B-planilla-ciega.csv` | la tabla | **experto B** (con `PARA-EXPERTO-criterio.md`) |
| `T3-H2-experto-{A,B}-clave-NO-MOSTRAR.csv` | la tabla | solo para el análisis |
| `T3-H3-rubrica-evaluador-{A,B,C}.csv` | la tabla | **evaluadores** (con `PARA-EVALUADORES-rubrica.md`) |
| `T3-H3-clave-NO-MOSTRAR.csv` | la tabla | solo para el análisis |

La tabla tiene las mismas 16 columnas que `datos-crudos-ronda2-55-sesiones.csv`. En
`Escenario` va el id del plan: `I-03-2` quiere decir cuenta 3, tercer abandono,
contador 2. Los productos de cada planilla salen del plan a partir de ese id, con los
nombres normalizados de las planillas de la Ronda 2.

Las dos planillas de experto tienen las mismas 55 sesiones en **distinto orden**
(semillas 20260912 y 20260919). La semilla de B es la primera desde 20260914 que no
deja ninguna sesión en la misma posición que en la planilla de A ni que en las
rúbricas. Cada una tiene su propia clave. Las rúbricas A, B y C comparten orden y
clave, como en la Ronda 2 (semilla 20260913).

Los instrumentos tienen **las mismas columnas** que los de la Ronda 2. Los instructivos
se reutilizan sin cambios, para que H2 y H3 sigan siendo comparables entre rondas.

## Análisis (H1, H2, H3)

Cuando vuelvan las planillas, guardalas en `validacion/` con estos nombres:
`T3-H2-experto-{A,B}-planilla-completa.csv` y `T3-H3-rubrica-evaluador-{A,B,C}-completa.csv`.
Después corré:

```
python analisis_tanda3.py
```

H1 se calcula siempre. H2 se calcula con al menos una planilla de experto, y H3 solo
con las tres rúbricas. Antes de calcular, cada planilla devuelta se compara con la que
se entregó: si falta una respuesta, hay un valor fuera de escala o se tocó algún dato
de la sesión, el script se detiene e indica la fila. Escribe `T3-ANEXO-E-*.csv` y
`T3-ANEXO-E-informe.md`.

Los estadísticos están en `estadistica.py`. `test_estadistica.py` reproduce los valores
publicados de la Ronda 2, con una corrección: el IC95% del CCI(2,k) de la Ronda 2 es
[0,702 , 0,886], con gl = 79,7, y no [0,698 , 0,887]. El informe anterior había usado
el CCI(2,k) en lugar del CCI(2,1) en la fórmula de Satterthwaite de McGraw y Wong. La
implementación se verificó contra el ejemplo de Shrout y Fleiss (1979).

En la Tanda 3 no hay escenarios B40/B70. Los casos de frontera se definen por
valor: carritos a ±$10.000 de un umbral ($60.000 o $140.000).

## Controles de integridad

- `extraer_n8n.py` reproduce **exactamente** los datos crudos de la Ronda 2
  (exec 102 a 157): 55 filas y 0 celdas distintas, tanto en la versión
  seudonimizada como en la identificable.
- `armar_tanda3.py datos` exige que, para cada cliente, sus ejecuciones en orden
  cronológico coincidan con el plan (valor de carrito) y que el contador que viajó
  en el payload sea 0, 1, 2… Cualquier faltante, duplicado o salto detiene el armado.
- `armar_tanda3.py instrumentos` vuelve a verificar la tabla antes de usarla: que
  tenga 55 filas, que los escenarios, las cuentas, los carritos y los contadores
  coincidan con el plan, y que esté seudonimizada. Si alguien la edita a mano y algo
  deja de cerrar, no genera nada.
- Tests: `python -m pytest -q` en esta carpeta.
