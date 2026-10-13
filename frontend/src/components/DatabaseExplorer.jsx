import { useMemo, useState } from 'react'
import { ChevronDown, Database, KeyRound, Link2, Search, Table2 } from 'lucide-react'

function Column({ column }) {
  const fk = column.references
  return (
    <li className="column-row">
      <span className="column-key">
        {column.primary_key && (
          <span title="Primary key" role="img" aria-label="Primary key" className="key pk">
            <KeyRound size={13} />
          </span>
        )}
        {fk && (
          <span title={`Foreign key → ${fk.table}.${fk.column}`} role="img" aria-label="Foreign key" className="key fk">
            <Link2 size={13} />
          </span>
        )}
      </span>
      <span className="column-main">
        <span className={column.primary_key ? 'column-name pk' : 'column-name'}>{column.name}</span>
        {fk && (
          <span className="column-ref">
            → {fk.table}.{fk.column}
          </span>
        )}
      </span>
      <span className="column-type">
        {column.type || 'ANY'}
        {column.nullable && !column.primary_key && <span className="nullable"> · nullable</span>}
      </span>
    </li>
  )
}

function TableCard({ table, columns, open, onToggle }) {
  const bodyId = `table-${table.name}`
  return (
    <li className={`table-card${open ? ' open' : ''}`}>
      <button type="button" className="table-toggle" aria-expanded={open} aria-controls={bodyId} onClick={onToggle}>
        <ChevronDown size={15} className="chevron" aria-hidden="true" />
        <Table2 size={15} className="table-icon" aria-hidden="true" />
        <span className="table-name">{table.name}</span>
        <span className="table-rows">
          {table.row_count != null ? `${table.row_count.toLocaleString()} rows` : `${table.columns.length} cols`}
        </span>
      </button>
      {open && (
        <ul className="column-list" id={bodyId}>
          {columns.map((column) => (
            <Column key={column.name} column={column} />
          ))}
        </ul>
      )}
    </li>
  )
}

export default function DatabaseExplorer({ tables }) {
  const [query, setQuery] = useState('')
  const [collapsed, setCollapsed] = useState(() => new Set())
  const needle = query.trim().toLowerCase()

  const visible = useMemo(() => {
    if (!tables) return []
    return tables
      .map((table) => {
        const tableMatch = table.name.toLowerCase().includes(needle)
        const columns = !needle || tableMatch ? table.columns : table.columns.filter((c) => c.name.toLowerCase().includes(needle))
        return { table, columns, show: !needle || tableMatch || columns.length > 0 }
      })
      .filter((entry) => entry.show)
  }, [tables, needle])

  const allCollapsed = tables ? collapsed.size >= tables.length : false
  const toggle = (name) =>
    setCollapsed((current) => {
      const next = new Set(current)
      if (!next.delete(name)) next.add(name)
      return next
    })

  return (
    <div className="explorer">
      <div className="explorer-head">
        <div className="explorer-title">
          <div>
            <p className="eyebrow">Database</p>
            <h2>
              <Database size={16} aria-hidden="true" /> Brightcart
            </h2>
          </div>
          {tables && (
            <button
              type="button"
              className="btn btn-ghost btn-sm"
              onClick={() => setCollapsed(allCollapsed ? new Set() : new Set(tables.map((t) => t.name)))}
            >
              {allCollapsed ? 'Expand all' : 'Collapse all'}
            </button>
          )}
        </div>
        <label className="search">
          <Search size={15} aria-hidden="true" />
          <span className="sr-only">Search tables and columns</span>
          <input
            type="search"
            placeholder="Search tables and columns"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
          />
        </label>
      </div>

      <div className="explorer-scroll">
        {!tables ? (
          <div aria-busy="true" aria-label="Loading schema">
            <p className="sr-only">Loading schema…</p>
            {[0, 1, 2].map((i) => (
              <div key={i} className="skeleton skeleton-table" />
            ))}
          </div>
        ) : visible.length === 0 ? (
          <p className="muted pad">No tables or columns match “{query}”.</p>
        ) : (
          <ul className="table-list">
            {visible.map(({ table, columns }) => (
              <TableCard
                key={table.name}
                table={table}
                columns={columns}
                open={Boolean(needle) || !collapsed.has(table.name)}
                onToggle={() => toggle(table.name)}
              />
            ))}
          </ul>
        )}
        {tables && (
          <p className="explorer-note">
            Your Brightcart database. Changes from completed levels that change data persist here.
          </p>
        )}
      </div>
    </div>
  )
}
