import { beforeEach, describe, expect, it, vi } from 'vitest'
import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import App from '../src/App.jsx'
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

const detail = (status) => ({
  id: 'one',
  title: 'Customer contact list',
  difficulty: 'beginner',
  status,
  instructions: 'Show every customer.',
  hints: [],
  total_hints: 2,
})

beforeEach(() => {
  vi.resetAllMocks()
  api.health.mockResolvedValue({ status: 'ok', sqlite_version: '3.50.0', seed_version: 1 })
  api.startSession.mockResolvedValue({ learner_id: '11111111-1111-4111-8111-111111111111', stale: false })
  api.schema.mockResolvedValue({ tables: [] })
  api.listChallenges
    .mockResolvedValueOnce([
      { id: 'one', title: 'Customer contact list', difficulty: 'beginner', status: 'unlocked' },
      { id: 'two', title: 'Premium products', difficulty: 'beginner', status: 'locked' },
    ])
    .mockResolvedValue([
      { id: 'one', title: 'Customer contact list', difficulty: 'beginner', status: 'completed' },
      { id: 'two', title: 'Premium products', difficulty: 'beginner', status: 'unlocked' },
    ])
  api.getChallenge.mockResolvedValueOnce(detail('unlocked')).mockResolvedValue(detail('completed'))
})

describe('App challenge flow', () => {
  it('submits SQL, shows results and unlocks the next challenge', async () => {
    api.submit.mockResolvedValue({
      passed: true,
      code: 'pass',
      message: 'Correct! Your query returns exactly the right result.',
      result: { columns: ['first_name'], rows: [['Ada']], truncated: false },
      newly_completed: true,
      next_challenge_id: 'two',
    })
    render(<App />)

    expect(await screen.findByText('Show every customer.')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /Premium products.*Locked/ })).toBeDisabled()

    fireEvent.click(screen.getByRole('button', { name: 'Submit' }))

    expect(await screen.findByText(/Correct!/)).toBeInTheDocument()
    expect(screen.getByRole('cell', { name: 'Ada' })).toBeInTheDocument()
    expect(api.submit).toHaveBeenCalledWith('one', expect.stringContaining('SELECT'))
    await waitFor(() => expect(screen.getByRole('button', { name: /Premium products.*Open/ })).toBeEnabled())
    expect(screen.getByRole('button', { name: /next challenge/i })).toBeInTheDocument()
  })

  it('shows failure feedback and keeps the next challenge locked', async () => {
    api.submit.mockResolvedValue({
      passed: false,
      code: 'row_count',
      message: 'Your query returns 10 rows, which is fewer than expected (60).',
      result: { columns: ['first_name'], rows: [['Ada']], truncated: false },
      newly_completed: false,
      next_challenge_id: null,
    })
    render(<App />)
    await screen.findByText('Show every customer.')

    fireEvent.click(screen.getByRole('button', { name: 'Submit' }))

    expect(await screen.findByText(/fewer than expected/)).toBeInTheDocument()
    expect(api.listChallenges).toHaveBeenCalledTimes(1)
    expect(screen.getByRole('button', { name: /Premium products.*Locked/ })).toBeDisabled()
  })
})
