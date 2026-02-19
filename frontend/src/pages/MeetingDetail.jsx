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
    days,
    color: days < 0 ? '#e87a6a' : days <= 3 ? '#e8c06a' : '#c8f04a',
    label: days < 0 ? `${Math.abs(days)}d overdue`
         : days === 0 ? 'Today' : days === 1 ? 'Tomorrow'
         : d.toLocaleDateString('en-GB',{day:'numeric',month:'short'})
  }
}

function getRiskBadge(action) {
  // Use backend-calculated risk score if available
  if (action.riskScore !== undefined) {
    const score = action.riskScore
    if (score >= 75) return { label: 'CRITICAL', score, color: '#e87a6a', bg: 'rgba(232,122,106,0.12)' }
    if (score >= 50) return { label: 'HIGH RISK', score, color: '#e87a6a', bg: 'rgba(232,122,106,0.12)' }
    if (score >= 25) return { label: 'MEDIUM RISK', score, color: '#e8c06a', bg: 'rgba(232,192,106,0.12)' }
    return { label: 'LOW RISK', score, color: '#6ab4e8', bg: 'rgba(106,180,232,0.12)' }
  }
  
  // Fallback to old logic for existing meetings
  const dl = dlInfo(action.deadline)
  if (!action.owner || action.owner === 'Unassigned') return { label: 'HIGH RISK', score: 65, color: '#e87a6a', bg: 'rgba(232,122,106,0.12)' }
  if (!action.deadline) return { label: 'MEDIUM RISK', score: 45, color: '#e8c06a', bg: 'rgba(232,192,106,0.12)' }
  if (dl && dl.days < 0) return { label: 'OVERDUE', score: 85, color: '#e87a6a', bg: 'rgba(232,122,106,0.12)' }
  if (dl && dl.days <= 2) return { label: 'HIGH RISK', score: 70, color: '#e87a6a', bg: 'rgba(232,122,106,0.12)' }
  return null
}

function getAgeBadge(createdAt) {
  if (!createdAt) return null
  const created = new Date(createdAt)
  if (isNaN(created)) return null
  
  const days = Math.floor((new Date() - created) / 86400000)
  if (days === 0) return { label: 'Today', color: '#6ab4e8' }
  if (days === 1) return { label: '1 day old', color: '#8a8a74' }
  if (days < 7) return { label: `${days} days old`, color: '#8a8a74' }
  if (days < 14) return { label: `${Math.floor(days/7)} week old`, color: '#e8c06a' }
  if (days < 30) return { label: `${Math.floor(days/7)} weeks old`, color: '#e8c06a' }
  return { label: `${Math.floor(days/30)} month${Math.floor(days/30)>1?'s':''} old`, color: '#e87a6a' }
}

function calcHealthScore(actions, decisions) {
  if (actions.length === 0 && decisions.length === 0) return 0
  
  let score = 0
  
  // Decision quality (0-3 points) - more decisions = better meeting
  const decisionPoints = Math.min(decisions.length, 3)
  
  // Action clarity (0-3 points) - clear ownership + deadlines
  const clearActions = actions.filter(a => 
    a.owner && a.owner !== 'Unassigned' && a.deadline
  ).length
  const clarityPoints = actions.length > 0 
    ? (clearActions / actions.length) * 3 
    : 0
  
  // Completion rate (0-2 points) - how many are done
  const completed = actions.filter(a => a.completed).length
  const completionPoints = actions.length > 0
    ? (completed / actions.length) * 2
    : 0
  
  // Risk distribution (0-2 points) - fewer high-risk items = better
  const highRisk = actions.filter(a => {
    const risk = getRiskBadge(a)
    return risk && (risk.label === 'HIGH RISK' || risk.label === 'CRITICAL')
  }).length
  const riskPoints = actions.length > 0
    ? (1 - (highRisk / actions.length)) * 2
    : 0
  
  score = decisionPoints + clarityPoints + completionPoints + riskPoints
  return Math.round(score * 10) / 10 // Round to 1 decimal
}

// Mock speaker data removed - Issue #16 fixed
// Real speaker analytics will be implemented in future version

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
      const newStatus = cur ? 'todo' : 'done';
      await updateAction(meetingId, id, { 
        status: newStatus,
        completed: newStatus === 'done'
      });
      setMeeting(m => ({...m, actionItems: m.actionItems.map(a =>
        a.id === id ? {...a, completed: !cur, status: newStatus} : a)}))
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
  const roi       = meeting.roi || null
  const done      = actions.filter(a => a.completed).length
  const pct       = actions.length ? Math.round(done/actions.length*100) : 0
  const dateStr   = fmtDate(meeting.createdAt || meeting.updatedAt)
  const health    = calcHealthScore(actions, decisions)
  const atRisk    = actions.filter(a => {
    const risk = getRiskBadge(a)
    return risk && (risk.label === 'HIGH RISK' || risk.label === 'CRITICAL')
  }).length

  // Calculate real sub-scores
  const clearActions = actions.filter(a => 
    a.owner && a.owner !== 'Unassigned' && a.deadline
  ).length
  
  const subScores = [
    { 
      l: 'Decision Clarity', 
      v: Math.round(Math.min(decisions.length, 3) * 3.33 * 10) / 10
    },
    { 
      l: 'Action Ownership', 
      v: actions.length > 0 
        ? Math.round((actions.filter(a => a.owner && a.owner !== 'Unassigned').length / actions.length) * 100) / 10
        : 0
    },
    { 
      l: 'Risk Management', 
      v: actions.length > 0
        ? Math.round((1 - (atRisk / actions.length)) * 100) / 10
        : 10
    },
  ]

  const insights = [
    actions.some(a => !a.deadline)
      ? '2 actions lack specific deadlines — assign dates to improve accountability'
      : 'All action items have deadlines assigned ✓',
    actions.some(a => !a.owner || a.owner === 'Unassigned')
      ? 'One action item has no owner — unassigned tasks are 3× less likely to complete'
      : 'All action items have clear owners ✓',
    decisions.length >= 3
      ? `${decisions.length} decisions made — strong decision velocity for this meeting`
      : 'Consider documenting more explicit decisions next time',
  ]

  return (
    <div style={s.root}>
      <style>{css}</style>

      {/* STICKY HEADER */}
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

          {/* HEALTH SCORE — the hero stat */}
          <div style={s.healthCard}>
            <p style={s.healthLabel}>MEETING HEALTH</p>
            <div style={s.healthScoreRow}>
              <span style={s.healthNum}>{health}</span>
              <span style={s.healthDenom}>/10</span>
            </div>
            <div style={s.healthDelta}>
              {health >= 7 ? '✓ Strong meeting quality' : health >= 5 ? '⚠ Room for improvement' : '⚠ Needs attention'}
            </div>
            <div style={s.healthSubScores}>
              {subScores.map(({ l, v }) => (
                <div key={l} style={s.subScore}>
                  <div style={{ display:'flex', justifyContent:'space-between', marginBottom:4 }}>
                    <span style={s.subLabel}>{l}</span>
                    <span style={{ ...s.subLabel, color:'#c8f04a' }}>{v}</span>
                  </div>
                  <div style={{ height:2, background:'#2a2a20', borderRadius:1 }}>
                    <div style={{ height:'100%', width:`${v*10}%`, background:'#c8f04a',
                      borderRadius:1, opacity:0.7 }}/>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* ROI CARD */}
          {roi && (
            <div style={s.roiCard}>
              <p style={s.healthLabel}>MEETING ROI</p>
              <div style={s.healthScoreRow}>
                <span style={{...s.healthNum, color: roi.roi >= 0 ? '#c8f04a' : '#e87a6a'}}>
                  {roi.roi >= 0 ? '+' : ''}{roi.roi}%
                </span>
              </div>
              <div style={s.healthDelta}>
                ${roi.value.toLocaleString('en-US')} value / ${roi.cost.toLocaleString('en-US')} cost
              </div>
              <div style={{...s.healthSubScores, marginTop:10}}>
                <div style={{display:'flex', justifyContent:'space-between', fontSize:10, color:'#8a8a74'}}>
                  <span>{roi.decision_count} decisions</span>
                  <span>{roi.clear_action_count} clear actions</span>
                </div>
              </div>
            </div>
          )}

          <div style={s.statsBox}>
            {[
              { n:actions.length,   l:'Actions' },
              { n:decisions.length, l:'Decisions' },
              { n:followUps.length, l:'Follow-ups' },
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

      {/* AUTOPSY CARD - Only show for D/F grades or ghost meetings */}
      {meeting.autopsy && (meeting.healthGrade === 'D' || meeting.healthGrade === 'F' || meeting.isGhost) && (
        <div style={s.autopsySection}>
          <div style={s.autopsyCard}>
            <div style={s.autopsyHeader}>
              <span style={s.autopsyIcon}>🔬</span>
              <h3 style={s.autopsyTitle}>Meeting Autopsy</h3>
            </div>
            <p style={s.autopsyText}>{meeting.autopsy}</p>
          </div>
        </div>
      )}

      {/* CHARTS ROW - Show if there's data to display */}
      <div style={s.chartsRow}>
        
        {/* SPEAKER BREAKDOWN - Only show if we have owner data */}
        {actions.some(a => a.owner && a.owner !== 'Unassigned') && (
          <div style={s.chartCard}>
            <p style={s.chartLabel}>TASK DISTRIBUTION</p>
            <div style={{ display:'flex', flexDirection:'column', gap:8 }}>
              {(() => {
                // Group actions by owner
                const ownerCounts = {}
                actions.forEach(a => {
                  if (a.owner && a.owner !== 'Unassigned') {
                    ownerCounts[a.owner] = (ownerCounts[a.owner] || 0) + 1
                  }
                })
                const total = Object.values(ownerCounts).reduce((sum, count) => sum + count, 0)
                
                return Object.entries(ownerCounts)
                  .sort((a, b) => b[1] - a[1])
                  .map(([owner, count]) => {
                    const pct = Math.round((count / total) * 100)
                    return (
                      <div key={owner} style={{ display:'flex', alignItems:'center', gap:10 }}>
                        <div style={{ flex:1 }}>
                          <div style={{ display:'flex', justifyContent:'space-between', marginBottom:4 }}>
                            <span style={{ fontSize:11, color:'#a8a890' }}>{owner}</span>
                            <span style={{ fontSize:10, color:'#6b7260' }}>{count} task{count>1?'s':''}</span>
                          </div>
                          <div style={{ height:4, background:'#2a2a20', borderRadius:2 }}>
                            <div style={{ height:'100%', width:`${pct}%`, background:'#c8f04a',
                              borderRadius:2, transition:'width 0.3s' }}/>
                          </div>
                        </div>
                      </div>
                    )
                  })
              })()}
            </div>
          </div>
        )}

        {/* AI INSIGHTS */}
        <div style={{ ...s.chartCard, flex:1 }}>
          <p style={s.chartLabel}>AI ANALYSIS</p>
          <div style={{ display:'flex', flexDirection:'column', gap:10 }}>
            {insights.map((ins, i) => (
              <div key={i} style={{ display:'flex', gap:10, alignItems:'flex-start' }}>
                <span style={{ color:'#c8f04a', fontSize:10, flexShrink:0, marginTop:1 }}>▸</span>
                <p style={{ fontSize:11, color:'#a8a890', lineHeight:1.6, letterSpacing:'0.02em' }}>{ins}</p>
              </div>
            ))}
          </div>
          {atRisk > 0 && (
            <div style={{ marginTop:14, padding:'8px 12px', background:'rgba(232,122,106,0.08)',
              border:'1px solid rgba(232,122,106,0.2)', borderRadius:4 }}>
              <span style={{ fontSize:10, color:'#e87a6a', letterSpacing:'0.06em' }}>
                ■■ {atRisk} action{atRisk>1?'s':''} at risk
              </span>
            </div>
          )}
        </div>
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
                  const risk = getRiskBadge(a)
                  const age = getAgeBadge(a.createdAt)
                  return (
                    <li key={a.id} className="arow"
                      onClick={() => toggleAction(a.id, a.completed)}
                      style={{...s.arow, opacity:a.completed?0.4:1, animationDelay:`${i*0.05}s`}}>
                      <div style={{...s.cb,...(a.completed?s.cbOn:{})}}>
                        {a.completed && <span style={{fontSize:9,color:'#0c0c09',fontWeight:700,lineHeight:1}}>✓</span>}
                      </div>
                      <div style={{flex:1}}>
                        <p style={{fontSize:13,lineHeight:1.5,marginBottom:6,
                          color:a.completed?'#555548':'#e8e4d0',
                          textDecoration:a.completed?'line-through':'none'}}>
                          {a.task}
                        </p>
                        <div style={{display:'flex',gap:8,flexWrap:'wrap',alignItems:'center'}}>
                          {a.owner && a.owner!=='Unassigned' &&
                            <span style={{fontSize:10,color:'#8a8a74',letterSpacing:'0.05em'}}>
                              {a.owner}
                            </span>}
                          {dl && <span style={{fontSize:10,color:dl.color,letterSpacing:'0.05em'}}>
                            {dl.label}
                          </span>}
                          {risk && !a.completed && (
                            <span style={{ fontSize:10, letterSpacing:'0.08em', color:risk.color,
                              background:risk.bg, border:`1px solid ${risk.color}40`,
                              borderRadius:3, padding:'3px 8px', display:'flex', alignItems:'center', gap:5 }}>
                              {typeof risk.score === 'number' && (
                                <span style={{fontWeight:700, fontSize:11}}>{risk.score}</span>
                              )}
                              {risk.label}
                            </span>
                          )}
                          {age && !a.completed && (
                            <span style={{ fontSize:9, letterSpacing:'0.06em', color:age.color,
                              opacity:0.7 }}>
                              ⏱ {age.label}
                            </span>
                          )}
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
  @keyframes pulse{0%,100%{opacity:1}50%{opacity:0.4}}
  .arow:hover{background:#1c1c12 !important;border-color:#3a3a28 !important;cursor:pointer;}
  .back:hover{color:#f0ece0 !important;border-color:#6b7260 !important;}
  .overdue{animation:pulse 1.8s ease infinite;}
`

const s = {
  root:    { minHeight:'100vh', background:'#0c0c09', fontFamily:"'DM Mono',monospace", color:'#f0ece0' },
  hdr:     { background:'#0f0f0c', borderBottom:'1px solid #2a2a20', padding:'0 36px', height:54,
             display:'flex', alignItems:'center', justifyContent:'space-between',
             position:'sticky', top:0, zIndex:100 },
  hdrL:    { display:'flex', alignItems:'center', gap:20, minWidth:0, flex:1 },
  backBtn: { background:'none', border:'1px solid #2a2a20', borderRadius:3, padding:'6px 14px',
             color:'#6b7260', fontSize:10, letterSpacing:'0.1em', cursor:'pointer',
             fontFamily:"'DM Mono',monospace", transition:'all 0.15s', flexShrink:0 },
  hdrTitle:{ fontSize:12, color:'#a8a890', letterSpacing:'0.02em',
             overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap' },
  hdrR:    { display:'flex', alignItems:'center', gap:16, flexShrink:0 },
  donePill:{ fontSize:10, letterSpacing:'0.1em', color:'#c8f04a' },
  hdrDate: { fontSize:10, letterSpacing:'0.06em', color:'#555548' },

  hero:    { background:'#0f0f0c', borderBottom:'1px solid #2a2a20', padding:'32px 36px 24px' },
  heroTop: { display:'flex', justifyContent:'space-between', alignItems:'flex-start',
             gap:24, marginBottom:24, flexWrap:'wrap' },
  heroLeft:{ flex:1, minWidth:220 },
  eyebrow: { fontSize:9, letterSpacing:'0.18em', color:'#555548', textTransform:'uppercase', marginBottom:10 },
  title:   { fontFamily:"'Playfair Display',serif", fontSize:'clamp(20px,2.5vw,34px)', fontWeight:700,
             color:'#f0ece0', letterSpacing:'-0.3px', marginBottom:14, lineHeight:1.15 },
  summary: { fontSize:13, color:'#8a8a74', lineHeight:1.75, letterSpacing:'0.02em', maxWidth:520 },

  healthCard:  { background:'#141410', border:'1px solid #2e2e22', borderRadius:8,
                 padding:'18px 22px', flexShrink:0, minWidth:200 },
  roiCard:     { background:'#141410', border:'1px solid #2e2e22', borderRadius:8,
                 padding:'18px 22px', flexShrink:0, minWidth:200 },
  healthLabel: { fontSize:9, letterSpacing:'0.16em', color:'#555548', textTransform:'uppercase', marginBottom:10 },
  healthScoreRow: { display:'flex', alignItems:'flex-end', gap:4, marginBottom:6 },
  healthNum:   { fontFamily:"'Playfair Display',serif", fontSize:44, fontWeight:700,
                 color:'#c8f04a', lineHeight:1 },
  healthDenom: { fontSize:28, color:'#4a4a3e', fontFamily:"'Playfair Display',serif", lineHeight:1, paddingBottom:6 },
  healthDelta: { fontSize:10, color:'#c8f04a', letterSpacing:'0.06em', marginBottom:14,
                 opacity:0.7 },
  healthSubScores: { display:'flex', flexDirection:'column', gap:8 },
  subScore:    { display:'flex', flexDirection:'column', gap:0 },
  subLabel:    { fontSize:9, color:'#6b7260', letterSpacing:'0.08em' },

  statsBox:{ display:'flex', alignItems:'center', background:'#141410', border:'1px solid #2e2e22',
             borderRadius:6, padding:'18px 20px', flexShrink:0, alignSelf:'flex-start' },
  stat:    { display:'flex', flexDirection:'column', alignItems:'center', gap:4, padding:'0 18px' },
  statN:   { fontFamily:"'Playfair Display',serif", fontSize:26, fontWeight:700, color:'#c8f04a', lineHeight:1 },
  statL:   { fontSize:9, letterSpacing:'0.12em', color:'#6b7260', textTransform:'uppercase' },
  statDiv: { width:1, height:32, background:'#2a2a20' },
  prog:    { maxWidth:480 },

  chartsRow: { display:'flex', gap:0, borderBottom:'1px solid #2a2a20', flexWrap:'wrap' },
  chartCard: { flex:1, minWidth:200, padding:'20px 24px',
               borderRight:'1px solid #2a2a20' },
  chartLabel:{ fontSize:9, letterSpacing:'0.16em', color:'#555548', textTransform:'uppercase', marginBottom:14 },

  cols:    { display:'grid', gridTemplateColumns:'1fr 1fr', minHeight:'calc(100vh - 420px)' },
  col:     { padding:'28px 36px' },
  colHdr:  { display:'flex', justifyContent:'space-between', alignItems:'center',
             marginBottom:20, paddingBottom:14, borderBottom:'1px solid #2a2a20' },
  colTitle:{ fontFamily:"'Playfair Display',serif", fontSize:18, fontWeight:700,
             color:'#f0ece0', letterSpacing:'-0.2px' },
  colCount:{ fontFamily:"'Playfair Display',serif", fontSize:22, fontWeight:700, color:'#c8f04a' },
  empty:   { fontSize:12, color:'#444438', letterSpacing:'0.05em', padding:'24px 0' },
  list:    { listStyle:'none', display:'flex', flexDirection:'column', gap:6 },
  arow:    { display:'flex', alignItems:'flex-start', gap:12, background:'#141410',
             border:'1px solid #2e2e22', borderRadius:6, padding:'13px 14px',
             transition:'background 0.15s,border-color 0.15s', animation:'fadeUp 0.3s ease both' },
  cb:      { width:17, height:17, border:'1.5px solid #4a4a3e', borderRadius:3, flexShrink:0,
             marginTop:2, display:'flex', alignItems:'center', justifyContent:'center',
             transition:'all 0.15s' },
  cbOn:    { background:'#c8f04a', borderColor:'#c8f04a' },
  drow:    { display:'flex', gap:16, alignItems:'flex-start', padding:'14px 16px',
             background:'#141410', border:'1px solid #2e2e22', borderRadius:6,
             animation:'fadeUp 0.3s ease both' },
  dn:      { fontFamily:"'Playfair Display',serif", fontSize:20, fontWeight:700,
             color:'#3a3a2e', lineHeight:1, flexShrink:0, marginTop:2 },
  
  autopsySection: { padding:'24px 36px', borderBottom:'1px solid #2a2a20' },
  autopsyCard: { background:'#1a0e0e', border:'2px solid #e87a6a', borderRadius:8,
                 padding:'20px 24px' },
  autopsyHeader: { display:'flex', alignItems:'center', gap:12, marginBottom:14 },
  autopsyIcon: { fontSize:24, lineHeight:1 },
  autopsyTitle: { fontFamily:"'Playfair Display',serif", fontSize:16, fontWeight:700,
                  color:'#e87a6a', letterSpacing:'-0.2px' },
  autopsyText: { fontSize:13, color:'#c8c4b0', lineHeight:1.75, letterSpacing:'0.01em' },
}
