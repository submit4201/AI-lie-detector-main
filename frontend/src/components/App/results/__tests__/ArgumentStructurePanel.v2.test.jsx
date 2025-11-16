import React from 'react'
import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import ArgumentStructurePanel from '../ArgumentStructurePanel'

describe('ArgumentStructurePanel extra UI', () => {
  it('renders coherence chart and claims list', () => {
    const svc = { overall_argument_coherence_score: 85, key_arguments: [{ claim: 'A', evidence: 'B', confidence: 0.9 }] };
    render(<ArgumentStructurePanel serviceData={svc} finalArgument={null} />);
    expect(screen.getByText('Argument Coherence')).toBeInTheDocument();
    expect(screen.getByText('Claim: A')).toBeInTheDocument();
    expect(screen.getByText(/Evidence: B/i)).toBeInTheDocument();
  });
});
