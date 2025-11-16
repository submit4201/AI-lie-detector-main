import React, { useMemo } from 'react';
import ServiceCard from './ServiceCard';
import { V2_SERVICE_CATALOG } from '../../data/v2ServiceCatalog';

const getStatus = ({ key, payload, state, isStreaming, lastReceived }) => {
  if (!payload && key === 'transcription' && !isStreaming) {
    return 'pending';
  }
  if (!payload && state?.status === 'idle') {
    return 'pending';
  }
  if (payload?.errors && payload.errors.length > 0) {
    return 'error';
  }
  if (isStreaming && lastReceived === key) {
    return 'streaming';
  }
  if (payload) {
    return 'completed';
  }
  if (state?.status === 'completed') {
    return 'missing';
  }
  return 'pending';
};

const normalizeServices = ({ services = {}, transcript, meta }) => {
  const normalized = { ...services };
  if (!normalized.transcription && transcript) {
    normalized.transcription = {
      service_name: 'transcription',
      transcript,
      auto_generated: Boolean(meta?.transcript_auto_generated),
    };
  }
  return normalized;
};

const V2ServiceGrid = ({
  services,
  transcript,
  meta,
  isStreaming,
  lastReceived,
  state,
}) => {
  const normalizedServices = useMemo(() => normalizeServices({ services, transcript, meta }), [services, transcript, meta]);
  const activeServices = useMemo(() => V2_SERVICE_CATALOG.filter((svc) => !svc.hidden), []);
  const serviceCount = Object.keys(normalizedServices).length;
  const shouldDisplay = isStreaming || serviceCount > 0 || (state && state.status && state.status !== 'idle');
  if (!shouldDisplay) {
    return null;
  }

  const trackedKeys = new Set(activeServices.map((svc) => svc.key));
  const extraKeys = Object.keys(normalizedServices).filter((key) => !trackedKeys.has(key));
  const totalTrackable = activeServices.filter((svc) => !svc.planned).length || 1;
  const completedCount = activeServices.filter((svc) => !svc.planned && normalizedServices[svc.key]).length;

  return (
    <section className="bg-black/30 border border-white/10 rounded-2xl p-4">
      <div className="flex flex-wrap items-center gap-3 mb-4">
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-blue-400 animate-pulse" />
          <p className="text-sm text-white font-semibold">Service Pipeline</p>
        </div>
        <span className="text-xs text-gray-300">{completedCount}/{totalTrackable} active services responding</span>
        {state?.status && (
          <span className="text-xs px-2 py-0.5 rounded-full border border-white/20 text-white/80 uppercase tracking-widest">
            {state.status}
          </span>
        )}
      </div>

      <div className="grid gap-4 grid-cols-1 md:grid-cols-2 xl:grid-cols-3">
        {activeServices.map((service) => (
          <ServiceCard
            key={service.key}
            service={service}
            payload={normalizedServices[service.key]}
            status={service.planned && !normalizedServices[service.key]
              ? 'planned'
              : getStatus({ key: service.key, payload: normalizedServices[service.key], state, isStreaming, lastReceived })}
            isHighlighted={lastReceived === service.key}
            showRaw={Boolean(normalizedServices[service.key]?.errors)}
          />
        ))}

        {extraKeys.map((key) => (
          <ServiceCard
            key={key}
            service={{ key, title: key.replace(/_/g, ' '), description: 'Additional service', accent: 'slate' }}
            payload={normalizedServices[key]}
            status={getStatus({ key, payload: normalizedServices[key], state, isStreaming, lastReceived })}
            isHighlighted={lastReceived === key}
            showRaw
          />
        ))}
      </div>
    </section>
  );
};

export default V2ServiceGrid;
