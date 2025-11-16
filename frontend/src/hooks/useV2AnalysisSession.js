import { useCallback, useEffect, useReducer, useRef } from 'react';
import { v2SseStream } from '../lib/streaming/v2SseClient';

const API_URL = 'http://localhost:8000';

const initialState = {
  status: 'idle', // idle | streaming | completed | error
  transcript: null,
  services: {},
  meta: {},
  progress: 0,
  errors: [],
  lastReceived: null,
  lastReceivedAt: null,
};

function reducer(state, action) {
  switch (action.type) {
    case 'start':
      return { ...initialState, status: 'streaming' };
    case 'update':
      {
        const { service, payload, meta } = action;
        const newServices = { ...state.services };
        if (service === 'transcript') {
          return {
            ...state,
            transcript: payload,
            lastReceived: service,
            lastReceivedAt: new Date().toISOString(),
            meta: { ...state.meta, ...meta },
          };
        }
        newServices[service] = {
          ...(newServices[service] || {}),
          ...payload,
        };
        return { ...state, services: newServices, lastReceived: service, lastReceivedAt: new Date().toISOString() };
      }
    case 'progress':
      return { ...state, progress: action.percent, status: 'streaming', lastReceivedAt: new Date().toISOString() };
    case 'done':
      return { ...state, status: 'completed', ...action.payload };
    case 'error':
      return { ...state, status: 'error', errors: [...(state.errors || []), action.error] };
    case 'reset':
      return initialState;
    default:
      return state;
  }
}

export const useV2AnalysisSession = ({ sessionId } = {}) => {
  const [state, dispatch] = useReducer(reducer, initialState);
  const abortControllerRef = useRef(null);

  const startStreaming = useCallback(async (audioFile, transcriptOverride = '') => {
    if (!sessionId) {
      dispatch({ type: 'error', error: 'Missing session ID' });
      return null;
    }
    if (!audioFile) {
      dispatch({ type: 'error', error: 'Missing audio file' });
      return null;
    }

    dispatch({ type: 'start' });

    const formData = new FormData();
    formData.append('audio', audioFile);
    formData.append('session_id', sessionId);
    if (transcriptOverride) formData.append('transcript', transcriptOverride);

    // abort controller to stop the fetch loop
    const abortController = new AbortController();
    abortControllerRef.current = abortController;
    try {
      for await (const event of v2SseStream(formData, { fetchOptions: { signal: abortController.signal }})) {
        if (event.type === 'analysis.update') {
          dispatch({ type: 'update', service: event.service || 'unknown', payload: event.payload || {}, meta: event.meta });
        } else if (event.type === 'analysis.progress') {
          const percent = Math.min(100, Math.round(((event.meta?.progress || 0) * 100)));
          dispatch({ type: 'progress', percent });
        } else if (event.type === 'analysis.done') {
          // event.payload is final structure for the analysis
          const finalPayload = event.payload || {};
          // merge transcript/services if present
          if (finalPayload.transcript) {
            dispatch({ type: 'update', service: 'transcript', payload: finalPayload.transcript });
          }
          if (finalPayload.services) {
            Object.entries(finalPayload.services).forEach(([svc, p]) => {
              dispatch({ type: 'update', service: svc, payload: p });
            });
          }
          // set final state
          dispatch({ type: 'done', payload: finalPayload });
          return finalPayload;
        }
      }
    } catch (err) {
      if (err.name === 'AbortError') {
        // aborted by user
        dispatch({ type: 'error', error: 'stream_aborted' });
        return null;
      }
      console.error('V2 streaming error', err);
      dispatch({ type: 'error', error: err.message || String(err) });
      return null;
    } finally {
      abortControllerRef.current = null;
    }
  }, [sessionId]);

  const stopStreaming = useCallback(() => {
    const ctrl = abortControllerRef.current;
    if (ctrl) ctrl.abort();
  }, []);

  const runSnapshot = useCallback(async (audioFile, transcriptOverride = '') => {
    if (!sessionId) {
      dispatch({ type: 'error', error: 'Missing session ID' });
      return null;
    }
    if (!audioFile) {
      dispatch({ type: 'error', error: 'Missing audio file' });
      return null;
    }
    try {
      const formData = new FormData();
      formData.append('audio', audioFile);
      formData.append('session_id', sessionId);
      if (transcriptOverride) formData.append('transcript', transcriptOverride);
      const response = await fetch(`${API_URL}/v2/analyze`, { method: 'POST', body: formData });
      if (!response.ok) {
        const txt = await response.text();
        throw new Error(`HTTP ${response.status} - ${txt}`);
      }
      const json = await response.json();
      // Merge into state
      if (json.transcript) dispatch({ type: 'update', service: 'transcript', payload: json.transcript });
      if (json.services) {
        Object.entries(json.services).forEach(([svc, p]) => dispatch({ type: 'update', service: svc, payload: p }));
      }
      dispatch({ type: 'done', payload: json });
      return json;
    } catch (err) {
      console.error('Snapshot analysis failed', err);
      dispatch({ type: 'error', error: err.message || String(err) });
      return null;
    }
  }, [sessionId]);

  const reset = useCallback(() => dispatch({ type: 'reset' }), []);

  return {
    state,
    startStreaming,
    stopStreaming,
    runSnapshot,
    reset,
  };
};
