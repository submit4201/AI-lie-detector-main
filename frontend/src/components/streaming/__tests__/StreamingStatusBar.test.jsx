import React from 'react'
import { describe, it, expect } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import StreamingStatusBar from '../StreamingStatusBar'
import { vi } from 'vitest'

describe('StreamingStatusBar', () => {
  it('renders status and last received with aria-live', () => {
    vi.useFakeTimers();
    vi.setSystemTime(new Date('2025-01-01T12:34:56Z'));
    const state = { status: 'streaming', progress: 42, lastReceived: 'transcript', lastReceivedAt: new Date().toISOString() };
    render(<StreamingStatusBar state={state} onStop={() => {}} onReset={() => {}} />);
    expect(screen.getByText('Streaming')).toBeInTheDocument();
    expect(screen.getByTestId('stream-last-received')).toHaveAttribute('aria-live', 'polite');
    // ensure timestamp added as dataset
    const el = screen.getByTestId('stream-last-received');
    expect(el.dataset.timestamp).toBeDefined();
    expect(el.dataset.timestamp.length).toBeGreaterThan(0);
    vi.useRealTimers();
  });
});
