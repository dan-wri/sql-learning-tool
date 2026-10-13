import { useState } from 'react'
import { ChevronDown, Lightbulb } from 'lucide-react'

export default function HintPanel({ hints, totalHints, onReveal, revealing }) {
  const [collapsed, setCollapsed] = useState(false)
  const used = hints.length
  const exhausted = used >= totalHints
  return (
    <section className="hint-panel" aria-label="Hints">
      <div className="hint-bar">
        <p>
          <Lightbulb size={16} aria-hidden="true" /> <strong>Need a hint?</strong>
          <span className="muted"> · {used}/{totalHints} used</span>
        </p>
        <div className="hint-actions">
          {used > 0 && (
            <button
              type="button"
              className="btn btn-ghost btn-sm"
              aria-expanded={!collapsed}
              aria-controls="hint-list"
              onClick={() => setCollapsed((value) => !value)}
            >
              <ChevronDown size={14} className={collapsed ? 'chevron collapsed' : 'chevron'} aria-hidden="true" />
              {collapsed ? 'Show hints' : 'Hide hints'}
            </button>
          )}
          <button type="button" className="btn btn-secondary btn-sm" onClick={onReveal} disabled={exhausted || revealing}>
            {exhausted ? 'No more hints' : used === 0 ? 'Reveal hint' : 'Reveal next hint'}
          </button>
        </div>
      </div>
      {used > 0 && !collapsed && (
        <ol className="hints" id="hint-list">
          {hints.map((hint, index) => (
            <li key={index}>
              <span className="hint-label">Hint {index + 1}</span>
              {hint}
            </li>
          ))}
        </ol>
      )}
    </section>
  )
}
