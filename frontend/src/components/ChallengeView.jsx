import { BookOpen, DatabaseZap, RotateCcw } from 'lucide-react'
import { TOTAL_LEVELS, chapterName, chapterOf } from '../lib/chapters.js'

// Task text marks identifiers with `backticks`; render them as inline code.
function inlineCode(text) {
  return text.split('`').map((part, index) => (index % 2 === 1 ? <code key={index}>{part}</code> : part))
}

export function ChallengeHeader({ challenge }) {
  const chapterId = chapterOf(challenge)
  const concepts = (challenge.concepts ?? []).slice(0, 3)
  return (
    <header className="challenge-header">
      <div className="challenge-meta">
        <p className="eyebrow">
          Chapter {chapterId} · {chapterName(chapterId)}
        </p>
        {challenge.level != null && (
          <p className="eyebrow level-label">
            Level {challenge.level} / {TOTAL_LEVELS}
          </p>
        )}
      </div>
      <div className="challenge-title-row">
        <h2>{challenge.title}</h2>
        {challenge.status === 'completed' && <span className="status-chip done">Completed</span>}
        {challenge.kind === 'mutation' && (
          <span className="status-chip mutation">
            <DatabaseZap size={13} aria-hidden="true" /> Changes data
          </span>
        )}
      </div>
      <div className="challenge-tags">
        {concepts.length > 0 && (
          <ul className="concepts" aria-label="Concepts">
            {concepts.map((concept) => (
              <li key={concept}>{concept}</li>
            ))}
          </ul>
        )}
        <span className="difficulty">
          <span className="sr-only">Difficulty: </span>
          {challenge.difficulty}
        </span>
      </div>
    </header>
  )
}

export function ReviewBanner({ mutation }) {
  return (
    <div className="review-banner" role="note">
      <RotateCcw size={16} aria-hidden="true" />
      <p>
        <strong>Review mode</strong>{' '}
        {mutation
          ? "You've already completed this level. Practise it again for the usual feedback — changes from this attempt won't be saved to your database."
          : "You've already completed this level. Your attempt runs against the data as it was when you first met this challenge, so later changes to the database won't affect it."}
      </p>
    </div>
  )
}

export function SituationCard({ story }) {
  return (
    <section className="situation" aria-labelledby="situation-heading">
      <h3 id="situation-heading" className="eyebrow">
        <BookOpen size={14} aria-hidden="true" /> The situation
      </h3>
      <p>{inlineCode(story)}</p>
    </section>
  )
}

export function TaskCard({ instructions }) {
  return (
    <section className="task" aria-labelledby="task-heading">
      <h3 id="task-heading" className="eyebrow">
        Your task
      </h3>
      <p className="task-text">{inlineCode(instructions)}</p>
    </section>
  )
}

export default function ChallengeView({ challenge, loading = false }) {
  if (!challenge) {
    return loading ? (
      <div className="challenge-view" aria-busy="true" aria-label="Loading level">
        <div className="skeleton skeleton-line short" />
        <div className="skeleton skeleton-title" />
        <div className="skeleton skeleton-block" />
        <div className="skeleton skeleton-block" />
      </div>
    ) : (
      <p className="muted pad">Select a level to begin.</p>
    )
  }
  const mutation = challenge.kind === 'mutation'
  return (
    <div className="challenge-view">
      <ChallengeHeader challenge={challenge} />
      {challenge.review_mode && <ReviewBanner mutation={mutation} />}
      {challenge.story && <SituationCard story={challenge.story} />}
      <TaskCard instructions={challenge.instructions} />
      {mutation && !challenge.review_mode && (
        <p className="mutation-note">
          <DatabaseZap size={14} aria-hidden="true" /> This level changes your Brightcart database, and the change is saved
          when you pass.
        </p>
      )}
    </div>
  )
}
