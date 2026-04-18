const ACCESS_TOKEN_KEY = 'auth_token'
const REFRESH_TOKEN_KEY = 'refresh_token'
const STORAGE_MODE_KEY = 'auth_storage_mode'

function getStorage(mode) {
  return mode === 'session' ? sessionStorage : localStorage
}

function readStorageMode() {
  const mode = localStorage.getItem(STORAGE_MODE_KEY)
  return mode === 'session' ? 'session' : 'local'
}

export function persistAuthTokens(tokens, { rememberMe = true } = {}) {
  const mode = rememberMe ? 'local' : 'session'
  const storage = getStorage(mode)

  localStorage.removeItem(ACCESS_TOKEN_KEY)
  localStorage.removeItem(REFRESH_TOKEN_KEY)
  sessionStorage.removeItem(ACCESS_TOKEN_KEY)
  sessionStorage.removeItem(REFRESH_TOKEN_KEY)

  storage.setItem(ACCESS_TOKEN_KEY, tokens.authToken)
  if (tokens.refreshToken) {
    storage.setItem(REFRESH_TOKEN_KEY, tokens.refreshToken)
  }

  localStorage.setItem(STORAGE_MODE_KEY, mode)
}

export function clearAuthTokens() {
  localStorage.removeItem(ACCESS_TOKEN_KEY)
  localStorage.removeItem(REFRESH_TOKEN_KEY)
  sessionStorage.removeItem(ACCESS_TOKEN_KEY)
  sessionStorage.removeItem(REFRESH_TOKEN_KEY)
  localStorage.removeItem(STORAGE_MODE_KEY)
}

export function getAccessToken() {
  const mode = readStorageMode()
  return getStorage(mode).getItem(ACCESS_TOKEN_KEY)
}

export function getRefreshToken() {
  const mode = readStorageMode()
  return getStorage(mode).getItem(REFRESH_TOKEN_KEY)
}

export function setAccessToken(authToken) {
  if (!authToken) {
    return
  }

  const mode = readStorageMode()
  getStorage(mode).setItem(ACCESS_TOKEN_KEY, authToken)
}
