import React, { useState, useEffect } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { checkSession } from '../utils/auth.js'
import { getMeeting, updateAction } from '../utils/api.js'

export default function MeetingDetail() {
  const { meetingId } = useParams()
  const navigate = useNavigate()
  const [meeting, setMeeting] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error,   setError]   = useState('')
  const [tab,     setTab]     = useState('actions')

  useEffect(() => {
    checkSession().then(u => { if (!u) navigate('/login') })
    fetchMeeting()
  }, [])

  async function fetchMeeting() {
    try {
      const data = await getMeeting(meetingId)
      setMeeting(data)
    } catch (e) {
      setError('Failed to load meeting')
    } finally {
      setLoading(false)
    }
  }

  async function toggleAction(actionId, current) {
    try {
      await updateAction(meetingId, actionId, !current)
      setMeeting(m => ({
        ...m,
        actionItems: m.actionItems.map(a =>
          a.id === actionId ? { ...a, completed: !current } : a
        )
      }))
    } catch (e) {
      setError('Failed to update action')
    }
  }

  function deadlineColor(deadline) {
    if (!deadline) return '#555548'
    const days = Math.ceil((new Date(deadline) - new Date()) / 86400000)
    if (days < 0)  return '#e87a6a'
    if (days <= 3) return '#e8c06a'
    return '#c8f04a'
  }

  function deadlineLabel(deadline) {
    if (!deadline) return null
    const days = Math.ceil((new Date(deadline) - new Date()) / 86400000)
    if (days < 0)  return `${Math.abs(days)}d overdue`
    if (days === 0) return 'Due today'
    if (days === 1) return 'Due tomorrow'
    return new Date(deadline).toLocaleDateString('en-GB', {day:'numeric', month:'short'})
  }

  if (loading) return (
    <div style={{...s.root, display:'flex', alignItems:'center', justifyContent:'center'}}>
      <style>{fonts}</style>
      <div style={{...s.spinner, animation:'spin 1s linear infinite'}}/>
    </div>
  )

  if (error || !meeting) return (
    <div style={{...s.root, display:'flex', alignItems:'center', justifyContent:'center'}}>
      <style>{fonts}</style>
      <div style={{textAlign:'center'}}>
        <p style={{color:'#e87a6a', marginBottom:16, fontSize:13}}>{error || 'Meeting not found'}</p>
        <button onClick={() => navigate('/')} style={s.backBtn}>← Back to dashboard</button>
      </div>
    </div>
  )

  const actions   = meeting.actionItems   || []
  const decisions = meeting.decisions     || []
  const followUps = meeting.followUps     || []
  const done      = actions.filter(a => a.completed).length
  const pct       = actions.length ? Math.round((done / actions.length) * 100) : 0

  return (
    <div style={s.root}>
      <style>{fonts}</style>

      {/* HEADER */}
      <header style={s.hdr}>
        <button onClick={() => navigate('/')} style={s.backBtn}>← Meetings</button>
        <div style={s.hdrMeta}>
          <span style={s.statusDot}>● Done</span>
          <span style={s.hdrDate}>
            {new Date(meeting.createdAt).toLocaleDateString('en-GB',
              {day:'numeric', month:'long', year:'numeric'})}
          </span>
        </div>
      </header>

      {/* HERO */}
      <div style={s.hero}>
        <h1 style={s.heroTitle}>{meeting.title}</h1>
        {meeting.summary && <p style={s.heroSummary}>{meeting.summary}</p>}

        {/* Progress bar */}
        {actions.length > 0 && (
          <div style={s.progressWrap}>
            <div style={s.progressMeta}>
              <span style={s.progressLabel}>ACTION ITEMS</span>
              <span style={s.progressCount}>{done}/{actions.length} complete</span>
            </div>
            <div style={s.progressTrack}>
              <div style={{...s.progressFill, width:`${pct}%`}}/>
            </div>
          </div>
        )}
      </div>

      {/* TABS */}
      <div style={s.tabBar}>
        {[
          {id:'actions',   label:`Actions (${actions.length})`},
          {id:'decisions', label:`Decisions (${decisions.length})`},
          {id:'transcript',label:'Transcript'},
          {id:'followups', label:`Follow-ups (${followUps.length})`},
        ].map(t => (
          <button key={t.id} onClick={() => setTab(t.id)}
            style={{...s.tab, ...(tab===t.id ? s.tabActive : {})}}>
            {t.label}
          </button>
        ))}
      </div>

      {/* CONTENT */}
      <main style={s.main}>

        {/* ACTIONS */}
        {tab === 'actions' && (
          <div style={s.section}>
            {actions.length === 0 ? (
              <p style={s.empty}>No action items extracted</p>
            ) : (
              <ul style={s.actionList}>
                {actions.map(a => (
                  <li key={a.id}
                    onClick={() => toggleAction(a.id, a.completed)}
                    style={{...s.actionRow, opacity: a.completed ? 0.5 : 1}}>
                    <div style={{...s.checkbox, ...(a.completed ? s.checkboxDone : {})}}>
                      {a.completed && <span style={s.checkmark}>✓</span>}
                    </div>
                    <div style={s.actionBody}>
                      <p style={{
                        ...s.actionTask,
                        textDecoration: a.completed ? 'line-through' : 'none',
                        color: a.completed ? '#555548' : '#e8e4d0'
                      }}>{a.task}</p>
                      <div style={s.actionMeta}>
                        {a.owner && a.owner !== 'Unassigned' && (
                          <span style={s.owner}>{a.owner}</span>
                        )}
                        {a.deadline && (
                          <span style={{...s.deadline, color: deadlineColor(a.deadline)}}>
                            {deadlineLabel(a.deadline)}
                          </span>
                        )}
                      </div>
                    </div>
                  </li>
                ))}
              </ul>
            )}
          </div>
        )}

        {/* DECISIONS */}
        {tab === 'decisions' && (
          <div style={s.section}>
            {decisions.length === 0 ? (
              <p style={s.empty}>No decisions extracted</p>
            ) : (
              <ul style={s.decisionList}>
                {decisions.map((d, i) => (
                  <li key={i} style={s.decisionRow}>
                    <span style={s.decisionN}>{String(i+1).padStart(2,'0')}</span>
                    <p style={s.decisionText}>{d}</p>
                  </li>
                ))}
              </ul>
            )}
          </div>
        )}

        {/* TRANSCRIPT */}
        {tab === 'transcript' && (
          <div style={s.section}>
            {meeting.transcript ? (
              <pre style={s.transcript}>{meeting.transcript}</pre>
            ) : (
              <p style={s.empty}>Transcript not available</p>
            )}
          </div>
        )}

        {/* FOLLOW-UPS */}
        {tab === 'followups' && (
          <div style={s.section}>
            {followUps.length === 0 ? (
              <p style={s.empty}>No follow-up items</p>
            ) : (
              <ul style={s.decisionList}>
                {followUps.map((f, i) => (
                  <li key={i} style={s.decisionRow}>
                    <span style={s.decisionN}>{String(i+1).padStart(2,'0')}</span>
                    <p style={s.decisionText}>{f}</p>
                  </li>
                ))}
              </ul>
            )}
          </div>
        )}

      </main>
    </div>
  )
}

const fonts = `
  @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=DM+Mono:wght@300;400&display=swap');
  *{box-sizing:border-box;margin:0;padding:0;}
  body{background:#0c0c09;}
  @keyframes spin{to{transform:rotate(360deg)}}
  @keyframes fadeUp{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:translateY(0)}}
  li[style*='cursor']:hover{background:#1a1a12 !important;}
`

const s = {
  root:     {minHeight:'100vh', background:'#0c0c09',
             fontFamily:"'DM Mono',monospace", color:'#f0ece0'},
  spinner:  {width:24, height:24, border:'2px solid #2a2a20',
             borderTopColor:'#c8f04a', borderRadius:'50%'},

  hdr:      {background:'#0f0f0c', borderBottom:'1px solid #2a2a20',
             padding:'0 40px', height:54,
             display:'flex', alignItems:'center', justifyContent:'space-between',
             position:'sticky', top:0, zIndex:100},
  backBtn:  {background:'none', border:'1px solid #2a2a20', borderRadius:3,
             padding:'6px 14px', color:'#8a8a74', fontSize:10,
             letterSpacing:'0.1em', cursor:'pointer',
             fontFamily:"'DM Mono',monospace"},
  hdrMeta:  {display:'flex', alignItems:'center', gap:16},
  statusDot:{fontSize:10, letterSpacing:'0.08em', color:'#c8f04a'},
  hdrDate:  {fontSize:10, letterSpacing:'0.06em', color:'#555548'},

  hero:     {padding:'40px 40px 32px', borderBottom:'1px solid #1a1a14',
             animation:'fadeUp 0.4s ease both'},
  heroTitle:{fontFamily:"'Playfair Display',serif", fontSize:'clamp(24px,4vw,42px)',
             fontWeight:700, color:'#f0ece0', letterSpacing:'-0.5px', marginBottom:14},
  heroSummary:{fontSize:13, color:'#8a8a74', lineHeight:1.7, maxWidth:700,
               marginBottom:24, letterSpacing:'0.02em'},

  progressWrap:{maxWidth:500},
  progressMeta:{display:'flex', justifyContent:'space-between', marginBottom:8},
  progressLabel:{fontSize:9, letterSpacing:'0.15em', color:'#555548', textTransform:'uppercase'},
  progressCount:{fontSize:10, color:'#c8f04a', letterSpacing:'0.06em'},
  progressTrack:{height:3, background:'#1a1a14', borderRadius:2},
  progressFill: {height:'100%', background:'#c8f04a', borderRadius:2,
                 transition:'width 0.5s ease'},

  tabBar:   {display:'flex', gap:0, borderBottom:'1px solid #1a1a14',
             padding:'0 40px', background:'#0f0f0c'},
  tab:      {background:'none', border:'none', borderBottom:'2px solid transparent',
             padding:'14px 20px', color:'#555548', fontSize:10,
             letterSpacing:'0.1em', cursor:'pointer',
             fontFamily:"'DM Mono',monospace", textTransform:'uppercase',
             transition:'color 0.15s, border-color 0.15s'},
  tabActive:{color:'#c8f04a', borderBottomColor:'#c8f04a'},

  main:     {padding:'32px 40px', maxWidth:800, animation:'fadeUp 0.4s ease 0.1s both'},
  section:  {},
  empty:    {fontSize:12, color:'#444438', letterSpacing:'0.05em', padding:'32px 0'},

  actionList:{listStyle:'none', display:'flex', flexDirection:'column', gap:6},
  actionRow: {display:'flex', alignItems:'flex-start', gap:14,
              background:'#111108', border:'1px solid #1e1e14',
              borderRadius:6, padding:'14px 16px', cursor:'pointer',
              transition:'background 0.15s, border-color 0.15s'},
  checkbox:  {width:18, height:18, border:'1px solid #3a3a2e', borderRadius:3,
              flexShrink:0, marginTop:1, display:'flex',
              alignItems:'center', justifyContent:'center',
              transition:'background 0.15s, border-color 0.15s'},
  checkboxDone:{background:'#c8f04a', borderColor:'#c8f04a'},
  checkmark: {fontSize:10, color:'#0c0c09', fontWeight:700},
  actionBody:{flex:1},
  actionTask:{fontSize:13, color:'#e8e4d0', marginBottom:6, lineHeight:1.5},
  actionMeta:{display:'flex', gap:12, alignItems:'center'},
  owner:     {fontSize:10, color:'#6b7260', letterSpacing:'0.06em'},
  deadline:  {fontSize:10, letterSpacing:'0.06em'},

  decisionList:{listStyle:'none', display:'flex', flexDirection:'column', gap:8},
  decisionRow: {display:'flex', gap:16, alignItems:'flex-start',
                padding:'14px 16px', background:'#111108',
                border:'1px solid #1e1e14', borderRadius:6},
  decisionN:   {fontFamily:"'Playfair Display',serif", fontSize:20, fontWeight:700,
                color:'#2a2a22', lineHeight:1, flexShrink:0, marginTop:2},
  decisionText:{fontSize:13, color:'#a8a890', lineHeight:1.6, letterSpacing:'0.02em'},

  transcript:  {fontSize:11, color:'#6b7260', lineHeight:1.8, letterSpacing:'0.03em',
                whiteSpace:'pre-wrap', background:'#111108',
                border:'1px solid #1e1e14', borderRadius:6,
                padding:'20px', maxHeight:500, overflowY:'auto'},
}
