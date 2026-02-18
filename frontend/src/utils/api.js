import axios from 'axios'
import { getToken } from './auth.js'

const BASE = window.__MM_CONFIG__?.apiUrl || import.meta.env.VITE_API_URL || ''

async function authHeaders() {
  const token = await getToken()
  return { Authorization: `Bearer ${token}` }
}

export async function getUploadUrl(title, contentType, fileSize, teamId = null) {
  const headers = await authHeaders()
  const body = { title, contentType, fileSize }
  if (teamId) body.teamId = teamId
  
  const res = await axios.post(`${BASE}/upload-url`, body, { headers })
  return res.data
}

export async function uploadAudioToS3(uploadUrl, file) {
  // No Content-Type header — must match what was signed (nothing)
  await axios.put(uploadUrl, file, {
    headers: {},
    onUploadProgress: () => {}
  })
}

export async function listMeetings() {
  const headers = await authHeaders()
  const res = await axios.get(`${BASE}/meetings`, { headers })
  return res.data.meetings
}

export async function getMeeting(meetingId) {
  const headers = await authHeaders()
  const res = await axios.get(`${BASE}/meetings/${meetingId}`, { headers })
  return res.data
}

export async function updateAction(meetingId, actionId, updates) {
  const headers = await authHeaders()
  const res = await axios.put(
    `${BASE}/meetings/${meetingId}/actions/${actionId}`,
    updates,
    { headers }
  )
  return res.data
}

export async function getDebtAnalytics(teamId = null) {
  const headers = await authHeaders()
  const params = {}
  if (teamId) params.teamId = teamId
  const res = await axios.get(`${BASE}/debt-analytics`, { headers, params })
  return res.data
}

export async function getAllActions(status, owner, teamId = null) {
  const headers = await authHeaders()
  const params = {}
  if (status) params.status = status
  if (owner) params.owner = owner
  if (teamId) params.teamId = teamId
  const res = await axios.get(`${BASE}/all-actions`, { headers, params })
  return res.data
}

export async function checkDuplicate(task) {
  const headers = await authHeaders()
  const res = await axios.post(`${BASE}/check-duplicate`, { task }, { headers })
  return res.data
}

export async function createTeam(teamName) {
  const headers = await authHeaders()
  const res = await axios.post(`${BASE}/teams`, { teamName }, { headers })
  return res.data
}

export async function joinTeam(inviteCode) {
  const headers = await authHeaders()
  const res = await axios.post(`${BASE}/teams/join`, { inviteCode }, { headers })
  return res.data
}

export async function getTeam(teamId) {
  const headers = await authHeaders()
  const res = await axios.get(`${BASE}/teams/${teamId}`, { headers })
  return res.data
}

export async function listUserTeams() {
  const headers = await authHeaders()
  const res = await axios.get(`${BASE}/teams`, { headers })
  return res.data
}
