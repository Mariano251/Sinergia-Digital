import { useState } from 'react';
import { formatPrice, formatDate, toISODate } from '../utils/formatters';

// Estados de orden → etiqueta, estilo e ícono.
// El ícono acompaña SIEMPRE al texto: el color nunca es el único indicador de estado.
const STATUS = {
  pending: {
    label: 'Pendiente',
    cls: 'bg-tn-warning/15 text-tn-warning border-tn-warning/30',
    path: 'M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z',
  },
  pendiente_mp: {
    label: 'Pendiente de pago',
    cls: 'bg-tn-warning/15 text-tn-warning border-tn-warning/30',
    path: 'M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z',
  },
  paid: {
    label: 'Pagada',
    cls: 'bg-tn-success/15 text-tn-success border-tn-success/30',
    path: 'M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z',
  },
  shipped: {
    label: 'Enviada',
    cls: 'bg-tn-accent/15 text-tn-accent border-tn-accent/30',
    path: 'M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4',
  },
  delivered: {
    label: 'Entregada',
    cls: 'bg-tn-success/15 text-tn-success border-tn-success/30',
    path: 'M5 13l4 4L19 7',
  },
  cancelled: {
    label: 'Cancelada',
    cls: 'bg-tn-danger/15 text-tn-danger border-tn-danger/30',
    path: 'M6 18L18 6M6 6l12 12',
  },
};

const FALLBACK_STATUS = {
  cls: 'bg-tn-dark-2 text-tn-muted border-tn-border',
  path: 'M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z',
};

// Cuántos productos se muestran antes de plegar el resto.
const MAX_VISIBLE_ITEMS = 3;

function StatusBadge({ status }) {
  const config = STATUS[status] || { ...FALLBACK_STATUS, label: status || 'Sin estado' };

  return (
    <span className={`badge border gap-1.5 ${config.cls}`}>
      <svg className="w-3.5 h-3.5 flex-shrink-0" fill="none" stroke="currentColor"
           viewBox="0 0 24 24" aria-hidden="true">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={config.path} />
      </svg>
      {config.label}
    </span>
  );
}

function OrderItem({ item }) {
  return (
    <li className="flex items-center gap-3">
      <img
        src={item.image_url}
        alt=""
        className="w-11 h-11 object-cover rounded-lg flex-shrink-0 bg-tn-dark-2"
        onError={e => { e.target.src = 'https://placehold.co/44x44/1a1a2e/4f8ef7?text=TN'; }}
      />
      <div className="flex-1 min-w-0">
        <p className="text-tn-text text-sm font-medium truncate" title={item.name}>{item.name}</p>
        <p className="text-tn-muted text-xs">Cantidad: {item.quantity}</p>
      </div>
      <span className="text-tn-text text-sm font-semibold flex-shrink-0 tabular-nums">
        {formatPrice(item.price * item.quantity)}
      </span>
    </li>
  );
}

export default function OrderCard({ order }) {
  const [expanded, setExpanded] = useState(false);

  const items  = Array.isArray(order.items) ? order.items.filter(Boolean) : [];
  const hidden = Math.max(0, items.length - MAX_VISIBLE_ITEMS);
  const shown  = expanded ? items : items.slice(0, MAX_VISIBLE_ITEMS);
  const listId = `order-${order.id}-items`;

  return (
    <article className="card p-4 sm:p-5">
      {/* Cabecera: identificación y estado */}
      <div className="flex flex-wrap items-start justify-between gap-3 pb-4 border-b border-tn-border">
        <div className="min-w-0">
          <h3 className="text-tn-text font-semibold">Orden #{order.id}</h3>
          <time dateTime={toISODate(order.created_at)} className="text-tn-muted text-xs mt-0.5 block">
            {formatDate(order.created_at)}
          </time>
        </div>
        <StatusBadge status={order.status} />
      </div>

      {/* Productos */}
      {items.length > 0 ? (
        <>
          <ul id={listId} className="space-y-3 py-4">
            {shown.map(item => <OrderItem key={item.id} item={item} />)}
          </ul>

          {hidden > 0 && (
            <button
              type="button"
              onClick={() => setExpanded(v => !v)}
              aria-expanded={expanded}
              aria-controls={listId}
              className="btn-ghost text-xs font-semibold -mt-1 mb-3 rounded
                         focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-tn-accent"
            >
              {expanded
                ? 'Mostrar menos'
                : `Ver ${hidden} producto${hidden > 1 ? 's' : ''} más`}
            </button>
          )}
        </>
      ) : (
        <p className="text-tn-muted text-sm py-4">Esta orden no tiene productos cargados.</p>
      )}

      {/* Total: el dato que el usuario busca cuando escanea el historial */}
      <div className="flex justify-between items-baseline pt-3 border-t border-tn-border">
        <span className="text-tn-muted text-sm">Total</span>
        <span className="text-tn-accent font-bold text-lg tabular-nums">
          {formatPrice(order.total_amount)}
        </span>
      </div>
    </article>
  );
}
