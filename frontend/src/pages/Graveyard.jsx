import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { logout, checkSession, getUser } from '../utils/auth.js'
import { getAllActions, updateAction } from '../utils/api.js'
import TeamSelector from '../components/TeamSelector.jsx'
import { EpitaphCardSkeleton } from '../components/SkeletonLoader.jsx'

function getDaysOld(createdAt) {
  if (!createdAt) return 0
  const now = new Date()
  const created = new Date(createdAt)
  return Math.floor((now - created) / (1000 * 60 * 60 * 24))
}

function fmtDate(iso) {
  if (!iso) return 'Unknown'
  const d = new Date(iso)
  if (isNaN(d)) return 'Unknown'
  return d.toLocaleDateString('en-GB', {day:'numeric', month:'short', year:'numeric'})
}

export default function Graveyard() {
  const navigate = useNavigate()
  const [user, setUser] = useState('')
  const [buried, setBuried] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [resurrectModal, setResurrectModal] = useState(null)
  const [newOwner, setNewOwner] = useState('')
  const [newDeadline, setNewDeadline] = useState('')
  const [resurrecting, setResurrecting] = useState(false)
  const [selectedTeamId, setSelectedTeamId] = useState(null)

  useEffect(() => {
    checkSession().then(u => {
      if (!u) { navigate('/login'); return }
      setUser(getUser() || '')
      fetchBuried()
    })
  }, [selectedTeamId])

  async function fetchBuried() {
    try {
      // Add minimum loading time for better UX (skeleton visibility)
      const [data] = await Promise.all([
        getAllActions(null, null, selectedTeamId),
        new Promise(resolve => setTimeout(resolve, 2000))
      ])
      const actions = data.actions || []
      
      console.log('Fetched actions:', actions.length)
      
      // Filter: >30 days old and incomplete
      const graveyard = actions.filter(a => {
        if (a.completed) return false
        const daysOld = getDaysOld(a.createdAt)
        return daysOld > 30
      })
      
      console.log('Graveyard items:', graveyard.length)
      if (graveyard.length > 0) {
        console.log('First graveyard item:', {
          id: graveyard[0].id,
          meetingId: graveyard[0].meetingId,
          task: graveyard[0].task
        })
      }
      
      // Sort by age (oldest first)
      graveyard.sort((a, b) => {
        const aDate = new Date(a.createdAt)
        const bDate = new Date(b.createdAt)
        return aDate - bDate
      })
      
      setBuried(graveyard)
    } catch (e) {
      console.error('Failed to load graveyard:', e)
      setError('Failed to load graveyard')
    } finally {
      setLoading(false)
    }
  }

  function openResurrectModal(action) {
    console.log('Opening modal for action:', {
      id: action.id,
      meetingId: action.meetingId,
      task: action.task,
      fullAction: action
    })
    setResurrectModal(action)
    setNewOwner(action.owner || '')
    // Set deadline to 7 days from now
    const future = new Date()
    future.setDate(future.getDate() + 7)
    setNewDeadline(future.toISOString().split('T')[0])
  }

  async function resurrect() {
    if (!resurrectModal) return
    setResurrecting(true)
    setError('') // Clear previous errors
    
    // Debug logging
    console.log('Resurrecting action:', {
      meetingId: resurrectModal.meetingId,
      actionId: resurrectModal.id,
      owner: newOwner,
      deadline: newDeadline
    })
    
    try {
      // Resurrect: move to 'todo' status with new owner and deadline
      await updateAction(resurrectModal.meetingId, resurrectModal.id, {
        status: 'todo',
        owner: newOwner,
        deadline: newDeadline,
        completed: false
      })
      
      // Remove from graveyard
      setBuried(buried.filter(a => a.id !== resurrectModal.id))
      
      // Show success message
      setError('') // Clear any errors
      alert('✅ Action resurrected successfully! It will appear in your Kanban board.')
      
      setResurrectModal(null)
      setNewOwner('')
      setNewDeadline('')
    } catch (e) {
      console.error('Resurrection error:', e)
      console.error('Error response:', e.response)
      
      // Show specific error messages
      if (e.message && e.message.includes('401')) {
        setError('Your session expired. Please logout and login again.')
      } else if (e.message && e.message.includes('403')) {
        setError('Not authorized to update this action.')
      } else if (e.message && e.message.includes('404')) {
        setError('Action item not found.')
      } else if (e.message && e.message.includes('Network')) {
        setError('Connection lost. Check your internet and try again.')
      } else {
        setError(`Failed to resurrect action: ${e.message || 'Unknown error'}`)
      }
    } finally {
      setResurrecting(false)
    }
  }

  // Calculate stats
  const totalBuried = buried.length
  const avgDaysOld = buried.length > 0
    ? Math.round(buried.reduce((sum, a) => sum + getDaysOld(a.createdAt), 0) / buried.length)
    : 0
  const oldestDays = buried.length > 0
    ? Math.max(...buried.map(a => getDaysOld(a.createdAt)))
    : 0

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
            <h1 style={s.pageTitle}>🪦 Action Item Graveyard</h1>
            <p style={s.pageSub}>
              Items abandoned for more than 30 days
            </p>
          </div>
          <div style={s.statsBox}>
            <div style={s.statItem}>
              <span style={{...s.statNum, color:'#8a8a74'}}>{totalBuried}</span>
              <span style={s.statLbl}>Buried</span>
            </div>
            <div style={s.statItem}>
              <span style={{...s.statNum, color:'#e87a6a'}}>{avgDaysOld}</span>
              <span style={s.statLbl}>Avg Days</span>
            </div>
            <div style={s.statItem}>
              <span style={{...s.statNum, color:'#6b7260'}}>{oldestDays}</span>
              <span style={s.statLbl}>Oldest</span>
            </div>
          </div>
        </div>

        {error && <div style={s.errBox}>{error}</div>}

        {loading ? (
          <div style={s.cemetery}>
            <EpitaphCardSkeleton />
            <EpitaphCardSkeleton />
            <EpitaphCardSkeleton />
            <EpitaphCardSkeleton />
          </div>
        ) : buried.length === 0 ? (
          <div style={s.empty}>
            <p style={s.emptyIcon}>✨</p>
            <p style={s.emptyTitle}>No buried action items</p>
            <p style={s.emptySub}>
              All your action items are fresh! Keep up the good work.
            </p>
          </div>
        ) : (
          <div style={s.cemetery}>
            {buried.map((action, idx) => {
              const daysOld = getDaysOld(action.createdAt)
              const isAncient = daysOld > 90
              
              return (
                <div key={action.id} style={{...s.tombstone,
                  animationDelay:`${idx*0.05}s`}} className="tombstone">
                  <div style={s.tombTop}>
                    <span style={s.tombIcon}>🪦</span>
                    {isAncient && <span style={s.ancientBadge}>ANCIENT</span>}
                  </div>
                  
                  <div style={s.tombBody}>
                    <p style={s.tombEpitaph}>Here lies</p>
                    <p style={s.tombTask}>{action.task}</p>
                    
                    {/* AI-Generated Epitaph */}
                    {action.epitaph && (
                      <p style={s.aiEpitaph}>{action.epitaph}</p>
                    )}
                    
                    <div style={s.tombMeta}>
                      <div style={s.tombMetaRow}>
                        <span style={s.tombLabel}>Owner:</span>
                        <span style={s.tombValue}>{action.owner || 'Unassigned'}</span>
                      </div>
                      <div style={s.tombMetaRow}>
                        <span style={s.tombLabel}>Created:</span>
                        <span style={s.tombValue}>{fmtDate(action.createdAt)}</span>
                      </div>
                      <div style={s.tombMetaRow}>
                        <span style={s.tombLabel}>Buried:</span>
                        <span style={{...s.tombValue, color:'#e87a6a'}}>
                          {daysOld} days ago
                        </span>
                      </div>
                      <div style={s.tombMetaRow}>
                        <span style={s.tombLabel}>From:</span>
                        <span style={s.tombValue}>{action.meetingTitle}</span>
                      </div>
                    </div>
                  </div>
                  
                  <div style={s.tombFooter}>
                    <button onClick={() => openResurrectModal(action)}
                      style={s.resurrectBtn} className="resurrectbtn">
                      ⚡ Resurrect
                    </button>
                  </div>
                </div>
              )
            })}
          </div>
        )}
      </main>

      {/* Resurrect Modal */}
      {resurrectModal && (
        <div style={s.modalOverlay} onClick={() => !resurrecting && setResurrectModal(null)}>
          <div style={s.modal} onClick={e => e.stopPropagation()}>
            <div style={s.modalHeader}>
              <h3 style={s.modalTitle}>⚡ Resurrect Action Item</h3>
              <button onClick={() => setResurrectModal(null)}
                style={s.modalClose}>✕</button>
            </div>
            
            <div style={s.modalBody}>
              <p style={s.modalTask}>{resurrectModal.task}</p>
              
              <div style={s.modalField}>
                <label style={s.modalLabel}>ASSIGN TO</label>
                <input type="text" value={newOwner}
                  onChange={e => setNewOwner(e.target.value)}
                  placeholder="Owner name"
                  style={s.modalInput}/>
              </div>
              
              <div style={s.modalField}>
                <label style={s.modalLabel}>NEW DEADLINE</label>
                <input type="date" value={newDeadline}
                  onChange={e => setNewDeadline(e.target.value)}
                  style={s.modalInput}/>
              </div>
              
              <p style={s.modalHint}>
                This will move the item back to "To Do" status with the updated owner and deadline.
                The item will appear in your Kanban board.
              </p>
            </div>
            
            <div style={s.modalFooter}>
              <button onClick={() => setResurrectModal(null)}
                disabled={resurrecting}
                style={s.modalCancel}>
                Cancel
              </button>
              <button onClick={resurrect}
                disabled={resurrecting}
                style={{...s.modalConfirm, ...(resurrecting ? {opacity:0.5} : {})}}>
                {resurrecting ? 'Resurrecting...' : '⚡ Resurrect'}
              </button>
            </div>
          </div>
        </div>
      )}
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
  .tombstone{animation:fadeUp 0.35s ease both;}
  .tombstone:hover{transform:translateY(-2px);border-color:#3a3a2e;}
  .resurrectbtn:hover{background:#d0f860 !important;}
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
  errBox:{background:'#1a0e0e', border:'1px solid #4a2a2a', borderRadius:4,
          padding:'10px 12px', color:'#e87a6a', fontSize:11, marginBottom:16},
  center:{display:'flex', alignItems:'center', justifyContent:'center',
          padding:'80px 0'},
  spin:{width:20, height:20, border:'2px solid #2a2a20',
        borderTopColor:'#c8f04a', borderRadius:'50%'},
  empty:{textAlign:'center', padding:'80px 20px'},
  emptyIcon:{fontSize:48, marginBottom:16},
  emptyTitle:{fontSize:16, color:'#8a8a74', marginBottom:8},
  emptySub:{fontSize:12, color:'#6b7260'},
  cemetery:{display:'grid', gridTemplateColumns:'repeat(auto-fill, minmax(320px, 1fr))',
            gap:20},
  tombstone:{background:'#111108', border:'1px solid #2a2a20', borderRadius:8,
             padding:'20px', transition:'all 0.2s', cursor:'default'},
  tombTop:{display:'flex', justifyContent:'space-between', alignItems:'center',
           marginBottom:16},
  tombIcon:{fontSize:32, opacity:0.6},
  ancientBadge:{fontSize:8, letterSpacing:'0.15em', color:'#e87a6a',
                background:'#1a0e0e', border:'1px solid #4a2a2a',
                padding:'3px 8px', borderRadius:3},
  tombBody:{marginBottom:16},
  tombEpitaph:{fontSize:10, letterSpacing:'0.1em', color:'#6b7260',
               textTransform:'uppercase', marginBottom:8},
  tombTask:{fontSize:14, color:'#e8e4d0', marginBottom:16, lineHeight:1.5,
            fontStyle:'italic'},
  aiEpitaph:{fontSize:12, color:'#8a8a74', marginBottom:16, lineHeight:1.6,
             fontStyle:'italic', paddingLeft:12, borderLeft:'2px solid #3a3a2e'},
  tombMeta:{display:'flex', flexDirection:'column', gap:6,
            paddingTop:12, borderTop:'1px solid #2a2a20'},
  tombMetaRow:{display:'flex', justifyContent:'space-between', alignItems:'center'},
  tombLabel:{fontSize:9, letterSpacing:'0.1em', color:'#6b7260',
             textTransform:'uppercase'},
  tombValue:{fontSize:10, color:'#8a8a74'},
  tombFooter:{paddingTop:12, borderTop:'1px solid #2a2a20'},
  resurrectBtn:{width:'100%', background:'#c8f04a', border:'none', borderRadius:4,
                padding:'8px 14px', color:'#0c0c09', fontSize:11,
                letterSpacing:'0.05em', cursor:'pointer',
                fontFamily:"'DM Mono',monospace", transition:'background 0.15s'},
  modalOverlay:{position:'fixed', inset:0, background:'rgba(0,0,0,0.8)',
                display:'flex', alignItems:'center', justifyContent:'center',
                zIndex:1000, padding:20},
  modal:{background:'#111108', border:'1px solid #3a3a2e', borderRadius:8,
         maxWidth:500, width:'100%', maxHeight:'90vh', overflow:'auto'},
  modalHeader:{display:'flex', justifyContent:'space-between', alignItems:'center',
               padding:'20px 24px', borderBottom:'1px solid #2a2a20'},
  modalTitle:{fontSize:16, color:'#f0ece0', letterSpacing:'0.01em'},
  modalClose:{background:'none', border:'none', color:'#6b7260', fontSize:18,
              cursor:'pointer', padding:0, lineHeight:1},
  modalBody:{padding:'20px 24px'},
  modalTask:{fontSize:13, color:'#e8e4d0', marginBottom:20, lineHeight:1.5,
             fontStyle:'italic', padding:12, background:'#0f0f0c',
             border:'1px solid #2a2a20', borderRadius:4},
  modalField:{marginBottom:16},
  modalLabel:{display:'block', fontSize:9, letterSpacing:'0.15em', color:'#8a8a74',
              textTransform:'uppercase', marginBottom:8},
  modalInput:{width:'100%', background:'#1e1e16', border:'1px solid #3a3a2e',
              borderRadius:4, padding:'10px 12px', color:'#f0ece0',
              fontSize:13, fontFamily:"'DM Mono',monospace", outline:'none'},
  modalHint:{fontSize:10, color:'#6b7260', lineHeight:1.6, marginTop:12,
             padding:10, background:'#0f0f0c', border:'1px solid #2a2a20',
             borderRadius:4},
  modalFooter:{display:'flex', gap:12, padding:'20px 24px',
               borderTop:'1px solid #2a2a20'},
  modalCancel:{flex:1, background:'none', border:'1px solid #3a3a2e',
               borderRadius:4, padding:'8px 14px', color:'#8a8a74',
               fontSize:11, letterSpacing:'0.05em', cursor:'pointer',
               fontFamily:"'DM Mono',monospace"},
  modalConfirm:{flex:1, background:'#c8f04a', border:'none', borderRadius:4,
                padding:'8px 14px', color:'#0c0c09', fontSize:11,
                letterSpacing:'0.05em', cursor:'pointer',
                fontFamily:"'DM Mono',monospace", transition:'opacity 0.15s'},
}
