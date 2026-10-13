import { beforeEach, describe, expect, it, vi } from 'vitest'
import { fireEvent, render, screen, waitFor, within } from '@testing-library/react'
import App from '../src/App.jsx'
import ChallengeList from '../src/components/ChallengeList.jsx'
import ChallengeView from '../src/components/ChallengeView.jsx'
import { api } from '../src/api/client.js'

vi.mock('../src/api/client.js', () => ({
  api: {
    health: vi.fn(),
    startSession: vi.fn(),
    resetDatabase: vi.fn(),
    schema: vi.fn(),
    listChallenges: vi.fn(),
    getChallenge: vi.fn(),
    revealHint: vi.fn(),
    submit: vi.fn(),
  },
}))

const TITLES = [
  'Meet the catalogue',
  'First contact sheet',
  'UK customers',
  'Budget finds',
  'Ready to sell',
  'Products needing attention',
  'Price list',
  'Premium range',
  'Top five by stock',
  'Missing phone numbers',
]

function listing(completedCount) {
  return TITLES.map((title, index) => ({
    id: `l${index + 1}`,
    level: index + 1,
    chapter: 1,
    title,
    difficulty: 'beginner',
    kind: 'query',
    status: index < completedCount ? 'completed' : index === completedCount ? 'unlocked' : 'locked',
  }))
}

const detailFor = (level, status = 'unlocked', hints = []) => ({
  ...listing(0)[level - 1],
  status,
  story: `Story for level ${level}.`,
  instructions: `Task for level ${level}.`,
  concepts: ['SELECT', 'FROM'],
  hints,
  total_hints: 3,
  review_mode: status === 'completed',
})

describe('ChallengeList with the Levels 1-10 block', () => {
  it('renders ten levels with locked, open and completed states', () => {
    render(<ChallengeList challenges={listing(3)} selectedId="l4" onSelect={vi.fn()} />)

    expect(screen.getAllByRole('button')).toHaveLength(10)
    expect(screen.getByRole('button', { name: /^1 Meet the catalogue.*Completed/ })).toBeEnabled()
    expect(screen.getByRole('button', { name: /^3 UK customers.*Completed/ })).toBeEnabled()
    expect(screen.getByRole('button', { name: /^4 Budget finds.*Open/ })).toHaveAttribute('aria-current', 'true')
    expect(screen.getByRole('button', { name: /^5 Ready to sell.*Locked/ })).toBeDisabled()
    expect(screen.getByRole('button', { name: /^10 Missing phone numbers.*Locked/ })).toBeDisabled()
  })

  it('only the first level is open on a fresh start', () => {
    render(<ChallengeList challenges={listing(0)} selectedId="l1" onSelect={vi.fn()} />)
    expect(screen.getAllByRole('button', { name: /Open/ })).toHaveLength(1)
    expect(screen.getAllByRole('button', { name: /Locked/ })).toHaveLength(9)
  })
})

describe('ChallengeView story and task', () => {
  it('shows the story separately from the task, in that order', () => {
    render(<ChallengeView challenge={detailFor(2)} />)

    const story = screen.getByRole('region', { name: 'The situation' })
    const task = screen.getByRole('region', { name: 'Your task' })
    expect(within(story).getByText('Story for level 2.')).toBeInTheDocument()
    expect(within(task).getByText('Task for level 2.')).toBeInTheDocument()
    expect(within(story).queryByText('Task for level 2.')).toBeNull()
    expect(story.compareDocumentPosition(task) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy()
    expect(screen.getByText('Chapter 1 · Foundations')).toBeInTheDocument()
    expect(screen.getByText('Level 2 / 100')).toBeInTheDocument()
    expect(screen.getByRole('list', { name: 'Concepts' })).toHaveTextContent('SELECT')
  })

  it('renders backticked identifiers in the task as inline code', () => {
    render(<ChallengeView challenge={{ ...detailFor(1), instructions: 'Return rows from `categories`.' }} />)
    expect(screen.getByText('categories').tagName).toBe('CODE')
  })

  it('explains review mode for a completed query without mentioning saved changes', () => {
    render(<ChallengeView challenge={detailFor(1, 'completed')} />)
    const note = screen.getByRole('note')
    expect(note).toHaveTextContent('Review mode')
    expect(note).toHaveTextContent('as it was when you first met this challenge')
    expect(note).not.toHaveTextContent("won't be saved")
  })
})

describe('App sequential progression', () => {
  let completed
  beforeEach(() => {
    vi.resetAllMocks()
    completed = 0
    api.health.mockResolvedValue({ status: 'ok', sqlite_version: '3.50.0', seed_version: 2 })
    api.startSession.mockResolvedValue({ learner_id: '11111111-1111-4111-8111-111111111111', stale: false })
    api.schema.mockResolvedValue({ tables: [] })
    api.listChallenges.mockImplementation(async () => listing(completed))
    api.getChallenge.mockImplementation(async (id) => {
      const level = Number(id.slice(1))
      return detailFor(level, level <= completed ? 'completed' : 'unlocked')
    })
  })

  it('unlocks the next level after a pass and lets the learner switch back to completed levels', async () => {
    api.submit.mockImplementation(async () => {
      completed += 1
      return {
        passed: true,
        code: 'pass',
        message: 'Correct! Your query returns exactly the right result.',
        result: { columns: ['name'], rows: [['Books']], truncated: false },
        newly_completed: true,
        next_challenge_id: `l${completed + 1}`,
      }
    })
    render(<App />)

    expect(await screen.findByText('Story for level 1.')).toBeInTheDocument()
    expect(screen.getAllByRole('button', { name: /Locked/ })).toHaveLength(9)

    fireEvent.click(screen.getByRole('button', { name: 'Submit' }))
    expect(await screen.findByText(/Correct!/)).toBeInTheDocument()
    await waitFor(() => expect(screen.getByRole('button', { name: /^2 First contact sheet.*Open/ })).toBeEnabled())
    expect(screen.getAllByRole('button', { name: /Locked/ })).toHaveLength(8)

    fireEvent.click(screen.getByRole('button', { name: /Continue to Level 2/ }))
    expect(await screen.findByText('Story for level 2.')).toBeInTheDocument()
    expect(screen.getByText('Task for level 2.')).toBeInTheDocument()

    fireEvent.click(screen.getByRole('button', { name: /^1 Meet the catalogue.*Completed/ }))
    expect(await screen.findByText('Story for level 1.')).toBeInTheDocument()
    expect(screen.getByRole('note')).toHaveTextContent('Review mode')
  })

  it('reveals hints one at a time', async () => {
    api.revealHint
      .mockResolvedValueOnce({ hints: ['First nudge.'], total_hints: 3 })
      .mockResolvedValueOnce({ hints: ['First nudge.', 'Second nudge.'], total_hints: 3 })
    render(<App />)
    await screen.findByText('Story for level 1.')

    fireEvent.click(screen.getByRole('button', { name: 'Reveal hint' }))
    expect(await screen.findByText('First nudge.')).toBeInTheDocument()
    expect(screen.queryByText('Second nudge.')).toBeNull()

    fireEvent.click(screen.getByRole('button', { name: 'Reveal next hint' }))
    expect(await screen.findByText('Second nudge.')).toBeInTheDocument()
    expect(screen.getByText('2/3 used', { exact: false })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Reveal next hint' })).toBeEnabled()
  })

  it('shows feedback for a wrong answer and leaves the next level locked', async () => {
    api.submit.mockResolvedValue({
      passed: false,
      code: 'row_order',
      message: 'You have the right rows, but not in the order the task asks for. Check your ORDER BY.',
      result: { columns: ['name'], rows: [['Books']], truncated: false },
      newly_completed: false,
      next_challenge_id: null,
    })
    render(<App />)
    await screen.findByText('Story for level 1.')

    fireEvent.click(screen.getByRole('button', { name: 'Submit' }))

    expect(await screen.findByText(/Check your ORDER BY/)).toBeInTheDocument()
    expect(screen.getAllByRole('button', { name: /Locked/ })).toHaveLength(9)
  })

  it('opens the level navigator and database explorer as drawers on narrow screens', async () => {
    render(<App />)
    await screen.findByText('Story for level 1.')
    const nav = screen.getByRole('complementary', { name: 'Level navigator' })
    const explorer = screen.getByRole('complementary', { name: 'Database explorer' })
    expect(nav).toHaveAttribute('data-open', 'false')

    fireEvent.click(screen.getByRole('button', { name: /Levels/ }))
    expect(nav).toHaveAttribute('data-open', 'true')
    fireEvent.click(within(nav).getByRole('button', { name: 'Close' }))
    expect(nav).toHaveAttribute('data-open', 'false')

    fireEvent.click(screen.getByRole('button', { name: /Database/ }))
    expect(explorer).toHaveAttribute('data-open', 'true')
  })

  it('returns to Level 1 only after a reset', async () => {
    completed = 4
    api.resetDatabase.mockImplementation(async () => {
      completed = 0
      return { learner_id: '11111111-1111-4111-8111-111111111111', stale: false }
    })
        render(<App />)
    expect(await screen.findByText('Story for level 5.')).toBeInTheDocument()

    fireEvent.click(screen.getByRole('button', { name: 'Reset database' }))
    const dialog = screen.getByRole('dialog')
    expect(dialog).toHaveTextContent('remove your Brightcart database changes and all course progress')
    expect(api.resetDatabase).not.toHaveBeenCalled()
    fireEvent.click(within(dialog).getByRole('button', { name: 'Reset database' }))

    expect(await screen.findByText('Story for level 1.')).toBeInTheDocument()
    expect(screen.getAllByRole('button', { name: /Open/ })).toHaveLength(1)
    expect(screen.getAllByRole('button', { name: /Locked/ })).toHaveLength(9)
  })
})
