require('dotenv').config();
const pool = require('./src/config/database');
const axios = require('axios');

const API = 'http://localhost:3001/api/webhook/cart-abandoned';
const ESPERA_MS = 8000;

// Composiciones exactas por cart_value objetivo -> [[product_id, qty], ...]
// 8=Cable 4000 · 2=MousePad 20000 · 6=Webcam 35000 · 3=Auriculares 45000
// 1=Teclado 55000 · 7=Headset 65000 · 5=SSD 85000 · 4=Monitor 180000
const CARRITOS = {
   40000: [[2,2]],
   64000: [[2,3],[8,1]],
   68000: [[2,3],[8,2]],
   72000: [[2,3],[8,3]],
   76000: [[2,3],[8,4]],
   80000: [[3,1],[6,1]],
  112000: [[6,1],[3,1],[2,1],[8,3]],
  116000: [[6,1],[3,1],[2,1],[8,4]],
  120000: [[5,1],[6,1]],
  124000: [[5,1],[6,1],[8,1]],
  128000: [[5,1],[6,1],[8,2]],
  160000: [[5,1],[1,1],[2,1]],
  200000: [[4,1],[2,1]],
};

const escenarios = [];
let n = 0;
for (const cv of [40000, 80000, 120000, 160000, 200000])
  for (const ab of [0, 1, 2, 3, 5])
    escenarios.push({ id: `F-${String(++n).padStart(2,'0')}`, cv, ab });

[[64000,2],[68000,2],[72000,2],[76000,2],[80000,2]].forEach(([cv,ab],i) =>
  escenarios.push({ id: `B40-0${i+1}`, cv, ab }));
[[112000,5],[116000,5],[120000,5],[124000,5],[128000,5]].forEach(([cv,ab],i) =>
  escenarios.push({ id: `B70-0${i+1}`, cv, ab }));

const esperado = (cv, ab) => {
  const p = Math.round((50*Math.min(cv/200000,1) + 30*Math.min(ab/5,1) + 10)*100)/100;
  return { p, prio: p >= 70 ? 'ALTA' : p >= 40 ? 'MEDIA' : 'BAJA' };
};

const sleep = ms => new Promise(r => setTimeout(r, ms));

(async () => {
  console.log(`INICIO ${new Date().toISOString()} — ${escenarios.length} escenarios\n`);
  const res = [];
  for (let i = 0; i < escenarios.length; i++) {
    const e = escenarios[i];
    const userId = (i % 10) + 1;                 // reparto round-robin sobre las 10 cuentas
    const exp = esperado(e.cv, e.ab);
    try {
      await pool.query('DELETE FROM cart_items WHERE user_id = $1', [userId]);
      for (const [pid, qty] of CARRITOS[e.cv]) {
        await pool.query(
          `INSERT INTO cart_items (user_id, product_id, quantity, abandoned_notified, updated_at)
           VALUES ($1,$2,$3,false,NOW())`, [userId, pid, qty]);
      }
      const chk = await pool.query(
        `SELECT SUM(p.price*ci.quantity)::float AS v FROM cart_items ci
         JOIN products p ON p.id=ci.product_id WHERE ci.user_id=$1`, [userId]);
      if (Math.round(chk.rows[0].v) !== e.cv) throw new Error(`carrito ${chk.rows[0].v} != ${e.cv}`);

      await pool.query('UPDATE users SET previous_abandonment_count=$1 WHERE id=$2', [e.ab, userId]);
      await axios.post(API, { user_id: userId, escenario: e.id }, { timeout: 60000 });

      console.log(`[${String(i+1).padStart(2)}/35] ${e.id.padEnd(7)} user=${String(userId).padStart(2)} $${String(e.cv).padStart(6)} ab=${e.ab} -> ${String(exp.p).padStart(5)} ${exp.prio.padEnd(5)} OK`);
      res.push({ ...e, userId, ...exp, ok: true });
    } catch (err) {
      console.log(`[${String(i+1).padStart(2)}/35] ${e.id.padEnd(7)} user=${String(userId).padStart(2)} FALLO: ${err.message}`);
      res.push({ ...e, userId, ...exp, ok: false, err: err.message });
    }
    if (i < escenarios.length - 1) await sleep(ESPERA_MS);
  }
  const ok = res.filter(r => r.ok).length;
  console.log(`\nFIN ${new Date().toISOString()}`);
  console.log(`enviados OK: ${ok}/35`);
  const c = {ALTA:0,MEDIA:0,BAJA:0}; res.filter(r=>r.ok).forEach(r=>c[r.prio]++);
  console.log(`reparto esperado -> ALTA ${c.ALTA} | MEDIA ${c.MEDIA} | BAJA ${c.BAJA}`);
  require('fs').writeFileSync('validacion-resultados.json', JSON.stringify(res, null, 2));
  await pool.end();
})();
