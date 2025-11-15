import { useState, useCallback } from 'react';

const API_URL = 'http://localhost:8000'; // DO NOT CHANGE THIS IF ITS NOT CONNECTING STOP THE BACKEND AND ENSURE IT ON THIS PORT

export const useSessionManagement = () => {
  const [sessionId, setSessionId] = useState(null);
  const [sessionHistory, setSessionHistory] = useState([]);
  const [sessionInsights, _setSessionInsights] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const createNewSession = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_URL}/session/new`, { method: 'POST' });
      if (!response.ok) {
        throw new Error('Failed to create new session');
      }
      const data = await response.json();
      setSessionId(data.session_id);
      return data.session_id;
    } catch (error) {
      console.error("Error creating new session:", error);
      setError(error.message);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  const loadSessionHistory = useCallback(async (currentSessionId) => {
    if (!currentSessionId) return;
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_URL}/session/${currentSessionId}/history`);
      if (!response.ok) {
        throw new Error(`Failed to load session history for session ${currentSessionId}`);
      }
      const data = await response.json();
      setSessionHistory(data.history || []);
      _setSessionInsights(data.insights || null); // Added to handle session insights data
    } catch (error) {
      console.error("Error loading session history:", error);
      setError(error.message);
    } finally {
      setLoading(false);
    }
  }, []);

  const clearCurrentSession = useCallback(async () => {
    const currentSessionId = sessionId;
    setSessionId(null);
    setSessionHistory([]);
    setLoading(true);
    setError(null);

    if (currentSessionId) {
      try {
        const response = await fetch(`${API_URL}/session/${currentSessionId}`, { method: 'DELETE' });
        if (!response.ok) {
          console.warn(`Failed to delete session ${currentSessionId} on backend: ${response.status}`);
        }
      } catch (error) {
        console.error("Error clearing session on backend:", error);
        setError(error.message);
      } finally {
        setLoading(false);
      }
    }
  }, [sessionId]);

  return {
    sessionId,
    sessionHistory,
    sessionInsights,
    loading,
    error,
    createNewSession,
    loadSessionHistory,
    clearCurrentSession,
  };
};
