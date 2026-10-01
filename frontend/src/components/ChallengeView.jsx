export default function ChallengeView({ challenge }) {
  if (!challenge) {
    return <p className="muted">Select a challenge to begin.</p>
  }
  return (
    <div className="challenge-view">
      <div className="challenge-heading">
        <h2>{challenge.title}</h2>
        <span className="badge">{challenge.difficulty}</span>
        {challenge.status === 'completed' && <span className="status-badge completed">Completed</span>}
      </div>
      <p className="instructions">{challenge.instructions}</p>
    </div>
  )
}
