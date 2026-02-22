import React, { useState, useEffect, useRef, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { logout, checkSession, getUser } from '../utils/auth.js'
import { listMeetings, getUploadUrl, uploadAudioToS3 } from '../utils/api.js'
import Leaderboard from '../components/Leaderboard.jsx'
import PatternCards from '../components/PatternCards.jsx'
import TeamSelector from '../components/TeamSelector.jsx'
import DemoWarningBanner from '../components/DemoWarningBanner.jsx'
import { MeetingCardSkeleton } from '../components/SkeletonLoader.jsx'

const STATUS = {
  PENDING:      { label: 'Pending',      color: '#8a8a74' },
  TRANSCRIBING: { label: 'Transcribing', color: '#e8c06a' },
  ANALYZING:    { label: 'Analyzing',    color: '#6a9ae8' },
  DONE:         { label: 'Done',         color: '#c8f04a' },
  FAILED:       { label: 'Failed',       color: '#e87a6a' },
}

function fmtDate(iso) {
  if (!iso) return ''
  const d = new Date(iso)
  if (isNaN(d)) return ''
  return d.toLocaleDateString('en-GB', {day:'numeric', month:'short', year:'numeric'})
}

function WaveformBars({ active }) {
  const heights = [3,6,10,16,22,18,12,20,24,14,8,18,22,10,6,14,20,16,8,12]
  return (
    <div style={{display:'flex',alignItems:'center',gap:2,height:28}}>
      {heights.map((h,i) => (
        <div key={i} style={{
          width:2, height:h, background:'#c8f04a', borderRadius:1,
          opacity: active ? 0.9 : 0.25,
          animation: active ? `wavebar 0.8s ease-in-out ${i*0.04}s infinite alternate` : 'none',
          transition:'opacity 0.3s',
        }}/>
      ))}
    </div>
  )
}

function EmptyState() {
  const lines = [
    {w:'60%',delay:0},{w:'45%',delay:0.1},{w:'70%',delay:0.2},
    {w:'40%',delay:0.15},{w:'55%',delay:0.25},
  ]
  return (
    <div style={es.wrap}>
      <div style={es.ghost}>
        <div style={es.ghostTop}>
          <div style={es.ghostLabel}>YOUR FIRST MEETING</div>
          <div style={es.ghostDot}>◎</div>
        </div>
        <div style={es.ghostTitle}/>
        <div style={{...es.ghostTitle, width:'55%', height:10, marginTop:8, opacity:0.4}}/>
        <div style={es.ghostLines}>
          {lines.map((l,i) => (
            <div key={i} style={{...es.ghostLine, width:l.w, animationDelay:`${l.delay}s`}}/>
          ))}
        </div>
        <div style={es.ghostFooter}>
          <span style={es.ghostStatus}>● Waiting for audio</span>
          <WaveformBars active={false}/>
        </div>
      </div>
      <div style={es.cta}>
        <p style={es.ctaLine}>Upload a recording to begin</p>
        <div style={es.ctaArrow}>
          <span style={es.arrowLine}/>
          <span style={es.arrowHead}>→</span>
        </div>
      </div>
      <p style={es.hint}>
        Supports MP3 · MP4 · WAV · M4A<br/>
        AI extracts decisions, actions, follow-ups
      </p>
    </div>
  )
}

export default function Dashboard() {
  const navigate = useNavigate()
  const fileRef  = useRef()
  const [user,      setUser]      = useState('')
  const [userEmail, setUserEmail] = useState('')
  const [meetings,  setMeetings]  = useState([])
  const [loading,   setLoading]   = useState(true)
  const [uploading, setUploading] = useState(false)
  const [dragOver,  setDragOver]  = useState(false)
  const [uploadMsg, setUploadMsg] = useState('')
  const [title,     setTitle]     = useState('')
  const [error,     setError]     = useState('')
  const [uploadPct, setUploadPct] = useState(0)
  const [zoneHover, setZoneHover] = useState(false)
  
  // Initialize from localStorage immediately
  const [selectedTeamId, setSelectedTeamId] = useState(() => {
    const saved = localStorage.getItem('selectedTeamId')
    return (saved && saved !== 'null' && saved !== '') ? saved : null
  })
  const [selectedTeamName, setSelectedTeamName] = useState('')

  // Use ref to track the current teamId for polling
  const selectedTeamIdRef = useRef(selectedTeamId)
  
  // Update ref whenever selectedTeamId changes
  useEffect(() => {
    selectedTeamIdRef.current = selectedTeamId
  }, [selectedTeamId])

  // Fetch meetings function that uses the ref to get current teamId
  const fetchMeetings = useCallback(async () => {
    const currentTeamId = selectedTeamIdRef.current
    
    try { 
      // Add minimum loading time for better UX (skeleton visibility)
      const [data] = await Promise.all([
        listMeetings(currentTeamId),
        new Promise(resolve => setTimeout(resolve, 2000))
      ])
      setMeetings(data || [])
      setError('')
    }
    catch (err) { 
      if (err.response?.status !== 404) {
        setError('Failed to load meetings')
      }
      setMeetings([])
    }
    finally { setLoading(false) }
  }, []) // No dependencies - uses ref instead

  // Handle team change with localStorage persistence
  const handleTeamChange = useCallback((teamId) => {
    setSelectedTeamId(teamId)
    localStorage.setItem('selectedTeamId', teamId || '')
  }, [])

  // Initial setup and polling
  useEffect(() => {
    let mounted = true
    
    checkSession().then(async u => {
      if (!mounted) return
      if (!u) { navigate('/login'); return }
      setUser(getUser() || '')
      
      // Get user email for demo detection - try multiple methods
      try {
        // Method 1: Try fetchUserAttributes
        const { fetchUserAttributes } = await import('aws-amplify/auth')
        const attributes = await fetchUserAttributes()
        const email = attributes.email || ''
        console.log('User email from attributes:', email)
        setUserEmail(email)
      } catch (e) {
        console.log('fetchUserAttributes failed:', e)
        // Method 2: Try getting from user object
        try {
          const { getCurrentUser } = await import('aws-amplify/auth')
          const currentUser = await getCurrentUser()
          const email = currentUser.signInDetails?.loginId || currentUser.username || ''
          console.log('User email from getCurrentUser:', email)
          setUserEmail(email)
        } catch (e2) {
          console.log('getCurrentUser also failed:', e2)
        }
      }
      
      fetchMeetings()
    })
    
    // Set up polling interval
    const interval = setInterval(() => {
      fetchMeetings()
    }, 8000)
    
    return () => {
      mounted = false
      clearInterval(interval)
    }
  }, [fetchMeetings, navigate])

  // Fetch meetings when team changes
  useEffect(() => {
    fetchMeetings()
  }, [selectedTeamId, fetchMeetings])

  async function handleFile(file) {
    if (!file) return
    
    const currentTeamId = selectedTeamIdRef.current
    const meetingTitle = title.trim() || file.name.replace(/\.[^/.]+$/, '')
    setUploading(true); setUploadPct(0)
    setUploadMsg('Requesting upload slot…'); setError('')
    try {
      const { uploadUrl } = await getUploadUrl(meetingTitle, file.type || 'audio/mpeg', file.size, currentTeamId)
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

  const isProcessing = meetings.some(m => ['TRANSCRIBING','ANALYZING'].includes(m.status))

  return (
    <div style={s.root}>
      <style>{css}</style>
      <div style={s.grain} aria-hidden="true"/>

      <header style={s.hdr}>
        <div style={s.hdrL}>
          <div style={s.logo}>
            <span style={s.logoM}>M</span>
            <span style={s.logoR}>eetingMind</span>
          </div>
          {isProcessing && (
            <div style={s.pill}>
              <span style={{...s.pillDot, animation:'pulse 1.5s infinite'}}/>
              Processing
            </div>
          )}
        </div>
        <div style={s.hdrR}>
          <span style={s.userTxt}>{user}</span>
          <button className="signout"
            onClick={async () => { await logout(); navigate('/login') }}
            style={s.signOut}>↗ Sign out</button>
        </div>
      </header>

      <main style={s.main}>
        <section style={s.left}>
          {/* Team Selector */}
          <div style={{marginBottom: 24}}>
            <TeamSelector 
              selectedTeamId={selectedTeamId}
              onTeamChange={handleTeamChange}
              onTeamNameChange={setSelectedTeamName}
            />
          </div>

          {/* Demo Warning Banner */}
          <DemoWarningBanner userEmail={userEmail} />

          <div style={s.secHead}>
            <div>
              <h2 style={s.secTitle}>Your Meetings</h2>
              {!loading && (
                <p style={s.secSub}>
                  {meetings.length === 0 ? '' 
                    : `${meetings.length} recording${meetings.length !== 1 ? 's' : ''}`}
                </p>
              )}
            </div>
            <div style={{display:'flex', alignItems:'center', gap:12}}>
              {meetings.length > 0 && (
                <>
                  <button onClick={() => navigate('/actions')} style={s.actionsBtn}>
                    ✓ All Actions
                  </button>
                  <button onClick={() => navigate('/graveyard')} style={s.graveyardBtn}>
                    🪦 Graveyard
                  </button>
                  <button onClick={() => navigate('/debt')} style={s.debtBtn}>
                    💰 View Debt
                  </button>
                </>
              )}
              {meetings.length > 0 && <span style={s.bigCount}>{meetings.length}</span>}
            </div>
          </div>

          {error && <div style={s.errBox}>{error}</div>}

          {loading ? (
            <div style={{display:'flex', flexDirection:'column', gap:8}}>
              <MeetingCardSkeleton />
              <MeetingCardSkeleton />
              <MeetingCardSkeleton />
            </div>
          ) : meetings.length === 0 ? (
            <EmptyState/>
          ) : (
            <ul style={s.list}>
              {meetings.map((m, i) => {
                const cfg  = STATUS[m.status] || STATUS.PENDING
                const done = m.status === 'DONE'
                const date = fmtDate(m.createdAt || m.updatedAt)
                
                // Health grade colors
                const gradeColors = {
                  'A': '#10b981',
                  'B': '#c8f04a',
                  'C': '#f59e0b',
                  'D': '#f97316',
                  'F': '#ef4444'
                }
                const gradeColor = gradeColors[m.healthGrade] || '#6b7260'
                
                return (
                  <li key={m.meetingId} className="mrow"
                    onClick={() => done && navigate(`/meeting/${m.meetingId}`)}
                    style={{...s.row, cursor: done ? 'pointer' : 'default',
                      opacity: m.status === 'FAILED' ? 0.5 : 1,
                      animationDelay:`${i*0.06}s`}}>
                    <div style={s.rowTop}>
                      <span style={s.rowTitle}>{m.title}</span>
                      <div style={{display:'flex', alignItems:'center', gap:8}}>
                        {done && m.isGhost && (
                          <span style={s.ghostBadge}>
                            👻 GHOST
                          </span>
                        )}
                        {done && m.healthGrade && (
                          <span style={{...s.healthBadge, background: gradeColor}}>
                            {m.healthGrade}
                          </span>
                        )}
                        {done && <span className="rowarr" style={s.rowArr}>→</span>}
                      </div>
                    </div>
                    <div style={s.rowBot}>
                      <span style={{...s.rowStatus, color: cfg.color}}>● {cfg.label}</span>
                      {date && <span style={s.rowDate}>{date}</span>}
                    </div>
                    {m.summary && (
                      <p style={s.rowSumm}>{m.summary.slice(0,110)}…</p>
                    )}
                    {done && m.healthLabel && (
                      <p style={s.healthLabel}>{m.healthLabel}</p>
                    )}
                    {['TRANSCRIBING','ANALYZING'].includes(m.status) && (
                      <div style={s.progTrack}>
                        <div style={{...s.progFill,
                          width: m.status === 'TRANSCRIBING' ? '40%' : '75%'}}/>
                      </div>
                    )}
                  </li>
                )
              })}
            </ul>
          )}

          {/* Leaderboard */}
          {!loading && meetings.length > 0 && <Leaderboard teamId={selectedTeamId} />}

          {/* Pattern Detection */}
          {!loading && meetings.length > 0 && <PatternCards meetings={meetings} />}
        </section>

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

          {/* Visual confirmation of upload destination */}
          <div style={s.uploadDestination}>
            <span style={s.uploadDestLabel}>📤 UPLOADING TO:</span>
            <span style={s.uploadDestValue}>
              {selectedTeamId && selectedTeamName ? (
                <>
                  <span style={s.teamEmoji}>👥</span> {selectedTeamName}
                </>
              ) : (
                <>
                  <span style={s.teamEmoji}>📋</span> Personal (Just Me)
                </>
              )}
            </span>
          </div>

          <div className="uzone"
            onClick={() => !uploading && fileRef.current?.click()}
            onMouseEnter={() => setZoneHover(true)}
            onMouseLeave={() => setZoneHover(false)}
            onDragOver={e => { e.preventDefault(); setDragOver(true) }}
            onDragLeave={() => setDragOver(false)}
            onDrop={onDrop}
            style={{...s.zone,
              ...(dragOver||zoneHover ? {borderColor:'#c8f04a', background:'#131309'} : {}),
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
                <div style={{marginBottom:14, display:'flex', justifyContent:'center'}}>
                  <WaveformBars active={zoneHover||dragOver}/>
                </div>
                <p style={s.zoneTitle}>Drop audio file here</p>
                <p style={s.zoneSub}>or click to browse</p>
                <p style={s.zoneFmt}>MP3 · MP4 · WAV · M4A · WEBM · max 500MB</p>
              </>
            )}
          </div>

          {uploadMsg && !uploading && <div style={s.okBox}>{uploadMsg}</div>}

          <div style={s.pipeline}>
            <p style={s.pipeLbl}>WHAT HAPPENS NEXT</p>
            {[
              {n:'01', t:'Transcribe', d:'Speaker-labeled text via AWS Transcribe'},
              {n:'02', t:'Analyze',    d:'Decisions + action items via Bedrock Claude'},
              {n:'03', t:'Notify',     d:'Email reminders for approaching deadlines'},
            ].map((step,i) => (
              <div key={step.n} style={{...s.pipeStep, animationDelay:`${0.2+i*0.1}s`}}
                className="pipestep">
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

const es = {
  wrap:      {padding:'24px 0 0', animation:'fadeUp 0.5s ease 0.1s both'},
  ghost:     {background:'#111108', border:'1px solid #2a2a20', borderRadius:8,
              padding:'20px 22px', marginBottom:24, overflow:'hidden'},
  ghostTop:  {display:'flex', justifyContent:'space-between', alignItems:'center', marginBottom:16},
  ghostLabel:{fontSize:9, letterSpacing:'0.16em', color:'#3a3a2e', textTransform:'uppercase'},
  ghostDot:  {fontSize:18, color:'#2a2a20', animation:'ghostpulse 2.5s ease infinite'},
  ghostTitle:{height:14, background:'#2a2a24', borderRadius:3, width:'72%', marginBottom:12,
              animation:'ghostpulse 2.5s ease 0.3s infinite'},
  ghostLines:{display:'flex', flexDirection:'column', gap:8, marginBottom:18},
  ghostLine: {height:8, background:'#252520', borderRadius:2,
              animation:'ghostpulse 2.5s ease infinite'},
  ghostFooter:{display:'flex', justifyContent:'space-between', alignItems:'center',
               paddingTop:14, borderTop:'1px solid #1e1e18'},
  ghostStatus:{fontSize:9, letterSpacing:'0.12em', color:'#3a3a2e'},
  cta:       {display:'flex', alignItems:'center', gap:16, marginBottom:20},
  ctaLine:   {fontSize:12, color:'#6b7260', letterSpacing:'0.05em', whiteSpace:'nowrap'},
  ctaArrow:  {display:'flex', alignItems:'center', gap:6, flex:1},
  arrowLine: {display:'block', height:1, flex:1,
              background:'linear-gradient(90deg,#3a3a2e,transparent)'},
  arrowHead: {fontSize:14, color:'#c8f04a', animation:'arrowpulse 1.5s ease infinite'},
  hint:      {fontSize:10, color:'#444438', letterSpacing:'0.05em', lineHeight:1.8},
}

const css = `
  @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=DM+Mono:wght@300;400&display=swap');
  *{box-sizing:border-box;margin:0;padding:0;}
  body{background:#0c0c09;}
  @keyframes fadeUp{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:translateY(0)}}
  @keyframes spin{to{transform:rotate(360deg)}}
  @keyframes pulse{0%,100%{opacity:1}50%{opacity:0.3}}
  @keyframes shimmer{0%,100%{opacity:0.4}50%{opacity:0.7}}
  @keyframes shimmerSlide{0%{left:-100%}100%{left:100%}}
  @keyframes ghostpulse{0%,100%{opacity:0.6}50%{opacity:1}}
  @keyframes arrowpulse{0%,100%{transform:translateX(0);opacity:1}50%{transform:translateX(4px);opacity:0.6}}
  @keyframes wavebar{from{transform:scaleY(0.4)}to{transform:scaleY(1.4)}}
  .mrow:hover{background:#1c1c14 !important;border-color:#3a3a28 !important;}
  .mrow:hover .rowarr{color:#c8f04a !important;}
  .uzone{transition:all 0.2s;}
  input::placeholder{color:#555548;}
  input:focus{outline:none;border-color:#c8f04a !important;}
  .signout:hover{color:#f0ece0 !important;border-color:#6b7260 !important;}
  .pipestep{animation:fadeUp 0.4s ease both;}
  .patterncard{animation:fadeUp 0.3s ease both;}
  .patterncard:hover{border-color:#c8f04a !important;}
`

const s = {
  root: {minHeight:'100vh', background:'#0c0c09', fontFamily:"'DM Mono',monospace",
         color:'#f0ece0', position:'relative'},
  grain:{position:'fixed', inset:0, pointerEvents:'none', zIndex:999, opacity:0.035,
         backgroundImage:`url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)'/%3E%3C/svg%3E")`,
         backgroundRepeat:'repeat', backgroundSize:'128px'},
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
  main: {display:'grid', gridTemplateColumns:'1fr 420px', minHeight:'calc(100vh - 54px)'},
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
  actionsBtn:{background:'#6a9ae8', border:'none', borderRadius:4,
              padding:'6px 14px', color:'#0c0c09', fontSize:11, letterSpacing:'0.05em',
              cursor:'pointer', fontFamily:"'DM Mono',monospace", fontWeight:400,
              transition:'opacity 0.15s'},
  graveyardBtn:{background:'#8a8a74', border:'none', borderRadius:4,
                padding:'6px 14px', color:'#0c0c09', fontSize:11, letterSpacing:'0.05em',
                cursor:'pointer', fontFamily:"'DM Mono',monospace", fontWeight:400,
                transition:'opacity 0.15s'},
  debtBtn:{background:'#c8f04a', border:'none', borderRadius:4,
           padding:'6px 14px', color:'#0c0c09', fontSize:11, letterSpacing:'0.05em',
           cursor:'pointer', fontFamily:"'DM Mono',monospace", fontWeight:400,
           transition:'opacity 0.15s'},
  errBox:{background:'#1a0e0e', border:'1px solid #4a2a2a', borderRadius:4,
          padding:'10px 12px', color:'#e87a6a', fontSize:11, marginBottom:16},
  center:{display:'flex', alignItems:'center', justifyContent:'center', padding:'80px 0'},
  spin:  {width:20, height:20, border:'2px solid #2a2a20',
          borderTopColor:'#c8f04a', borderRadius:'50%'},
  list: {listStyle:'none', display:'flex', flexDirection:'column', gap:8},
  row:  {background:'#141410', border:'1px solid #2e2e22', borderRadius:6,
         padding:'14px 16px', transition:'background 0.15s, border-color 0.15s',
         animation:'fadeUp 0.35s ease both'},
  rowTop:   {display:'flex', justifyContent:'space-between', alignItems:'center', marginBottom:8},
  rowTitle: {fontSize:13, color:'#e8e4d0', letterSpacing:'0.01em', lineHeight:1.4},
  rowArr:   {fontSize:14, color:'#6b7260', transition:'color 0.15s', flexShrink:0},
  rowBot:   {display:'flex', justifyContent:'space-between', alignItems:'center'},
  rowStatus:{fontSize:10, letterSpacing:'0.07em'},
  rowDate:  {fontSize:10, color:'#6b7260', letterSpacing:'0.05em'},
  rowSumm:  {fontSize:11, color:'#6b7260', marginTop:10, lineHeight:1.6,
             borderTop:'1px solid #2a2a20', paddingTop:10},
  healthBadge:{fontFamily:"'Playfair Display',serif", fontSize:16, fontWeight:900,
               color:'#0c0c09', padding:'2px 10px', borderRadius:4,
               display:'inline-block', lineHeight:1.2},
  ghostBadge:{fontSize:10, letterSpacing:'0.1em', color:'#8a8a74',
              background:'#1a1a16', border:'1px solid #3a3a2e',
              padding:'3px 8px', borderRadius:3, display:'inline-block'},
  healthLabel:{fontSize:10, color:'#8a8a74', marginTop:8, letterSpacing:'0.05em',
               fontStyle:'italic'},
  progTrack:{height:2, background:'#2a2a20', borderRadius:1, marginTop:10},
  progFill: {height:'100%', background:'#c8f04a', borderRadius:1, transition:'width 1s ease'},
  fGroup:{marginBottom:18},
  lbl:  {display:'block', fontSize:9, letterSpacing:'0.15em', color:'#8a8a74',
         textTransform:'uppercase', marginBottom:8},
  inp:  {width:'100%', background:'#1e1e16', border:'1px solid #3a3a2e',
         borderRadius:4, padding:'10px 12px', color:'#f0ece0',
         fontSize:13, fontFamily:"'DM Mono',monospace", caretColor:'#c8f04a',
         outline:'none', transition:'border-color 0.2s'},
  uploadDestination:{background:'#141a09', border:'1px solid #3a4a18', borderRadius:4,
                     padding:'10px 14px', marginBottom:14, display:'flex',
                     alignItems:'center', gap:10},
  uploadDestLabel:{fontSize:9, letterSpacing:'0.12em', color:'#6b7260',
                   textTransform:'uppercase'},
  uploadDestValue:{fontSize:12, color:'#c8f04a', letterSpacing:'0.02em',
                   fontWeight:500, display:'flex', alignItems:'center', gap:6},
  teamEmoji:{fontSize:14},
  zone: {border:'1px dashed #3a3a2e', borderRadius:8, padding:'28px 20px',
         textAlign:'center', cursor:'pointer', marginBottom:14, background:'#111108'},
  zoneTitle:{fontSize:13, color:'#e8e4d0', marginBottom:4, marginTop:4},
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
