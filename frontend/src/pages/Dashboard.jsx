import React, { useState, useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { logout, checkSession } from '../utils/auth.js'
import { listMeetings, getUploadUrl, uploadAudioToS3 } from '../utils/api.js'

const STATUS = {
  PENDING:      { label: 'Pending',      color: '#8a8a74' },
  TRANSCRIBING: { label: 'Transcribing', color: '#e8c06a' },
  ANALYZING:    { label: 'Analyzing',    color: '#6a9ae8' },
  DONE:         { label: 'Done',         color: '#c8f04a' },
  FAILED:       { label: 'Failed',       color: '#e87a6a' },
}

export default function Dashboard() {
  const navigate = useNavigate()
  const fileRef  = useRef()
  const pollRef  = useRef()

  const [user,      setUser]      = useState('')
  const [meetings,  setMeetings]  = useState([])
  const [loading,   setLoading]   = useState(true)
  const [uploading, setUploading] = useState(false)
  const [dragOver,  setDragOver]  = useState(false)
  const [uploadMsg, setUploadMsg] = useState('')
  const [title,     setTitle]     = useState('')
  const [error,     setError]     = useState('')
  const [uploadPct, setUploadPct] = useState(0)

  useEffect(() => {
    checkSession().then(u => {
      if (!u) { navigate('/login'); return }
      setUser(u.signInDetails?.loginId || '')
      fetchMeetings()
    })
    pollRef.current = setInterval(fetchMeetings, 8000)
    return () => clearInterval(pollRef.current)
  }, [])

  async function fetchMeetings() {
    try {
      const data = await listMeetings()
      setMeetings(data)
    } catch { setError('Failed to load meetings') }
    finally  { setLoading(false) }
  }

  async function handleFile(file) {
    if (!file) return
    const meetingTitle = title.trim() || file.name.replace(/\.[^/.]+$/, '')
    setUploading(true); setUploadPct(0)
    setUploadMsg('Requesting upload slot…'); setError('')
    try {
      const { uploadUrl } = await getUploadUrl(meetingTitle, file.type || 'audio/mpeg', file.size)
      setUploadMsg('Uploading audio…'); setUploadPct(40)
      await uploadAudioToS3(uploadUrl, file)
      setUploadPct(100); setUploadMsg('✓ Upload complete — AI processing started')
      setTitle('')
      setTimeout(() => { setUploadMsg(''); setUploadPct(0); fetchMeetings() }, 3000)
    } catch (e) {
      setError(e.response?.data?.error || e.message || 'Upload failed')
      setUploadMsg(''); setUploadPct(0)
    } finally { setUploading(false) }
  }

  function onDrop(e) {
    e.preventDefault(); setDragOver(false)
    handleFile(e.dataTransfer.files[0])
  }

  const hasPending = meetings.some(m => ['TRANSCRIBING','ANALYZING','PENDING'].includes(m.status))

  return (
    <div style={s.root}>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=DM+Mono:wght@300;400&display=swap');
        *{box-sizing:border-box;margin:0;padding:0;}
        body{background:#0c0c09;}
        @keyframes fadeUp{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:translateY(0)}}
        @keyframes spin{to{transform:rotate(360deg)}}
        @keyframes pulse{0%,100%{opacity:1}50%{opacity:0.3}}
        .mrow:hover{ background:#1a1a12 !important; border-color:#3a3a2a !important; }
        .uzone:hover{ border-color:#c8f04a !important; }
        input::placeholder{color:#6b7260;}
        input:focus{outline:none; border-color:#c8f04a !important;}
        input:-webkit-autofill{
          -webkit-box-shadow:0 0 0 100px #1e1e16 inset !important;
          -webkit-text-fill-color:#f0ece0 !important;
        }
      `}</style>

      {/* HEADER */}
      <header style={s.hdr}>
        <div style={s.hdrL}>
          <div style={s.logo}>
            <span style={s.logoM}>M</span>
            <span style={s.logoR}>eetingMind</span>
          </div>
          {hasPending && (
            <div style={s.pill}>
              <span style={{...s.pillDot, animation:'pulse 1.5s infinite'}}/>
              Processing
            </div>
          )}
        </div>
        <div style={s.hdrR}>
          <span style={s.userTxt}>{user}</span>
          <button onClick={async () => { await logout(); navigate('/login') }}
            style={s.signOut}>↗ Sign out</button>
        </div>
      </header>

      {/* LAYOUT */}
      <main style={s.main}>

        {/* LEFT — meetings */}
        <section style={s.left}>
          <div style={s.secHead}>
            <div>
              <h2 style={s.secTitle}>Your Meetings</h2>
              <p style={s.secSub}>
                {loading ? 'Loading…'
                  : meetings.length === 0 ? 'No recordings yet'
                  : `${meetings.length} recording${meetings.length !== 1 ? 's' : ''}`}
              </p>
            </div>
            {meetings.length > 0 &&
              <span style={s.bigCount}>{meetings.length}</span>}
          </div>

          {error && <div style={s.errBox}>{error}</div>}

          {loading ? (
            <div style={s.center}>
              <div style={{...s.spin, animation:'spin 1s linear infinite'}}/>
              <p style={s.centerTxt}>Loading meetings…</p>
            </div>
          ) : meetings.length === 0 ? (
            <div style={s.empty}>
              <div style={s.emptyRing}>◎</div>
              <p style={s.emptyH}>No meetings yet</p>
              <p style={s.emptyP}>Upload your first recording →</p>
            </div>
          ) : (
            <ul style={s.list}>
              {meetings.map((m, i) => {
                const cfg = STATUS[m.status] || STATUS.PENDING
                const done = m.status === 'DONE'
                return (
                  <li key={m.meetingId} className="mrow"
                    onClick={() => done && navigate(`/meeting/${m.meetingId}`)}
                    style={{...s.row, cursor: done ? 'pointer' : 'default',
                      opacity: m.status === 'FAILED' ? 0.5 : 1,
                      animationDelay:`${i*0.04}s`}}>
                    <div style={s.rowTop}>
                      <span style={s.rowTitle}>{m.title}</span>
                      {done && <span style={s.rowArr}>→</span>}
                    </div>
                    <div style={s.rowBot}>
                      <span style={{...s.rowStatus, color: cfg.color}}>
                        ● {cfg.label}
                      </span>
                      <span style={s.rowDate}>
                        {new Date(m.createdAt).toLocaleDateString('en-GB',
                          {day:'numeric', month:'short', year:'numeric'})}
                      </span>
                    </div>
                    {m.summary && (
                      <p style={s.rowSumm}>{m.summary.slice(0,90)}…</p>
                    )}
                    {['TRANSCRIBING','ANALYZING'].includes(m.status) && (
                      <div style={s.progTrack}>
                        <div style={{...s.progFill,
                          width: m.status === 'TRANSCRIBING' ? '45%' : '80%'}}/>
                      </div>
                    )}
                  </li>
                )
              })}
            </ul>
          )}
        </section>

        {/* RIGHT — upload */}
        <section style={s.right}>
          <div style={s.secHead}>
            <div>
              <h2 style={s.secTitle}>New Recording</h2>
              <p style={s.secSub}>Upload audio to start AI analysis</p>
            </div>
          </div>

          <div style={s.fGroup}>
            <label style={s.lbl}>MEETING TITLE</label>
            <input type="text" value={title}
              onChange={e => setTitle(e.target.value)}
              placeholder="e.g. Q1 Planning Session"
              style={s.inp}/>
          </div>

          <div className="uzone"
            onClick={() => !uploading && fileRef.current?.click()}
            onDragOver={e => { e.preventDefault(); setDragOver(true) }}
            onDragLeave={() => setDragOver(false)}
            onDrop={onDrop}
            style={{...s.zone,
              ...(dragOver ? {borderColor:'#c8f04a', background:'#161609'} : {}),
              ...(uploading ? {opacity:0.5, pointerEvents:'none'} : {})}}>
            <input ref={fileRef} type="file" accept="audio/*,video/mp4"
              onChange={e => handleFile(e.target.files[0])}
              style={{display:'none'}}/>
            {uploading ? (
              <>
                <div style={{...s.spin, animation:'spin 1s linear infinite', marginBottom:14}}/>
                <p style={s.zoneTitle}>{uploadMsg}</p>
                {uploadPct > 0 && (
                  <div style={s.upTrack}>
                    <div style={{...s.upFill, width:`${uploadPct}%`}}/>
                  </div>
                )}
              </>
            ) : (
              <>
                <div style={s.upArrow}>↑</div>
                <p style={s.zoneTitle}>Drop audio file here</p>
                <p style={s.zoneSub}>or click to browse</p>
                <p style={s.zoneFmt}>MP3 · MP4 · WAV · M4A · WEBM · max 500MB</p>
              </>
            )}
          </div>

          {uploadMsg && !uploading && (
            <div style={s.okBox}>{uploadMsg}</div>
          )}

          <div style={s.pipeline}>
            <p style={s.pipeLbl}>WHAT HAPPENS NEXT</p>
            {[
              {n:'01', t:'Transcribe', d:'Speaker-labeled text via AWS Transcribe'},
              {n:'02', t:'Analyze',    d:'Decisions + action items via Bedrock Claude'},
              {n:'03', t:'Notify',     d:'Email reminders for approaching deadlines'},
            ].map(step => (
              <div key={step.n} style={s.pipeStep}>
                <span style={s.pipeN}>{step.n}</span>
                <div>
                  <p style={s.pipeT}>{step.t}</p>
                  <p style={s.pipeD}>{step.d}</p>
                </div>
              </div>
            ))}
          </div>
        </section>
      </main>
    </div>
  )
}

const s = {
  root: {minHeight:'100vh', background:'#0c0c09', fontFamily:"'DM Mono',monospace", color:'#f0ece0'},

  hdr:  {background:'#0f0f0c', borderBottom:'1px solid #2a2a20', padding:'0 36px',
         height:54, display:'flex', alignItems:'center', justifyContent:'space-between',
         position:'sticky', top:0, zIndex:100},
  hdrL: {display:'flex', alignItems:'center', gap:16},
  logo: {display:'flex', alignItems:'baseline', gap:1},
  logoM:{fontFamily:"'Playfair Display',serif", fontSize:20, fontWeight:900, color:'#c8f04a'},
  logoR:{fontFamily:"'Playfair Display',serif", fontSize:17, fontWeight:700, color:'#f0ece0'},
  pill: {display:'flex', alignItems:'center', gap:6, background:'#181809',
         border:'1px solid #3a3a18', borderRadius:20, padding:'3px 10px',
         fontSize:10, letterSpacing:'0.1em', color:'#c8f04a'},
  pillDot:{width:5, height:5, borderRadius:'50%', background:'#c8f04a', flexShrink:0},
  hdrR: {display:'flex', alignItems:'center', gap:14},
  userTxt:{fontSize:11, letterSpacing:'0.06em', color:'#8a8a74'},
  signOut:{background:'none', border:'1px solid #3a3a2e', borderRadius:3,
           padding:'5px 12px', color:'#8a8a74', fontSize:10, letterSpacing:'0.1em',
           cursor:'pointer', fontFamily:"'DM Mono',monospace",
           transition:'color 0.15s, border-color 0.15s'},

  main: {display:'grid', gridTemplateColumns:'1fr 400px',
         minHeight:'calc(100vh - 54px)'},

  left: {borderRight:'1px solid #2a2a20', padding:'32px 36px',
         animation:'fadeUp 0.4s ease both'},
  right:{background:'#0f0f0c', padding:'32px 36px',
         animation:'fadeUp 0.4s ease 0.08s both'},

  secHead:{display:'flex', justifyContent:'space-between', alignItems:'flex-start',
           marginBottom:24, paddingBottom:18, borderBottom:'1px solid #2a2a20'},
  secTitle:{fontFamily:"'Playfair Display',serif", fontSize:22, fontWeight:700,
            color:'#f0ece0', letterSpacing:'-0.3px', marginBottom:4},
  secSub:  {fontSize:10, letterSpacing:'0.1em', color:'#6b7260', textTransform:'uppercase'},
  bigCount:{fontFamily:"'Playfair Display',serif", fontSize:32, fontWeight:900, color:'#c8f04a'},

  errBox:{background:'#1a0e0e', border:'1px solid #4a2a2a', borderRadius:4,
          padding:'10px 12px', color:'#e87a6a', fontSize:11, marginBottom:16},

  center:{display:'flex', flexDirection:'column', alignItems:'center',
          justifyContent:'center', padding:'80px 0', gap:14},
  centerTxt:{fontSize:11, color:'#6b7260', letterSpacing:'0.1em'},
  spin:  {width:20, height:20, border:'2px solid #2a2a20',
          borderTopColor:'#c8f04a', borderRadius:'50%'},

  empty:{display:'flex', flexDirection:'column', alignItems:'center',
         justifyContent:'center', padding:'80px 0', gap:10},
  emptyRing:{fontSize:48, color:'#3a3a2e', marginBottom:4},
  emptyH:   {fontSize:15, color:'#8a8a74', letterSpacing:'-0.2px'},
  emptyP:   {fontSize:11, color:'#6b7260', letterSpacing:'0.05em'},

  list: {listStyle:'none', display:'flex', flexDirection:'column', gap:8},
  row:  {background:'#141410', border:'1px solid #2a2a20', borderRadius:6,
         padding:'14px 16px', transition:'background 0.15s, border-color 0.15s',
         animation:'fadeUp 0.35s ease both'},
  rowTop:   {display:'flex', justifyContent:'space-between', alignItems:'center', marginBottom:8},
  rowTitle: {fontSize:13, color:'#e8e4d0', letterSpacing:'0.01em'},
  rowArr:   {fontSize:12, color:'#8a8a74'},
  rowBot:   {display:'flex', justifyContent:'space-between', alignItems:'center'},
  rowStatus:{fontSize:10, letterSpacing:'0.07em'},
  rowDate:  {fontSize:10, color:'#555548', letterSpacing:'0.05em'},
  rowSumm:  {fontSize:11, color:'#6b7260', marginTop:8, lineHeight:1.55,
             borderTop:'1px solid #2a2a20', paddingTop:8},
  progTrack:{height:2, background:'#2a2a20', borderRadius:1, marginTop:10},
  progFill: {height:'100%', background:'#c8f04a', borderRadius:1, transition:'width 1s ease'},

  fGroup:{marginBottom:18},
  lbl:  {display:'block', fontSize:9, letterSpacing:'0.15em', color:'#8a8a74',
         textTransform:'uppercase', marginBottom:8},
  inp:  {width:'100%', background:'#1e1e16', border:'1px solid #3a3a2e',
         borderRadius:4, padding:'10px 12px', color:'#f0ece0',
         fontSize:13, fontFamily:"'DM Mono',monospace", caretColor:'#c8f04a',
         outline:'none', transition:'border-color 0.2s'},

  zone: {border:'1px dashed #3a3a2e', borderRadius:6, padding:'32px 20px',
         textAlign:'center', cursor:'pointer', transition:'border-color 0.2s',
         marginBottom:14, background:'#111108'},
  upArrow: {fontSize:26, color:'#c8f04a', marginBottom:12, lineHeight:1},
  zoneTitle:{fontSize:13, color:'#e8e4d0', marginBottom:4},
  zoneSub:  {fontSize:11, color:'#8a8a74', marginBottom:8},
  zoneFmt:  {fontSize:9, color:'#555548', letterSpacing:'0.1em', textTransform:'uppercase'},
  upTrack:  {height:2, background:'#2a2a20', borderRadius:1,
             marginTop:12, width:'80%', margin:'12px auto 0'},
  upFill:   {height:'100%', background:'#c8f04a', borderRadius:1, transition:'width 0.3s'},
  okBox:    {background:'#141a09', border:'1px solid #3a4a18', borderRadius:4,
             padding:'10px 12px', color:'#c8f04a', fontSize:11,
             letterSpacing:'0.04em', marginBottom:14},

  pipeline:{marginTop:8, paddingTop:18, borderTop:'1px solid #2a2a20'},
  pipeLbl: {fontSize:9, letterSpacing:'0.15em', color:'#555548',
            textTransform:'uppercase', marginBottom:16},
  pipeStep:{display:'flex', gap:14, alignItems:'flex-start', marginBottom:14},
  pipeN:   {fontFamily:"'Playfair Display',serif", fontSize:18, fontWeight:700,
            color:'#3a3a2e', lineHeight:1, flexShrink:0, marginTop:1},
  pipeT:   {fontSize:12, color:'#a8a890', marginBottom:3, letterSpacing:'0.02em'},
  pipeD:   {fontSize:10, color:'#6b7260', letterSpacing:'0.03em', lineHeight:1.5},
}
