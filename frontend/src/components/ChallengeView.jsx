// Task text marks identifiers with `backticks`; render them as inline code.
function inlineCode(text) {
  return text.split('`').map((part, index) => (index % 2 === 1 ? <code key={index}>{part}</code> : part))
}

export default function ChallengeView({ challenge }) {
  if (!challenge) {
    return <p className="muted">Select a challenge to begin.</p>
  }
  const isMutation = challenge.kind === 'mutation'
  return (
    <div className="challenge-view">
      {challenge.level != null && (
        <p className="challenge-eyebrow">
          Level {challenge.level}
          {challenge.chapter != null && ` · Chapter ${challenge.chapter}`}
        </p>
      )}
      <div className="challenge-heading">
        <h2>{challenge.title}</h2>
        <span className="badge">{challenge.difficulty}</span>
        {isMutation && <span className="badge mutation">Changes data</span>}
        {challenge.status === 'completed' && <span className="status-badge completed">Completed</span>}
      </div>
      {challenge.concepts?.length > 0 && (
        <ul className="concepts" aria-label="Concepts">
          {challenge.concepts.map((concept) => (
            <li key={concept} className="badge">
              {concept}
            </li>
          ))}
        </ul>
      )}
      {challenge.review_mode && (
        <div className="alert review" role="note">
          <strong>Review mode</strong> —{' '}
          {isMutation
            ? "You've already completed this challenge. You can practise it again and get the usual feedback, but any database changes from this attempt won't be saved to your training database."
            : "You've already completed this challenge. Your query runs against the data as it was when you first met this challenge, so later changes to the database won't affect your result."}
        </div>
      )}
      {challenge.story && (
        <section className="challenge-story" aria-labelledby="story-heading">
          <h3 id="story-heading">The situation</h3>
          <p>{inlineCode(challenge.story)}</p>
        </section>
      )}
      <section className="challenge-task" aria-labelledby="task-heading">
        <h3 id="task-heading">Your task</h3>
        <p className="instructions">{inlineCode(challenge.instructions)}</p>
      </section>
    </div>
  )
}
