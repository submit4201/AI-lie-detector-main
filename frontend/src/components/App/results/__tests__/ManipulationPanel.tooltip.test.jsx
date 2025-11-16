import React from 'react'
import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import ManipulationAssessmentCard from '../ManipulationAssessmentCard'

describe('ManipulationAssessmentCard tooltip', () => {
  it('shows a title attribute (tooltip) for tactics', () => {
    const assessment = {
      manipulation_score: 80,
      manipulation_tactics: ['pressure', 'appeal_to_emotion'],
      manipulation_explanation: 'Test',
      example_phrases: ['say this']
    };
    render(<ManipulationAssessmentCard assessment={assessment} />);
    // the first tactic should have a title attribute coming from Tooltip
    const first = screen.getByText('pressure');
    expect(first).toHaveAttribute('title');
  });
});
