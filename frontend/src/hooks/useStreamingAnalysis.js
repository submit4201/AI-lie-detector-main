import { useState, useCallback, useRef, useEffect } from 'react';

const API_URL = 'http://localhost:8000'; // DO NOT CHANGE THIS IF ITS NOT CONNECTING STOP THE BACKEND AND ENSURE IT ON THIS PORT

const createEmptyAggregate = () => ({
  transcript: null,
  services: {},
  errors: [],
  meta: {},
});

export const useStreamingAnalysis = (sessionId, onAnalysisUpdate) => {
  const [isStreaming, setIsStreaming] = useState(false);
  const [streamingProgress, setStreamingProgress] = useState(0);
  const [streamingStep, setStreamingStep] = useState('');
  const [streamingError, setStreamingError] = useState(null);
  const [partialResults, setPartialResults] = useState(null);
  const [lastReceivedComponent, setLastReceivedComponent] = useState(null);
  const [componentsReceived, setComponentsReceived] = useState([]);
  
  const websocketRef = useRef(null);

  // WebSocket connection for real-time updates
  const connectWebSocket = useCallback(() => {
    if (!sessionId || websocketRef.current) return;

    try {
      const wsUrl = `ws://localhost:8000/ws/${sessionId}`;//DO NOT CHANGE THIS
      websocketRef.current = new WebSocket(wsUrl);

      websocketRef.current.onopen = () => {
        console.log('WebSocket connected for session:', sessionId);
      };

      websocketRef.current.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);
          console.log('WebSocket message received:', message);

          switch (message.type) {
            case 'progress_update':
              setStreamingProgress(message.percentage || 0);
              setStreamingStep(message.step || '');
              break;
            
            case 'analysis_update':
              setPartialResults(prev => ({
                ...(prev ?? {}),
                [message.analysis_type]: message.data
              }));
              if (onAnalysisUpdate) {
                onAnalysisUpdate(message.analysis_type, message.data);
              }
              break;
            
            case 'error':
              setStreamingError(message.message);
              setIsStreaming(false);
              break;
            
            default:
              console.log('Unknown message type:', message.type);
          }
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };

      websocketRef.current.onerror = (error) => {
        console.error('WebSocket error:', error);
        setStreamingError('WebSocket connection failed');
      };

      websocketRef.current.onclose = () => {
        console.log('WebSocket disconnected');
        websocketRef.current = null;
      };
    } catch (error) {
      console.error('Failed to connect WebSocket:', error);
    }
  }, [sessionId, onAnalysisUpdate]);

  // Disconnect WebSocket
  const disconnectWebSocket = useCallback(() => {
    if (websocketRef.current) {
      websocketRef.current.close();
      websocketRef.current = null;
    }
  }, []);
  // Server-Sent Events streaming analysis
  const startStreamingAnalysis = useCallback(async (audioFile, transcriptOverride = '') => {
    if (!audioFile || !sessionId) {
      setStreamingError('Missing audio file or session ID');
      return null;
    }

    setIsStreaming(true);
    setStreamingError(null);
    setStreamingProgress(0);
    setStreamingStep('Initializing...');
    const initialAggregate = createEmptyAggregate();
    setPartialResults(initialAggregate);
    setComponentsReceived([]);
    setLastReceivedComponent(null);

    try {
      const formData = new FormData();
      formData.append('audio', audioFile);
      formData.append('session_id', sessionId);
      if (transcriptOverride) {
        formData.append('transcript', transcriptOverride);
      }

      const eventSourceUrl = `${API_URL}/v2/analyze/stream`;
      const response = await fetch(eventSourceUrl, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';
      let finalResult = null;
      let fallbackResult = initialAggregate;

      const processEvent = (rawEvent) => {
        const trimmed = rawEvent.trim();
        if (!trimmed.startsWith('data:')) {
          return;
        }
        const jsonPayload = trimmed.slice(5).trimStart();
        if (!jsonPayload) {
          return;
        }
        try {
          const event = JSON.parse(jsonPayload);
          console.log('SSE data received:', event);
          switch (event.event) {
            case 'analysis.update': {
              const serviceName = event.service || 'unknown';
              const payload = event.payload || {};

              setPartialResults(prev => {
                const base = prev ?? createEmptyAggregate();
                const nextValue = (() => {
                  if (serviceName === 'transcript') {
                    return {
                      ...base,
                      transcript: payload,
                    };
                  }
                  return {
                    ...base,
                    services: {
                      ...base.services,
                      [serviceName]: payload,
                    },
                    errors: event.errors
                      ? [...base.errors, { service: serviceName, message: event.errors }]
                      : base.errors,
                  };
                })();
                fallbackResult = nextValue;
                return nextValue;
              });

              setLastReceivedComponent(serviceName);
              setComponentsReceived(prev => (prev.includes(serviceName) ? prev : [...prev, serviceName]));
              setTimeout(() => setLastReceivedComponent(null), 2500);

              if (onAnalysisUpdate) {
                onAnalysisUpdate(serviceName, payload);
              }
              break;
            }
            case 'analysis.progress': {
              const completed = event.completed || 0;
              const total = event.total || 1;
              const percent = Math.min(100, Math.round((completed / total) * 100));
              setStreamingProgress(percent);
              setStreamingStep(`Processed ${completed} of ${total} services`);
              break;
            }
            case 'analysis.done': {
              finalResult = event.payload || null;
              fallbackResult = finalResult;
              setPartialResults(finalResult);
              setStreamingProgress(100);
              setStreamingStep('Analysis complete');
              break;
            }
            default:
              break;
          }
        } catch (error) {
          console.error('Error parsing SSE data:', error);
        }
      };

      try {
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          buffer += decoder.decode(value, { stream: true });
          const events = buffer.split('\n\n');
          buffer = events.pop() || '';
          events.forEach(processEvent);
        }
      } finally {
        reader.releaseLock();
      }

      setIsStreaming(false);
      const resolvedResult = finalResult || fallbackResult;
      console.log('Returning final result:', resolvedResult);
      return resolvedResult;

    } catch (error) {
      console.error('Streaming analysis error:', error);
      setStreamingError(error.message || 'Streaming analysis failed');
      setIsStreaming(false);
      return null;
    }
  }, [sessionId, onAnalysisUpdate]);
  // Reset streaming state
  const resetStreamingState = useCallback(() => {
    setIsStreaming(false);
    setStreamingProgress(0);
    setStreamingStep('');
    setStreamingError(null);
    setPartialResults(null);
    setLastReceivedComponent(null);
    setComponentsReceived([]);
    disconnectWebSocket();
  }, [disconnectWebSocket]);

  // Connect WebSocket when sessionId changes
  useEffect(() => {
    if (sessionId) {
      connectWebSocket();
    }
    return () => {
      disconnectWebSocket();
    };
  }, [sessionId, connectWebSocket, disconnectWebSocket]);
  // Cleanup on unmount
  useEffect(() => {
    return () => {
      disconnectWebSocket();
    };
  }, [disconnectWebSocket]);

  return {
    isStreaming,
    streamingProgress,
    streamingStep,
    streamingError,
    partialResults,
    lastReceivedComponent,
    componentsReceived,
    startStreamingAnalysis,
    connectWebSocket,
    disconnectWebSocket,
    resetStreamingState,
  };
};
