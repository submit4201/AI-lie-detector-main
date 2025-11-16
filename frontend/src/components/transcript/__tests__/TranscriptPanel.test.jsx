import React from 'react'
import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import TranscriptPanel from '../TranscriptPanel'

describe('TranscriptPanel accessibility', () => {
  it('uses aria-live when streaming', () => {
    render(<TranscriptPanel transcriptText="Hello" isStreaming={true} lastReceivedComponent={'transcript'} />);
    const p = screen.getByText('Hello');
    expect(p).toHaveAttribute('aria-live', 'polite');
  });

  it('turns aria-live off for final transcripts', () => {
    render(<TranscriptPanel transcriptText="Done" isStreaming={false} lastReceivedComponent={null} />);
    const p = screen.getByText('Done');
    expect(p).toHaveAttribute('aria-live', 'off');
  });
});
