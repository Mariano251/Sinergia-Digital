const pool = require('../config/database');

const addItem = async (req, res, next) => {
  try {
    const { product_id, quantity = 1 } = req.body;
    if (!product_id) {
      return res.status(400).json({ error: 'product_id es requerido' });
    }
    const product = await pool.query(
      'SELECT * FROM products WHERE id = $1 AND active = true',
      [product_id]
    );
    if (!product.rows[0]) {
      return res.status(404).json({ error: 'Producto no encontrado' });
    }
    if (product.rows[0].stock < quantity) {
      return res.status(400).json({ error: 'Stock insuficiente' });
    }
    const existing = await pool.query(
      'SELECT * FROM cart_items WHERE user_id = $1 AND product_id = $2',
      [req.user.id, product_id]
    );
    let item;
    if (existing.rows[0]) {
      const result = await pool.query(
        `UPDATE cart_items
         SET quantity = quantity + $1, updated_at = NOW(), abandoned_notified = false
         WHERE user_id = $2 AND product_id = $3
         RETURNING *`,
        [quantity, req.user.id, product_id]
      );
      item = result.rows[0];
    } else {
      const result = await pool.query(
        `INSERT INTO cart_items (user_id, product_id, quantity)
         VALUES ($1, $2, $3)
         RETURNING *`,
        [req.user.id, product_id, quantity]
      );
      item = result.rows[0];
    }
    await pool.query(
      'UPDATE cart_items SET abandoned_notified = false WHERE user_id = $1',
      [req.user.id]
    );
    res.status(201).json(item);
  } catch (err) {
    next(err);
  }
};

module.exports = { addItem };
