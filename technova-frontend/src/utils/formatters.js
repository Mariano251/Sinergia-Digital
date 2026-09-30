// Formateadores compartidos de TechNova.
// Vivían duplicados en ProductCard, CartDrawer, Checkout, ProductDetail y Profile.
// Las instancias de Intl se crean una sola vez: construirlas en cada render es caro.

const priceFormatter = new Intl.NumberFormat('es-AR', {
  style: 'currency',
  currency: 'ARS',
  maximumFractionDigits: 0,
});

const dateFormatter = new Intl.DateTimeFormat('es-AR', {
  day: '2-digit',
  month: 'long',
  year: 'numeric',
});

const dateShortFormatter = new Intl.DateTimeFormat('es-AR', {
  day: '2-digit',
  month: 'short',
  year: 'numeric',
});

// Precio en pesos, sin decimales. Un valor inválido se muestra como $ 0
// en vez de "NaN": la UI nunca debe filtrar basura al usuario.
export const formatPrice = (n) => {
  const value = Number(n);
  return priceFormatter.format(Number.isFinite(value) ? value : 0);
};

// Devuelve null si la fecha no es parseable, para que quien llama decida el fallback.
const parseDate = (d) => {
  if (!d) return null;
  const date = new Date(d);
  return Number.isNaN(date.getTime()) ? null : date;
};

// "05 de marzo de 2026"
export const formatDate = (d) => {
  const date = parseDate(d);
  return date ? dateFormatter.format(date) : '—';
};

// "05 mar 2026" — para espacios angostos (KPIs, tarjetas densas)
export const formatDateShort = (d) => {
  const date = parseDate(d);
  return date ? dateShortFormatter.format(date) : '—';
};

// Formato ISO (YYYY-MM-DD) para el atributo dateTime de <time>.
// Es lo que leen los lectores de pantalla y los buscadores.
export const toISODate = (d) => {
  const date = parseDate(d);
  return date ? date.toISOString().slice(0, 10) : undefined;
};
