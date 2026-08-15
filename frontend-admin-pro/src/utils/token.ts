import { clearAuthToken, getAuthToken, setAuthToken } from '@/utils/session-token'

const KEY = 'lightmes_admin_token'

export function getToken(): string | null {
  return getAuthToken(KEY)
}

export function setToken(token: string, remember = false) {
  setAuthToken(KEY, token, remember)
}

export function clearToken() {
  clearAuthToken(KEY)
}
