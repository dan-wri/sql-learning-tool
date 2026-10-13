import { ArrowRight, Check, CircleAlert, ShieldAlert } from 'lucide-react'

const HEADINGS = {
  not_allowed: 'That statement isn’t allowed here',
  multiple_statements: 'One statement at a time',
  sql_error: 'SQL error',
  timeout: 'That query took too long',
}
const BLOCKED = new Set(['not_allowed', 'multiple_statements', 'wrong_statement'])

export default function FeedbackPanel({ submission, onNext, nextLabel = 'Next challenge' }) {
  if (!submission) {
    return null
  }
  const { passed, message, code, review_mode: review, next_challenge_id: nextId } = submission
  const kind = passed ? 'pass' : BLOCKED.has(code) ? 'blocked' : 'fail'
  const heading = passed
    ? review
      ? 'Review attempt passed'
      : 'Challenge complete'
    : (HEADINGS[code] ?? 'Not quite yet')
  const Icon = passed ? Check : kind === 'blocked' ? ShieldAlert : CircleAlert
  return (
    <div className={`feedback ${kind}`} role="status">
      <span className="feedback-icon" aria-hidden="true">
        <Icon size={18} strokeWidth={2.5} />
      </span>
      <div className="feedback-body">
        <strong>{heading}</strong>
        <p>{message}</p>
      </div>
      {passed && nextId && onNext && (
        <button type="button" className="btn btn-primary" onClick={() => onNext(nextId)}>
          {nextLabel}
          <ArrowRight size={16} aria-hidden="true" />
        </button>
      )}
    </div>
  )
}
