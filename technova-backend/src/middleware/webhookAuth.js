const crypto = require('crypto');

// Valida el token compartido entre el backend y n8n en las rutas de webhook.
//
// El emisor (este backend, o el script de validacion) manda la cabecera
// X-Webhook-Token; el receptor la compara contra WEBHOOK_TOKEN del entorno.
//
// Falla cerrado: si WEBHOOK_TOKEN no esta configurado, no se acepta ninguna
// peticion. Es preferible que el endpoint deje de responder a que quede
// abierto sin que nadie lo note.
const CABECERA = 'x-webhook-token';

// Comparacion en tiempo constante: evita que el tiempo de respuesta filtre
// cuantos caracteres del token son correctos.
const iguales = (a, b) => {
  const ba = Buffer.from(a, 'utf8');
  const bb = Buffer.from(b, 'utf8');
  if (ba.length !== bb.length) return false;
  return crypto.timingSafeEqual(ba, bb);
};

const webhookAuth = (req, res, next) => {
  const esperado = (process.env.WEBHOOK_TOKEN || '').trim();

  if (!esperado) {
    console.error('WEBHOOK_TOKEN no esta configurado: se rechaza la peticion al webhook');
    return res.status(500).json({ error: 'El servidor no tiene configurado WEBHOOK_TOKEN' });
  }

  const recibido = ((req.headers || {})[CABECERA] || '').trim();

  if (!recibido || !iguales(recibido, esperado)) {
    return res.status(401).json({ error: 'Token de webhook invalido o ausente' });
  }

  return next();
};

module.exports = webhookAuth;
module.exports.CABECERA = CABECERA;
