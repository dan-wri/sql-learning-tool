import { useCallback, useEffect, useMemo, useState } from 'react'
import { Database, ListTree, TriangleAlert, X } from 'lucide-react'
import { api } from './api/client.js'
import ChallengeNavigator from './components/ChallengeNavigator.jsx'
import ChallengeView from './components/ChallengeView.jsx'
import ChapterRail from './components/ChapterRail.jsx'
import ConfirmDialog from './components/ConfirmDialog.jsx'
import DatabaseExplorer from './components/DatabaseExplorer.jsx'
import HintPanel from './components/HintPanel.jsx'
import OutputWorkspace from './components/OutputWorkspace.jsx'
import ProductHeader from './components/ProductHeader.jsx'
import SqlWorkspace from './components/SqlWorkspace.jsx'
import { chapterOf, summariseChapters } from './lib/chapters.js'

const STARTER_SQL = 'SELECT *\nFROM customers\nLIMIT 10;\n'

function defaultChallenge(challenges) {
  return challenges.find((c) => c.status === 'unlocked') ?? challenges[0] ?? null
}

// Network failures get a product-level message; server messages are already learner-friendly.
function describeError(err) {
  if (err instanceof TypeError) {
    return {
      message: "We couldn't reach the local SQL service. Check that the backend is running, then try again.",
      details: err.message,
    }
  }
  return { message: err.message, details: null }
}

export default function App() {
  const [health, setHealth] = useState(null)
  const [session, setSession] = useState(null)
  const [tables, setTables] = useState(null)
  const [challenges, setChallenges] = useState(null)
  const [selectedId, setSelectedId] = useState(null)
  const [chapterId, setChapterId] = useState(1)
  const [challenge, setChallenge] = useState(null)
  const [sqlText, setSqlText] = useState(STARTER_SQL)
  const [submission, setSubmission] = useState(null)
  const [submitting, setSubmitting] = useState(false)
  const [revealingHint, setRevealingHint] = useState(false)
  const [error, setError] = useState(null)
  const [backendOk, setBackendOk] = useState(true)
  const [confirmingReset, setConfirmingReset] = useState(false)
  const [resetting, setResetting] = useState(false)
  const [panel, setPanel] = useState(null)

  const fail = useCallback((err) => setError(describeError(err)), [])

  const loadSchema = useCallback(async () => {
    const result = await api.schema()
    setTables(result.tables)
  }, [])

  const loadChallenges = useCallback(async () => {
    const list = await api.listChallenges()
    setChallenges(list)
    return list
  }, [])

  const selectChallenge = useCallback(
    (id, list) => {
      const target = (list ?? challenges ?? []).find((c) => c.id === id)
      if (target) setChapterId(chapterOf(target))
      setSelectedId(id)
      setPanel(null)
    },
    [challenges],
  )

  const bootstrap = useCallback(() => {
    setError(null)
    Promise.all([api.health(), api.startSession()])
      .then(([healthResult, sessionResult]) => {
        setHealth(healthResult)
        setSession(sessionResult)
        setBackendOk(true)
        return Promise.all([loadSchema(), loadChallenges()])
      })
      .then(([, list]) => {
        const first = defaultChallenge(list)
        if (first) selectChallenge(first.id, list)
      })
      .catch((err) => {
        setBackendOk(!(err instanceof TypeError))
        fail(err)
      })
  }, [loadSchema, loadChallenges, selectChallenge, fail])

  useEffect(() => {
    bootstrap()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  useEffect(() => {
    if (!selectedId) {
      setChallenge(null)
      return undefined
    }
    let cancelled = false
    setSubmission(null)
    setChallenge(null)
    api
      .getChallenge(selectedId)
      .then((detail) => !cancelled && setChallenge(detail))
      .catch((err) => !cancelled && fail(err))
    return () => {
      cancelled = true
    }
  }, [selectedId, fail])

  const editorSchema = useMemo(
    () => Object.fromEntries((tables ?? []).map((t) => [t.name, t.columns.map((c) => c.name)])),
    [tables],
  )
  const chapters = useMemo(() => summariseChapters(challenges), [challenges])
  const activeChapter = chapters.find((c) => c.id === chapterId) ?? chapters[0]
  const chapterChallenges = useMemo(
    () => (challenges ? challenges.filter((c) => chapterOf(c) === chapterId) : null),
    [challenges, chapterId],
  )
  const selectedSummary = challenges?.find((c) => c.id === selectedId)
  const completedCount = challenges ? challenges.filter((c) => c.status === 'completed').length : 0

  const nextChallenge = submission?.next_challenge_id
    ? challenges?.find((c) => c.id === submission.next_challenge_id)
    : null
  const canContinue = Boolean(nextChallenge && nextChallenge.status !== 'locked')

  async function handleSubmit() {
    if (!challenge || submitting) return
    setSubmitting(true)
    setError(null)
    try {
      const outcome = await api.submit(selectedId, sqlText)
      if (outcome.passed) {
        const [, detail] = await Promise.all([loadChallenges(), api.getChallenge(selectedId)])
        setChallenge(detail)
      }
      if (outcome.persisted && outcome.changes?.length) {
        await loadSchema()
      }
      setSubmission(outcome)
    } catch (err) {
      fail(err)
    } finally {
      setSubmitting(false)
    }
  }

  async function handleRevealHint() {
    setRevealingHint(true)
    try {
      const { hints } = await api.revealHint(selectedId)
      setChallenge((current) => ({ ...current, hints }))
    } catch (err) {
      fail(err)
    } finally {
      setRevealingHint(false)
    }
  }

  async function handleReset() {
    setConfirmingReset(false)
    setResetting(true)
    setError(null)
    try {
      setSession(await api.resetDatabase())
      const [, list] = await Promise.all([loadSchema(), loadChallenges()])
      const next = defaultChallenge(list)
      setSubmission(null)
      if (next) setChapterId(chapterOf(next))
      setSelectedId(next?.id ?? null)
      // Selecting the same id again wouldn't re-trigger the effect, so refresh the detail directly.
      setChallenge(next ? await api.getChallenge(next.id) : null)
    } catch (err) {
      fail(err)
    } finally {
      setResetting(false)
    }
  }

  const loadFailed = !challenges && error

  return (
    <div className="studio">
      <ProductHeader
        health={health}
        session={session}
        backendOk={backendOk}
        currentLevel={selectedSummary?.level ?? null}
        completedCount={completedCount}
        onResetRequest={() => setConfirmingReset(true)}
        resetting={resetting}
      />
      <ChapterRail
        chapters={chapters}
        selectedId={activeChapter?.id}
        onSelect={(id) => {
          setChapterId(id)
          const first = challenges?.find((c) => chapterOf(c) === id && c.status !== 'locked')
          if (first && chapterOf(selectedSummary) !== id) selectChallenge(first.id)
        }}
      />

      {panel && <div className="drawer-scrim" onClick={() => setPanel(null)} aria-hidden="true" />}

      <div className="studio-body">
        <aside className="side-panel nav-panel panel" data-open={panel === 'nav'} aria-label="Level navigator">
          <button type="button" className="btn btn-ghost drawer-close" onClick={() => setPanel(null)}>
            <X size={16} aria-hidden="true" /> Close
          </button>
          {activeChapter && (
            <ChallengeNavigator
              chapter={activeChapter}
              challenges={chapterChallenges}
              selectedId={selectedId}
              onSelect={selectChallenge}
            />
          )}
        </aside>

        <main className="workspace" data-chapter={chapterOf(selectedSummary ?? challenge)}>
          <div className="workspace-bar">
            <button type="button" className="btn btn-secondary btn-sm bar-levels" onClick={() => setPanel('nav')}>
              <ListTree size={15} aria-hidden="true" /> Levels
            </button>
            <button type="button" className="btn btn-secondary btn-sm bar-database" onClick={() => setPanel('db')}>
              <Database size={15} aria-hidden="true" /> Database
            </button>
          </div>

          {error && (
            <div className="alert error" role="alert">
              <TriangleAlert size={18} aria-hidden="true" />
              <div>
                <p>{error.message}</p>
                {error.details && (
                  <details>
                    <summary>Technical details</summary>
                    <code>{error.details}</code>
                  </details>
                )}
              </div>
              {loadFailed && (
                <button type="button" className="btn btn-secondary btn-sm" onClick={bootstrap}>
                  Try again
                </button>
              )}
            </div>
          )}
          {session?.stale && (
            <div className="alert warning" role="note">
              <TriangleAlert size={18} aria-hidden="true" />
              <p>Your training database was created from an older dataset. Reset it to get the latest version.</p>
            </div>
          )}

          <section className="card challenge-card">
            <ChallengeView challenge={challenge} loading={Boolean(selectedId) && !error} />
            {challenge && (
              <HintPanel
                hints={challenge.hints}
                totalHints={challenge.total_hints}
                onReveal={handleRevealHint}
                revealing={revealingHint}
              />
            )}
          </section>

          <SqlWorkspace
            starterSql={STARTER_SQL}
            onChange={setSqlText}
            onSubmit={handleSubmit}
            schema={editorSchema}
            submitting={submitting}
            disabled={!challenge}
          />
          <OutputWorkspace
            submission={submission}
            submitting={submitting}
            onNext={canContinue ? selectChallenge : undefined}
            nextLabel={nextChallenge?.level ? `Continue to Level ${nextChallenge.level}` : 'Next challenge'}
          />
        </main>

        <aside className="side-panel explorer-panel panel" data-open={panel === 'db'} aria-label="Database explorer">
          <button type="button" className="btn btn-ghost drawer-close" onClick={() => setPanel(null)}>
            <X size={16} aria-hidden="true" /> Close
          </button>
          <DatabaseExplorer tables={tables} />
        </aside>
      </div>

      {confirmingReset && (
        <ConfirmDialog
          title="Reset training database?"
          confirmLabel="Reset database"
          onConfirm={handleReset}
          onCancel={() => setConfirmingReset(false)}
        >
          Resetting will remove your Brightcart database changes and all course progress for this learner.
        </ConfirmDialog>
      )}
    </div>
  )
}
