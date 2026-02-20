import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { logout, checkSession, getUser } from '../utils/auth.js'
import { getAllActions, checkDuplicate, updateAction } from '../utils/api.js'
import TeamSelector from '../components/TeamSelector.jsx'
import KanbanBoard from '../components/KanbanBoard.jsx'

const RISK_COLORS = {
  LOW:      '#c8f04a',
  MEDIUM:   '#e8c06a',
  HIGH:     '#e89a6a',
  CRITICAL: '#e87a6a',
}

function fmtDate(iso) {
  if (!iso) return 'No deadline'
  const d = new Date(iso)
  if (isNaN(d)) return 'No deadline'
  return d.toLocaleDateString('en-GB', {day:'numeric', month:'short', year:'numeric'})
}

function getDaysUntil(deadline) {
  if (!deadline) return null
  const now = new Date()
  const target = new Date(deadline)
  const diff = Math.ceil((target - now) / (1000 * 60 * 60 * 24))
  return diff
}

export default function ActionsOverview() {
  const navigate = useNavigate()
  const [user, setUser] = useState('')
  const [actions, setActions] = useState([])
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [statusFilter, setStatusFilter] = useState('all')
  const [ownerFilter, setOwnerFilter] = useState('')
  const [checkingDuplicates, setCheckingDuplicates] = useState(false)
  const [duplicateResults, setDuplicateResults] = useState(null)
  const [selectedTeamId, setSelectedTeamId] = useState(null)
  const [view, setView] = useState('list') // 'list' or 'kanban'

  useEffect(() => {
    checkSession().then(u => {
      if (!u) { navigate('/login'); return }
      setUser(getUser() || '')
      fetchActions()
    })
  }, [selectedTeamId])

  async function fetchActions() {
    try {
      const data = await getAllActions(null, null, selectedTeamId)
      setActions(data.actions || [])
      setStats(data.stats || {})
    } catch (e) {
      setError('Failed to load action items')
    } finally {
      setLoading(false)
    }
  }

  async function scanForDuplicates() {
    setCheckingDuplicates(true)
    setDuplicateResults(null)
    
    try {
      const incompleteActions = actions.filter(a => !a.completed)
      const duplicates = []
      
      for (const action of incompleteActions) {
        try {
          const result = await checkDuplicate(action.task)
          if (result.isDuplicate && result.similarity >= 85) {
            duplicates.push({
              action,
              ...result
            })
          }
        } catch (e) {
          console.error('Failed to check duplicate for:', action.task, e)
        }
      }
      
      setDuplicateResults({
        total: incompleteActions.length,
        duplicates,
        chronicBlockers: duplicates.filter(d => d.isChronicBlocker)
      })
    } catch (e) {
      setError('Failed to scan for duplicates')
    } finally {
      setCheckingDuplicates(false)
    }
  }

  async function handleStatusChange(meetingId, actionId, newStatus) {
    try {
      // Optimistic update
      setActions(prev => prev.map(a => 
        a.id === actionId ? { ...a, status: newStatus, completed: newStatus === 'done' } : a
      ))
      
      // API call
      await updateAction(meetingId, actionId, { 
        status: newStatus,
        completed: newStatus === 'done'
      })
      
      // Don't refresh - trust the optimistic update
      // The status will persist in backend for next page load
    } catch (e) {
      console.error('Failed to update status:', e)
      setError('Failed to update action status')
      // Revert on error by refreshing
      await fetchActions()
    }
  }

  // Get unique owners for filter
  const owners = [...new Set(actions.map(a => a.owner).filter(Boolean))]

  // Apply filters
  const filteredActions = actions.filter(a => {
    if (statusFilter === 'incomplete' && a.completed) return false
    if (statusFilter === 'complete' && !a.completed) return false
    if (ownerFilter && a.owner !== ownerFilter) return false
    return true
  })

  // Group by meeting
  const actionsByMeeting = filteredActions.reduce((acc, action) => {
    const key = action.meetingId
    if (!acc[key]) {
      acc[key] = {
        meetingId: action.meetingId,
        meetingTitle: action.meetingTitle,
        meetingDate: action.meetingDate,
        actions: []
      }
    }
    acc[key].actions.push(action)
    return acc
  }, {})

  const meetings = Object.values(actionsByMeeting)

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
        </div>
        <div style={s.hdrR}>
          <button onClick={() => navigate('/')} style={s.navBtn}>
            ← Dashboard
          </button>
          <span style={s.userTxt}>{user}</span>
          <button className="signout"
            onClick={async () => { await logout(); navigate('/login') }}
            style={s.signOut}>↗ Sign out</button>
        </div>
      </header>

      <main style={s.main}>
        {/* Team Selector */}
        <div style={{marginBottom: 24}}>
          <TeamSelector 
            selectedTeamId={selectedTeamId}
            onTeamChange={setSelectedTeamId}
          />
        </div>

        <div style={s.topBar}>
          <div>
            <h1 style={s.pageTitle}>Action Items from Meetings</h1>
            <p style={s.pageSub}>
              All action items extracted from your meetings, organized by source
            </p>
          </div>
          {stats && (
            <div style={s.statsBox}>
              <div style={s.statItem}>
                <span style={s.statNum}>{stats.total || 0}</span>
                <span style={s.statLbl}>Total</span>
              </div>
              <div style={s.statItem}>
                <span style={{...s.statNum, color:'#c8f04a'}}>{stats.completed || 0}</span>
                <span style={s.statLbl}>Done</span>
              </div>
              <div style={s.statItem}>
                <span style={{...s.statNum, color:'#e8c06a'}}>{stats.incomplete || 0}</span>
                <span style={s.statLbl}>Pending</span>
              </div>
            </div>
          )}
        </div>

        <div style={s.filters}>
          <div style={s.filterGroup}>
            <label style={s.filterLbl}>VIEW</label>
            <div style={s.viewToggle}>
              <button 
                onClick={() => setView('list')}
                style={{...s.viewToggleBtn, ...(view === 'list' ? s.viewBtnActive : s.viewBtnInactive)}}>
                📋 List
              </button>
              <button 
                onClick={() => setView('kanban')}
                style={{...s.viewToggleBtn, ...(view === 'kanban' ? s.viewBtnActive : s.viewBtnInactive)}}>
                📊 Kanban
              </button>
            </div>
          </div>
          <div style={s.filterGroup}>
            <label style={s.filterLbl}>STATUS</label>
            <select value={statusFilter} onChange={e => setStatusFilter(e.target.value)}
              style={s.select}>
              <option value="all">All</option>
              <option value="incomplete">Incomplete</option>
              <option value="complete">Complete</option>
            </select>
          </div>
          <div style={s.filterGroup}>
            <label style={s.filterLbl}>OWNER</label>
            <select value={ownerFilter} onChange={e => setOwnerFilter(e.target.value)}
              style={s.select}>
              <option value="">All owners</option>
              {owners.map(owner => (
                <option key={owner} value={owner}>{owner}</option>
              ))}
            </select>
          </div>
          <div style={s.filterGroup}>
            <button onClick={scanForDuplicates} disabled={checkingDuplicates || loading}
              style={{...s.scanBtn, ...(checkingDuplicates ? {opacity:0.5} : {})}}>
              {checkingDuplicates ? '🔍 Scanning...' : '🔍 Check Duplicates'}
            </button>
          </div>
          <div style={s.filterGroup}>
            <span style={s.resultCount}>
              {filteredActions.length} action{filteredActions.length !== 1 ? 's' : ''}
            </span>
          </div>
        </div>

        {duplicateResults && (
          <div style={s.duplicatePanel}>
            <div style={s.duplicateHeader}>
              <h3 style={s.duplicateTitle}>
                🔍 Duplicate Detection Results
              </h3>
              <button onClick={() => setDuplicateResults(null)} style={s.closeBtn}>✕</button>
            </div>
            {duplicateResults.duplicates.length === 0 ? (
              <p style={s.duplicateEmpty}>
                ✓ No duplicates found! All {duplicateResults.total} incomplete actions are unique.
              </p>
            ) : (
              <>
                <p style={s.duplicateSummary}>
                  Found {duplicateResults.duplicates.length} potential duplicate{duplicateResults.duplicates.length !== 1 ? 's' : ''} 
                  {duplicateResults.chronicBlockers.length > 0 && (
                    <span style={{color:'#e87a6a'}}>
                      {' '}({duplicateResults.chronicBlockers.length} chronic blocker{duplicateResults.chronicBlockers.length !== 1 ? 's' : ''})
                    </span>
                  )}
                </p>
                <div style={s.duplicateList}>
                  {duplicateResults.duplicates.map((dup, idx) => (
                    <div key={idx} style={s.duplicateCard}>
                      <div style={s.duplicateCardHeader}>
                        <span style={s.similarityBadge}>
                          {dup.similarity}% similar
                        </span>
                        {dup.isChronicBlocker && (
                          <span style={s.chronicBadge}>
                            ⚠ Chronic Blocker (repeated {dup.repeatCount}× )
                          </span>
                        )}
                      </div>
                      <p style={s.duplicateTask}>
                        <strong>Current:</strong> {dup.action.task}
                      </p>
                      {dup.bestMatch && (
                        <p style={s.duplicateMatch}>
                          <strong>Similar to:</strong> {dup.bestMatch.task}
                          <span style={s.duplicateMatchMeta}>
                            {' '}from "{dup.bestMatch.meetingTitle}" 
                            ({new Date(dup.bestMatch.createdAt).toLocaleDateString('en-GB', {day:'numeric', month:'short'})})
                          </span>
                        </p>
                      )}
                      {dup.history && dup.history.length > 1 && (
                        <details style={s.historyDetails}>
                          <summary style={s.historySummary}>
                            View history ({dup.history.length} similar items)
                          </summary>
                          <ul style={s.historyList}>
                            {dup.history.slice(0, 5).map((h, i) => (
                              <li key={i} style={s.historyItem}>
                                {h.task} ({h.similarity}% similar)
                              </li>
                            ))}
                          </ul>
                        </details>
                      )}
                    </div>
                  ))}
                </div>
              </>
            )}
          </div>
        )}

        {error && <div style={s.errBox}>{error}</div>}

        {loading ? (
          <div style={s.center}>
            <div style={{...s.spin, animation:'spin 1s linear infinite'}}/>
          </div>
        ) : filteredActions.length === 0 ? (
          <div style={s.empty}>
            <p style={s.emptyTitle}>No action items found</p>
            <p style={s.emptySub}>
              {statusFilter !== 'all' || ownerFilter 
                ? 'Try adjusting your filters'
                : 'Upload a meeting to get started'}
            </p>
          </div>
        ) : view === 'kanban' ? (
          <KanbanBoard 
            actions={filteredActions}
            onStatusChange={handleStatusChange}
          />
        ) : (
          <div style={s.meetingsList}>
            {meetings.map((meeting, idx) => (
              <div key={meeting.meetingId} style={{...s.meetingCard,
                animationDelay:`${idx*0.05}s`}} className="meetingcard">
                <div style={s.meetingHeader}>
                  <div>
                    <h3 style={s.meetingTitle}>{meeting.meetingTitle}</h3>
                    <p style={s.meetingDate}>{fmtDate(meeting.meetingDate)}</p>
                  </div>
                  <button onClick={() => navigate(`/meeting/${meeting.meetingId}`)}
                    style={s.viewBtn} className="viewbtn">
                    View Meeting →
                  </button>
                </div>
                <div style={s.actionsList}>
                  {meeting.actions.map((action, aidx) => {
                    const daysUntil = getDaysUntil(action.deadline)
                    const isOverdue = daysUntil !== null && daysUntil < 0
                    const isToday = daysUntil === 0
                    const isSoon = daysUntil !== null && daysUntil > 0 && daysUntil <= 3
                    
                    return (
                      <div key={action.id} style={{...s.actionCard,
                        ...(action.completed ? {opacity:0.5} : {}),
                        animationDelay:`${(idx*0.05)+(aidx*0.03)}s`}}
                        className="actioncard">
                        <div style={s.actionTop}>
                          <div style={s.actionLeft}>
                            <input type="checkbox" checked={action.completed}
                              onChange={() => handleStatusChange(action.meetingId, action.id, action.completed ? 'todo' : 'done')}
                              style={s.checkbox}/>
                            <div>
                              <p style={{...s.actionTask,
                                ...(action.completed ? {textDecoration:'line-through'} : {})}}>
                                {action.task}
                              </p>
                              <div style={s.actionMeta}>
                                <span style={s.metaItem}>
                                  👤 {action.owner || 'Unassigned'}
                                </span>
                                <span style={s.metaItem}>
                                  📅 {fmtDate(action.deadline)}
                                </span>
                                {daysUntil !== null && !action.completed && (
                                  <span style={{...s.metaItem,
                                    ...(isOverdue ? {color:'#e87a6a'} : {}),
                                    ...(isToday ? {color:'#e8c06a'} : {}),
                                    ...(isSoon ? {color:'#e8c06a'} : {})}}>
                                    {isOverdue ? `⚠ ${Math.abs(daysUntil)} days overdue` :
                                     isToday ? '⏱ Today' :
                                     isSoon ? `⏱ ${daysUntil} days left` :
                                     `${daysUntil} days`}
                                  </span>
                                )}
                              </div>
                            </div>
                          </div>
                          <div style={s.actionRight}>
                            <span style={{...s.riskBadge,
                              background: RISK_COLORS[action.riskLevel] || RISK_COLORS.LOW}}>
                              {action.riskLevel || 'LOW'}
                            </span>
                          </div>
                        </div>
                      </div>
                    )
                  })}
                </div>
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  )
}

const css = `
  @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=DM+Mono:wght@300;400&display=swap');
  *{box-sizing:border-box;margin:0;padding:0;}
  body{background:#0c0c09;}
  @keyframes fadeUp{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:translateY(0)}}
  @keyframes spin{to{transform:rotate(360deg)}}
  .signout:hover{color:#f0ece0 !important;border-color:#6b7260 !important;}
  .navBtn:hover{color:#f0ece0 !important;border-color:#6b7260 !important;}
  .meetingcard{animation:fadeUp 0.35s ease both;}
  .actioncard{animation:fadeUp 0.25s ease both;}
  .viewbtn:hover{background:#d0f860 !important;}
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
  hdrR: {display:'flex', alignItems:'center', gap:14},
  navBtn:{background:'none', border:'1px solid #3a3a2e', borderRadius:3,
          padding:'5px 12px', color:'#8a8a74', fontSize:10, letterSpacing:'0.1em',
          cursor:'pointer', fontFamily:"'DM Mono',monospace",
          transition:'color 0.15s, border-color 0.15s'},
  userTxt:{fontSize:11, letterSpacing:'0.06em', color:'#8a8a74'},
  signOut:{background:'none', border:'1px solid #3a3a2e', borderRadius:3,
           padding:'5px 12px', color:'#8a8a74', fontSize:10, letterSpacing:'0.1em',
           cursor:'pointer', fontFamily:"'DM Mono',monospace",
           transition:'color 0.15s, border-color 0.15s'},
  main: {maxWidth:1200, margin:'0 auto', padding:'32px 36px'},
  topBar:{display:'flex', justifyContent:'space-between', alignItems:'flex-start',
          marginBottom:32, paddingBottom:24, borderBottom:'1px solid #2a2a20'},
  pageTitle:{fontFamily:"'Playfair Display',serif", fontSize:28, fontWeight:700,
             color:'#f0ece0', letterSpacing:'-0.3px', marginBottom:6},
  pageSub:{fontSize:11, letterSpacing:'0.05em', color:'#6b7260'},
  statsBox:{display:'flex', gap:24},
  statItem:{display:'flex', flexDirection:'column', alignItems:'center'},
  statNum:{fontFamily:"'Playfair Display',serif", fontSize:32, fontWeight:900,
           color:'#f0ece0', lineHeight:1},
  statLbl:{fontSize:9, letterSpacing:'0.12em', color:'#6b7260',
           textTransform:'uppercase', marginTop:4},
  filters:{display:'flex', gap:16, marginBottom:24, alignItems:'flex-end'},
  filterGroup:{display:'flex', flexDirection:'column', gap:6},
  filterLbl:{fontSize:9, letterSpacing:'0.15em', color:'#8a8a74',
             textTransform:'uppercase'},
  select:{background:'#1e1e16', border:'1px solid #3a3a2e', borderRadius:4,
          padding:'8px 12px', color:'#f0ece0', fontSize:12,
          fontFamily:"'DM Mono',monospace", cursor:'pointer',
          outline:'none'},
  resultCount:{fontSize:11, color:'#8a8a74', letterSpacing:'0.05em',
               padding:'8px 0'},
  errBox:{background:'#1a0e0e', border:'1px solid #4a2a2a', borderRadius:4,
          padding:'10px 12px', color:'#e87a6a', fontSize:11, marginBottom:16},
  center:{display:'flex', alignItems:'center', justifyContent:'center',
          padding:'80px 0'},
  spin:{width:20, height:20, border:'2px solid #2a2a20',
        borderTopColor:'#c8f04a', borderRadius:'50%'},
  empty:{textAlign:'center', padding:'80px 20px'},
  emptyTitle:{fontSize:16, color:'#8a8a74', marginBottom:8},
  emptySub:{fontSize:12, color:'#6b7260'},
  meetingsList:{display:'flex', flexDirection:'column', gap:24},
  meetingCard:{background:'#111108', border:'1px solid #2a2a20', borderRadius:8,
               padding:'20px 24px'},
  meetingHeader:{display:'flex', justifyContent:'space-between', alignItems:'center',
                 marginBottom:16, paddingBottom:16, borderBottom:'1px solid #2a2a20'},
  meetingTitle:{fontSize:16, color:'#f0ece0', letterSpacing:'0.01em',
                marginBottom:4},
  meetingDate:{fontSize:10, color:'#6b7260', letterSpacing:'0.05em'},
  viewBtn:{background:'#c8f04a', border:'none', borderRadius:4,
           padding:'6px 14px', color:'#0c0c09', fontSize:11,
           letterSpacing:'0.05em', cursor:'pointer',
           fontFamily:"'DM Mono',monospace", transition:'background 0.15s'},
  actionsList:{display:'flex', flexDirection:'column', gap:10},
  actionCard:{background:'#141410', border:'1px solid #2e2e22', borderRadius:6,
              padding:'12px 14px', transition:'background 0.15s'},
  actionTop:{display:'flex', justifyContent:'space-between', alignItems:'flex-start'},
  actionLeft:{display:'flex', gap:12, flex:1},
  checkbox:{width:16, height:16, cursor:'pointer', marginTop:2, flexShrink:0},
  actionTask:{fontSize:13, color:'#e8e4d0', marginBottom:6, lineHeight:1.4},
  actionMeta:{display:'flex', gap:12, flexWrap:'wrap'},
  metaItem:{fontSize:10, color:'#6b7260', letterSpacing:'0.03em'},
  actionRight:{display:'flex', alignItems:'center', gap:8},
  riskBadge:{fontSize:8, letterSpacing:'0.12em', color:'#0c0c09',
             padding:'3px 8px', borderRadius:3, fontWeight:400,
             textTransform:'uppercase'},
  scanBtn:{background:'#2a2a20', border:'1px solid #3a3a2e', borderRadius:4,
           padding:'8px 16px', color:'#c8f04a', fontSize:11,
           letterSpacing:'0.05em', cursor:'pointer',
           fontFamily:"'DM Mono',monospace", transition:'all 0.15s'},
  duplicatePanel:{background:'#141410', border:'1px solid #3a3a2e', borderRadius:8,
                  padding:'20px 24px', marginBottom:24},
  duplicateHeader:{display:'flex', justifyContent:'space-between', alignItems:'center',
                   marginBottom:16},
  duplicateTitle:{fontSize:16, color:'#f0ece0', letterSpacing:'0.01em'},
  closeBtn:{background:'none', border:'none', color:'#6b7260', fontSize:18,
            cursor:'pointer', padding:0, lineHeight:1},
  duplicateEmpty:{fontSize:12, color:'#8a8a74', padding:'12px 0'},
  duplicateSummary:{fontSize:12, color:'#c8f04a', marginBottom:16,
                    letterSpacing:'0.03em'},
  duplicateList:{display:'flex', flexDirection:'column', gap:12},
  duplicateCard:{background:'#1a1a14', border:'1px solid #2e2e22', borderRadius:6,
                 padding:'14px 16px'},
  duplicateCardHeader:{display:'flex', gap:10, marginBottom:10, flexWrap:'wrap'},
  similarityBadge:{fontSize:10, letterSpacing:'0.08em', color:'#0c0c09',
                   background:'#e8c06a', padding:'3px 10px', borderRadius:3},
  chronicBadge:{fontSize:10, letterSpacing:'0.08em', color:'#0c0c09',
                background:'#e87a6a', padding:'3px 10px', borderRadius:3},
  duplicateTask:{fontSize:12, color:'#e8e4d0', marginBottom:8, lineHeight:1.5},
  duplicateMatch:{fontSize:11, color:'#8a8a74', lineHeight:1.5},
  duplicateMatchMeta:{color:'#6b7260', fontSize:10},
  historyDetails:{marginTop:10, fontSize:11},
  historySummary:{color:'#6b7260', cursor:'pointer', fontSize:10,
                  letterSpacing:'0.05em', marginBottom:6},
  historyList:{listStyle:'none', paddingLeft:12, marginTop:8},
  historyItem:{fontSize:10, color:'#6b7260', marginBottom:4, lineHeight:1.5},
  viewToggle:{display:'flex', gap:8},
  viewToggleBtn:{background:'none', border:'1px solid #3a3a2e', borderRadius:4,
           padding:'8px 14px', fontSize:11, letterSpacing:'0.05em',
           cursor:'pointer', fontFamily:"'DM Mono',monospace",
           transition:'all 0.15s'},
  viewBtnActive:{background:'#c8f04a', color:'#0c0c09', borderColor:'#c8f04a'},
  viewBtnInactive:{background:'#1e1e16', color:'#8a8a74', borderColor:'#3a3a2e'},
}
