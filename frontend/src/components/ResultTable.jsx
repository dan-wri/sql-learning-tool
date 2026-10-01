function formatCell(value) {
  return value === null ? <span className="null">NULL</span> : String(value)
}

export default function ResultTable({ result }) {
  if (!result) {
    return null
  }
  const { columns, rows, truncated } = result
  return (
    <div className="result">
      <p className="muted">
        {rows.length} {rows.length === 1 ? 'row' : 'rows'}
        {truncated && ' (showing the first rows only)'}
      </p>
      <div className="result-scroll">
        <table>
          <thead>
            <tr>
              {columns.map((column, index) => (
                <th key={index}>{column}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((row, rowIndex) => (
              <tr key={rowIndex}>
                {row.map((value, colIndex) => (
                  <td key={colIndex}>{formatCell(value)}</td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
