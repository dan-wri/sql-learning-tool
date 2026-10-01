const STATUS_LABELS = {
  completed: 'Completed',
  unlocked: 'Open',
  locked: 'Locked',
}

export default function ChallengeList({ challenges, selectedId, onSelect }) {
  if (!challenges) {
    return <p className="muted">Loading challenges…</p>
  }
  return (
    <ol className="challenge-list">
      {challenges.map((challenge, index) => {
        const locked = challenge.status === 'locked'
        const classes = ['challenge-item', challenge.status, challenge.id === selectedId ? 'selected' : '']
        return (
          <li key={challenge.id}>
            <button
              type="button"
              className={classes.join(' ').trim()}
              disabled={locked}
              aria-current={challenge.id === selectedId ? 'true' : undefined}
              onClick={() => onSelect(challenge.id)}
            >
              <span className="challenge-title">
                {index + 1}. {challenge.title}
              </span>
              <span className={`status-badge ${challenge.status}`}>{STATUS_LABELS[challenge.status]}</span>
            </button>
          </li>
        )
      })}
    </ol>
  )
}
