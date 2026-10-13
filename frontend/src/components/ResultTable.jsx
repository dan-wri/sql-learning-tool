const isNumber = (value) => typeof value === 'number'

function Cell({ value }) {
  return value === null ? <span className="null">NULL</span> : String(value)
}

export default function ResultTable({ result }) {
  if (!result) {
    return null
  }
  const { columns, rows, truncated } = result
  const count = `${rows.length} ${rows.length === 1 ? 'row' : 'rows'}`
  return (
    <section className="result" aria-label="Query result">
      <div className="output-head">
        <h3 className="eyebrow">Result</h3>
        <span className="row-count">
          {count}
          {truncated && ' · showing the first rows only'}
        </span>
      </div>
      {rows.length === 0 ? (
        <p className="empty-result">Query succeeded — 0 rows returned.</p>
      ) : (
        <div className="result-scroll" tabIndex={0} role="region" aria-label="Result rows">
          <table className="data-grid">
            <thead>
              <tr>
                {columns.map((column, index) => (
                  <th key={index} className={isNumber(rows[0][index]) ? 'num' : undefined}>
                    {column}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {rows.map((row, rowIndex) => (
                <tr key={rowIndex}>
                  {row.map((value, colIndex) => (
                    <td key={colIndex} className={isNumber(value) ? 'num' : undefined}>
                      <Cell value={value} />
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  )
}
