import { describe, expect, it, vi } from 'vitest'
import { fireEvent, render, screen } from '@testing-library/react'
import FeedbackPanel from '../src/components/FeedbackPanel.jsx'
import HintPanel from '../src/components/HintPanel.jsx'
import OutputWorkspace from '../src/components/OutputWorkspace.jsx'
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
    fireEvent.click(screen.getByRole('button', { name: 'Reveal hint' }))
    expect(onReveal).toHaveBeenCalledTimes(1)

    rerender(<HintPanel hints={['a', 'b']} totalHints={2} onReveal={onReveal} />)
    expect(screen.getAllByRole('listitem')).toHaveLength(2)
    expect(screen.getByText('2/2 used', { exact: false })).toBeInTheDocument()
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

describe('OutputWorkspace states', () => {
  it('shows an empty prompt before the first run and a busy state while running', () => {
    const { rerender } = render(<OutputWorkspace submission={null} submitting={false} />)
    expect(screen.getByText('Run your query to see the result here.')).toBeInTheDocument()
    rerender(<OutputWorkspace submission={null} submitting />)
    expect(screen.getByText('Running your query…')).toBeInTheDocument()
  })

  it('separates feedback from the result and explains a zero-row result', () => {
    render(
      <OutputWorkspace
        submission={{ passed: false, code: 'row_count', message: 'Too few rows.', result: { columns: ['a'], rows: [], truncated: false } }}
        submitting={false}
      />,
    )
    expect(screen.getByRole('status')).toHaveTextContent('Not quite yet')
    expect(screen.getByText('Query succeeded — 0 rows returned.')).toBeInTheDocument()
  })

  it('presents blocked statements as an explanation, not a failed answer', () => {
    render(
      <OutputWorkspace
        submission={{ passed: false, code: 'not_allowed', message: 'DROP isn’t allowed here.', result: null }}
        submitting={false}
      />,
    )
    expect(screen.getByRole('status')).toHaveClass('blocked')
    expect(screen.getByRole('status')).toHaveTextContent('isn’t allowed here')
  })

  it('shows saved changes for a mutation', () => {
    const changes = [{ table: 'customers', columns: ['id'], inserted: [[1]], updated: [], deleted: [], counts: { inserted: 1, updated: 0, deleted: 0 } }]
    render(<OutputWorkspace submission={{ passed: true, message: 'ok', changes, persisted: true, result: null }} submitting={false} />)
    expect(screen.getByRole('status')).toHaveTextContent('Challenge complete')
    expect(screen.getByText('Saved to your Brightcart database.')).toBeInTheDocument()
  })
})
