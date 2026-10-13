import { useEffect, useRef, useState } from 'react'
import { Database, RotateCcw, Server } from 'lucide-react'
import { TOTAL_LEVELS } from '../lib/chapters.js'

function SystemMenu({ health, session, backendOk }) {
  const [open, setOpen] = useState(false)
  const ref = useRef(null)

  useEffect(() => {
    if (!open) return undefined
    const onPointer = (event) => {
      if (!ref.current?.contains(event.target)) setOpen(false)
    }
    const onKey = (event) => {
      if (event.key === 'Escape') setOpen(false)
    }
    document.addEventListener('pointerdown', onPointer)
    document.addEventListener('keydown', onKey)
    return () => {
      document.removeEventListener('pointerdown', onPointer)
      document.removeEventListener('keydown', onKey)
    }
  }, [open])

  return (
    <div className="system" ref={ref}>
      <button
        type="button"
        className="btn btn-ghost system-trigger"
        aria-expanded={open}
        aria-controls="system-popover"
        aria-label={`System status: ${backendOk ? 'Connected' : 'Offline'}`}
        onClick={() => setOpen((value) => !value)}
      >
        <span className={`status-dot ${backendOk ? 'ok' : 'down'}`} aria-hidden="true" />
        <span>{backendOk ? 'Connected' : 'Offline'}</span>
      </button>
      {open && (
        <div className="popover" id="system-popover" role="region" aria-label="System details">
          <h2 className="eyebrow">System</h2>
          <dl>
            <div>
              <dt><Server size={14} aria-hidden="true" /> Backend</dt>
              <dd>{backendOk ? 'Connected' : 'Not reachable'}</dd>
            </div>
            <div>
              <dt><Database size={14} aria-hidden="true" /> SQLite</dt>
              <dd>{health?.sqlite_version ?? '—'}</dd>
            </div>
            <div>
              <dt>Learner</dt>
              <dd title={session?.learner_id}>{session ? session.learner_id.slice(0, 8) : '—'}</dd>
            </div>
          </dl>
        </div>
      )}
    </div>
  )
}

export default function ProductHeader({ health, session, backendOk, currentLevel, completedCount, onResetRequest, resetting }) {
  const percent = Math.round((completedCount / TOTAL_LEVELS) * 100)
  return (
    <header className="product-header">
      <div className="brand">
        <span className="brand-mark" aria-hidden="true">
          <Database size={18} />
        </span>
        <h1>
          <span className="brand-name">Brightcart</span>
          <span className="brand-sub">SQL Studio</span>
        </h1>
      </div>

      <div className="course-progress">
        <p>
          <strong>{currentLevel ? `Level ${currentLevel} of ${TOTAL_LEVELS}` : `${TOTAL_LEVELS} levels`}</strong>
          <span className="muted"> · {percent}% complete</span>
        </p>
        <div
          className="progress-track"
          role="progressbar"
          aria-label="Course completion"
          aria-valuemin={0}
          aria-valuemax={TOTAL_LEVELS}
          aria-valuenow={completedCount}
          aria-valuetext={`${completedCount} of ${TOTAL_LEVELS} levels complete`}
        >
          <span style={{ width: `${percent}%` }} />
        </div>
      </div>

      <div className="header-tools">
        <SystemMenu health={health} session={session} backendOk={backendOk} />
        <button type="button" className="btn btn-ghost btn-reset" onClick={onResetRequest} disabled={!session || resetting}>
          <RotateCcw size={15} aria-hidden="true" />
          <span>{resetting ? 'Resetting…' : 'Reset database'}</span>
        </button>
      </div>
    </header>
  )
}
