export default function ChallengeView({ challenge }) {
  if (!challenge) {
    return <p className="muted">Select a challenge to begin.</p>
  }
  return (
    <div className="challenge-view">
      <div className="challenge-heading">
        <h2>{challenge.title}</h2>
        <span className="badge">{challenge.difficulty}</span>
        {challenge.kind === 'mutation' && <span className="badge mutation">Changes data</span>}
        {challenge.status === 'completed' && <span className="status-badge completed">Completed</span>}
      </div>
      {challenge.review_mode && (
        <div className="alert review" role="note">
          <strong>Review mode</strong> — You&apos;ve already completed this challenge. You can practise it again and
          get the usual feedback, but any database changes from this attempt won&apos;t be saved to your training
          database.
        </div>
      )}
      <p className="instructions">{challenge.instructions}</p>
    </div>
  )
}
