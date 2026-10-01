import { describe, expect, it, vi } from 'vitest'
import { fireEvent, render, screen } from '@testing-library/react'
import ChallengeList from '../src/components/ChallengeList.jsx'

const CHALLENGES = [
  { id: 'one', title: 'First', difficulty: 'beginner', status: 'completed' },
  { id: 'two', title: 'Second', difficulty: 'beginner', status: 'unlocked' },
  { id: 'three', title: 'Third', difficulty: 'beginner', status: 'locked' },
]

describe('ChallengeList', () => {
  it('shows each status and disables locked challenges', () => {
    render(<ChallengeList challenges={CHALLENGES} selectedId="two" onSelect={vi.fn()} />)

    expect(screen.getByRole('button', { name: /First.*Completed/ })).toBeEnabled()
    expect(screen.getByRole('button', { name: /Second.*Open/ })).toHaveAttribute('aria-current', 'true')
    expect(screen.getByRole('button', { name: /Third.*Locked/ })).toBeDisabled()
  })

  it('selects an unlocked challenge', () => {
    const onSelect = vi.fn()
    render(<ChallengeList challenges={CHALLENGES} selectedId="two" onSelect={onSelect} />)

    fireEvent.click(screen.getByRole('button', { name: /First/ }))
    fireEvent.click(screen.getByRole('button', { name: /Third/ }))

    expect(onSelect).toHaveBeenCalledTimes(1)
    expect(onSelect).toHaveBeenCalledWith('one')
  })
})
