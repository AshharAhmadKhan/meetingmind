import React, { useState, useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { logout, checkSession } from '../utils/auth.js'
import { listMeetings, getUploadUrl, uploadAudioToS3 } from '../utils/api.js'
import { Mic, Upload, LogOut, Clock, CheckCircle,
         AlertCircle, Loader, ChevronRight, FileAudio, Brain } from 'lucide-react'

const STATUS_CONFIG = {
  PENDING:      { label: 'Pending',      color: '#4a5f84', bg: 'rgba(74,95,132,0.12)' },
  TRANSCRIBING: { label: 'Transcribing', color: '#f59e0b', bg: 'rgba(245,158,11,0.12)' },
  ANALYZING:    { label: 'Analyzing',    color: '#3b82f6', bg: 'rgba(59,130,246,0.12)' },
  DONE:         { label: 'Done',         color: '#10b981', bg: 'rgba(16,185,129,0.12)' },
  FAILED:       { label: 'Failed',       color: '#ef4444', bg: 'rgba(239,68,68,0.12)'  },
}

function StatusBadge({ status }) {
  const cfg = STATUS_CONFIG[status] || STATUS_CONFIG.PENDING
  return (
    <span style={{
      fontSize: 11, fontWeight: 600, letterSpacing: '0.4px',
      padding: '3px 9px', borderRadius: 20,
      color: cfg.color, background: cfg.bg,
      textTransform: 'uppercase',
    }}>
      {cfg.label}
    </span>
  )
}

function StatusIcon({ status }) {
  const props = { size: 14 }
  if (status === 'DONE')         return <CheckCircle  {...props} color="#10b981" />
  if (status === 'FAILED')       return <AlertCircle  {...props} color="#ef4444" />
  if (status === 'TRANSCRIBING') return <Loader       {...props} color="#f59e0b" style={{animation:'spin 1s linear infinite'}} />
  if (status === 'ANALYZING')    return <Brain        {...props} color="#3b82f6" />
  return                                <Clock        {...props} color="#4a5f84" />
}

export default function Dashboard() {
  const navigate  = useNavigate()
  const fileRef   = useRef()
  const pollRef   = useRef()

  const [user,      setUser]      = useState('')
  const [meetings,  setMeetings]  = useState([])
  const [loading,   setLoading]   = useState(true)
  const [uploading, setUploading] = useState(false)
  const [dragOver,  setDragOver]  = useState(false)
  const [uploadMsg, setUploadMsg] = useState('')
  const [title,     setTitle]     = useState('')
  const [error,     setError]     = useState('')

  useEffect(() => {
    checkSession().then(u => {
      if (!u) { navigate('/login'); return }
      setUser(u.signInDetails?.loginId || '')
      fetchMeetings()
    })
    // Poll every 8 seconds for status updates
    pollRef.current = setInterval(fetchMeetings, 8000)
    return () => clearInterval(pollRef.current)
  }, [])

  async function fetchMeetings() {
    try {
      const data = await listMeetings()
      setMeetings(data)
    } catch (e) {
      setError('Failed to load meetings')
    } finally {
      setLoading(false)
    }
  }

  async function handleFile(file) {
    if (!file) return
    const meetingTitle = title.trim() || file.name.replace(/\.[^/.]+$/, '')
    setUploading(true)
    setUploadMsg('Getting upload URL…')
    setError('')
    try {
      const { meetingId, uploadUrl } = await getUploadUrl(
        meetingTitle, file.type || 'audio/mpeg', file.size
      )
      setUploadMsg('Uploading audio…')
      await uploadAudioToS3(uploadUrl, file)
      setUploadMsg('Upload complete! Processing started.')
      setTitle('')
      setTimeout(() => {
        setUploadMsg('')
        fetchMeetings()
      }, 2500)
    } catch (e) {
      setError(e.response?.data?.error || e.message || 'Upload failed')
      setUploadMsg('')
    } finally {
      setUploading(false)
    }
  }

  function onFileChange(e) { handleFile(e.target.files[0]) }

  function onDrop(e) {
    e.preventDefault(); setDragOver(false)
    handleFile(e.dataTransfer.files[0])
  }

  async function handleLogout() {
    await logout()
    navigate('/login')
  }

  const hasPending = meetings.some(m =>
    m.status === 'TRANSCRIBING' || m.status === 'ANALYZING' || m.status === 'PENDING'
  )

  return (
    <div style={styles.root}>
      {/* Topbar */}
      <header style={styles.header}>
        <div style={styles.headerLeft}>
          <div style={styles.logoIcon}><Mic size={18} color="#3b82f6" /></div>
          <span style={styles.logoText}>MeetingMind</span>
          {hasPending && (
            <span style={styles.liveTag}>
              <span style={styles.liveDot} />
              Processing
            </span>
          )}
        </div>
        <div style={styles.headerRight}>
          <span style={styles.userEmail}>{user}</span>
          <button onClick={handleLogout} style={styles.logoutBtn} title="Sign out">
            <LogOut size={16} />
          </button>
        </div>
      </header>

      <main style={styles.main}>
        <div style={styles.layout}>

          {/* LEFT — Meeting list */}
          <section style={styles.listPanel}>
            <div style={styles.panelHeader}>
              <h2 style={styles.panelTitle}>Your Meetings</h2>
              <span style={styles.count}>{meetings.length}</span>
            </div>

            {error && (
              <div style={styles.errorBox}>{error}</div>
            )}

            {loading ? (
              <div style={styles.emptyState}>
                <Loader size={24} color="#3b82f6" style={{animation:'spin 1s linear infinite'}} />
                <p style={{color:'#4a5f84', marginTop: 12}}>Loading meetings…</p>
              </div>
            ) : meetings.length === 0 ? (
              <div style={styles.emptyState}>
                <FileAudio size={40} color="#1e2f50" />
                <p style={{color:'#4a5f84', marginTop: 12, textAlign:'center'}}>
                  No meetings yet.<br />Upload your first recording →
                </p>
              </div>
            ) : (
              <ul style={styles.list}>
                {meetings.map(m => (
                  <li key={m.meetingId}
                    onClick={() => m.status === 'DONE' && navigate(`/meeting/${m.meetingId}`)}
                    style={{
                      ...styles.listItem,
                      cursor: m.status === 'DONE' ? 'pointer' : 'default',
                      opacity: m.status === 'FAILED' ? 0.5 : 1,
                    }}
                    onMouseEnter={e => {
                      if (m.status === 'DONE') e.currentTarget.style.background = '#162340'
                      if (m.status === 'DONE') e.currentTarget.style.borderColor = '#243660'
                    }}
                    onMouseLeave={e => {
                      e.currentTarget.style.background = '#111e35'
                      e.currentTarget.style.borderColor = '#1e2f50'
                    }}
                  >
                    <div style={styles.listItemTop}>
                      <div style={styles.listItemLeft}>
                        <StatusIcon status={m.status} />
                        <span style={styles.meetingTitle}>{m.title}</span>
                      </div>
                      {m.status === 'DONE' && <ChevronRight size={14} color="#4a5f84" />}
                    </div>
                    <div style={styles.listItemBottom}>
                      <StatusBadge status={m.status} />
                      <span style={styles.dateText}>
                        {new Date(m.createdAt).toLocaleDateString('en-US',
                          {month:'short', day:'numeric', year:'numeric'})}
                      </span>
                    </div>
                    {m.summary && (
                      <p style={styles.summaryPreview}>
                        {m.summary.slice(0, 100)}…
                      </p>
                    )}
                  </li>
                ))}
              </ul>
            )}
          </section>

          {/* RIGHT — Upload panel */}
          <section style={styles.uploadPanel}>
            <div style={styles.panelHeader}>
              <h2 style={styles.panelTitle}>New Meeting</h2>
            </div>

            {/* Title input */}
            <div style={styles.field}>
              <label style={styles.label}>Meeting Title</label>
              <input
                type="text"
                value={title}
                onChange={e => setTitle(e.target.value)}
                placeholder="e.g. Q1 Planning Session"
                style={styles.input}
                onFocus={e => e.target.style.borderColor = '#3b82f6'}
                onBlur={e  => e.target.style.borderColor = '#1e2f50'}
              />
            </div>

            {/* Drop zone */}
            <div
              style={{
                ...styles.dropZone,
                ...(dragOver ? styles.dropZoneActive : {}),
                ...(uploading ? {opacity: 0.6, pointerEvents: 'none'} : {}),
              }}
              onClick={() => !uploading && fileRef.current?.click()}
              onDragOver={e => { e.preventDefault(); setDragOver(true) }}
              onDragLeave={() => setDragOver(false)}
              onDrop={onDrop}
            >
              <input
                ref={fileRef} type="file"
                accept="audio/*,video/mp4"
                onChange={onFileChange}
                style={{display:'none'}}
              />

              {uploading ? (
                <>
                  <Loader size={36} color="#3b82f6"
                    style={{animation:'spin 1s linear infinite', marginBottom: 16}} />
                  <p style={styles.dropText}>{uploadMsg}</p>
                </>
              ) : (
                <>
                  <div style={styles.uploadIconWrap}>
                    <Upload size={28} color="#3b82f6" />
                  </div>
                  <p style={styles.dropText}>
                    Drop audio file here<br />
                    <span style={styles.dropSub}>or click to browse</span>
                  </p>
                  <p style={styles.dropFormats}>MP3 · MP4 · WAV · M4A · WEBM · max 500MB</p>
                </>
              )}
            </div>

            {uploadMsg && !uploading && (
              <div style={styles.successBox}>{uploadMsg}</div>
            )}

            {/* Info cards */}
            <div style={styles.infoCards}>
              {[
                { icon: <Mic size={16} color="#3b82f6"/>,         title: 'Transcribed',    sub: 'Speaker-labeled text' },
                { icon: <Brain size={16} color="#10b981"/>,        title: 'AI Analyzed',    sub: 'Decisions extracted'  },
                { icon: <CheckCircle size={16} color="#f59e0b"/>,  title: 'Action Tracked', sub: 'With deadline reminders' },
              ].map(c => (
                <div key={c.title} style={styles.infoCard}>
                  {c.icon}
                  <div>
                    <p style={styles.infoCardTitle}>{c.title}</p>
                    <p style={styles.infoCardSub}>{c.sub}</p>
                  </div>
                </div>
              ))}
            </div>
          </section>

        </div>
      </main>

      <style>{`
        @keyframes spin { to { transform: rotate(360deg); } }
      `}</style>
    </div>
  )
}

const styles = {
  root:       { minHeight: '100vh', background: '#070d1a', display: 'flex', flexDirection: 'column' },
  header:     { background: '#0d1629', borderBottom: '1px solid #1e2f50',
                padding: '0 32px', height: 60, display: 'flex',
                alignItems: 'center', justifyContent: 'space-between',
                position: 'sticky', top: 0, zIndex: 100 },
  headerLeft: { display: 'flex', alignItems: 'center', gap: 12 },
  logoIcon:   { width: 34, height: 34, background: 'rgba(59,130,246,0.12)',
                border: '1px solid rgba(59,130,246,0.25)', borderRadius: 8,
                display: 'flex', alignItems: 'center', justifyContent: 'center' },
  logoText:   { fontFamily: 'Syne, sans-serif', fontSize: 17, fontWeight: 700, color: '#f0f4ff' },
  liveTag:    { display: 'flex', alignItems: 'center', gap: 6,
                background: 'rgba(59,130,246,0.1)', border: '1px solid rgba(59,130,246,0.2)',
                borderRadius: 20, padding: '3px 10px', fontSize: 11,
                color: '#3b82f6', fontWeight: 600, letterSpacing: '0.3px' },
  liveDot:    { width: 6, height: 6, borderRadius: '50%', background: '#3b82f6',
                animation: 'pulse 1.5s infinite' },
  headerRight:{ display: 'flex', alignItems: 'center', gap: 12 },
  userEmail:  { fontSize: 13, color: '#4a5f84' },
  logoutBtn:  { background: 'none', border: 'none', color: '#4a5f84',
                cursor: 'pointer', padding: 6, borderRadius: 6,
                display: 'flex', alignItems: 'center' },
  main:       { flex: 1, padding: '32px', maxWidth: 1200, margin: '0 auto', width: '100%' },
  layout:     { display: 'grid', gridTemplateColumns: '1fr 420px', gap: 24, alignItems: 'start' },
  listPanel:  { background: '#0d1629', border: '1px solid #1e2f50',
                borderRadius: 16, overflow: 'hidden' },
  uploadPanel:{ background: '#0d1629', border: '1px solid #1e2f50',
                borderRadius: 16, padding: 24, position: 'sticky', top: 80 },
  panelHeader:{ padding: '20px 24px 16px', borderBottom: '1px solid #1e2f50',
                display: 'flex', alignItems: 'center', gap: 10 },
  panelTitle: { fontFamily: 'Syne, sans-serif', fontSize: 16, fontWeight: 700, color: '#f0f4ff' },
  count:      { background: '#111e35', border: '1px solid #1e2f50',
                borderRadius: 20, padding: '1px 8px',
                fontSize: 12, color: '#4a5f84', fontWeight: 600 },
  emptyState: { display: 'flex', flexDirection: 'column', alignItems: 'center',
                justifyContent: 'center', padding: '60px 24px' },
  list:       { listStyle: 'none', padding: '12px' },
  listItem:   { background: '#111e35', border: '1px solid #1e2f50',
                borderRadius: 10, padding: '14px 16px', marginBottom: 8,
                transition: 'background 0.18s, border-color 0.18s' },
  listItemTop:    { display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 8 },
  listItemLeft:   { display: 'flex', alignItems: 'center', gap: 8, minWidth: 0 },
  listItemBottom: { display: 'flex', alignItems: 'center', justifyContent: 'space-between' },
  meetingTitle:   { fontSize: 14, fontWeight: 500, color: '#f0f4ff',
                    overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', maxWidth: 300 },
  dateText:       { fontSize: 12, color: '#4a5f84' },
  summaryPreview: { fontSize: 12, color: '#8da0c4', marginTop: 8,
                    lineHeight: 1.5, borderTop: '1px solid #1e2f50', paddingTop: 8 },
  field:      { marginBottom: 16 },
  label:      { display: 'block', fontSize: 13, fontWeight: 500,
                color: '#8da0c4', marginBottom: 6 },
  input:      { width: '100%', background: '#111e35', border: '1px solid #1e2f50',
                borderRadius: 8, padding: '10px 12px', color: '#f0f4ff',
                fontSize: 14, outline: 'none', transition: 'border-color 0.18s',
                fontFamily: 'DM Sans, sans-serif' },
  dropZone:   { border: '2px dashed #1e2f50', borderRadius: 12,
                padding: '40px 24px', textAlign: 'center',
                cursor: 'pointer', transition: 'all 0.18s', marginBottom: 16 },
  dropZoneActive: { borderColor: '#3b82f6', background: 'rgba(59,130,246,0.05)' },
  uploadIconWrap: { width: 60, height: 60, background: 'rgba(59,130,246,0.1)',
                    border: '1px solid rgba(59,130,246,0.2)', borderRadius: 12,
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    margin: '0 auto 16px' },
  dropText:   { fontSize: 14, color: '#f0f4ff', marginBottom: 6, lineHeight: 1.6 },
  dropSub:    { color: '#4a5f84' },
  dropFormats:{ fontSize: 11, color: '#4a5f84', letterSpacing: '0.3px' },
  successBox: { background: 'rgba(16,185,129,0.1)', border: '1px solid rgba(16,185,129,0.2)',
                borderRadius: 8, padding: '10px 14px', color: '#6ee7b7',
                fontSize: 13, marginBottom: 16 },
  errorBox:   { background: 'rgba(239,68,68,0.08)', border: '1px solid rgba(239,68,68,0.2)',
                borderRadius: 8, padding: '10px 14px', color: '#fca5a5',
                fontSize: 13, margin: '0 12px 8px' },
  infoCards:  { display: 'flex', flexDirection: 'column', gap: 8, marginTop: 8 },
  infoCard:   { background: '#111e35', border: '1px solid #1e2f50', borderRadius: 8,
                padding: '10px 14px', display: 'flex', alignItems: 'center', gap: 10 },
  infoCardTitle: { fontSize: 13, fontWeight: 500, color: '#f0f4ff', marginBottom: 1 },
  infoCardSub:   { fontSize: 11, color: '#4a5f84' },
}
