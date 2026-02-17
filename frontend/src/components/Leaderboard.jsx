import React, { useState, useEffect } from 'react'
import { getAllActions } from '../utils/api.js'

function calculateStats(actions) {
  // Group by owner
  const byOwner = {}
  
  actions.forEach(action => {
    const owner = action.owner || 'Unassigned'
    if (!byOwner[owner]) {
      byOwner[owner] = {
        owner,
        total: 0,
        completed: 0,
        incomplete: 0,
        avgCompletionDays: 0,
        completionTimes: [],
        achievements: []
      }
    }
    
    byOwner[owner].total++
    
    if (action.completed) {
      byOwner[owner].completed++
      
      // Calculate completion time if we have dates
      if (action.createdAt && action.completedAt) {
        const created = new Date(action.createdAt)
        const completed = new Date(action.completedAt)
        const days = Math.floor((completed - created) / (1000 * 60 * 60 * 24))
        byOwner[owner].completionTimes.push(days)
      }
    } else {
      byOwner[owner].incomplete++
    }
  })
  
  // Calculate averages and achievements
  Object.values(byOwner).forEach(stats => {
    // Completion rate
    stats.completionRate = stats.total > 0
      ? Math.round((stats.completed / stats.total) * 100)
      : 0
    
    // Average completion time
    if (stats.completionTimes.length > 0) {
      stats.avgCompletionDays = Math.round(
        stats.completionTimes.reduce((sum, days) => sum + days, 0) / stats.completionTimes.length
      )
    }
    
    // Achievements
    if (stats.completionRate === 100 && stats.total >= 5) {
      stats.achievements.push({ icon: '🏆', name: 'Perfectionist', color: '#c8f04a' })
    }
    if (stats.avgCompletionDays <= 2 && stats.completionTimes.length >= 3) {
      stats.achievements.push({ icon: '⚡', name: 'Speed Demon', color: '#6a9ae8' })
    }
    if (stats.completed >= 20) {
      stats.achievements.push({ icon: '💪', name: 'Workhorse', color: '#e8c06a' })
    }
    if (stats.completionRate >= 90 && stats.total >= 10) {
      stats.achievements.push({ icon: '⭐', name: 'Consistent', color: '#c8f04a' })
    }
  })
  
  // Convert to array and sort by completion rate
  const leaderboard = Object.values(byOwner)
    .filter(s => s.owner !== 'Unassigned')
    .sort((a, b) => {
      // Sort by completion rate, then by total completed
      if (b.completionRate !== a.completionRate) {
        return b.completionRate - a.completionRate
      }
      return b.completed - a.completed
    })
  
  return leaderboard
}

export default function Leaderboard() {
  const [leaderboard, setLeaderboard] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    fetchLeaderboard()
  }, [])

  async function fetchLeaderboard() {
    try {
      const data = await getAllActions()
      const actions = data.actions || []
      const stats = calculateStats(actions)
      setLeaderboard(stats)
    } catch (e) {
      setError('Failed to load leaderboard')
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div style={s.loading}>
        <div style={{...s.spin, animation:'spin 1s linear infinite'}}/>
      </div>
    )
  }

  if (error) {
    return <div style={s.error}>{error}</div>
  }

  if (leaderboard.length === 0) {
    return (
      <div style={s.empty}>
        <p style={s.emptyText}>No team members yet</p>
      </div>
    )
  }

  const medals = ['🥇', '🥈', '🥉']

  return (
    <div style={s.root}>
      <div style={s.header}>
        <h3 style={s.title}>🏆 Team Leaderboard</h3>
        <p style={s.subtitle}>Ranked by completion rate</p>
      </div>
      
      <div style={s.list}>
        {leaderboard.map((member, idx) => {
          const rank = idx + 1
          const medal = medals[idx]
          const isTop3 = rank <= 3
          
          return (
            <div key={member.owner} style={{...s.row,
              ...(isTop3 ? {background:'#141410', borderColor:'#3a3a2e'} : {}),
              animationDelay:`${idx*0.05}s`}}
              className="leaderrow">
              <div style={s.rowLeft}>
                <span style={{...s.rank, ...(isTop3 ? {color:'#c8f04a'} : {})}}>
                  {medal || `#${rank}`}
                </span>
                <div style={s.info}>
                  <div style={s.nameRow}>
                    <span style={s.name}>{member.owner}</span>
                    {member.achievements.length > 0 && (
                      <div style={s.badges}>
                        {member.achievements.map((ach, i) => (
                          <span key={i} style={{...s.badge, color:ach.color}}
                            title={ach.name}>
                            {ach.icon}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                  <div style={s.stats}>
                    <span style={s.stat}>
                      {member.completed}/{member.total} completed
                    </span>
                    {member.avgCompletionDays > 0 && (
                      <span style={s.stat}>
                        • Avg {member.avgCompletionDays}d
                      </span>
                    )}
                  </div>
                </div>
              </div>
              <div style={s.rowRight}>
                <span style={{...s.rate,
                  color: member.completionRate >= 90 ? '#c8f04a' :
                         member.completionRate >= 70 ? '#e8c06a' : '#8a8a74'}}>
                  {member.completionRate}%
                </span>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}

const s = {
  root: {background:'#111108', border:'1px solid #2a2a20', borderRadius:8,
         padding:'20px 24px', marginTop:24},
  header:{marginBottom:20, paddingBottom:16, borderBottom:'1px solid #2a2a20'},
  title:{fontSize:16, color:'#f0ece0', letterSpacing:'0.01em', marginBottom:4,
         fontFamily:"'Playfair Display',serif", fontWeight:700},
  subtitle:{fontSize:10, letterSpacing:'0.05em', color:'#6b7260'},
  loading:{display:'flex', alignItems:'center', justifyContent:'center',
           padding:'40px 0'},
  spin:{width:16, height:16, border:'2px solid #2a2a20',
        borderTopColor:'#c8f04a', borderRadius:'50%'},
  error:{padding:'12px', background:'#1a0e0e', border:'1px solid #4a2a2a',
         borderRadius:4, color:'#e87a6a', fontSize:11},
  empty:{padding:'40px 0', textAlign:'center'},
  emptyText:{fontSize:12, color:'#6b7260'},
  list:{display:'flex', flexDirection:'column', gap:10},
  row:{background:'#0f0f0c', border:'1px solid #2e2e22', borderRadius:6,
       padding:'12px 14px', display:'flex', justifyContent:'space-between',
       alignItems:'center', transition:'all 0.2s',
       animation:'fadeUp 0.3s ease both'},
  rowLeft:{display:'flex', alignItems:'center', gap:14, flex:1},
  rank:{fontSize:18, fontWeight:700, color:'#6b7260', minWidth:32,
        fontFamily:"'Playfair Display',serif"},
  info:{flex:1},
  nameRow:{display:'flex', alignItems:'center', gap:8, marginBottom:4},
  name:{fontSize:13, color:'#e8e4d0', letterSpacing:'0.01em'},
  badges:{display:'flex', gap:4},
  badge:{fontSize:14, lineHeight:1},
  stats:{display:'flex', gap:8, flexWrap:'wrap'},
  stat:{fontSize:10, color:'#6b7260', letterSpacing:'0.03em'},
  rowRight:{},
  rate:{fontSize:20, fontWeight:700, color:'#c8f04a',
        fontFamily:"'Playfair Display',serif"},
}
