import React from 'react'
import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import ResultsDisplay from '../ResultsDisplay'

const samplePartial = {
  transcript: 'Partial text',
  services: {
    manipulation: { score: 0.75, tactics: ['pressure', 'appeal_to_emotion'], explanation: 'Evasive phrasing' },
    argument: { score: 0.6, strengths: ['clear claim'], weaknesses: ['missing evidence'] },
    quantitative_metrics: { local: { word_count: 120 } }
  }
};

const sampleFinal = {
  transcript: 'Final text',
  manipulation_assessment: {
    manipulation_score: 78,
    manipulation_tactics: ['pressure'],
    manipulation_explanation: 'Direct pressure'
  },
  argument_analysis: {
    overall_argument_coherence_score: 85,
    argument_strengths: ['structure'],
    argument_weaknesses: []
  },
  services: {
    quantitative_metrics: { local: { word_count: 150 } },
  }
};

describe('ResultsDisplay - streaming partial vs final', () => {
  it('renders manipulation and argument from partial streaming', async () => {
    render(<ResultsDisplay isStreaming={true} partialResults={samplePartial} analysisResults={null} />);
    expect(screen.getByText('Influence Signals')).toBeInTheDocument();
    expect(screen.getByText('Identified Tactics')).toBeInTheDocument();
    expect(screen.getAllByText('Argument Structure').length).toBeGreaterThan(0);
  });

  it('renders final manipulation and argument from final results', () => {
    render(<ResultsDisplay isStreaming={false} partialResults={null} analysisResults={sampleFinal} />);
    expect(screen.getByText('Influence Signals')).toBeInTheDocument();
    expect(screen.getByText('Manipulation Likelihood')).toBeInTheDocument();
    expect(screen.getAllByText('Argument Structure').length).toBeGreaterThan(0);
  });
});
