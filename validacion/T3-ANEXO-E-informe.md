# Evidencia primaria - Tanda 3 (55 sesiones, contador incremental)

Ejecuciones de n8n desde la 158. N sigue el orden cronologico de deteccion.
Salida literal de `tanda3-incremental/analisis_tanda3.py`:

```
====================================================================================================
H1 - LATENCIA DETECCION -> ENVIO (n=55, Tanda 3)
====================================================================================================
  n                 :       55
  minimo            :     2.18 s
  Q1                :     2.95 s
  mediana           :     3.39 s
  media             :     4.02 s
  Q3                :     3.95 s
  maximo            :    18.61 s
  desvio estandar   :     2.99 s
  < 300 s           : 55/55 = 100.0 %

  IQR = 0.99 s | bigotes de Tukey: [1.46 , 5.43]
  atipicos por 1.5*IQR: 5
    N30 I-01-2 Telegram 18.61 s | exec 187: IA 1.97 s, envio 15.90 s (Telegram - Enviar Mensaje)
    N27 I-04-2 Telegram 18.59 s | exec 184: IA 1.92 s, envio 15.91 s (Telegram - Enviar Mensaje)
    N6 I-10-0 Email    6.45 s | exec 163: IA 5.70 s, envio 0.42 s (Gmail - Baja Prioridad)
    N1 I-09-0 Email    6.18 s | exec 158: IA 3.52 s, envio 1.12 s (Gmail - Media Prioridad)
    N2 I-06-0 Email    5.47 s | exec 159: IA 2.81 s, envio 0.88 s (Gmail - Media Prioridad)

  por canal:
    Email     n=44  mediana 3.28 s  media 3.38 s  max 6.45 s
    Telegram  n=11  mediana 3.96 s  media 6.56 s  max 18.61 s

  componentes (tiempo de nodo en n8n):
    generacion con IA   : mediana 2.02 s  max 5.70 s
    Gmail - Baja Priorid: mediana 0.44 s  max 0.68 s  (n=18)
    Gmail - Media Priori: mediana 0.46 s  max 1.12 s  (n=26)
    Telegram - Enviar Me: mediana 0.90 s  max 15.91 s  (n=11)
    estado de las ejecuciones: {'success': 55}

  H1 (100 % bajo 300 s): SE CUMPLE

====================================================================================================
H2 - ALGORITMO vs EXPERTOS (Tanda 3)
====================================================================================================
  algoritmo: Alta 11, Media 26, Baja 18

  --- ALGORITMO vs EXPERTO A (experto 2) ---
  experto A (experto 2): Alta 21, Media 13, Baja 21

                Alta   Media    Baja   total   <- EXPERTO A (experto 2)
  Alta            11       0       0      11
  Media           10      12       4      26
  Baja             0       1      17      18
  total           21      13      21      55
  ^ ALGORITMO

  coincidencias        : 40/55
  concordancia simple  : 72.7 %   (umbral H2: 85 %)
  acuerdo esperado azar: 31.3 %
  Kappa de Cohen       : 0.603   Landis y Koch (1977): Moderado
  frontera de valor (+-$10.000 de $60.000 o $140.000):
    clara         : 34/46 =  73.9 %
    frontera      : 6/9 =  66.7 %
  castigo por abandono (contador >= 4):
    con castigo   : 12/15 =  80.0 %
    sin castigo   : 28/40 =  70.0 %
  nivel del contador:
    contador 0    : 6/10 =  60.0 %
    contador 1    : 7/10 =  70.0 %
    contador 2    : 7/10 =  70.0 %
    contador 3    : 8/10 =  80.0 %
    contador 4    : 8/10 =  80.0 %
    contador 5    : 4/5 =  80.0 %
  prioridad del algoritmo:
    ALTA          : 11/11 = 100.0 %
    BAJA          : 17/18 =  94.4 %
    MEDIA         : 12/26 =  46.2 %
  discordancias (escenario, carrito, contador, algoritmo -> experto):
    I-09-0  $120.000  ab=0  Media -> Alta
    I-06-0  $128.000  ab=0  Media -> Alta
    I-10-0  $ 55.000  ab=0  Baja  -> Media
    I-08-0  $112.000  ab=0  Media -> Alta
    I-01-1  $120.000  ab=1  Media -> Alta
    I-09-1  $120.000  ab=1  Media -> Alta
    I-03-1  $116.000  ab=1  Media -> Alta
    I-02-2  $ 72.000  ab=2  Media -> Baja
    I-06-2  $130.000  ab=2  Media -> Alta
    I-05-2  $ 80.000  ab=2  Media -> Baja
    I-10-3  $ 68.000  ab=3  Media -> Baja
    I-03-3  $ 80.000  ab=3  Media -> Baja
    I-03-4  $200.000  ab=4  Media -> Alta
    I-10-4  $180.000  ab=4  Media -> Alta
    I-01-5  $200.000  ab=5  Media -> Alta

  --- ALGORITMO vs EXPERTO B (experto 3) ---
  experto B (experto 3): Alta 16, Media 23, Baja 16

                Alta   Media    Baja   total   <- EXPERTO B (experto 3)
  Alta            10       1       0      11
  Media            6      18       2      26
  Baja             0       4      14      18
  total           16      23      16      55
  ^ ALGORITMO

  coincidencias        : 42/55
  concordancia simple  : 76.4 %   (umbral H2: 85 %)
  acuerdo esperado azar: 35.1 %
  Kappa de Cohen       : 0.636   Landis y Koch (1977): Sustancial
  frontera de valor (+-$10.000 de $60.000 o $140.000):
    clara         : 36/46 =  78.3 %
    frontera      : 6/9 =  66.7 %
  castigo por abandono (contador >= 4):
    con castigo   : 12/15 =  80.0 %
    sin castigo   : 30/40 =  75.0 %
  nivel del contador:
    contador 0    : 6/10 =  60.0 %
    contador 1    : 7/10 =  70.0 %
    contador 2    : 9/10 =  90.0 %
    contador 3    : 8/10 =  80.0 %
    contador 4    : 7/10 =  70.0 %
    contador 5    : 5/5 = 100.0 %
  prioridad del algoritmo:
    ALTA          : 10/11 =  90.9 %
    BAJA          : 14/18 =  77.8 %
    MEDIA         : 18/26 =  69.2 %
  discordancias (escenario, carrito, contador, algoritmo -> experto):
    I-09-0  $120.000  ab=0  Media -> Alta
    I-06-0  $128.000  ab=0  Media -> Alta
    I-10-0  $ 55.000  ab=0  Baja  -> Media
    I-08-0  $112.000  ab=0  Media -> Alta
    I-01-1  $120.000  ab=1  Media -> Alta
    I-09-1  $120.000  ab=1  Media -> Alta
    I-03-1  $116.000  ab=1  Media -> Alta
    I-02-2  $ 72.000  ab=2  Media -> Baja
    I-10-3  $ 68.000  ab=3  Media -> Baja
    I-05-3  $140.000  ab=3  Alta  -> Media
    I-02-4  $105.000  ab=4  Baja  -> Media
    I-01-4  $120.000  ab=4  Baja  -> Media
    I-06-4  $100.000  ab=4  Baja  -> Media

  --- EXPERTO A (experto 2) vs EXPERTO B (experto 3) (fiabilidad inter-observador) ---

                Alta   Media    Baja   total   <- EXPERTO B (experto 3)
  Alta            16       5       0      21
  Media            0      13       0      13
  Baja             0       5      16      21
  total           16      23      16      55
  ^ EXPERTO A (experto 2)

  coincidencias        : 45/55 =  81.8 %
  Kappa de Cohen       : 0.732   (Sustancial)
  discordancias        : {'A mas alto': 5, 'B mas alto': 5}, de dos escalones: 0
  algoritmo en las 45 sesiones con consenso de ambos: 36/45 =  80.0 %

====================================================================================================
H3 - CALIDAD DE LOS MENSAJES (Tanda 3)
====================================================================================================

  promedio global: 4.83 / 5,00   (umbral H3: 4.0)

  por criterio (evaluaciones individuales):
    Relevancia (1-5)          : media 4.99  desvio 0.08  [4-5]  n=165
    Precision factual (1-5)   : media 4.84  desvio 0.62  [2-5]  n=165
    Persuasion (1-5)          : media 4.81  desvio 0.57  [2-5]  n=165
    Uso de contexto (1-5)     : media 4.74  desvio 0.44  [4-5]  n=165
    Claridad (1-5)            : media 4.76  desvio 0.48  [3-5]  n=165

  por canal:
    Email     (n=44 mensajes): 4.83
    Telegram  (n=11 mensajes): 4.82

  por prioridad del algoritmo:
    Alta   (n=11): 4.82
    Media  (n=26): 4.90
    Baja   (n=18): 4.74

  por nivel del contador de abandonos:
    contador 0 (n=10): 4.83
    contador 1 (n=10): 4.88
    contador 2 (n=10): 4.91
    contador 3 (n=10): 4.74
    contador 4 (n=10): 4.87
    contador 5 (n= 5): 4.65

  por evaluador (severidad):
    Evaluador A: 4.84
    Evaluador B: 4.88
    Evaluador C: 4.76

  mensajes con promedio >= 4,0: 53/55 =  96.4 %

  CCI(2,k) medidas promedio : 0.931   IC95% [0.871 , 0.962]   (Excelente, Koo y Li 2016)
  CCI(2,1) medida individual: 0.818   IC95% [0.692 , 0.893]
  (dos vias, efectos aleatorios, acuerdo absoluto | MSR=0.2182 MSC=0.1949 MSE=0.0119 gl=33.7)

  H3 (promedio global >= 4.0): SE CUMPLE
```
