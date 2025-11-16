import React from 'react'
import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import ArgumentStructurePanel from '../ArgumentStructurePanel'

describe('ArgumentStructurePanel ConfidenceChip', () => {
  it('renders ConfidenceChip for claims', () => {
    const svc = { key_arguments: [{ claim: 'Tests', evidence: 'See logs', confidence: 0.92 }] };
    render(<ArgumentStructurePanel serviceData={svc} finalArgument={null} />);
    expect(screen.getByText('Claim: Tests')).toBeInTheDocument();
    // ConfidenceChip shows a 'High' label when >75
    expect(screen.getByText(/High/)).toBeInTheDocument();
  });
});
