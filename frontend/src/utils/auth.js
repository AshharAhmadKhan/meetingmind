import { Amplify } from 'aws-amplify'
import { signIn, signOut, getCurrentUser, fetchAuthSession } from 'aws-amplify/auth'

const cfg = (typeof window !== 'undefined' && window.__MM_CONFIG__) || {}
const userPoolId       = cfg.userPoolId       || import.meta.env.VITE_USER_POOL_ID       || 'ap-south-1_PLACEHOLDER'
const userPoolClientId = cfg.userPoolClientId || import.meta.env.VITE_USER_POOL_CLIENT_ID || 'PLACEHOLDERclientid'

// Only configure Amplify if we have real values
if (!userPoolId.includes('PLACEHOLDER')) {
  Amplify.configure({
    Auth: {
      Cognito: { userPoolId, userPoolClientId }
    }
  })
}

export async function login(email, password) {
  return await signIn({ username: email, password })
}

export async function logout() {
  try { await signOut() } catch(e) {}
  localStorage.removeItem('mm_user')
}

export async function getToken() {
  try {
    const session = await fetchAuthSession()
    return session.tokens?.idToken?.toString() || ''
  } catch { return '' }
}

export function getUser() {
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
