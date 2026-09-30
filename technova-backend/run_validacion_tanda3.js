// ═══════════════════════════════════════════════════════════════
// TANDA 3 — CONTADOR DE ABANDONOS INCREMENTAL (55 sesiones)
//
// Diferencia con las tandas 1 y 2: el script NO fija el contador en cada
// escenario. Lo pone en 0 una sola vez al inicio y despues lo incrementa
// el propio backend (+1 por cada abandono notificado), como en produccion.
// Antes y despues de cada sesion se VERIFICA el contador, sin escribirlo.
//
// Plan: ../validacion/tanda3-incremental/plan-tanda3.json (generar_plan.py)
//
// Uso:
//   node run_validacion_tanda3.js --dry            chequeos previos, no escribe nada
//   node run_validacion_tanda3.js                  modo job (deteccion automatica)
//   node run_validacion_tanda3.js --modo manual    dispara el endpoint del webhook
//
// Requisitos: backend corriendo (npm start) y n8n corriendo con el workflow activo.
// ═══════════════════════════════════════════════════════════════
require('dotenv').config();
const path  = require('path');
const fs    = require('fs');
const axios = require('axios');
const pool  = require('./src/config/database');

const DIR_T3  = path.join(__dirname, '..', 'validacion', 'tanda3-incremental');
const PLAN    = JSON.parse(fs.readFileSync(path.join(DIR_T3, 'plan-tanda3.json'), 'utf8')).sesiones;
const SALIDA  = path.join(DIR_T3, 'run-tanda3-resultados.json');
const API     = 'http://localhost:3001';
const CUENTAS = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10];

const args  = process.argv.slice(2);
const DRY   = args.includes('--dry');
const MODO  = args.includes('--modo') ? args[args.indexOf('--modo') + 1] : 'job';
const ESPERA_MANUAL_MS = 8000;
const MAX_ESPERA_JOB_MS = 13 * 60 * 1000;

const sleep = ms => new Promise(r => setTimeout(r, ms));
const ahora = () => new Date().toISOString();

async function contadores() {
  const r = await pool.query(
    'SELECT id, COALESCE(previous_abandonment_count,0) AS ab FROM users WHERE id = ANY($1)', [CUENTAS]);
  return Object.fromEntries(r.rows.map(x => [x.id, Number(x.ab)]));
}

async function verificarContadores(sesiones, campo, delta, momento) {
  const ab = await contadores();
  const mal = sesiones.filter(s => ab[s.u] !== s[campo] + delta);
  if (mal.length) {
    const det = mal.map(s => `${s.id}: contador ${ab[s.u]}, esperado ${s[campo] + delta}`).join(' | ');
    throw new Error(`contador inconsistente ${momento}: ${det}`);
  }
}

async function chequeosPrevios() {
  if (!['job', 'manual'].includes(MODO)) throw new Error(`--modo invalido: ${MODO}`);
  if (PLAN.length !== 55) throw new Error(`el plan tiene ${PLAN.length} sesiones, se esperaban 55`);

  try { await axios.get(`${API}/api/health`, { timeout: 5000 }); }
  catch { throw new Error('el backend no responde en localhost:3001 (npm start en technova-backend)'); }

  const n8n = new URL(process.env.N8N_WEBHOOK_URL || 'http://localhost:5678');
  try { await axios.get(`${n8n.protocol}//${n8n.host}/healthz`, { timeout: 5000 }); }
  catch { throw new Error(`n8n no responde en ${n8n.host} (arrancalo con el workflow activo)`); }

  const u = await pool.query(
    'SELECT id, telegram_chat_id IS NOT NULL AS tg FROM users WHERE id = ANY($1) ORDER BY id', [CUENTAS]);
  if (u.rows.length !== 10) throw new Error(`se encontraron ${u.rows.length} de las 10 cuentas`);

  const pend = await pool.query(
    'SELECT DISTINCT user_id FROM cart_items WHERE user_id = ANY($1) AND abandoned_notified = false', [CUENTAS]);
  if (pend.rows.length) {
    throw new Error(`hay carritos sin notificar en las cuentas ${pend.rows.map(r => r.user_id)}: ` +
      'el job los procesaria y romperia la secuencia del contador');
  }
  console.log(`chequeos OK — backend, n8n, 10 cuentas, sin carritos pendientes | modo: ${MODO}`);
}

async function montarCarrito(s) {
  await pool.query('DELETE FROM cart_items WHERE user_id = $1', [s.u]);
  for (const [pid, q] of s.items) {
    await pool.query(
      `INSERT INTO cart_items (user_id, product_id, quantity, abandoned_notified, updated_at)
       VALUES ($1,$2,$3,false,NOW())`, [s.u, pid, q]);
  }
  const chk = await pool.query(
    `SELECT SUM(p.price*ci.quantity)::float AS v, MAX(ci.updated_at) AS t
     FROM cart_items ci JOIN products p ON p.id = ci.product_id WHERE ci.user_id = $1`, [s.u]);
  if (Math.round(chk.rows[0].v) !== s.cv) throw new Error(`${s.id}: carrito ${chk.rows[0].v} != ${s.cv}`);
  return new Date(chk.rows[0].t).toISOString();
}

async function esperarJob(sesiones) {
  const ini = Date.now();
  const ids = sesiones.map(s => s.u);
  while (Date.now() - ini < MAX_ESPERA_JOB_MS) {
    const r = await pool.query(
      `SELECT user_id, BOOL_AND(abandoned_notified) AS listo
       FROM cart_items WHERE user_id = ANY($1) GROUP BY user_id`, [ids]);
    if (r.rows.filter(x => x.listo).length === ids.length) {
      console.log(`  el job notifico los ${ids.length} a los ${Math.round((Date.now() - ini) / 1000)} s`);
      return;
    }
    await sleep(10000);
  }
  throw new Error('TIMEOUT: el job no proceso el ciclo dentro de 13 min');
}

async function correrCiclo(ciclo, sesiones, registro) {
  console.log(`\n=== CICLO ${ciclo}: ${sesiones.length} sesiones, contador esperado ${sesiones[0].ab_esperado} ===`);
  await verificarContadores(sesiones, 'ab_esperado', 0, `antes del ciclo ${ciclo}`);

  if (MODO === 'job') {
    for (const s of sesiones) {
      s.t_montado = await montarCarrito(s);
      console.log(`  ${s.id} user=${String(s.u).padStart(2)} $${String(s.cv).padStart(6)} ab=${s.ab_esperado} -> ${s.prioridad_esperada}`);
    }
    await esperarJob(sesiones);
    sesiones.forEach(s => { s.t_notificado = ahora(); });
  } else {
    for (const s of sesiones) {
      s.t_montado = await montarCarrito(s);
      await axios.post(`${API}/api/webhook/cart-abandoned`, { user_id: s.u, escenario: s.id }, { timeout: 60000 });
      s.t_notificado = ahora();
      console.log(`  ${s.id} user=${String(s.u).padStart(2)} $${String(s.cv).padStart(6)} ab=${s.ab_esperado} -> ${s.prioridad_esperada} OK`);
      await sleep(ESPERA_MANUAL_MS);
    }
  }

  await verificarContadores(sesiones, 'ab_esperado', 1, `despues del ciclo ${ciclo}`);
  console.log(`  contadores incrementados por el backend: OK (${sesiones[0].ab_esperado} -> ${sesiones[0].ab_esperado + 1})`);
  registro.push(...sesiones);
}

(async () => {
  const registro = [];
  const salida = { modo: MODO, inicio: null, fin: null, sesiones: registro, error: null };
  try {
    await chequeosPrevios();
    if (DRY) {
      console.log('--dry: no se escribio nada. Contadores actuales:', await contadores());
      return;
    }

    salida.inicio = ahora();
    // UNICA escritura del contador en toda la tanda: todas las cuentas arrancan en 0
    await pool.query('UPDATE users SET previous_abandonment_count = 0 WHERE id = ANY($1)', [CUENTAS]);
    console.log(`INICIO ${salida.inicio} — contadores de las 10 cuentas en 0`);

    for (let ciclo = 1; ciclo <= 6; ciclo++) {
      await correrCiclo(ciclo, PLAN.filter(s => s.ciclo === ciclo), registro);
      fs.writeFileSync(SALIDA, JSON.stringify(salida, null, 2));
    }
    salida.fin = ahora();
    console.log(`\nFIN ${salida.fin} — ${registro.length}/55 sesiones, contadores finales:`, await contadores());
  } catch (err) {
    salida.error = err.message;
    console.error(`\nDETENIDO: ${err.message}`);
    process.exitCode = 1;
  } finally {
    if (!DRY) fs.writeFileSync(SALIDA, JSON.stringify(salida, null, 2));
    await pool.end();
  }
})();
