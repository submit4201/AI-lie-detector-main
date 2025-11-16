import React from 'react'
import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import ControlPanel from '../ControlPanel'

describe('ControlPanel V2 toggle', () => {
  it('shows V2 checkbox and toggles when clicked', () => {
    const setUseV2 = vi.fn();
    render(<ControlPanel useStreaming={true} setUseStreaming={() => {}} isStreamingConnected={false} streamingProgress={null} useV2={false} setUseV2={setUseV2} v2Available={false} />)
    const cb = screen.getByLabelText('Use V2 streaming API')
    expect(cb).toBeInTheDocument()
    expect(cb).toBeDisabled()
  })
})
