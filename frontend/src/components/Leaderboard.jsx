import { useState, useEffect, useMemo, useRef } from 'react'
import { getAllActions } from '../utils/api.js'

// Production-grade stats calculation with proper weighting
function calculateStats(actions) {
  // Group by owner (case-insensitive, trimmed)
  const byOwner = {}
  
  actions.forEach(action => {
    // Normalize owner name to prevent duplicates
    const rawOwner = action.owner || 'Unassigned'
    const owner = rawOwner.trim().toLowerCase()
    const displayName = rawOwner.trim()
    
    if (!byOwner[owner]) {
      byOwner[owner] = {
        owner: displayName, // Use original casing for display
        ownerId: owner, // Normalized for grouping
        total: 0,
        completed: 0,
        incomplete: 0,
        avgCompletionDays: 0,
        completionTimes: [],
        totalRiskScore: 0,
        achievements: []
      }
    }
    
    byOwner[owner].total++
    byOwner[owner].totalRiskScore += (action.riskScore || 0)
    
    if (action.completed) {
      byOwner[owner].completed++
      
      // Calculate completion time with timezone-safe date handling
      if (action.createdAt && action.completedAt) {
        try {
          const created = new Date(action.createdAt)
          const completed = new Date(action.completedAt)
          
          // Normalize to start of day for accurate comparison
          const createdStart = new Date(created.getFullYear(), created.getMonth(), created.getDate())
          const completedStart = new Date(completed.getFullYear(), completed.getMonth(), completed.getDate())
          
          const days = Math.round((completedStart - createdStart) / (1000 * 60 * 60 * 24))
          
          // Guard against negative durations
          if (days >= 0) {
            byOwner[owner].completionTimes.push(days)
          }
        } catch (e) {
          console.warn('Invalid date format for action:', action.id)
        }
      }
    } else {
      byOwner[owner].incomplete++
    }
  })
  
  // Calculate averages, weighted scores, and achievements
  Object.values(byOwner).forEach(stats => {
    // Completion rate
    stats.completionRate = stats.total > 0
      ? (stats.completed / stats.total)
      : 0
    
    // Average completion time
    if (stats.completionTimes.length > 0) {
      stats.avgCompletionDays = Math.round(
        stats.completionTimes.reduce((sum, days) => sum + days, 0) / stats.completionTimes.length
      )
    }
    
    // Average risk score (task difficulty)
    stats.avgRiskScore = stats.total > 0
      ? Math.round(stats.totalRiskScore / stats.total)
      : 0
    
    // CRITICAL FIX: Weighted score prevents gaming
    // Formula: completionRate * log(total + 1) * riskWeight
    // This rewards both quality AND volume AND difficulty
    const volumeWeight = Math.log(stats.total + 1) // Logarithmic scaling
    const riskWeight = 1 + (stats.avgRiskScore / 200) // Higher risk = higher weight
    stats.weightedScore = stats.completionRate * volumeWeight * riskWeight
    
    // Achievements (with minimum thresholds to prevent gaming)
    if (stats.completionRate === 1.0 && stats.total >= 10) {
      stats.achievements.push({ icon: '🏆', name: 'Perfectionist', color: '#c8f04a' })
    }
    if (stats.avgCompletionDays <= 2 && stats.completionTimes.length >= 5) {
      stats.achievements.push({ icon: '⚡', name: 'Speed Demon', color: '#6a9ae8' })
    }
    if (stats.completed >= 30) {
      stats.achievements.push({ icon: '💪', name: 'Workhorse', color: '#e8c06a' })
    }
    if (stats.completionRate >= 0.9 && stats.total >= 15) {
      stats.achievements.push({ icon: '⭐', name: 'Consistent', color: '#c8f04a' })
    }
    if (stats.avgRiskScore >= 50 && stats.completed >= 10) {
      stats.achievements.push({ icon: '🔥', name: 'Risk Taker', color: '#e87a6a' })
    }
    
    // Format completion rate as percentage for display
    stats.completionRatePercent = Math.round(stats.completionRate * 100)
  })
  
  // Convert to array and sort by weighted score
  const leaderboard = Object.values(byOwner)
    .filter(s => {
      const owner = s.ownerId.toLowerCase()
      // Exclude unassigned
      if (owner === 'unassigned') return false
      // Exclude entries that look like task descriptions (contain common task words)
      const taskWords = ['person who', 'responsible for', 'will write', 'will handle', 'will do', 'someone to', "i'll do", "i will", "someone", "person"]
      if (taskWords.some(word => owner.includes(word))) return false
      // Exclude very long names (likely descriptions, not names)
      if (s.owner.length > 30) return false
      // Exclude very short names (likely incomplete)
      if (s.owner.length < 3) return false
      return true
    })
    .sort((a, b) => {
      // Primary: Weighted score
      if (Math.abs(b.weightedScore - a.weightedScore) > 0.01) {
        return b.weightedScore - a.weightedScore
      }
      // Secondary: Completed count
      if (b.completed !== a.completed) {
        return b.completed - a.completed
      }
      // Tertiary: Lower avg completion days
      if (a.avgCompletionDays !== b.avgCompletionDays) {
        return a.avgCompletionDays - b.avgCompletionDays
      }
      // Quaternary: Lower incomplete count
      return a.incomplete - b.incomplete
    })
  
  return leaderboard
}

export default function Leaderboard({ teamId = null }) {
  const [leaderboard, setLeaderboard] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const abortControllerRef = useRef(null)

  useEffect(() => {
    fetchLeaderboard()
    
    // Cleanup: cancel fetch on unmount
    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort()
      }
    }
  }, [teamId])

  async function fetchLeaderboard() {
    try {
      // Cancel previous request if still pending
      if (abortControllerRef.current) {
        abortControllerRef.current.abort()
      }
      
      abortControllerRef.current = new AbortController()
      
      const data = await getAllActions(null, null, teamId)
      const actions = data.actions || []
      const stats = calculateStats(actions)
      
      // Only update if not aborted
      if (!abortControllerRef.current.signal.aborted) {
        setLeaderboard(stats)
      }
    } catch (e) {
      if (e.name !== 'AbortError') {
        setError('Failed to load leaderboard')
      }
    } finally {
      if (abortControllerRef.current && !abortControllerRef.current.signal.aborted) {
        setLoading(false)
      }
    }
  }

  // Memoize medals to prevent recreation
  const medals = useMemo(() => ['🥇', '🥈', '🥉'], [])

  if (loading) {
    return (
      <div style={s.loading}>
        <div className="spinner" style={s.spin}/>
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

  return (
    <div style={s.root}>
      <div style={s.header}>
        <h3 style={s.title}>🏆 Team Leaderboard</h3>
        <p style={s.subtitle}>Ranked by weighted performance score</p>
      </div>
      
      <div style={s.list}>
        {leaderboard.map((member, idx) => {
          const rank = idx + 1
          const medal = medals[idx]
          const isTop3 = rank <= 3
          
          return (
            <div key={member.ownerId} style={{...s.row,
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
                    {member.avgRiskScore > 0 && (
                      <span style={s.stat}>
                        • Risk {member.avgRiskScore}
                      </span>
                    )}
                  </div>
                </div>
              </div>
              <div style={s.rowRight}>
                <span style={{...s.rate,
                  color: member.completionRatePercent >= 90 ? '#c8f04a' :
                         member.completionRatePercent >= 70 ? '#e8c06a' : '#8a8a74'}}>
                  {member.completionRatePercent}%
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
        borderTopColor:'#c8f04a', borderRadius:'50%',
        animation:'spin 1s linear infinite'}, // Fixed: animation now works
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
