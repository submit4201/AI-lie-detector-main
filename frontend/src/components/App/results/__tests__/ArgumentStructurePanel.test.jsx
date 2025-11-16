import React from 'react'
import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import ArgumentStructurePanel from '../ArgumentStructurePanel'

describe('ArgumentStructurePanel', () => {
  it('renders argument analysis card for service payload', () => {
    const svc = { score: 0.6, strengths: ['Clear premise'], weaknesses: ['Missing evidence'] };
    render(<ArgumentStructurePanel serviceData={svc} finalArgument={null} />);
    expect(screen.getByText('Argument Coherence Score')).toBeInTheDocument();
  });

  it('renders final argument analysis when provided', () => {
    const final = { overall_argument_coherence_score: 88, argument_strengths: ['Structure'] };
    render(<ArgumentStructurePanel serviceData={null} finalArgument={final} />);
    expect(screen.getByText('Argument Coherence Score')).toBeInTheDocument();
  });
});
