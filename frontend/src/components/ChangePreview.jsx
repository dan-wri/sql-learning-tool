import { DatabaseZap, Minus, Pencil, Plus } from 'lucide-react'

function Cell({ value }) {
  return value === null ? <span className="null">NULL</span> : String(value)
}

function RowsTable({ columns, rows, kind }) {
  return (
    <div className="result-scroll short" tabIndex={0} role="region" aria-label={`${kind} rows`}>
      <table className="data-grid">
        <thead>
          <tr>
            {kind === 'updated' && <th aria-label="version" />}
            {columns.map((column) => (
              <th key={column}>{column}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map(({ label, values, changed }, index) => (
            <tr key={index} className={label ? `${kind} ${label}` : kind}>
              {kind === 'updated' && <td className="row-label">{label}</td>}
              {values.map((value, colIndex) => (
                <td key={colIndex} className={changed?.[colIndex] ? 'changed' : undefined}>
                  <Cell value={value} />
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

const SECTION_ICONS = { added: Plus, updated: Pencil, removed: Minus }

function Section({ kind, title, total, shown, children }) {
  if (total === 0) {
    return null
  }
  const Icon = SECTION_ICONS[kind]
  return (
    <div className={`change-section ${kind}`}>
      <h4>
        <Icon size={14} aria-hidden="true" />
        {title} ({total})
        {shown < total && <span className="muted"> · showing first {shown}</span>}
      </h4>
      {children}
    </div>
  )
}

function TableChanges({ change }) {
  const { table, columns, inserted, updated, deleted, counts } = change
  const updatedRows = updated.flatMap(({ before, after }) => {
    const changed = after.map((value, i) => value !== before[i])
    return [
      { label: 'before', values: before, changed },
      { label: 'after', values: after, changed },
    ]
  })
  return (
    <div className="table-changes">
      <h3>{table}</h3>
      <Section kind="added" title="Added" total={counts.inserted} shown={inserted.length}>
        <RowsTable columns={columns} rows={inserted.map((values) => ({ values }))} kind="inserted" />
      </Section>
      <Section kind="updated" title="Updated" total={counts.updated} shown={updated.length}>
        <RowsTable columns={columns} rows={updatedRows} kind="updated" />
      </Section>
      <Section kind="removed" title="Removed" total={counts.deleted} shown={deleted.length}>
        <RowsTable columns={columns} rows={deleted.map((values) => ({ values }))} kind="deleted" />
      </Section>
    </div>
  )
}

function persistenceNote(persisted, reviewMode) {
  if (persisted) {
    return { className: 'saved', text: 'Saved to your Brightcart database.' }
  }
  if (reviewMode) {
    return { className: 'discarded', text: 'Practice attempt — changes were rolled back and not saved.' }
  }
  return { className: 'discarded', text: 'Not saved — these changes were rolled back.' }
}

export default function ChangePreview({ changes, persisted, reviewMode }) {
  if (!changes) {
    return null
  }
  const note = persistenceNote(persisted, reviewMode)
  return (
    <section className="change-preview" aria-label="Your changes">
      <div className="output-head">
        <h3 className="eyebrow">
          <DatabaseZap size={14} aria-hidden="true" /> Your changes
        </h3>
        <span className={`persist-note ${note.className}`}>{note.text}</span>
      </div>
      {changes.length === 0 ? (
        <p className="empty-result">Your statement didn&apos;t change any data.</p>
      ) : (
        changes.map((change) => <TableChanges key={change.table} change={change} />)
      )}
    </section>
  )
}
