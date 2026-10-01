export default function HintPanel({ hints, totalHints, onReveal, revealing }) {
  const remaining = totalHints - hints.length
  return (
    <div className="hint-panel">
      {hints.length > 0 && (
        <ol className="hints">
          {hints.map((hint, index) => (
            <li key={index}>{hint}</li>
          ))}
        </ol>
      )}
      <button type="button" className="secondary" onClick={onReveal} disabled={remaining <= 0 || revealing}>
        {remaining <= 0 ? 'No more hints' : `Show hint (${hints.length + 1} of ${totalHints})`}
      </button>
    </div>
  )
}
