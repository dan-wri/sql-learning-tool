// Chapter names and accents are defined by the approved curriculum / UI brief.
export const LEVELS_PER_CHAPTER = 20

export const CHAPTERS = [
  { id: 1, name: 'Foundations' },
  { id: 2, name: 'Relational SQL' },
  { id: 3, name: 'Intermediate SQL' },
  { id: 4, name: 'Advanced Query Construction' },
  { id: 5, name: 'Advanced Analytics' },
]

export const TOTAL_LEVELS = CHAPTERS.length * LEVELS_PER_CHAPTER

export const chapterOf = (challenge) => challenge?.chapter ?? 1

export function chapterName(id) {
  return CHAPTERS.find((chapter) => chapter.id === id)?.name ?? ''
}

// Chapter N+1 stays locked until every one of the 20 levels of chapter N is complete.
export function summariseChapters(challenges) {
  const list = challenges ?? []
  let previousComplete = true
  return CHAPTERS.map((chapter) => {
    const inChapter = list.filter((c) => chapterOf(c) === chapter.id)
    const completed = inChapter.filter((c) => c.status === 'completed').length
    const unlocked = previousComplete
    const complete = completed >= LEVELS_PER_CHAPTER
    previousComplete = unlocked && complete
    return { ...chapter, total: LEVELS_PER_CHAPTER, available: inChapter.length, completed, unlocked, complete }
  })
}

export function lockedReason(chapters, chapter) {
  const previous = chapters.find((c) => c.id === chapter.id - 1)
  return previous ? `Complete Chapter ${previous.id} to unlock ${chapter.name}.` : ''
}
