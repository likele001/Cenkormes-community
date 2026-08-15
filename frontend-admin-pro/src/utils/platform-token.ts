import { clearAuthToken, getAuthToken, setAuthToken } from '@/utils/session-token'

const PLATFORM_TOKEN_KEY = 'lightmes_platform_token'

export function getPlatformToken() {
  return getAuthToken(PLATFORM_TOKEN_KEY) || ''
}

export function setPlatformToken(token: string, remember = false) {
  if (!token) {
    clearAuthToken(PLATFORM_TOKEN_KEY)
    return
  }
  setAuthToken(PLATFORM_TOKEN_KEY, token, remember)
}
