const router = require('express').Router();
const webhookAuth = require('../middleware/webhookAuth');
const { cartAbandoned } = require('../controllers/webhookController');

// POST /api/webhook/cart-abandoned
// Recibe { user_id } y dispara el webhook de n8n.
// Protegido por el token compartido de la cabecera X-Webhook-Token.
router.post('/cart-abandoned', webhookAuth, cartAbandoned);

module.exports = router;
