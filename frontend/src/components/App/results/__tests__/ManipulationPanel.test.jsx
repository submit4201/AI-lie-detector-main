import React from 'react'
import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import ManipulationPanel from '../ManipulationPanel'

describe('ManipulationPanel', () => {
  it('renders manipulation card for service payload', () => {
    const svc = { score: 0.8, tactics: ['pressure', 'appeal_to_emotion'], explanation: 'Evasive phrasing', examples: ['You must...'] };
    render(<ManipulationPanel serviceData={svc} finalAssessment={null} />);
    expect(screen.getByText('Manipulation Likelihood')).toBeInTheDocument();
    expect(screen.getByText('Identified Tactics')).toBeInTheDocument();
  });

  it('renders final assessment when provided', () => {
    const final = { manipulation_score: 72, manipulation_tactics: ['pressure'] };
    render(<ManipulationPanel serviceData={null} finalAssessment={final} />);
    expect(screen.getByText('Manipulation Likelihood')).toBeInTheDocument();
  });
});
