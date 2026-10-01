const STORAGE_KEY = 'sqlLearningTool.learnerId'
const UUID_RE = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/

export function getLearnerId(storage = window.localStorage) {
  const existing = storage.getItem(STORAGE_KEY)
  if (existing && UUID_RE.test(existing)) {
    return existing
  }
  const id = crypto.randomUUID()
  storage.setItem(STORAGE_KEY, id)
  return id
}
