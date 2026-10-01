export default function SchemaPanel({ tables }) {
  if (!tables) {
    return <p className="muted">Loading schema…</p>
  }
  return (
    <div className="schema-panel">
      {tables.map((table) => (
        <details key={table.name} open>
          <summary>{table.name}</summary>
          <ul>
            {table.columns.map((column) => (
              <li key={column.name}>
                <span className={column.primary_key ? 'column-name pk' : 'column-name'}>{column.name}</span>
                <span className="column-type">
                  {column.type}
                  {column.nullable ? '' : ' NOT NULL'}
                </span>
              </li>
            ))}
          </ul>
        </details>
      ))}
    </div>
  )
}
