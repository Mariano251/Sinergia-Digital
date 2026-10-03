// Extraído literalmente del nodo "Scoring - Clasificar Lead" (n8n-nodes-base.code)
// del workflow "Sinergia Digital - Recuperación de Carritos v4", que es el que corrió
// las 55 sesiones de la Tanda 3 (ejecuciones 158 a 212 de n8n, 11/09/2026).
//
// Se separa aquí SOLO para poder testear la lógica con Jest fuera del entorno de n8n.
// El nodo lee el payload del webhook y devuelve además los datos del cliente; acá queda
// únicamente el cálculo, que es idéntico:
//
//   puntuacion = 100 · min(cart_value / 200000, 1)
//   ALTA  ≥ 70  (equivale a $140.000)
//   MEDIA ≥ 30  (equivale a  $60.000)
//   BAJA  < 30
//   si previous_abandonment_count ≥ 4 → baja un nivel
//
// cart_stage NO participa del cálculo: el backend siempre manda 'cart'. Se acepta como
// parámetro porque el nodo lo conserva en la salida para el registro de auditoría.
//
// La prueba de que la lógica coincide con la que corrió está en scoringService.test.js:
// reproduce las 55 sesiones de la Tanda 3, puntuación y prioridad, una por una.

const CART_VALUE_MAX = 200000; // ARS — tope del catálogo para normalizar
const U_ALTA = 70;             // equivale a $140.000
const U_MEDIA = 30;            // equivale a  $60.000
const AB_CASTIGO = 4;          // a partir de aquí se degrada un nivel

const NIVELES = ['BAJA', 'MEDIA', 'ALTA'];

function calcularScoring({ cart_value, previous_abandonment_count } = {}) {
  const cartValue = parseFloat(cart_value) || 0;
  const abandonos = parseInt(previous_abandonment_count) || 0;

  const valorNorm = Math.min(cartValue / CART_VALUE_MAX, 1);
  const puntuacion = Math.round(valorNorm * 100 * 100) / 100;

  let nivel = puntuacion >= U_ALTA ? 2 : puntuacion >= U_MEDIA ? 1 : 0;

  const degradado = abandonos >= AB_CASTIGO;
  if (degradado) nivel = Math.max(0, nivel - 1);

  return { puntuacion, prioridad: NIVELES[nivel], degradado };
}

module.exports = { calcularScoring, CART_VALUE_MAX, U_ALTA, U_MEDIA, AB_CASTIGO, NIVELES };
