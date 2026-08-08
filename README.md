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
Sinergia-Digital-/
├── technova-frontend/     # Interfaz de usuario (React 18)
├── technova-backend/      # API REST (Node.js + Express)
├── n8n-workflows/         # Workflow de n8n exportado en JSON
├── render.yaml            # Configuración de deploy en Render
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

```
Puntuación = (cart_value × 50%) + (abandonment_count × 30%) + (cart_stage × 20%)

≥ 70 pts → Alta Prioridad → Telegram
40–69 pts → Media Prioridad → Email
< 40 pts  → Baja Prioridad → Email
```

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
FRONTEND_URL=
PORT=3001
```

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

## Resultados de validación (N=35 sesiones)

| Hipótesis | Métrica | Resultado | Umbral | Estado |
|---|---|---|---|---|
| H1 — Latencia | Notificaciones < 5 min | 91.4% | ≥ 90% | ✅ Superado |
| H2 — Scoring | Concordancia con experto | 91.4% (κ = 0.87) | ≥ 85% | ✅ Superado |
| H3 — Calidad IA | Rúbrica 5 criterios | 4.4 / 5.0 (CCI = 0.82) | ≥ 4.0 | ✅ Superado |

---

## Repositorio

[github.com/Mariano251/Sinergia-Digital-](https://github.com/Mariano251/Sinergia-Digital)
