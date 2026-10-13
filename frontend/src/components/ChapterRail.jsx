import { Check, Lock } from 'lucide-react'
import { lockedReason } from '../lib/chapters.js'

export default function ChapterRail({ chapters, selectedId, onSelect }) {
  return (
    <nav className="chapter-rail" aria-label="Course chapters">
      <ol>
        {chapters.map((chapter) => {
          const selected = chapter.id === selectedId
          const reason = chapter.unlocked ? '' : lockedReason(chapters, chapter)
          const classes = ['chapter-tab', selected ? 'selected' : '', chapter.unlocked ? '' : 'locked']
          return (
            <li key={chapter.id} data-chapter={chapter.id}>
              <button
                type="button"
                className={classes.join(' ').trim()}
                aria-current={selected ? 'true' : undefined}
                aria-disabled={chapter.unlocked ? undefined : 'true'}
                title={reason || undefined}
                onClick={() => chapter.unlocked && onSelect(chapter.id)}
              >
                <span className="chapter-num" aria-hidden="true">
                  {chapter.complete ? <Check size={14} strokeWidth={3} /> : chapter.id}
                </span>
                <span className="chapter-text">
                  <span className="chapter-name">
                    <span className="sr-only">Chapter {chapter.id}: </span>
                    {chapter.name}
                  </span>
                  <span className="chapter-count">
                    {chapter.completed}/{chapter.total}
                    {chapter.complete && <span className="sr-only"> complete</span>}
                    {!chapter.unlocked && <span className="sr-only"> — locked. {reason}</span>}
                  </span>
                </span>
                {!chapter.unlocked && <Lock size={14} className="chapter-lock" aria-hidden="true" />}
                <span className="chapter-bar" aria-hidden="true">
                  <span style={{ width: `${(chapter.completed / chapter.total) * 100}%` }} />
                </span>
              </button>
            </li>
          )
        })}
      </ol>
    </nav>
  )
}
