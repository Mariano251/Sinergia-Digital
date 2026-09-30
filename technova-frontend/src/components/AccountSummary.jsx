import { formatPrice, formatDateShort } from '../utils/formatters';

// Las órdenes canceladas no suman al total comprado: ese dinero nunca se gastó.
// Sí cuentan en "Órdenes", que es el historial completo.
const CANCELLED = 'cancelled';

function Kpi({ label, value, highlight = false }) {
  return (
    <div className="px-4 py-3 sm:px-5 sm:py-4">
      <dt className="text-tn-muted text-xs uppercase tracking-wider">{label}</dt>
      <dd className={`mt-1 font-bold text-2xl sm:text-3xl tabular-nums truncate
                      ${highlight ? 'text-tn-accent' : 'text-tn-text'}`}>
        {value}
      </dd>
    </div>
  );
}

export default function AccountSummary({ orders }) {
  const spent = orders
    .filter(o => o.status !== CANCELLED)
    .reduce((acc, o) => acc + (Number(o.total_amount) || 0), 0);

  // La API ya devuelve las órdenes ordenadas, pero no lo damos por sentado.
  const lastDate = orders.reduce((latest, o) => {
    const time = new Date(o.created_at).getTime();
    return Number.isFinite(time) && time > latest ? time : latest;
  }, 0);

  return (
    <dl className="card grid grid-cols-1 sm:grid-cols-3 divide-y sm:divide-y-0 sm:divide-x divide-tn-border mb-10">
      <Kpi label="Total comprado" value={formatPrice(spent)} highlight />
      <Kpi label="Órdenes" value={orders.length} />
      <Kpi label="Última compra" value={lastDate ? formatDateShort(lastDate) : '—'} />
    </dl>
  );
}
