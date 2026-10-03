const pool = require('../config/database');
const axios = require('axios');

const cartAbandoned = async (req, res, next) => {
  try {
    const { user_id } = req.body;
    if (!user_id) {
      return res.status(400).json({ error: 'user_id es requerido' });
    }
    const userResult = await pool.query(
      'SELECT id, name, email, telegram_chat_id, COALESCE(previous_abandonment_count, 0) AS previous_abandonment_count FROM users WHERE id = $1',
      [user_id]
    );
    if (!userResult.rows[0]) {
      return res.status(404).json({ error: 'Usuario no encontrado' });
    }
    const user = userResult.rows[0];
    const cartResult = await pool.query(
      `SELECT p.name, ci.quantity, p.price
       FROM cart_items ci
       JOIN products p ON ci.product_id = p.id
       WHERE ci.user_id = $1 AND p.active = true`,
      [user_id]
    );
    if (cartResult.rows.length === 0) {
      return res.status(400).json({ error: 'El carrito está vacío' });
    }
    const cartValue = cartResult.rows.reduce(
      (sum, item) => sum + (parseFloat(item.price) * item.quantity),
      0
    );
    const cartId = `cart_${user_id}_${Date.now()}`;
    const checkoutUrl = `${process.env.FRONTEND_URL || 'http://localhost:5173'}/checkout`;

    const payload = {
      customer_id: user.id,
      name: user.name,
      email: user.email,
      telegram_chat_id: user.telegram_chat_id,
      cart_value: cartValue,
      cart_stage: 'cart',
      previous_abandonment_count: user.previous_abandonment_count,
      cart: {
        cart_id: cartId,
        checkout_url: checkoutUrl,
        items: cartResult.rows.map(item => ({
          name: item.name,
          quantity: item.quantity,
          price: parseFloat(item.price)
        }))
      }
    };

    await axios.post(process.env.N8N_WEBHOOK_URL, payload, {
      headers: { 'Content-Type': 'application/json' },
      timeout: 15000
    });

    await pool.query(
      'UPDATE cart_items SET abandoned_notified = true WHERE user_id = $1',
      [user_id]
    );
    await pool.query(
      'UPDATE users SET previous_abandonment_count = previous_abandonment_count + 1 WHERE id = $1',
      [user_id]
    );

    res.json({
      message: 'Webhook de carrito abandonado enviado correctamente',
      user_email: user.email,
      cart_value: cartValue,
      items_count: cartResult.rows.length
    });
  } catch (err) {
    if (err.code === 'ECONNREFUSED' || err.response) {
      return res.status(502).json({
        error: 'No se pudo conectar con el servicio de notificaciones (n8n)',
        detail: err.message
      });
    }
    next(err);
  }
};

module.exports = { cartAbandoned };
