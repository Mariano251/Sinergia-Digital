jest.mock('../config/database');
const pool = require('../config/database');
const { addItem } = require('./cartController');

function mockRes() {
  return { status: jest.fn().mockReturnThis(), json: jest.fn() };
}

describe('addItem (POST /api/cart/items)', () => {
  beforeEach(() => jest.clearAllMocks());

  test('devuelve 400 si falta product_id', async () => {
    const req = { body: {}, user: { id: 1 } };
    const res = mockRes();
    await addItem(req, res, jest.fn());
    expect(res.status).toHaveBeenCalledWith(400);
    expect(res.json).toHaveBeenCalledWith({ error: 'product_id es requerido' });
  });

  test('devuelve 404 si el producto no existe o está inactivo', async () => {
    pool.query = jest.fn().mockResolvedValueOnce({ rows: [] });
    const req = { body: { product_id: 99 }, user: { id: 1 } };
    const res = mockRes();
    await addItem(req, res, jest.fn());
    expect(res.status).toHaveBeenCalledWith(404);
  });

  test('devuelve 400 si la cantidad pedida supera el stock', async () => {
    pool.query = jest.fn().mockResolvedValueOnce({ rows: [{ id: 5, stock: 2 }] });
    const req = { body: { product_id: 5, quantity: 3 }, user: { id: 1 } };
    const res = mockRes();
    await addItem(req, res, jest.fn());
    expect(res.status).toHaveBeenCalledWith(400);
    expect(res.json).toHaveBeenCalledWith({ error: 'Stock insuficiente' });
  });

  test('si el item ya existe en el carrito, suma la cantidad en vez de duplicar la fila', async () => {
    pool.query = jest.fn()
      .mockResolvedValueOnce({ rows: [{ id: 5, stock: 10 }] })              // producto
      .mockResolvedValueOnce({ rows: [{ id: 1, quantity: 2 }] })            // ya existe en carrito
      .mockResolvedValueOnce({ rows: [{ id: 1, quantity: 3 }] })            // UPDATE
      .mockResolvedValueOnce({});                                          // reset abandoned_notified

    const req = { body: { product_id: 5, quantity: 1 }, user: { id: 1 } };
    const res = mockRes();
    await addItem(req, res, jest.fn());

    expect(pool.query.mock.calls[2][0]).toMatch(/UPDATE cart_items/);
    expect(res.status).toHaveBeenCalledWith(201);
    expect(res.json).toHaveBeenCalledWith({ id: 1, quantity: 3 });
  });

  test('si el item no existe, inserta una fila nueva', async () => {
    pool.query = jest.fn()
      .mockResolvedValueOnce({ rows: [{ id: 5, stock: 10 }] })  // producto
      .mockResolvedValueOnce({ rows: [] })                      // no existe en carrito
      .mockResolvedValueOnce({ rows: [{ id: 9, quantity: 1 }] })// INSERT
      .mockResolvedValueOnce({});                               // reset abandoned_notified

    const req = { body: { product_id: 5, quantity: 1 }, user: { id: 1 } };
    const res = mockRes();
    await addItem(req, res, jest.fn());

    expect(pool.query.mock.calls[2][0]).toMatch(/INSERT INTO cart_items/);
    expect(res.status).toHaveBeenCalledWith(201);
  });
});
