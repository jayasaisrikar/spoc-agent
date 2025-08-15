// Centralized API utilities

const getBaseUrl = () => {
  // 1) Prefer Vite env at build time
  const envUrl = import.meta?.env?.VITE_API_BASE_URL
  if (envUrl) return envUrl

  // 2) Optional runtime override (can be injected before scripts)
  if (typeof window !== 'undefined' && window.__API_BASE_URL__) {
    return window.__API_BASE_URL__
  }

  // 3) Optional meta tag override in index.html
  if (typeof document !== 'undefined') {
    const meta = document.querySelector('meta[name="api-base-url"]')
    if (meta?.content) return meta.content
  }

  // 4) Fallbacks
  const { protocol, hostname } = window.location
  // Only force :8000 for local dev
  if (hostname === 'localhost' || hostname === '127.0.0.1') {
    return `${protocol}//${hostname}:8000`
  }

  // 5) As a last resort, same-origin (requires rewrites/proxy)
  if (import.meta?.env?.MODE === 'production') {
    // Warn once in production if no env is set
    // eslint-disable-next-line no-console
    console.warn('[API] VITE_API_BASE_URL is not set; falling back to same-origin. Configure it in Vercel envs.')
  }
  return `${protocol}//${hostname}`
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
