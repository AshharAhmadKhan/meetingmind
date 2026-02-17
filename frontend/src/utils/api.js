import axios from 'axios'
import { getToken } from './auth.js'

const BASE = window.__MM_CONFIG__?.apiUrl || import.meta.env.VITE_API_URL || ''

async function authHeaders() {
  const token = await getToken()
  return { Authorization: `Bearer ${token}` }
}

export async function getUploadUrl(title, contentType, fileSize) {
  const headers = await authHeaders()
  const res = await axios.post(`${BASE}/upload-url`,
    { title, contentType, fileSize },
    { headers }
  )
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

export async function updateAction(meetingId, actionId, completed) {
  const headers = await authHeaders()
  const res = await axios.put(
    `${BASE}/meetings/${meetingId}/actions/${actionId}`,
    { completed },
    { headers }
  )
  return res.data
}

export async function getDebtAnalytics() {
  const headers = await authHeaders()
  const res = await axios.get(`${BASE}/debt-analytics`, { headers })
  return res.data
}
