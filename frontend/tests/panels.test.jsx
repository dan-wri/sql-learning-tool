import { describe, expect, it, vi } from 'vitest'
import { fireEvent, render, screen } from '@testing-library/react'
import FeedbackPanel from '../src/components/FeedbackPanel.jsx'
import HintPanel from '../src/components/HintPanel.jsx'
import ResultTable from '../src/components/ResultTable.jsx'

describe('FeedbackPanel', () => {
  it('shows failure feedback without a next button', () => {
    render(<FeedbackPanel submission={{ passed: false, message: 'Your query returns 5 rows', next_challenge_id: null }} />)
    expect(screen.getByRole('status')).toHaveTextContent('Not quite')
    expect(screen.getByRole('status')).toHaveTextContent('Your query returns 5 rows')
    expect(screen.queryByRole('button')).toBeNull()
  })

  it('offers the next challenge after a pass', () => {
    const onNext = vi.fn()
    render(<FeedbackPanel submission={{ passed: true, message: 'Correct!', next_challenge_id: 'two' }} onNext={onNext} />)
    fireEvent.click(screen.getByRole('button', { name: /next challenge/i }))
    expect(onNext).toHaveBeenCalledWith('two')
  })
})

describe('HintPanel', () => {
  it('reveals hints one at a time and stops at the last', () => {
    const onReveal = vi.fn()
    const { rerender } = render(<HintPanel hints={[]} totalHints={2} onReveal={onReveal} />)
    fireEvent.click(screen.getByRole('button', { name: 'Show hint (1 of 2)' }))
    expect(onReveal).toHaveBeenCalledTimes(1)

    rerender(<HintPanel hints={['a', 'b']} totalHints={2} onReveal={onReveal} />)
    expect(screen.getAllByRole('listitem')).toHaveLength(2)
    expect(screen.getByRole('button', { name: 'No more hints' })).toBeDisabled()
  })
})

describe('ResultTable', () => {
  it('renders columns, rows and NULLs', () => {
    render(<ResultTable result={{ columns: ['name', 'phone'], rows: [['Ada', null]], truncated: false }} />)
    expect(screen.getByRole('columnheader', { name: 'phone' })).toBeInTheDocument()
    expect(screen.getByText('NULL')).toHaveClass('null')
    expect(screen.getByText('1 row')).toBeInTheDocument()
  })
})
