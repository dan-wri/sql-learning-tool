import { useCallback, useEffect, useMemo, useState } from 'react'
import { api } from './api/client.js'
import ChallengeList from './components/ChallengeList.jsx'
import ChallengeView from './components/ChallengeView.jsx'
import ChangePreview from './components/ChangePreview.jsx'
import FeedbackPanel from './components/FeedbackPanel.jsx'
import HintPanel from './components/HintPanel.jsx'
import ResultTable from './components/ResultTable.jsx'
import SchemaPanel from './components/SchemaPanel.jsx'
import SqlEditor from './components/SqlEditor.jsx'

const STARTER_SQL = 'SELECT *\nFROM customers\nLIMIT 10;\n'

function defaultChallengeId(challenges) {
  return (challenges.find((c) => c.status === 'unlocked') ?? challenges[0])?.id ?? null
}

export default function App() {
  const [health, setHealth] = useState(null)
  const [session, setSession] = useState(null)
  const [tables, setTables] = useState(null)
  const [challenges, setChallenges] = useState(null)
  const [selectedId, setSelectedId] = useState(null)
  const [challenge, setChallenge] = useState(null)
  const [sqlText, setSqlText] = useState(STARTER_SQL)
  const [submission, setSubmission] = useState(null)
  const [submitting, setSubmitting] = useState(false)
  const [revealingHint, setRevealingHint] = useState(false)
  const [error, setError] = useState(null)
  const [resetting, setResetting] = useState(false)

  const loadSchema = useCallback(async () => {
    const result = await api.schema()
    setTables(result.tables)
  }, [])

  const loadChallenges = useCallback(async () => {
    const list = await api.listChallenges()
    setChallenges(list)
    return list
  }, [])

  useEffect(() => {
    Promise.all([api.health(), api.startSession()])
      .then(([healthResult, sessionResult]) => {
        setHealth(healthResult)
        setSession(sessionResult)
        return Promise.all([loadSchema(), loadChallenges()])
      })
      .then(([, list]) => setSelectedId(defaultChallengeId(list)))
      .catch((err) => setError(err.message))
  }, [loadSchema, loadChallenges])

  useEffect(() => {
    if (!selectedId) {
      setChallenge(null)
      return
    }
    let cancelled = false
    setSubmission(null)
    api
      .getChallenge(selectedId)
      .then((detail) => !cancelled && setChallenge(detail))
      .catch((err) => !cancelled && setError(err.message))
    return () => {
      cancelled = true
    }
  }, [selectedId])

  const editorSchema = useMemo(
    () => Object.fromEntries((tables ?? []).map((t) => [t.name, t.columns.map((c) => c.name)])),
    [tables],
  )

  async function handleSubmit() {
    setSubmitting(true)
    setError(null)
    try {
      const outcome = await api.submit(selectedId, sqlText)
      setSubmission(outcome)
      if (outcome.passed) {
        const [, detail] = await Promise.all([loadChallenges(), api.getChallenge(selectedId)])
        setChallenge(detail)
      }
    } catch (err) {
      setError(err.message)
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
      setError(err.message)
    } finally {
      setRevealingHint(false)
    }
  }

  async function handleReset() {
    if (!window.confirm('Reset your training database? All changes and progress will be lost.')) {
      return
    }
    setResetting(true)
    setError(null)
    try {
      setSession(await api.resetDatabase())
      const [, list] = await Promise.all([loadSchema(), loadChallenges()])
      const nextId = defaultChallengeId(list)
      setSubmission(null)
      setSelectedId(nextId)
      // Selecting the same id again wouldn't re-trigger the effect, so refresh the detail directly.
      setChallenge(nextId ? await api.getChallenge(nextId) : null)
    } catch (err) {
      setError(err.message)
    } finally {
      setResetting(false)
    }
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1>SQL Learning Tool</h1>
        <div className="header-status">
          {health && <span className="badge ok">API ok · SQLite {health.sqlite_version}</span>}
          {session && <span className="badge" title={session.learner_id}>Learner {session.learner_id.slice(0, 8)}</span>}
          <button type="button" onClick={handleReset} disabled={!session || resetting}>
            {resetting ? 'Resetting…' : 'Reset database'}
          </button>
        </div>
      </header>

      {error && <div className="alert error">{error}</div>}
      {session?.stale && (
        <div className="alert warning">
          Your training database was created from an older dataset. Reset it to get the latest version.
        </div>
      )}

      <main className="layout">
        <aside className="sidebar">
          <h2>Challenges</h2>
          <ChallengeList challenges={challenges} selectedId={selectedId} onSelect={setSelectedId} />
          <h2 className="sidebar-section">Schema</h2>
          <SchemaPanel tables={tables} />
        </aside>

        <section className="workspace">
          <div className="card">
            <ChallengeView challenge={challenge} />
            {challenge && (
              <HintPanel
                hints={challenge.hints}
                totalHints={challenge.total_hints}
                onReveal={handleRevealHint}
                revealing={revealingHint}
              />
            )}
          </div>
          <SqlEditor initialValue={STARTER_SQL} onChange={setSqlText} schema={editorSchema} />
          <div className="actions">
            <button type="button" onClick={handleSubmit} disabled={!challenge || submitting}>
              {submitting ? 'Running…' : 'Submit'}
            </button>
          </div>
          <FeedbackPanel submission={submission} onNext={setSelectedId} />
          <ChangePreview
            changes={submission?.changes}
            persisted={submission?.persisted}
            reviewMode={submission?.review_mode}
          />
          <ResultTable result={submission?.result} />
        </section>
      </main>
    </div>
  )
}
