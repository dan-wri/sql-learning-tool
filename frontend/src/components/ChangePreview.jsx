function formatCell(value) {
  return value === null ? <span className="null">NULL</span> : String(value)
}

function RowsTable({ columns, rows, rowClass }) {
  return (
    <div className="result-scroll">
      <table>
        <thead>
          <tr>
            {rowClass === 'updated' && <th aria-label="version" />}
            {columns.map((column) => (
              <th key={column}>{column}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map(({ label, values, changed }, index) => (
            <tr key={index} className={label ? `${rowClass} ${label}` : rowClass}>
              {rowClass === 'updated' && <td className="row-label">{label}</td>}
              {values.map((value, colIndex) => (
                <td key={colIndex} className={changed?.[colIndex] ? 'changed' : undefined}>
                  {formatCell(value)}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

function Section({ title, total, shown, children }) {
  if (total === 0) {
    return null
  }
  return (
    <div className="change-section">
      <h4>
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
      <Section title="Inserted rows" total={counts.inserted} shown={inserted.length}>
        <RowsTable columns={columns} rows={inserted.map((values) => ({ values }))} rowClass="inserted" />
      </Section>
      <Section title="Updated rows" total={counts.updated} shown={updated.length}>
        <RowsTable columns={columns} rows={updatedRows} rowClass="updated" />
      </Section>
      <Section title="Deleted rows" total={counts.deleted} shown={deleted.length}>
        <RowsTable columns={columns} rows={deleted.map((values) => ({ values }))} rowClass="deleted" />
      </Section>
    </div>
  )
}

function persistenceNote(persisted, reviewMode) {
  if (persisted) {
    return { className: 'saved', text: 'Saved to your training database.' }
  }
  if (reviewMode) {
    return { className: 'discarded', text: 'Review mode: these changes were rolled back and not saved.' }
  }
  return { className: 'discarded', text: 'Not saved: these changes were rolled back.' }
}

export default function ChangePreview({ changes, persisted, reviewMode }) {
  if (!changes) {
    return null
  }
  const note = persistenceNote(persisted, reviewMode)
  return (
    <section className="change-preview" aria-label="Your changes">
      <div className="change-preview-header">
        <h2>Your changes</h2>
        <span className={`persist-note ${note.className}`}>{note.text}</span>
      </div>
      {changes.length === 0 ? (
        <p className="muted">Your statement didn't change any data.</p>
      ) : (
        changes.map((change) => <TableChanges key={change.table} change={change} />)
      )}
    </section>
  )
}
