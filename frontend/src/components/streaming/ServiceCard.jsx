import React from 'react';

const STATUS_THEME = {
  pending: { label: 'Pending', badge: 'bg-gray-700/40 text-gray-200 border border-gray-600/40' },
  streaming: { label: 'Streaming', badge: 'bg-blue-500/20 text-blue-100 border border-blue-500/40' },
  completed: { label: 'Complete', badge: 'bg-emerald-500/20 text-emerald-100 border border-emerald-500/40' },
  error: { label: 'Error', badge: 'bg-rose-500/20 text-rose-100 border border-rose-500/40' },
  planned: { label: 'Coming Soon', badge: 'bg-slate-700/40 text-slate-200 border border-slate-600/40' },
  missing: { label: 'Missing', badge: 'bg-amber-500/20 text-amber-100 border border-amber-500/40' },
};

const ACCENT_TO_RING = {
  emerald: 'border-emerald-400/40',
  cyan: 'border-cyan-400/40',
  violet: 'border-violet-400/40',
  rose: 'border-rose-400/40',
  amber: 'border-amber-400/40',
  indigo: 'border-indigo-400/40',
  fuchsia: 'border-fuchsia-400/40',
  blue: 'border-blue-400/40',
  sky: 'border-sky-400/40',
  lime: 'border-lime-400/40',
  teal: 'border-teal-400/40',
  slate: 'border-slate-400/40',
  orange: 'border-orange-400/40',
};

const ERROR_MAX = 2;

const renderHighlights = (service = {}, payload) => {
  if (!Array.isArray(service.kpi) || service.kpi.length === 0) {
    return null;
  }
  const rows = service.kpi.map((item) => {
    try {
      const value = typeof item.compute === 'function' ? item.compute(payload || {}) : undefined;
      return { label: item.label, value: value ?? '—' };
    } catch (err) {
      return { label: item.label, value: '—' };
    }
  }).filter(Boolean);
  if (rows.length === 0) return null;
  return (
    <dl className="mt-3 grid grid-cols-2 gap-2 text-xs text-gray-200">
      {rows.map((row) => (
        <div key={`${service.key}-${row.label}`} className="bg-black/20 rounded p-2 border border-white/5">
          <dt className="uppercase tracking-widest text-[10px] text-gray-400">{row.label}</dt>
          <dd className="text-sm text-white truncate" title={row.value}>{row.value}</dd>
        </div>
      ))}
    </dl>
  );
};

const buildErrorList = (payload) => {
  if (!payload) return [];
  if (Array.isArray(payload.errors)) return payload.errors;
  if (payload.errors) return [payload.errors];
  return [];
};

const ServiceCard = ({
  service,
  payload,
  status = 'pending',
  isHighlighted = false,
  showRaw = false,
}) => {
  const accentRing = service?.accent ? ACCENT_TO_RING[service.accent] || 'border-white/10' : 'border-white/10';
  const resolvedStatus = service?.planned && !payload ? 'planned' : status;
  const badgeTheme = STATUS_THEME[resolvedStatus] || STATUS_THEME.pending;
  const errors = buildErrorList(payload);
  const cardTitle = service?.title || service?.key || 'Service';
  const description = service?.description || 'Streaming component';
  const serviceKey = service?.key || cardTitle.toLowerCase().replace(/\s+/g, '_');

  return (
    <div
      className={`bg-gray-900/40 border rounded-xl p-4 transition-all duration-200 ${accentRing} ${isHighlighted ? 'ring-2 ring-blue-400' : 'border-white/10'}`}
      data-service-key={serviceKey}
      data-service-status={resolvedStatus}
      aria-label={`${cardTitle} service card`}
    >
      <div className="flex items-center gap-2">
        <div className={`w-2 h-2 rounded-full ${isHighlighted ? 'bg-blue-400 animate-ping' : 'bg-white/40'}`} />
        <h3 className="text-base font-semibold text-white tracking-tight">{cardTitle}</h3>
        <span className={`ml-auto text-[11px] font-medium px-2 py-0.5 rounded-full ${badgeTheme.badge}`}>
          {badgeTheme.label}
        </span>
      </div>
      <span className="sr-only" data-testid={`service-label-${serviceKey}`}>{serviceKey}</span>
      <p className="text-xs text-gray-400 mt-1 leading-relaxed">{description}</p>

      {renderHighlights(service, payload)}

      {errors.length > 0 && (
        <div className="mt-3 bg-rose-500/10 border border-rose-500/40 rounded-lg p-3">
          <p className="text-xs font-semibold text-rose-200 mb-1">Errors</p>
          <ul className="space-y-1 text-[11px] text-rose-100">
            {errors.slice(0, ERROR_MAX).map((err, idx) => (
              <li key={`err-${idx}`}>{err.error || err.message || JSON.stringify(err)}</li>
            ))}
            {errors.length > ERROR_MAX && <li>+{errors.length - ERROR_MAX} more…</li>}
          </ul>
        </div>
      )}

      {showRaw && payload && (
        <details className="mt-3 text-xs text-gray-300">
          <summary className="cursor-pointer text-[11px] uppercase tracking-widest text-gray-400">Raw payload</summary>
          <pre className="mt-2 max-h-48 overflow-auto bg-black/40 rounded p-2">{JSON.stringify(payload, null, 2)}</pre>
        </details>
      )}
    </div>
  );
};

export default ServiceCard;