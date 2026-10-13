import { describe, expect, it, vi } from 'vitest'
import { fireEvent, render, screen, within } from '@testing-library/react'
import ChallengeList from '../src/components/ChallengeList.jsx'
import ChallengeNavigator from '../src/components/ChallengeNavigator.jsx'
import ChapterRail from '../src/components/ChapterRail.jsx'
import DatabaseExplorer from '../src/components/DatabaseExplorer.jsx'
import ProductHeader from '../src/components/ProductHeader.jsx'
import SqlWorkspace from '../src/components/SqlWorkspace.jsx'
import { summariseChapters } from '../src/lib/chapters.js'

const CHALLENGES = [
  { id: 'one', level: 1, chapter: 1, title: 'First', concepts: ['SELECT'], kind: 'query', status: 'completed' },
  { id: 'two', level: 2, chapter: 1, title: 'Second', concepts: ['WHERE'], kind: 'query', status: 'unlocked' },
  { id: 'three', level: 3, chapter: 1, title: 'Third', concepts: [], kind: 'mutation', status: 'locked' },
]

describe('ChallengeList', () => {
  it('shows each state in text and disables locked levels', () => {
    render(<ChallengeList challenges={CHALLENGES} selectedId="two" onSelect={vi.fn()} />)

    expect(screen.getByRole('button', { name: /First.*Completed/ })).toBeEnabled()
    expect(screen.getByRole('button', { name: /Second.*Open/ })).toHaveAttribute('aria-current', 'true')
    expect(screen.getByRole('button', { name: /Third.*Locked/ })).toBeDisabled()
    expect(screen.getByRole('img', { name: 'Changes data' })).toBeInTheDocument()
  })

  it('selects unlocked levels only', () => {
    const onSelect = vi.fn()
    render(<ChallengeList challenges={CHALLENGES} selectedId="two" onSelect={onSelect} />)

    fireEvent.click(screen.getByRole('button', { name: /First/ }))
    fireEvent.click(screen.getByRole('button', { name: /Third/ }))

    expect(onSelect).toHaveBeenCalledTimes(1)
    expect(onSelect).toHaveBeenCalledWith('one')
  })

  it('shows a skeleton while loading', () => {
    render(<ChallengeList challenges={null} selectedId={null} onSelect={vi.fn()} />)
    expect(screen.getByLabelText('Loading levels')).toHaveAttribute('aria-busy', 'true')
  })
})

describe('chapter summaries', () => {
  it('keeps later chapters locked until all 20 levels of the previous one are complete', () => {
    const tenDone = Array.from({ length: 10 }, (_, i) => ({ id: `c${i}`, chapter: 1, status: 'completed' }))
    const [one, two] = summariseChapters(tenDone)
    expect(one).toMatchObject({ completed: 10, total: 20, unlocked: true, complete: false })
    expect(two.unlocked).toBe(false)

    const twentyDone = Array.from({ length: 20 }, (_, i) => ({ id: `c${i}`, chapter: 1, status: 'completed' }))
    const chapters = summariseChapters(twentyDone)
    expect(chapters[0].complete).toBe(true)
    expect(chapters[1].unlocked).toBe(true)
    expect(chapters[2].unlocked).toBe(false)
  })
})

describe('ChapterRail', () => {
  const chapters = summariseChapters(CHALLENGES)

  it('shows all five chapters with progress, selected and locked states', () => {
    render(<ChapterRail chapters={chapters} selectedId={1} onSelect={vi.fn()} />)

    expect(screen.getAllByRole('listitem')).toHaveLength(5)
    expect(screen.getByRole('button', { name: /Foundations.*1\/20/ })).toHaveAttribute('aria-current', 'true')
    const locked = screen.getByRole('button', { name: /Relational SQL.*locked/ })
    expect(locked).toHaveAttribute('aria-disabled', 'true')
    expect(locked).toHaveAttribute('title', 'Complete Chapter 1 to unlock Relational SQL.')
  })

  it('does not select a locked chapter', () => {
    const onSelect = vi.fn()
    render(<ChapterRail chapters={chapters} selectedId={1} onSelect={onSelect} />)
    fireEvent.click(screen.getByRole('button', { name: /Relational SQL/ }))
    expect(onSelect).not.toHaveBeenCalled()
    fireEvent.click(screen.getByRole('button', { name: /Foundations/ }))
    expect(onSelect).toHaveBeenCalledWith(1)
  })
})

describe('ChallengeNavigator', () => {
  it('shows the chapter, its progress and a note while the chapter is incomplete', () => {
    const chapter = summariseChapters(CHALLENGES)[0]
    render(<ChallengeNavigator chapter={chapter} challenges={CHALLENGES} selectedId="two" onSelect={vi.fn()} />)
    expect(screen.getByRole('heading', { name: 'Foundations' })).toBeInTheDocument()
    expect(screen.getByRole('progressbar', { name: 'Chapter 1 progress' })).toHaveAttribute('aria-valuenow', '1')
    expect(screen.getByText(/More levels in this chapter are on the way/)).toBeInTheDocument()
  })
})

describe('ProductHeader', () => {
  it('leads with course progress and keeps system details secondary', () => {
    const onReset = vi.fn()
    render(
      <ProductHeader
        health={{ sqlite_version: '3.54.0' }}
        session={{ learner_id: '16395757-aaaa-4aaa-8aaa-aaaaaaaaaaaa' }}
        backendOk
        currentLevel={7}
        completedCount={7}
        onResetRequest={onReset}
        resetting={false}
      />,
    )
    expect(screen.getByRole('heading', { name: /Brightcart\s*SQL Studio/ })).toBeInTheDocument()
    expect(screen.getByText('Level 7 of 100')).toBeInTheDocument()
    expect(screen.getByRole('progressbar', { name: 'Course completion' })).toHaveAttribute('aria-valuenow', '7')
    expect(screen.queryByText('3.54.0')).toBeNull()

    fireEvent.click(screen.getByRole('button', { name: /Connected/ }))
    const system = screen.getByRole('region', { name: 'System details' })
    expect(within(system).getByText('3.54.0')).toBeInTheDocument()
    expect(within(system).getByText('16395757')).toBeInTheDocument()

    fireEvent.click(screen.getByRole('button', { name: 'Reset database' }))
    expect(onReset).toHaveBeenCalled()
  })
})

describe('SqlWorkspace', () => {
  it('runs from the toolbar button and from the keyboard shortcut', () => {
    const onSubmit = vi.fn()
    render(<SqlWorkspace starterSql="SELECT 1;" onChange={vi.fn()} onSubmit={onSubmit} schema={{}} />)

    fireEvent.click(screen.getByRole('button', { name: 'Submit' }))
    expect(onSubmit).toHaveBeenCalledTimes(1)

    const content = screen.getByTestId('sql-editor').querySelector('.cm-content')
    fireEvent.keyDown(content, { key: 'Enter', code: 'Enter', ctrlKey: true })
    expect(onSubmit).toHaveBeenCalledTimes(2)
  })

  it('disables Submit while running', () => {
    render(<SqlWorkspace starterSql="" onChange={vi.fn()} onSubmit={vi.fn()} schema={{}} submitting />)
    expect(screen.getByRole('button', { name: 'Running…' })).toBeDisabled()
  })
})

const TABLES = [
  {
    name: 'customers',
    row_count: 80,
    columns: [
      { name: 'customer_id', type: 'INTEGER', nullable: false, primary_key: true, references: null },
      { name: 'phone', type: 'TEXT', nullable: true, primary_key: false, references: null },
    ],
  },
  {
    name: 'orders',
    row_count: 405,
    columns: [
      { name: 'order_id', type: 'INTEGER', nullable: false, primary_key: true, references: null },
      {
        name: 'customer_id',
        type: 'INTEGER',
        nullable: false,
        primary_key: false,
        references: { table: 'customers', column: 'customer_id' },
      },
    ],
  },
]

describe('DatabaseExplorer', () => {
  it('shows a loading state before the schema arrives', () => {
    render(<DatabaseExplorer tables={null} />)
    expect(screen.getByLabelText('Loading schema')).toHaveAttribute('aria-busy', 'true')
  })

  it('shows tables with row counts, keys, relationships and nullability', () => {
    render(<DatabaseExplorer tables={TABLES} />)

    expect(screen.getByRole('button', { name: /customers.*80 rows/ })).toHaveAttribute('aria-expanded', 'true')
    expect(screen.getAllByRole('img', { name: 'Primary key' })).toHaveLength(2)
    expect(screen.getByRole('img', { name: 'Foreign key' })).toBeInTheDocument()
    expect(screen.getByText('→ customers.customer_id')).toBeInTheDocument()
    expect(screen.getByText(/nullable/)).toBeInTheDocument()
  })

  it('collapses tables individually and all at once', () => {
    render(<DatabaseExplorer tables={TABLES} />)
    fireEvent.click(screen.getByRole('button', { name: /customers/ }))
    expect(screen.getByRole('button', { name: /customers/ })).toHaveAttribute('aria-expanded', 'false')
    expect(screen.queryByText('phone')).toBeNull()

    fireEvent.click(screen.getByRole('button', { name: 'Collapse all' }))
    expect(screen.queryByText('order_id')).toBeNull()
    fireEvent.click(screen.getByRole('button', { name: 'Expand all' }))
    expect(screen.getByText('order_id')).toBeInTheDocument()
  })

  it('filters by table name and column name', () => {
    render(<DatabaseExplorer tables={TABLES} />)
    const search = screen.getByRole('searchbox', { name: /search tables and columns/i })

    fireEvent.change(search, { target: { value: 'phone' } })
    expect(screen.getByRole('button', { name: /customers/ })).toBeInTheDocument()
    expect(screen.queryByRole('button', { name: /orders/ })).toBeNull()
    expect(screen.queryByText('customer_id')).toBeNull()

    fireEvent.change(search, { target: { value: 'orders' } })
    expect(screen.getByText('order_id')).toBeInTheDocument()

    fireEvent.change(search, { target: { value: 'zzz' } })
    expect(screen.getByText(/No tables or columns match/)).toBeInTheDocument()
  })
})
