import React, { useState, useEffect } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { checkSession } from '../utils/auth.js'
import { getMeeting, updateAction } from '../utils/api.js'

function fmtDate(iso) {
  if (!iso) return null
  const d = new Date(iso)
  return isNaN(d) ? null : d.toLocaleDateString('en-GB',{day:'numeric',month:'long',year:'numeric'})
}

function dlInfo(dl) {
  if (!dl) return null
  const d = new Date(dl)
  if (isNaN(d)) return null
  const days = Math.ceil((d - new Date()) / 86400000)
  return {
    color: days < 0 ? '#e87a6a' : days <= 3 ? '#e8c06a' : '#c8f04a',
    label: days < 0 ? `${Math.abs(days)}d overdue`
         : days === 0 ? 'Today' : days === 1 ? 'Tomorrow'
         : d.toLocaleDateString('en-GB',{day:'numeric',month:'short'})
  }
}

export default function MeetingDetail() {
  const { meetingId } = useParams()
  const navigate = useNavigate()
  const [meeting, setMeeting] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error,   setError]   = useState('')

  useEffect(() => {
    checkSession().then(u => { if (!u) navigate('/login') })
    getMeeting(meetingId)
      .then(setMeeting)
      .catch(() => setError('Failed to load meeting'))
      .finally(() => setLoading(false))
  }, [])

  async function toggleAction(id, cur) {
    try {
      await updateAction(meetingId, id, !cur)
      setMeeting(m => ({...m, actionItems: m.actionItems.map(a =>
        a.id === id ? {...a, completed: !cur} : a)}))
    } catch { setError('Failed to update') }
  }

  if (loading) return (
    <div style={{minHeight:'100vh',background:'#0c0c09',display:'flex',
      alignItems:'center',justifyContent:'center'}}>
      <style>{css}</style>
      <div style={{width:22,height:22,border:'2px solid #2a2a20',
        borderTopColor:'#c8f04a',borderRadius:'50%',animation:'spin 1s linear infinite'}}/>
    </div>
  )

  if (error || !meeting) return (
    <div style={{minHeight:'100vh',background:'#0c0c09',display:'flex',
      alignItems:'center',justifyContent:'center',fontFamily:"'DM Mono',monospace"}}>
      <style>{css}</style>
      <div style={{textAlign:'center'}}>
        <p style={{color:'#e87a6a',marginBottom:16,fontSize:13}}>{error||'Meeting not found'}</p>
        <button onClick={() => navigate('/')} style={s.backBtn}>← Back</button>
      </div>
    </div>
  )

  const actions   = meeting.actionItems || []
  const decisions = meeting.decisions   || []
  const followUps = meeting.followUps   || []
  const done      = actions.filter(a => a.completed).length
  const pct       = actions.length ? Math.round(done/actions.length*100) : 0
  const dateStr   = fmtDate(meeting.createdAt || meeting.updatedAt)

  return (
    <div style={s.root}>
      <style>{css}</style>

      {/* STICKY HEADER — always shows title */}
      <header style={s.hdr}>
        <div style={s.hdrL}>
          <button className="back" onClick={() => navigate('/')} style={s.backBtn}>← Meetings</button>
          <span style={s.hdrTitle}>{meeting.title}</span>
        </div>
        <div style={s.hdrR}>
          <span style={s.donePill}>● Done</span>
          {dateStr && <span style={s.hdrDate}>{dateStr}</span>}
        </div>
      </header>

      {/* HERO */}
      <div style={s.hero}>
        <div style={s.heroTop}>
          <div style={s.heroLeft}>
            <p style={s.eyebrow}>MEETING SUMMARY</p>
            <h1 style={s.title}>{meeting.title}</h1>
            {meeting.summary && <p style={s.summary}>{meeting.summary}</p>}
          </div>
          <div style={s.statsBox}>
            {[
              {n:actions.length,   l:'Actions'},
              {n:decisions.length, l:'Decisions'},
              {n:followUps.length, l:'Follow-ups'},
            ].map(({n,l},i) => (
              <React.Fragment key={l}>
                {i>0 && <div style={s.statDiv}/>}
                <div style={s.stat}>
                  <span style={s.statN}>{n}</span>
                  <span style={s.statL}>{l}</span>
                </div>
              </React.Fragment>
            ))}
          </div>
        </div>

        {actions.length > 0 && (
          <div style={s.prog}>
            <div style={{display:'flex',justifyContent:'space-between',marginBottom:8}}>
              <span style={{fontSize:9,letterSpacing:'0.14em',color:'#555548',textTransform:'uppercase'}}>
                Completion
              </span>
              <span style={{fontSize:10,letterSpacing:'0.06em'}}>
                <span style={{color:'#c8f04a'}}>{done}</span>
                <span style={{color:'#555548'}}>/{actions.length} · {pct}%</span>
              </span>
            </div>
            <div style={{height:3,background:'#1a1a14',borderRadius:2}}>
              <div style={{height:'100%',width:`${pct}%`,background:'#c8f04a',
                borderRadius:2,transition:'width 0.6s ease'}}/>
            </div>
          </div>
        )}
      </div>

      {/* TWO COLUMNS */}
      <div style={s.cols}>

        {/* LEFT — Actions */}
        <section style={s.col}>
          <div style={s.colHdr}>
            <h2 style={s.colTitle}>Action Items</h2>
            <span style={s.colCount}>{done}/{actions.length}</span>
          </div>
          {actions.length === 0
            ? <p style={s.empty}>No action items extracted</p>
            : <ul style={s.list}>
                {actions.map((a,i) => {
                  const dl = dlInfo(a.deadline)
                  return (
                    <li key={a.id} className="arow"
                      onClick={() => toggleAction(a.id, a.completed)}
                      style={{...s.arow,
                        opacity: a.completed ? 0.4 : 1,
                        animationDelay:`${i*0.05}s`}}>
                      <div style={{...s.cb,...(a.completed?s.cbOn:{})}}>
                        {a.completed && <span style={{fontSize:9,color:'#0c0c09',fontWeight:700,lineHeight:1}}>✓</span>}
                      </div>
                      <div style={{flex:1}}>
                        <p style={{fontSize:13,lineHeight:1.5,marginBottom:6,
                          color:a.completed?'#555548':'#e8e4d0',
                          textDecoration:a.completed?'line-through':'none'}}>
                          {a.task}
                        </p>
                        <div style={{display:'flex',gap:12,flexWrap:'wrap',alignItems:'center'}}>
                          {a.owner && a.owner!=='Unassigned' &&
                            <span style={{fontSize:10,color:'#8a8a74',letterSpacing:'0.05em'}}>
                              {a.owner}
                            </span>}
                          {dl && <span style={{fontSize:10,color:dl.color,letterSpacing:'0.05em',fontWeight:400}}>
                            {dl.label}
                          </span>}
                        </div>
                      </div>
                    </li>
                  )
                })}
              </ul>
          }
        </section>

        {/* RIGHT — Decisions + Follow-ups */}
        <section style={{...s.col, borderLeft:'1px solid #2a2a20'}}>

          <div style={s.colHdr}>
            <h2 style={s.colTitle}>Decisions</h2>
            <span style={s.colCount}>{decisions.length}</span>
          </div>
          {decisions.length === 0
            ? <p style={s.empty}>No decisions extracted</p>
            : <ul style={s.list}>
                {decisions.map((d,i) => (
                  <li key={i} style={{...s.drow,animationDelay:`${i*0.05}s`}}>
                    <span style={s.dn}>{String(i+1).padStart(2,'0')}</span>
                    <div style={{flex:1}}>
                      <div style={{width:20,height:2,background:'#c8f04a',marginBottom:10}}/>
                      <p style={{fontSize:13,color:'#c8c4b0',lineHeight:1.65,letterSpacing:'0.01em'}}>{d}</p>
                    </div>
                  </li>
                ))}
              </ul>
          }

          {followUps.length > 0 && (
            <>
              <div style={{...s.colHdr, marginTop:32}}>
                <h2 style={s.colTitle}>Follow-ups</h2>
                <span style={s.colCount}>{followUps.length}</span>
              </div>
              <ul style={s.list}>
                {followUps.map((f,i) => (
                  <li key={i} style={{...s.drow,animationDelay:`${i*0.05}s`}}>
                    <span style={{...s.dn,color:'#4a4a3e'}}>{String(i+1).padStart(2,'0')}</span>
                    <div style={{flex:1}}>
                      <div style={{width:20,height:2,background:'#4a4a3e',marginBottom:10}}/>
                      <p style={{fontSize:13,color:'#8a8a74',lineHeight:1.65,letterSpacing:'0.01em'}}>{f}</p>
                    </div>
                  </li>
                ))}
              </ul>
            </>
          )}

          {meeting.transcript && (
            <>
              <div style={{...s.colHdr, marginTop:32}}>
                <h2 style={s.colTitle}>Transcript</h2>
              </div>
              <pre style={{fontSize:11,color:'#6b7260',lineHeight:1.85,whiteSpace:'pre-wrap',
                background:'#111108',border:'1px solid #2a2a20',borderRadius:6,
                padding:'16px',maxHeight:280,overflowY:'auto',letterSpacing:'0.02em'}}>
                {meeting.transcript}
              </pre>
            </>
          )}
        </section>
      </div>
    </div>
  )
}

const css = `
  @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=DM+Mono:wght@300;400&display=swap');
  *{box-sizing:border-box;margin:0;padding:0;}
  body{background:#0c0c09;}
  @keyframes spin{to{transform:rotate(360deg)}}
  @keyframes fadeUp{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:translateY(0)}}
  .arow:hover{background:#1c1c12 !important;border-color:#3a3a28 !important;cursor:pointer;}
  .back:hover{color:#f0ece0 !important;border-color:#6b7260 !important;}
`

const s = {
  root:    {minHeight:'100vh',background:'#0c0c09',fontFamily:"'DM Mono',monospace",color:'#f0ece0'},

  /* sticky header with title */
  hdr:     {background:'#0f0f0c',borderBottom:'1px solid #2a2a20',padding:'0 36px',height:54,
            display:'flex',alignItems:'center',justifyContent:'space-between',
            position:'sticky',top:0,zIndex:100},
  hdrL:    {display:'flex',alignItems:'center',gap:20,minWidth:0,flex:1},
  backBtn: {background:'none',border:'1px solid #2a2a20',borderRadius:3,padding:'6px 14px',
            color:'#6b7260',fontSize:10,letterSpacing:'0.1em',cursor:'pointer',
            fontFamily:"'DM Mono',monospace",transition:'all 0.15s',flexShrink:0},
  hdrTitle:{fontSize:12,color:'#a8a890',letterSpacing:'0.02em',
            overflow:'hidden',textOverflow:'ellipsis',whiteSpace:'nowrap'},
  hdrR:    {display:'flex',alignItems:'center',gap:16,flexShrink:0},
  donePill:{fontSize:10,letterSpacing:'0.1em',color:'#c8f04a'},
  hdrDate: {fontSize:10,letterSpacing:'0.06em',color:'#555548'},

  /* hero */
  hero:    {background:'#0f0f0c',borderBottom:'1px solid #2a2a20',padding:'32px 36px 24px',},
  heroTop: {display:'flex',justifyContent:'space-between',alignItems:'flex-start',
            gap:32,marginBottom:24,flexWrap:'wrap'},
  heroLeft:{flex:1,minWidth:260},
  eyebrow: {fontSize:9,letterSpacing:'0.18em',color:'#555548',textTransform:'uppercase',marginBottom:10},
  title:   {fontFamily:"'Playfair Display',serif",fontSize:'clamp(22px,3vw,38px)',fontWeight:700,
            color:'#f0ece0',letterSpacing:'-0.3px',marginBottom:14,lineHeight:1.15},
  summary: {fontSize:13,color:'#8a8a74',lineHeight:1.75,letterSpacing:'0.02em',maxWidth:560},
  statsBox:{display:'flex',alignItems:'center',background:'#141410',border:'1px solid #2e2e22',
            borderRadius:6,padding:'18px 20px',flexShrink:0,alignSelf:'flex-start'},
  stat:    {display:'flex',flexDirection:'column',alignItems:'center',gap:4,padding:'0 18px'},
  statN:   {fontFamily:"'Playfair Display',serif",fontSize:26,fontWeight:700,color:'#c8f04a',lineHeight:1},
  statL:   {fontSize:9,letterSpacing:'0.12em',color:'#6b7260',textTransform:'uppercase'},
  statDiv: {width:1,height:32,background:'#2a2a20'},
  prog:    {maxWidth:480},

  /* columns */
  cols:    {display:'grid',gridTemplateColumns:'1fr 1fr',minHeight:'calc(100vh - 260px)'},
  col:     {padding:'28px 36px'},
  colHdr:  {display:'flex',justifyContent:'space-between',alignItems:'center',
            marginBottom:20,paddingBottom:14,borderBottom:'1px solid #2a2a20'},
  colTitle:{fontFamily:"'Playfair Display',serif",fontSize:18,fontWeight:700,
            color:'#f0ece0',letterSpacing:'-0.2px'},
  colCount:{fontFamily:"'Playfair Display',serif",fontSize:22,fontWeight:700,color:'#c8f04a'},
  empty:   {fontSize:12,color:'#444438',letterSpacing:'0.05em',padding:'24px 0'},
  list:    {listStyle:'none',display:'flex',flexDirection:'column',gap:6},

  arow:    {display:'flex',alignItems:'flex-start',gap:12,background:'#141410',
            border:'1px solid #2e2e22',borderRadius:6,padding:'13px 14px',
            transition:'background 0.15s,border-color 0.15s',
            animation:'fadeUp 0.3s ease both'},
  cb:      {width:17,height:17,border:'1.5px solid #4a4a3e',borderRadius:3,flexShrink:0,
            marginTop:2,display:'flex',alignItems:'center',justifyContent:'center',
            transition:'all 0.15s'},
  cbOn:    {background:'#c8f04a',borderColor:'#c8f04a'},

  drow:    {display:'flex',gap:16,alignItems:'flex-start',padding:'14px 16px',
            background:'#141410',border:'1px solid #2e2e22',borderRadius:6,
            animation:'fadeUp 0.3s ease both'},
  dn:      {fontFamily:"'Playfair Display',serif",fontSize:20,fontWeight:700,
            color:'#3a3a2e',lineHeight:1,flexShrink:0,marginTop:2},
}
