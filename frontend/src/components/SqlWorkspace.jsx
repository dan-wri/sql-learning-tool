import { Loader2, Play } from 'lucide-react'
import SqlEditor from './SqlEditor.jsx'

const isMac = typeof navigator !== 'undefined' && /mac|iphone|ipad/i.test(navigator.platform ?? navigator.userAgent ?? '')

export default function SqlWorkspace({ starterSql, onChange, onSubmit, schema, submitting, disabled }) {
  return (
    <section className="sql-workspace card" aria-label="SQL workspace">
      <div className="workspace-toolbar">
        <h3 className="eyebrow">SQL workspace</h3>
        <span className="dialect" title="Queries run against SQLite">SQLite</span>
        <span className="spacer" />
        <span className="shortcut" aria-hidden="true">
          <kbd>{isMac ? '⌘' : 'Ctrl'}</kbd>
          <kbd>Enter</kbd> to run
        </span>
        <button
          type="button"
          className="btn btn-primary"
          onClick={onSubmit}
          disabled={disabled || submitting}
          aria-keyshortcuts="Control+Enter Meta+Enter"
        >
          {submitting ? <Loader2 size={16} className="spin" aria-hidden="true" /> : <Play size={16} aria-hidden="true" />}
          {submitting ? 'Running…' : 'Submit'}
        </button>
      </div>
      <SqlEditor initialValue={starterSql} onChange={onChange} onSubmit={onSubmit} schema={schema} />
    </section>
  )
}
