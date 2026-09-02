const pool = require('../config/database');
const axios = require('axios');

// Buscar y procesar carritos abandonados (inactivos +2 min, no notificados)
const processAbandonedCarts = async () => {
  try {
    // Detectar usuarios que tienen ALGÚN item sin notificar e inactivo +2 min.
    // Solo se consideran items con abandoned_notified = false para evitar acumular
    // sesiones anteriores que ya fueron notificadas.
    const result = await pool.query(`
      SELECT DISTINCT u.id, u.name, u.email, u.telegram_chat_id,
             COALESCE(u.previous_abandonment_count, 0) AS previous_abandonment_count
      FROM cart_items ci
      JOIN users u ON ci.user_id = u.id
      WHERE ci.abandoned_notified = false
        AND ci.updated_at < NOW() - INTERVAL '2 minutes'
    `);

    if (result.rows.length === 0) return;

    console.log(`🛒 Encontrados ${result.rows.length} carrito(s) abandonado(s)`);

    for (const user of result.rows) {
      try {
        // Traer SOLO los items de la sesión actual: abandoned_notified = false.
        // Se incluye ci.id para luego marcar EXACTAMENTE estos items como
        // notificados (y no otros que el usuario haya agregado recién).
        const cartResult = await pool.query(
          `SELECT ci.id, p.name, ci.quantity, p.price
           FROM cart_items ci
           JOIN products p ON ci.product_id = p.id
           WHERE ci.user_id = $1
             AND ci.abandoned_notified = false
             AND ci.updated_at < NOW() - INTERVAL '2 minutes'
             AND p.active = true`,
          [user.id]
        );

        if (cartResult.rows.length === 0) continue;

        // Instante en que el sistema DETECTA el abandono: se toma apenas
        // confirmamos que este carrito califica y antes de armar el payload.
        // n8n lo lee como body.detected_at y con el calcula la latencia.
        const detectedAt = new Date().toISOString();

        const cartValue   = cartResult.rows.reduce(
          (sum, item) => sum + (parseFloat(item.price) * item.quantity), 0
        );
        const cartId      = `cart_${user.id}_${Date.now()}`;
        const checkoutUrl = `${process.env.FRONTEND_URL || 'http://localhost:5173'}/checkout`;

        // cart_stage: por ahora SIEMPRE 'cart'. La tabla cart_items no tiene
        // una columna checkout_stage, así que no podemos detectar la etapa real
        // (browsing / cart / checkout_started / payment_page) todavía. Cuando se
        // implemente el tracking del checkout, este valor se calcula de verdad.
        const cartStage = 'cart';

        const payload = {
          customer_id:                 user.id,
          name:                        user.name,
          email:                       user.email,
          telegram_chat_id:            user.telegram_chat_id,
          cart_value:                  cartValue,
          cart_stage:                  cartStage,
          previous_abandonment_count:  user.previous_abandonment_count,
          detected_at:                 detectedAt,
          cart: {
            cart_id:      cartId,
            checkout_url: checkoutUrl,
            items: cartResult.rows.map(item => ({
              name:     item.name,
              quantity: item.quantity,
              price:    parseFloat(item.price)
            }))
          }
        };

        // Log del payload completo ANTES de enviar, para verificar qué se manda
        // a n8n (incluido telegram_chat_id).
        console.log('📦 Payload enviado a n8n:', JSON.stringify(payload, null, 2));

        // Enviar a n8n
        await axios.post(process.env.N8N_WEBHOOK_URL, payload, {
          headers: { 'Content-Type': 'application/json' },
          timeout: 15000
        });

        // Marcar como notificados EXACTAMENTE los items que se enviaron en este
        // webhook (por su id). Así, los items que el usuario agregue después
        // siguen con abandoned_notified = false y se detectan en el próximo ciclo.
        const sentItemIds = cartResult.rows.map(item => item.id);
        await pool.query(
          'UPDATE cart_items SET abandoned_notified = true WHERE id = ANY($1)',
          [sentItemIds]
        );

        // Incrementar el contador de abandonos del usuario. Se hace DESPUÉS de
        // enviar el webhook: el payload ya viajó con el conteo "previo", y este
        // abandono pasa a sumar para la próxima notificación.
        await pool.query(
          'UPDATE users SET previous_abandonment_count = previous_abandonment_count + 1 WHERE id = $1',
          [user.id]
        );

        console.log(`📨 Webhook enviado para ${user.email} — ${cartResult.rows.length} item(s), $${cartValue.toFixed(2)}`);
      } catch (userErr) {
        console.error(`❌ Error procesando carrito de ${user.email}:`, userErr.message);
      }
    }
  } catch (err) {
    console.error('❌ Error en el job de carritos abandonados:', err.message);
  }
};

// Inicializar el job que corre cada 5 minutos
const setupAbandonedCartJob = () => {
  const INTERVAL_MS = 5 * 60 * 1000; // 5 minutos

  console.log('⏰ Job de carritos abandonados iniciado (intervalo: 5 min)');

  // Primera ejecución a los 30 segundos de iniciar el servidor
  setTimeout(processAbandonedCarts, 30 * 1000);

  // Luego cada 5 minutos
  setInterval(processAbandonedCarts, INTERVAL_MS);
};

module.exports = { setupAbandonedCartJob, processAbandonedCarts };
