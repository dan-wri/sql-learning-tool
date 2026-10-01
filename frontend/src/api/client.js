import { getLearnerId } from '../lib/learnerId.js'

async function request(path, options = {}) {
  const response = await fetch(`/api${path}`, {
    ...options,
    headers: {
      'X-Learner-Id': getLearnerId(),
      ...options.headers,
    },
  })
  if (!response.ok) {
    const body = await response.json().catch(() => ({}))
    throw new Error(body.detail ?? `Request failed (${response.status})`)
  }
  return response.json()
}

export const api = {
  health: () => request('/health'),
  startSession: () => request('/learner/session', { method: 'POST' }),
  resetDatabase: () => request('/learner/reset', { method: 'POST' }),
  schema: () => request('/learner/schema'),
  listChallenges: () => request('/challenges'),
  getChallenge: (id) => request(`/challenges/${encodeURIComponent(id)}`),
  revealHint: (id) => request(`/challenges/${encodeURIComponent(id)}/hints`, { method: 'POST' }),
  submit: (id, sql) =>
    request(`/challenges/${encodeURIComponent(id)}/submit`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ sql }),
    }),
}
