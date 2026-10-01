import { useCallback, useEffect, useMemo, useState } from 'react'
import { api } from './api/client.js'
import SchemaPanel from './components/SchemaPanel.jsx'
import SqlEditor from './components/SqlEditor.jsx'

const STARTER_SQL = 'SELECT *\nFROM customers\nLIMIT 10;\n'

export default function App() {
  const [health, setHealth] = useState(null)
  const [session, setSession] = useState(null)
  const [tables, setTables] = useState(null)
  const [error, setError] = useState(null)
  const [resetting, setResetting] = useState(false)
  const [, setSqlText] = useState(STARTER_SQL)

  const loadSchema = useCallback(async () => {
    const result = await api.schema()
    setTables(result.tables)
  }, [])

  useEffect(() => {
    Promise.all([api.health(), api.startSession()])
      .then(([healthResult, sessionResult]) => {
        setHealth(healthResult)
        setSession(sessionResult)
        return loadSchema()
      })
      .catch((err) => setError(err.message))
  }, [loadSchema])

  const editorSchema = useMemo(
    () => Object.fromEntries((tables ?? []).map((t) => [t.name, t.columns.map((c) => c.name)])),
    [tables],
  )

  async function handleReset() {
    if (!window.confirm('Reset your training database? All changes and progress will be lost.')) {
      return
    }
    setResetting(true)
    try {
      setSession(await api.resetDatabase())
      await loadSchema()
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
          <h2>Schema</h2>
          <SchemaPanel tables={tables} />
        </aside>

        <section className="workspace">
          <div className="card">
            <h2>Challenges</h2>
            <p className="muted">
              Challenges are coming next. The editor below already autocompletes table and column names from your
              training database; running queries arrives with the challenge engine.
            </p>
          </div>
          <SqlEditor initialValue={STARTER_SQL} onChange={setSqlText} schema={editorSchema} />
          <div className="actions">
            <button type="button" disabled title="Submission arrives with the challenge engine">
              Submit
            </button>
          </div>
        </section>
      </main>
    </div>
  )
}
