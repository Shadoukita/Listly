import { markOnline, markOffline } from './connection'

const BASE = '/api'

export async function api(path, method = 'GET', body = null) {
  const token  = localStorage.getItem('token')
  const locale = localStorage.getItem('locale') || 'en-US'
  const opts = {
    method,
    headers: {
      'Content-Type': 'application/json',
      'Accept-Language': locale,
    },
  }
  if (token) opts.headers['Authorization'] = `Bearer ${token}`
  if (body) opts.body = JSON.stringify(body)
  let res
  try {
    res = await fetch(`${BASE}${path}`, opts)
  } catch (_) {
    markOffline()
    throw new Error('Network error')
  }
  markOnline()
  const data = await res.json()
  if (!res.ok) throw new Error(data.error || 'Error')
  return data
}
