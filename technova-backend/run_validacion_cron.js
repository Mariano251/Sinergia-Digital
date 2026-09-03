require('dotenv').config();
const pool = require('./src/config/database');
const fs = require('fs');

// 8=Cable 4000 · 2=MousePad 20000 · 6=Webcam 35000 · 3=Auriculares 45000
// 1=Teclado 55000 · 7=Headset 65000 · 5=SSD 85000 · 4=Monitor 180000
const CICLO_1 = [
  { u: 1,  id:'C1-01', cv: 40000,  ab:0, items:[[2,2]] },
  { u: 2,  id:'C1-02', cv: 64000,  ab:1, items:[[2,3],[8,1]] },
  { u: 3,  id:'C1-03', cv: 90000,  ab:2, items:[[3,2]] },
  { u: 4,  id:'C1-04', cv:110000,  ab:3, items:[[3,1],[7,1]] },
  { u: 5,  id:'C1-05', cv:140000,  ab:5, items:[[5,1],[1,1]] },
  { u: 6,  id:'C1-06', cv: 55000,  ab:4, items:[[1,1]] },
  { u: 7,  id:'C1-07', cv:180000,  ab:1, items:[[4,1]] },
  { u: 8,  id:'C1-08', cv:200000,  ab:4, items:[[4,1],[2,1]] },
  { u: 9,  id:'C1-09', cv: 69000,  ab:0, items:[[7,1],[8,1]] },
  { u:10,  id:'C1-10', cv:130000,  ab:2, items:[[5,1],[3,1]] },
];
const CICLO_2 = [
  { u: 1,  id:'C2-01', cv:160000,  ab:5, items:[[5,1],[1,1],[2,1]] },
  { u: 2,  id:'C2-02', cv: 49000,  ab:3, items:[[3,1],[8,1]] },
  { u: 3,  id:'C2-03', cv:100000,  ab:1, items:[[3,1],[1,1]] },
  { u: 4,  id:'C2-04', cv: 24000,  ab:0, items:[[2,1],[8,1]] },
  { u: 5,  id:'C2-05', cv:200000,  ab:5, items:[[4,1],[2,1]] },
  { u: 6,  id:'C2-06', cv: 85000,  ab:2, items:[[5,1]] },
  { u: 7,  id:'C2-07', cv:120000,  ab:4, items:[[5,1],[6,1]] },
  { u: 8,  id:'C2-08', cv: 59000,  ab:1, items:[[1,1],[8,1]] },
  { u: 9,  id:'C2-09', cv:150000,  ab:3, items:[[5,1],[7,1]] },
  { u:10,  id:'C2-10', cv:105000,  ab:2, items:[[5,1],[2,1]] },
];

const esperado = (cv, ab) => {
  const p = Math.round((50*Math.min(cv/200000,1) + 30*Math.min(ab/5,1) + 10)*100)/100;
  return { p, prio: p>=70?'ALTA':p>=40?'MEDIA':'BAJA' };
};
const sleep = ms => new Promise(r => setTimeout(r, ms));

async function montarCiclo(ciclo, nombre) {
  console.log(`\n=== ${nombre}: montando 10 carritos ===`);
  const marcas = [];
  for (const e of ciclo) {
    await pool.query('DELETE FROM cart_items WHERE user_id=$1', [e.u]);
    for (const [pid, q] of e.items) {
      await pool.query(
        `INSERT INTO cart_items (user_id, product_id, quantity, abandoned_notified, updated_at)
         VALUES ($1,$2,$3,false,NOW())`, [e.u, pid, q]);
    }
    const chk = await pool.query(
      `SELECT SUM(p.price*ci.quantity)::float AS v, MAX(ci.updated_at) AS t
       FROM cart_items ci JOIN products p ON p.id=ci.product_id WHERE ci.user_id=$1`, [e.u]);
    if (Math.round(chk.rows[0].v) !== e.cv) throw new Error(`${e.id}: carrito ${chk.rows[0].v} != ${e.cv}`);
    await pool.query('UPDATE users SET previous_abandonment_count=$1 WHERE id=$2', [e.ab, e.u]);
    const exp = esperado(e.cv, e.ab);
    marcas.push({ ...e, ...exp, t_abandono: new Date(chk.rows[0].t).toISOString() });
    console.log(`  ${e.id} user=${String(e.u).padStart(2)} $${String(e.cv).padStart(6)} ab=${e.ab} -> ${String(exp.p).padStart(5)} ${exp.prio}`);
  }
  console.log(`  t_abandono registrado. El job detecta a partir de +120 s (tick cada 300 s).`);
  return marcas;
}

async function esperarDeteccion(ciclo, maxMs = 13*60*1000) {
  const ini = Date.now();
  const ids = ciclo.map(e => e.u);
  console.log('  esperando al job...');
  while (Date.now() - ini < maxMs) {
    const r = await pool.query(
      `SELECT user_id, BOOL_AND(abandoned_notified) AS listo, MAX(updated_at) AS t
       FROM cart_items WHERE user_id = ANY($1) GROUP BY user_id`, [ids]);
    const listos = r.rows.filter(x => x.listo);
    if (listos.length === ids.length) {
      console.log(`  DETECTADOS los 10 a los ${Math.round((Date.now()-ini)/1000)} s de montar los carritos`);
      return r.rows.reduce((a,x) => (a[x.user_id] = new Date(x.t).toISOString(), a), {});
    }
    await sleep(10000);
  }
  console.log('  TIMEOUT: el job no proceso los 10 dentro del limite');
  return null;
}

(async () => {
  console.log(`INICIO ${new Date().toISOString()} — 20 sesiones por el JOB AUTOMATICO`);
  const salida = { inicio: new Date().toISOString(), ciclos: [] };
  for (const [ciclo, nombre] of [[CICLO_1,'CICLO 1'], [CICLO_2,'CICLO 2']]) {
    const marcas = await montarCiclo(ciclo, nombre);
    const notif = await esperarDeteccion(ciclo);
    marcas.forEach(m => { m.t_notificado = notif ? notif[m.u] : null; });
    salida.ciclos.push({ nombre, marcas });
  }
  salida.fin = new Date().toISOString();
  fs.writeFileSync('validacion-cron-resultados.json', JSON.stringify(salida, null, 2));
  const todas = salida.ciclos.flatMap(c => c.marcas);
  const c = {ALTA:0,MEDIA:0,BAJA:0}; todas.forEach(m => c[m.prio]++);
  console.log(`\nFIN ${salida.fin}`);
  console.log(`sesiones: ${todas.length} | ALTA ${c.ALTA} · MEDIA ${c.MEDIA} · BAJA ${c.BAJA}`);
  await pool.end();
})();
