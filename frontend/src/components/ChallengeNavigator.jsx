import ChallengeList from './ChallengeList.jsx'
import { LEVELS_PER_CHAPTER } from '../lib/chapters.js'

export default function ChallengeNavigator({ chapter, challenges, selectedId, onSelect }) {
  const loaded = challenges !== null
  const inChapter = challenges ?? []
  return (
    <div className="navigator" data-chapter={chapter.id}>
      <div className="navigator-head">
        <p className="eyebrow">Chapter {chapter.id}</p>
        <h2>{chapter.name}</h2>
        <div className="navigator-progress">
          <div
            className="progress-track"
            role="progressbar"
            aria-label={`Chapter ${chapter.id} progress`}
            aria-valuemin={0}
            aria-valuemax={chapter.total}
            aria-valuenow={chapter.completed}
          >
            <span style={{ width: `${(chapter.completed / chapter.total) * 100}%` }} />
          </div>
          <span className="muted">
            {chapter.completed}/{chapter.total}
          </span>
        </div>
      </div>
      <div className="navigator-scroll">
        {loaded && inChapter.length === 0 ? (
          <p className="muted pad">The levels for this chapter aren&apos;t available yet.</p>
        ) : (
          <ChallengeList challenges={loaded ? inChapter : null} selectedId={selectedId} onSelect={onSelect} />
        )}
        {loaded && inChapter.length > 0 && inChapter.length < LEVELS_PER_CHAPTER && (
          <p className="navigator-note">More levels in this chapter are on the way.</p>
        )}
      </div>
    </div>
  )
}
