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
  return res.data   // { meetingId, uploadUrl, s3Key }
}

export async function uploadAudioToS3(uploadUrl, file) {
  await axios.put(uploadUrl, file, {
    headers: { 'Content-Type': file.type },
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
