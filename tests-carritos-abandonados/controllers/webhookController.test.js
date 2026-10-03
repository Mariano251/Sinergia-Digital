jest.mock('../config/database');
jest.mock('axios');

const pool = require('../config/database');
const axios = require('axios');
const { cartAbandoned } = require('./webhookController');

function mockRes() {
  return { status: jest.fn().mockReturnThis(), json: jest.fn() };
}

describe('cartAbandoned (POST /api/webhook/cart-abandoned)', () => {
  beforeEach(() => jest.clearAllMocks());

  test('devuelve 400 si falta user_id', async () => {
    const req = { body: {} };
    const res = mockRes();
    await cartAbandoned(req, res, jest.fn());
    expect(res.status).toHaveBeenCalledWith(400);
    expect(res.json).toHaveBeenCalledWith({ error: 'user_id es requerido' });
    expect(pool.query).not.toHaveBeenCalled();
  });

  test('devuelve 404 si el usuario no existe', async () => {
    pool.query = jest.fn().mockResolvedValueOnce({ rows: [] });
    const req = { body: { user_id: 999 } };
    const res = mockRes();
    await cartAbandoned(req, res, jest.fn());
    expect(res.status).toHaveBeenCalledWith(404);
    expect(res.json).toHaveBeenCalledWith({ error: 'Usuario no encontrado' });
  });

  test('devuelve 400 si el carrito está vacío', async () => {
    pool.query = jest.fn()
      .mockResolvedValueOnce({ rows: [{ id: 1, name: 'Ana', email: 'ana@test.com', telegram_chat_id: null, previous_abandonment_count: 0 }] })
      .mockResolvedValueOnce({ rows: [] });
    const req = { body: { user_id: 1 } };
    const res = mockRes();
    await cartAbandoned(req, res, jest.fn());
    expect(res.status).toHaveBeenCalledWith(400);
    expect(res.json).toHaveBeenCalledWith({ error: 'El carrito está vacío' });
  });

  test('camino feliz: arma el payload, llama a n8n y responde 200 con el resumen', async () => {
    pool.query = jest.fn()
      .mockResolvedValueOnce({ rows: [{ id: 1, name: 'Ana', email: 'ana@test.com', telegram_chat_id: 'xyz', previous_abandonment_count: 2 }] })
      .mockResolvedValueOnce({ rows: [{ name: 'Monitor', quantity: 1, price: '180000' }, { name: 'SSD', quantity: 1, price: '85000' }] })
      .mockResolvedValueOnce({}) // UPDATE cart_items
      .mockResolvedValueOnce({}); // UPDATE users
    axios.post = jest.fn().mockResolvedValueOnce({ status: 200 });

    const req = { body: { user_id: 1 } };
    const res = mockRes();
    await cartAbandoned(req, res, jest.fn());

    expect(axios.post).toHaveBeenCalledTimes(1);
    const [, payloadEnviado] = axios.post.mock.calls[0];
    expect(payloadEnviado.cart_value).toBeCloseTo(265000);
    expect(payloadEnviado.previous_abandonment_count).toBe(2);
    expect(res.json).toHaveBeenCalledWith(expect.objectContaining({
      user_email: 'ana@test.com',
      cart_value: 265000,
      items_count: 2
    }));
  });

  test('si n8n no responde (ECONNREFUSED), devuelve 502 sin romper el flujo', async () => {
    pool.query = jest.fn()
      .mockResolvedValueOnce({ rows: [{ id: 1, name: 'Ana', email: 'ana@test.com', telegram_chat_id: null, previous_abandonment_count: 0 }] })
      .mockResolvedValueOnce({ rows: [{ name: 'Monitor', quantity: 1, price: '180000' }] });
    const err = new Error('connect ECONNREFUSED');
    err.code = 'ECONNREFUSED';
    axios.post = jest.fn().mockRejectedValueOnce(err);

    const req = { body: { user_id: 1 } };
    const res = mockRes();
    await cartAbandoned(req, res, jest.fn());

    expect(res.status).toHaveBeenCalledWith(502);
    expect(res.json).toHaveBeenCalledWith(expect.objectContaining({
      error: 'No se pudo conectar con el servicio de notificaciones (n8n)'
    }));
  });
});
