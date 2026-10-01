import { describe, expect, it } from 'vitest'
import { getLearnerId } from '../src/lib/learnerId.js'

function memoryStorage(initial = {}) {
  const data = { ...initial }
  return {
    getItem: (key) => (key in data ? data[key] : null),
    setItem: (key, value) => {
      data[key] = String(value)
    },
    data,
  }
}

const UUID_RE = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/

describe('getLearnerId', () => {
  it('creates and persists a UUID on first use', () => {
    const storage = memoryStorage()
    const id = getLearnerId(storage)
    expect(id).toMatch(UUID_RE)
    expect(getLearnerId(storage)).toBe(id)
  })

  it('replaces a corrupted stored value', () => {
    const storage = memoryStorage({ 'sqlLearningTool.learnerId': '../../etc/passwd' })
    const id = getLearnerId(storage)
    expect(id).toMatch(UUID_RE)
    expect(storage.data['sqlLearningTool.learnerId']).toBe(id)
  })
})
