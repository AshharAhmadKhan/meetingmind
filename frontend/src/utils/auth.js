import { Amplify } from 'aws-amplify'
import { signIn, signOut, getCurrentUser, fetchAuthSession, signUp, fetchUserAttributes } from 'aws-amplify/auth'

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

export async function signup(email, password, name) {
  return await signUp({
    username: email,
    password,
    options: {
      userAttributes: { 
        email,
        name: name || email  // Fallback to email if name not provided
      }
    }
  })
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
    // Fetch user attributes to get display name
    const attributes = await fetchUserAttributes()
    const displayName = attributes.name || user.signInDetails?.loginId || user.username
    localStorage.setItem('mm_user', displayName)
    return user
  } catch {
    localStorage.removeItem('mm_user')
    return null
  }
}
