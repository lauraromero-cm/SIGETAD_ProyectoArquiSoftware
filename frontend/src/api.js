export const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'

export function getToken() {
  return localStorage.getItem('sigetad_token')
}

export function setSession(token, user) {
  localStorage.setItem('sigetad_token', token)
  localStorage.setItem('sigetad_user', JSON.stringify(user))
}

export function getUser() {
  const raw = localStorage.getItem('sigetad_user')
  return raw ? JSON.parse(raw) : null
}

export function clearSession() {
  localStorage.removeItem('sigetad_token')
  localStorage.removeItem('sigetad_user')
}

export async function api(path, options = {}) {
  const token = getToken()
  const isFormData = options.body instanceof FormData
  const headers = {
    ...(isFormData ? {} : { 'Content-Type': 'application/json' }),
    ...(options.headers || {})
  }
  if (token) headers.Authorization = `Bearer ${token}`

  const res = await fetch(`${API_URL}${path}`, {
    ...options,
    headers,
  })
  const body = await res.json().catch(() => ({ ok: false, error: 'Respuesta inválida' }))
  if (!res.ok || !body.ok) {
    throw new Error(body.error || 'Error en la solicitud')
  }
  return body.data
}

export const authApi = {
  login: (correo, contrasena) => api('/login/', { method: 'POST', body: JSON.stringify({ correo, contrasena }) }),
  register: (payload) => api('/register/', { method: 'POST', body: JSON.stringify(payload) }),
}
