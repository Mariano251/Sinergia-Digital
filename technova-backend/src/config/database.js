const { Pool } = require('pg');

const connectionString = process.env.DATABASE_URL || '';

if (!connectionString) {
  console.error('❌ Falta DATABASE_URL en el .env — la API no va a poder conectarse.');
}

// ── SSL condicional ─────────────────────────────────────────────────────────
// Neon y Render EXIGEN SSL y lo declaran en la URL con ?sslmode=require.
// Una base local (postgres en tu máquina o en Docker) normalmente NO tiene SSL,
// y forzarlo hace fallar la conexión con "The server does not support SSL".
// Regla: SSL activo si la URL lo pide o si estamos en producción;
//        sslmode=disable en la URL manda por encima de todo.
const sslDisabled  = /[?&]sslmode=disable/i.test(connectionString);
const sslRequested = /[?&]sslmode=(require|verify-ca|verify-full)/i.test(connectionString);
const useSSL       = !sslDisabled && (sslRequested || process.env.NODE_ENV === 'production');

const pool = new Pool({
  connectionString,
  // rejectUnauthorized: false acepta certificados intermedios/auto-firmados
  // (necesario en Render; inofensivo en Neon, que sí tiene cert válido).
  ssl: useSSL ? { rejectUnauthorized: false } : false
});

// Verificar la conexión al iniciar
pool.connect((err, client, release) => {
  if (err) {
    console.error('❌ Error conectando a PostgreSQL:', err.message);
    return;
  }
  release();
  console.log(`✅ Conectado a PostgreSQL correctamente (SSL: ${useSSL ? 'on' : 'off'})`);
});

module.exports = pool;
