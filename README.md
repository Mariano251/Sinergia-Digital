# TechNova — Sistema Inteligente de Detección, Scoring y Notificación de Carritos Abandonados

**Trabajo Final Integrador — Tecnicatura Universitaria en Programación**  
Universidad Tecnológica Nacional — Facultad Regional Mendoza  

**Autores:** Mariano Lopez Tubaro & Lucio Arena  
**Director:** Prof. Alberto Cortez  
**Año:** 2026

---

## Descripción

TechNova es una plataforma de e-commerce funcional integrada con un sistema automatizado de detección, scoring y notificación de carritos abandonados. El sistema utiliza Agentes de Inteligencia Artificial basados en Claude (Anthropic), un algoritmo de scoring multidimensional y orquestación omnicanal con n8n para identificar, clasificar y notificar sobre estos abandonos en tiempo real.

---

## Arquitectura del sistema

El ecosistema se organiza en cinco capas:

1. **Frontend** — React 18 + Vite + Tailwind CSS
2. **Backend** — Node.js + Express + JWT
3. **Base de datos** — PostgreSQL (Render)
4. **Orquestación** — n8n + Agente de IA (Claude de Anthropic)
5. **Canales de contacto** — Telegram Bot API + SMTP (Email)

---

## Estructura del repositorio

```
Sinergia-Digital/
├── technova-frontend/            # Interfaz de usuario (React 18)
├── technova-backend/             # API REST (Node.js + Express)
├── n8n-workflows/                # Workflows de n8n exportados en JSON
├── validacion/                   # Datos e instrumentos de validación (ver Licencia)
├── tests-carritos-abandonados/   # Suite de Jest y reporte de cobertura
├── render.yaml                   # Configuración de deploy en Render
├── LICENSE
└── README.md
```

---

## Flujo de detección y notificación

1. El usuario agrega productos al carrito y abandona la sesión
2. Un hook en el frontend o un job automático del backend detecta el abandono
3. Se dispara un webhook a n8n con el payload del carrito
4. El algoritmo de scoring multidimensional clasifica el lead en Alta, Media o Baja Prioridad
5. El Agente de IA basado en Claude genera un mensaje personalizado
6. Alta Prioridad → Telegram · Media y Baja Prioridad → Email
7. Cada interacción queda registrada automáticamente en Google Sheets

---

## Algoritmo de scoring (Anexo A de la tesis)

Puntuación por tramos de valor, con castigo por abandono recurrente:

```
puntuación = 100 × min(cart_value / 200.000, 1)

≥ 70 pts  → Alta Prioridad   → Telegram     (equivale a $140.000)
≥ 30 pts  → Media Prioridad  → Email        (equivale a  $60.000)
< 30 pts  → Baja Prioridad   → Email

si previous_abandonment_count ≥ 4 → baja un nivel
```

`cart_stage` no participa del cálculo: se conserva únicamente en el registro de auditoría.

Es la regla vigente desde la segunda ronda de validación, implementada en el nodo
`Scoring - Clasificar Lead` del workflow de n8n. Reemplazó a una fórmula anterior de tres componentes
ponderados (50 % valor, 30 % abandono, 20 % etapa), que se descartó porque dejaba una zona en la que la
prioridad Alta era inalcanzable con cualquier carrito y porque `cart_stage` aportaba una constante que no
discriminaba, dado que el backend siempre envía `cart`.

---

## Stack tecnológico

| Capa | Tecnología |
|---|---|
| Frontend | React 18, Vite 5, Tailwind CSS 3 |
| Backend | Node.js 18, Express 4, JWT |
| Base de datos | PostgreSQL 16 |
| Orquestación | n8n (Railway) |
| IA | Claude de Anthropic (claude-haiku-4-5) |
| Canal alta conversión | Telegram Bot API |
| Canal secundario | SMTP (Gmail) |
| Auditoría | Google Sheets API |
| Deploy | Render (backend + DB) |
| Control de versiones | GitHub |

---

## Instalación y ejecución local

### Backend

```bash
cd technova-backend
npm install
# Configurar variables de entorno en .env (ver .env.example)
npm run dev
```

Variables de entorno requeridas:

```
DATABASE_URL=
JWT_SECRET=
N8N_WEBHOOK_URL=
WEBHOOK_TOKEN=
FRONTEND_URL=
PORT=3001
```

`WEBHOOK_TOKEN` es el token compartido que protege `POST /api/webhook/cart-abandoned` y viaja en la cabecera
`X-Webhook-Token`. El mismo valor debe cargarse en n8n como credencial de tipo *Header Auth*. Sin esa
variable el endpoint responde 500 y no procesa nada.

### Frontend

```bash
cd technova-frontend
npm install
npm run dev
```

Abrí `http://localhost:5173` en el navegador.

### Workflow de n8n

El archivo JSON del workflow está en `n8n-workflows/`. Para importarlo:

1. Abrí tu instancia de n8n
2. Menú → Workflows → Import from file
3. Seleccioná el archivo JSON
4. Configurá las credenciales de Anthropic, Telegram, Gmail y Google Sheets

---

## Resultados de validación (Tanda 3 — 55 sesiones, 11/09/2026)

| Hipótesis | Métrica | Resultado | Umbral | Estado |
|---|---|---|---|---|
| H1 — Latencia | Detección → registro de la notificación | Mediana 3,39 s; 55/55 por debajo de 300 s | 100 % < 300 s | Cumplida |
| H2 — Scoring | Concordancia con la clasificación experta | 72,7 % (κ 0,603) y 76,4 % (κ 0,636) frente a dos expertos | ≥ 85 % | **No cumplida** |
| H3 — Calidad IA | Rúbrica de 5 criterios, 3 evaluadores | 4,83 / 5,00; CCI(2,k) 0,931 | ≥ 4,0 | Cumplida |

Los dos expertos de H2 coinciden entre sí en el 81,8 % de los casos (κ 0,732), de modo que el incumplimiento
no se explica por un criterio atípico de uno de ellos. Las discordancias se concentran en carritos de
$112.000 a $130.000 que el algoritmo clasifica como Media y ambos expertos consideran Alta, lo que sugiere
que el umbral de Alta, fijado en $140.000, está alto.

Los datos primarios, los instrumentos ciegos, las planillas completadas y los scripts de análisis están en
**[`validacion/`](validacion/)**. Las rondas anteriores, cerradas, están en
[`validacion/historico/`](validacion/historico/).

---

## Repositorio

[github.com/Mariano251/Sinergia-Digital](https://github.com/Mariano251/Sinergia-Digital)

---

## Licencia

El **código** de este repositorio se publica bajo licencia MIT. El texto completo está en
[`LICENSE`](LICENSE).

### La carpeta `validacion/` no está cubierta por la licencia MIT

`validacion/` no es código: son registros de sesiones de validación ejecutadas sobre cuentas de personas
reales, junto con los instrumentos que completaron los expertos y los evaluadores.

**Se publica seudonimizada y únicamente con fines de verificación académica**, para que el trabajo pueda
auditarse sesión por sesión. No se autoriza su reutilización, redistribución ni explotación con otros fines.

Los nombres, las direcciones de correo y los identificadores de mensajería fueron reemplazados por
identificadores de la forma `Cliente NN` y `clienteNN@ejemplo.test`, tanto en las columnas de datos como
dentro del texto de los mensajes generados. Los datos identificables no forman parte del repositorio: viven
en `validacion/_privado/`, que está excluida por `.gitignore`.

Si vas a citar o reproducir estos datos, hacelo con atribución al trabajo y conservando la seudonimización.
