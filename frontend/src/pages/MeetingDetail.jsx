import React, { useState, useEffect } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { checkSession } from '../utils/auth.js'
import { getMeeting, updateAction } from '../utils/api.js'
import {
  PieChart, Pie, Cell, ResponsiveContainer,
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ReferenceLine
} from 'recharts'

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
  const dl = dlInfo(action.deadline)
  if (!action.owner || action.owner === 'Unassigned') return { label: 'HIGH RISK', color: '#e87a6a', bg: 'rgba(232,122,106,0.12)' }
  if (!action.deadline) return { label: 'MEDIUM RISK', color: '#e8c06a', bg: 'rgba(232,192,106,0.12)' }
  if (dl && dl.days < 0) return { label: 'OVERDUE', color: '#e87a6a', bg: 'rgba(232,122,106,0.12)' }
  if (dl && dl.days <= 2) return { label: 'HIGH RISK', color: '#e87a6a', bg: 'rgba(232,122,106,0.12)' }
  return null
}

function calcHealthScore(actions, decisions) {
  let score = 0
  const hasDecisions = decisions.length >= 3 ? 3 : decisions.length
  const allOwners = actions.length > 0 && actions.every(a => a.owner && a.owner !== 'Unassigned') ? 2 : 1
  const allDeadlines = actions.length > 0 && actions.every(a => a.deadline) ? 2 : 1
  const balanced = 2
  const timebonus = 1
  score = hasDecisions + allOwners + allDeadlines + balanced + timebonus
  return Math.min(score, 10)
}

const SPEAKERS = [
  { name: 'Ashhar', color: '#c8f04a', pct: 42 },
  { name: 'Priya',  color: '#e8c06a', pct: 35 },
  { name: 'Zara',   color: '#6ab4e8', pct: 23 },
]

const SENTIMENT = [
  { t: '0:00', Ashhar: 65, Priya: 60, Zara: 58 },
  { t: '5:00', Ashhar: 62, Priya: 55, Zara: 70 },
  { t: '10:00', Ashhar: 48, Priya: 42, Zara: 45 },
  { t: '15:00', Ashhar: 38, Priya: 35, Zara: 40 },
  { t: '20:00', Ashhar: 55, Priya: 58, Zara: 52 },
  { t: '25:00', Ashhar: 72, Priya: 75, Zara: 68 },
  { t: '30:00', Ashhar: 85, Priya: 82, Zara: 80 },
]

const CustomDot = ({ cx, cy, stroke }) => (
  <circle cx={cx} cy={cy} r={3} fill={stroke} stroke="none" />
)

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
  const health    = calcHealthScore(actions, decisions)
  const atRisk    = actions.filter(a => getRiskBadge(a)).length

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
              <span style={s.healthNum}>{health}.6</span>
              <span style={s.healthDenom}>/10</span>
            </div>
            <div style={s.healthDelta}>↑ +1.2 from last meeting</div>
            <div style={s.healthSubScores}>
              {[
                { l: 'Decision Clarity', v: 9.1 },
                { l: 'Participation',    v: 7.8 },
                { l: 'Ownership',        v: 8.9 },
              ].map(({ l, v }) => (
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

      {/* CHARTS ROW */}
      <div style={s.chartsRow}>

        {/* DONUT — Speaking Time */}
        <div style={s.chartCard}>
          <p style={s.chartLabel}>SPEAKING TIME</p>
          <div style={{ display:'flex', alignItems:'center', gap:24 }}>
            <PieChart width={120} height={120}>
              <Pie data={SPEAKERS} dataKey="pct" innerRadius={36} outerRadius={56}
                paddingAngle={3} startAngle={90} endAngle={-270} stroke="none">
                {SPEAKERS.map((sp, i) => <Cell key={i} fill={sp.color} />)}
              </Pie>
            </PieChart>
            <div style={{ display:'flex', flexDirection:'column', gap:10 }}>
              {SPEAKERS.map(sp => (
                <div key={sp.name} style={{ display:'flex', alignItems:'center', gap:8 }}>
                  <div style={{ width:8, height:8, borderRadius:'50%', background:sp.color, flexShrink:0 }}/>
                  <div style={{ display:'flex', flexDirection:'column' }}>
                    <span style={{ fontSize:11, color:'#e8e4d0', letterSpacing:'0.04em' }}>{sp.name}</span>
                    <span style={{ fontSize:10, color:'#555548' }}>{sp.pct}%</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* SENTIMENT TIMELINE */}
        <div style={{ ...s.chartCard, flex:2 }}>
          <p style={s.chartLabel}>MEETING ENERGY OVER TIME</p>
          <ResponsiveContainer width="100%" height={120}>
            <LineChart data={SENTIMENT} margin={{ top:4, right:8, left:-20, bottom:0 }}>
              <CartesianGrid stroke="#1e1e16" strokeDasharray="3 3" vertical={false}/>
              <XAxis dataKey="t" tick={{ fontSize:9, fill:'#555548', fontFamily:"'DM Mono',monospace" }}
                axisLine={false} tickLine={false}/>
              <YAxis domain={[0,100]} tick={{ fontSize:9, fill:'#555548' }} axisLine={false} tickLine={false}/>
              <ReferenceLine y={50} stroke="#2a2a20" strokeDasharray="4 4"/>
              <Tooltip
                contentStyle={{ background:'#141410', border:'1px solid #2a2a20',
                  borderRadius:4, fontSize:10, fontFamily:"'DM Mono',monospace", color:'#e8e4d0' }}
                labelStyle={{ color:'#555548', marginBottom:4 }}
              />
              {SPEAKERS.map(sp => (
                <Line key={sp.name} type="monotone" dataKey={sp.name}
                  stroke={sp.color} strokeWidth={1.5} dot={<CustomDot/>} activeDot={{ r:4 }}/>
              ))}
            </LineChart>
          </ResponsiveContainer>
          <div style={{ display:'flex', gap:16, marginTop:8 }}>
            {SPEAKERS.map(sp => (
              <span key={sp.name} style={{ fontSize:9, color:sp.color, letterSpacing:'0.08em' }}>
                ── {sp.name}
              </span>
            ))}
          </div>
        </div>

        {/* AI INSIGHTS */}
        <div style={{ ...s.chartCard, flex:1.2 }}>
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
                            <span style={{ fontSize:9, letterSpacing:'0.08em', color:risk.color,
                              background:risk.bg, border:`1px solid ${risk.color}40`,
                              borderRadius:3, padding:'2px 6px' }}>
                              {risk.label}
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
}
