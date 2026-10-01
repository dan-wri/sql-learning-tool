export default function FeedbackPanel({ submission, onNext }) {
  if (!submission) {
    return null
  }
  const { passed, message, next_challenge_id: nextId } = submission
  return (
    <div className={`feedback ${passed ? 'pass' : 'fail'}`} role="status">
      <strong>{passed ? 'Passed' : 'Not quite'}</strong>
      <span>{message}</span>
      {passed && nextId && (
        <button type="button" onClick={() => onNext(nextId)}>
          Next challenge
        </button>
      )}
    </div>
  )
}
