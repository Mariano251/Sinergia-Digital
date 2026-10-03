// Estos tests apuntan al archivo REAL del backend, no a una copia:
// technova-backend/src/middleware/webhookAuth.js
const webhookAuth = require('../technova-backend/src/middleware/webhookAuth');

const TOKEN = 'token-de-prueba-0123456789';

function mockRes() {
  return { status: jest.fn().mockReturnThis(), json: jest.fn() };
}

// Centinela: pasar `undefined` activaria el valor por defecto del parametro,
// asi que hace falta un valor explicito para pedir "sin variable de entorno".
const SIN_TOKEN = Symbol('sin WEBHOOK_TOKEN');

function correr(headers, token = TOKEN) {
  const anterior = process.env.WEBHOOK_TOKEN;
  if (token === SIN_TOKEN) delete process.env.WEBHOOK_TOKEN;
  else process.env.WEBHOOK_TOKEN = token;
  const req = { headers };
  const res = mockRes();
  const next = jest.fn();
  try {
    webhookAuth(req, res, next);
  } finally {
    if (anterior === undefined) delete process.env.WEBHOOK_TOKEN;
    else process.env.WEBHOOK_TOKEN = anterior;
  }
  return { res, next };
}

describe('webhookAuth — token correcto', () => {
  test('deja pasar si la cabecera X-Webhook-Token coincide', () => {
    const { res, next } = correr({ 'x-webhook-token': TOKEN });
    expect(next).toHaveBeenCalledTimes(1);
    expect(res.status).not.toHaveBeenCalled();
  });

  test('la cabecera se reconoce sin importar mayusculas o minusculas', () => {
    // Express normaliza los nombres de cabecera a minusculas
    const { next } = correr({ 'X-Webhook-Token': TOKEN, 'x-webhook-token': TOKEN });
    expect(next).toHaveBeenCalledTimes(1);
  });

  test('tolera espacios alrededor del token', () => {
    const { next } = correr({ 'x-webhook-token': `  ${TOKEN}  ` });
    expect(next).toHaveBeenCalledTimes(1);
  });
});

describe('webhookAuth — token ausente o incorrecto', () => {
  test('devuelve 401 si no viene la cabecera', () => {
    const { res, next } = correr({});
    expect(res.status).toHaveBeenCalledWith(401);
    expect(res.json).toHaveBeenCalledWith({ error: 'Token de webhook invalido o ausente' });
    expect(next).not.toHaveBeenCalled();
  });

  test('devuelve 401 si el token no coincide', () => {
    const { res, next } = correr({ 'x-webhook-token': 'otro-token-cualquiera' });
    expect(res.status).toHaveBeenCalledWith(401);
    expect(next).not.toHaveBeenCalled();
  });

  test('devuelve 401 si el token es correcto pero con un caracter de mas', () => {
    const { res, next } = correr({ 'x-webhook-token': TOKEN + 'x' });
    expect(res.status).toHaveBeenCalledWith(401);
    expect(next).not.toHaveBeenCalled();
  });

  test('devuelve 401 si la cabecera viene vacia', () => {
    const { res, next } = correr({ 'x-webhook-token': '' });
    expect(res.status).toHaveBeenCalledWith(401);
    expect(next).not.toHaveBeenCalled();
  });

  test('el mensaje de error no revela el token esperado', () => {
    const { res } = correr({ 'x-webhook-token': 'incorrecto' });
    const cuerpo = JSON.stringify(res.json.mock.calls[0][0]);
    expect(cuerpo).not.toContain(TOKEN);
  });
});

describe('webhookAuth — el servidor no esta configurado', () => {
  test('si WEBHOOK_TOKEN no esta definido, rechaza con 500 y no deja pasar', () => {
    // Falla cerrado: sin token configurado no se acepta ninguna peticion
    const { res, next } = correr({ 'x-webhook-token': TOKEN }, SIN_TOKEN);
    expect(res.status).toHaveBeenCalledWith(500);
    expect(res.json).toHaveBeenCalledWith({ error: 'El servidor no tiene configurado WEBHOOK_TOKEN' });
    expect(next).not.toHaveBeenCalled();
  });

  test('si WEBHOOK_TOKEN esta vacio, tambien rechaza con 500', () => {
    const { res, next } = correr({ 'x-webhook-token': '' }, '   ');
    expect(res.status).toHaveBeenCalledWith(500);
    expect(next).not.toHaveBeenCalled();
  });
});
