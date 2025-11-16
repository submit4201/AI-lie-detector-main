import React from 'react'
import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import ResultsDisplay from '../ResultsDisplay'

const samplePartial = {
  transcript: 'Partial text',
  services: {
    manipulation: { score: 0.75, tactics: ['pressure', 'appeal_to_emotion'], explanation: 'Evasive phrasing' },
  }
};

const sampleFinal = {
  transcript: 'Final text',
  manipulation_assessment: {
    manipulation_score: 78,
    manipulation_tactics: ['pressure'],
    manipulation_explanation: 'Direct pressure'
  },
  services: {}
};

describe('ResultsDisplay ARIA and partial->final', () => {
  it('shows streaming badge for manipulation on partial and turns off on final', () => {
    const { rerender } = render(<ResultsDisplay isStreaming={true} partialResults={samplePartial} analysisResults={null} lastReceivedComponent={'manipulation'} />);
    // Should show the manipulation streaming component highlighted
    expect(screen.getByText('Influence Signals')).toBeInTheDocument();
    expect(screen.getByText('Identified Tactics')).toBeInTheDocument();
    const manipulationLabel = screen.getByTestId('service-label-manipulation');
    const streamingCard = manipulationLabel.closest('[data-service-key="manipulation"]');
    expect(streamingCard).not.toBeNull();
    expect(streamingCard?.getAttribute('data-service-status')).toBe('streaming');

    // Re-render with final analysis
    rerender(<ResultsDisplay isStreaming={false} partialResults={null} analysisResults={sampleFinal} lastReceivedComponent={null} />);
    // Final should show the Manipulation Likelihood card
    expect(screen.getByText('Manipulation Likelihood')).toBeInTheDocument();
    const finalCard = screen.getByTestId('service-label-manipulation').closest('[data-service-key="manipulation"]');
    expect(finalCard?.getAttribute('data-service-status')).not.toBe('streaming');
  });
});
