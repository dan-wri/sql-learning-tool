import { describe, expect, it, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import SqlEditor from '../src/components/SqlEditor.jsx'

describe('SqlEditor', () => {
  it('mounts CodeMirror with the initial SQL', () => {
    render(<SqlEditor initialValue="SELECT 1;" onChange={vi.fn()} />)
    const host = screen.getByTestId('sql-editor')
    expect(host.querySelector('.cm-editor')).not.toBeNull()
    expect(host.textContent).toContain('SELECT 1;')
  })
})
