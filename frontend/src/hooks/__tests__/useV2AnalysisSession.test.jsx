import React, { useEffect } from 'react'
import { describe, it, expect, vi } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'

// Mock the v2SseStream generator
vi.mock('../../lib/streaming/v2SseClient', () => {
  return {
    v2SseStream: async function* (formData) {
      // emit update for transcript
      yield { type: 'analysis.update', service: 'transcript', payload: 'Hello World' };
      // emit quantitative metrics update
      yield { type: 'analysis.update', service: 'quantitative_metrics', payload: { local: { word_count: 12 }}};
      // emit final done
      yield { type: 'analysis.done', payload: { transcript: 'Hello World Final', services: { quantitative_metrics: { local: { word_count: 12 } } } } };
    }
  }
})

import { useV2AnalysisSession } from '../useV2AnalysisSession'

const TestComponent = ({ sessionId }) => {
  const { state, startStreaming } = useV2AnalysisSession({ sessionId });
  useEffect(() => {
    const run = async () => {
      const fakeAudio = new Blob(['fake'], { type: 'audio/wav' });
      await startStreaming(fakeAudio);
    }
    run();
  }, [startStreaming]);

  return (
    <div>
      <div data-testid="status">{state.status}</div>
      <div data-testid="transcript">{state.transcript}</div>
      <div data-testid="wordcount">{state.services?.quantitative_metrics?.local?.word_count ?? ''}</div>
      <div data-testid="lastReceivedAt">{state.lastReceivedAt ?? ''}</div>
    </div>
  )
}

describe('useV2AnalysisSession', () => {
  it('processes SSE stream and updates state', async () => {
    render(<TestComponent sessionId={ 'session-1' } />);

    await waitFor(() => expect(screen.getByTestId('status').textContent).toBe('completed'), { timeout: 3000 });
    expect(screen.getByTestId('transcript').textContent).toBe('Hello World Final');
    expect(screen.getByTestId('wordcount').textContent).toBe('12');
    // Ensure a timestamp was set
    expect(screen.getByTestId('lastReceivedAt').textContent.length).toBeGreaterThan(0);
  })
})
