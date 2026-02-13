import { Amplify } from 'aws-amplify'
import { signIn, signOut, getCurrentUser, fetchAuthSession } from 'aws-amplify/auth'

// Config is injected at deploy time via env variables
// For local dev, we read from window.__MM_CONFIG__ set by config.js
const cfg = window.__MM_CONFIG__ || {}

Amplify.configure({
  Auth: {
    Cognito: {
      userPoolId:       cfg.userPoolId       || import.meta.env.VITE_USER_POOL_ID       || '',
      userPoolClientId: cfg.userPoolClientId || import.meta.env.VITE_USER_POOL_CLIENT_ID || '',
    }
  }
})

export async function login(email, password) {
  const result = await signIn({ username: email, password })
  return result
}

export async function logout() {
  await signOut()
  localStorage.removeItem('mm_user')
}

export async function getToken() {
  const session = await fetchAuthSession()
  return session.tokens?.idToken?.toString() || ''
}

export function getUser() {
  // Simple check — if token fetch works we're logged in
  // We cache email in localStorage for display only
  return localStorage.getItem('mm_user') || null
}

export async function checkSession() {
  try {
    const user = await getCurrentUser()
    localStorage.setItem('mm_user', user.signInDetails?.loginId || user.username)
    return user
  } catch {
    localStorage.removeItem('mm_user')
    return null
  }
}
