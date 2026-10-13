import { Check, DatabaseZap, Lock } from 'lucide-react'

const STATE_LABEL = { completed: 'Completed', unlocked: 'Open', locked: 'Locked' }

function StateIcon({ status }) {
  if (status === 'completed') return <Check size={16} strokeWidth={2.75} className="state-icon done" aria-hidden="true" />
  if (status === 'locked') return <Lock size={14} className="state-icon lock" aria-hidden="true" />
  return <span className="state-dot" aria-hidden="true" />
}

function Skeleton() {
  return (
    <ul className="challenge-list" aria-busy="true" aria-label="Loading levels">
      {Array.from({ length: 8 }, (_, index) => (
        <li key={index}>
          <div className="skeleton skeleton-row" />
        </li>
      ))}
    </ul>
  )
}

export default function ChallengeList({ challenges, selectedId, onSelect }) {
  if (!challenges) {
    return <Skeleton />
  }
  return (
    <ul className="challenge-list" aria-label="Levels">
      {challenges.map((challenge, index) => {
        const selected = challenge.id === selectedId
        const locked = challenge.status === 'locked'
        const classes = ['challenge-item', challenge.status, selected ? 'selected' : '']
        return (
          <li key={challenge.id}>
            <button
              type="button"
              className={classes.join(' ')}
              disabled={locked}
              aria-current={selected ? 'true' : undefined}
              onClick={() => onSelect(challenge.id)}
            >
              <span className="level-num">{challenge.level ?? index + 1}</span>
              <span className="item-main">
                <span className="item-title">{challenge.title}</span>
                {challenge.concepts?.[0] && <span className="item-concept">{challenge.concepts[0]}</span>}
              </span>
              {challenge.kind === 'mutation' && (
                <DatabaseZap size={14} className="item-mutation" aria-label="Changes data" role="img" />
              )}
              <StateIcon status={challenge.status} />
              <span className="sr-only">{STATE_LABEL[challenge.status]}</span>
            </button>
          </li>
        )
      })}
    </ul>
  )
}
