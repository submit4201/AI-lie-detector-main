import React from 'react'
import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import ManipulationPanel from '../ManipulationPanel'

describe('ManipulationPanel extra UI', () => {
  it('renders radial score and tactics chart', () => {
    const service = { manipulation_score: 0.8, tactics: ['pressure','appeal_to_emotion'], rationale: 'Some text', examples: ['Try this'] };
    render(<ManipulationPanel serviceData={service} finalAssessment={null} />);
    expect(screen.getByText('Manipulation Score')).toBeInTheDocument();
    expect(screen.getByText(/Detected Tactics/i)).toBeInTheDocument();
  });

  it('shows rationale and example phrases', () => {
    const final = { manipulation_score: 70, manipulation_tactics: ['pressure'], manipulation_explanation: 'Direct pressure', example_phrases: ['You must...'] };
    render(<ManipulationPanel serviceData={null} finalAssessment={final} />);
    // may appear more than once (summary + matched reason), check it exists
    expect(screen.getAllByText('Direct pressure').length).toBeGreaterThan(0);
    expect(screen.getAllByText('You must...').length).toBeGreaterThan(0);
  });
});
