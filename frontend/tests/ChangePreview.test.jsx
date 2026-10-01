import { describe, expect, it } from 'vitest'
import { render, screen, within } from '@testing-library/react'
import ChangePreview from '../src/components/ChangePreview.jsx'
import ChallengeView from '../src/components/ChallengeView.jsx'

const COLUMNS = ['customer_id', 'first_name', 'phone']

function change(overrides = {}) {
  return {
    table: 'customers',
    columns: COLUMNS,
    inserted: [],
    updated: [],
    deleted: [],
    counts: { inserted: 0, updated: 0, deleted: 0 },
    ...overrides,
  }
}

describe('ChangePreview', () => {
  it('renders nothing for query submissions', () => {
    const { container } = render(<ChangePreview changes={null} />)
    expect(container).toBeEmptyDOMElement()
  })

  it('shows inserted rows and that they were saved', () => {
    render(
      <ChangePreview
        changes={[change({ inserted: [[61, 'Grace', null]], counts: { inserted: 1, updated: 0, deleted: 0 } })]}
        persisted
      />,
    )
    expect(screen.getByText('Saved to your training database.')).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: 'Inserted rows (1)' })).toBeInTheDocument()
    expect(screen.getByRole('cell', { name: 'Grace' })).toBeInTheDocument()
    expect(screen.getByText('NULL')).toBeInTheDocument()
    expect(screen.queryByRole('heading', { name: /Updated rows/ })).toBeNull()
  })

  it('shows updated rows as before and after with changed cells marked', () => {
    render(
      <ChangePreview
        changes={[
          change({
            updated: [{ before: [1, 'Ava', null], after: [1, 'Ava', '0700'] }],
            counts: { inserted: 0, updated: 1, deleted: 0 },
          }),
        ]}
      />,
    )
    const section = screen.getByRole('heading', { name: 'Updated rows (1)' }).parentElement
    expect(within(section).getByText('before')).toBeInTheDocument()
    expect(within(section).getByRole('cell', { name: '0700' })).toHaveClass('changed')
    expect(screen.getByText('Not saved: these changes were rolled back.')).toBeInTheDocument()
  })

  it('shows deleted rows and notes when the list is capped', () => {
    render(
      <ChangePreview
        changes={[change({ deleted: [[5, 'Bo', null]], counts: { inserted: 0, updated: 0, deleted: 80 } })]}
        reviewMode
      />,
    )
    expect(screen.getByRole('heading', { name: /Deleted rows \(80\)/ })).toHaveTextContent('showing first 1')
    expect(screen.getByText(/Review mode: these changes were rolled back/)).toBeInTheDocument()
  })

  it('explains when nothing changed', () => {
    render(<ChangePreview changes={[]} />)
    expect(screen.getByText("Your statement didn't change any data.")).toBeInTheDocument()
  })
})

describe('ChallengeView', () => {
  const base = {
    id: 'add-new-customer',
    title: 'Welcome a new customer',
    difficulty: 'beginner',
    kind: 'mutation',
    instructions: 'Add Grace.',
    hints: [],
    total_hints: 3,
  }

  it('marks mutation challenges without review mode before completion', () => {
    render(<ChallengeView challenge={{ ...base, status: 'unlocked', review_mode: false }} />)
    expect(screen.getByText('Changes data')).toBeInTheDocument()
    expect(screen.queryByRole('note')).toBeNull()
  })

  it('explains review mode for completed mutation challenges', () => {
    render(<ChallengeView challenge={{ ...base, status: 'completed', review_mode: true }} />)
    const note = screen.getByRole('note')
    expect(note).toHaveTextContent('Review mode')
    expect(note).toHaveTextContent("won't be saved")
  })
})
