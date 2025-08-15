// Centralized API utilities

const getBaseUrl = () => {
  // Prefer Vite env if present, else fall back to window location with default port
  const envUrl = import.meta?.env?.VITE_API_BASE_URL
  if (envUrl) return envUrl
  // Fallback for local dev
  const { protocol, hostname } = window.location
  const port = '8000'
  return `${protocol}//${hostname}:${port}`
}

export const API_BASE_URL = getBaseUrl()

export async function apiFetch(path, options = {}) {
  const url = path.startsWith('http') ? path : `${API_BASE_URL}${path}`
  const resp = await fetch(url, options)
  const contentType = resp.headers.get('content-type') || ''
  const body = contentType.includes('application/json') ? await resp.json().catch(() => ({})) : await resp.text()
  if (!resp.ok) {
    const msg = typeof body === 'string' ? body : body?.message || `HTTP ${resp.status}`
    const err = new Error(msg)
    err.status = resp.status
    err.body = body
    throw err
  }
  return body
}

export async function pingHealth() {
  try {
    const res = await fetch(`${API_BASE_URL}/health`)
    return res.ok
  } catch {
    return false
  }
}
