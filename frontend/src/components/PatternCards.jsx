import { useState, useEffect, useMemo, useRef } from 'react'
import { getAllActions } from '../utils/api.js'

// Statistical utilities
function calculateStats(values) {
  if (values.length === 0) return { mean: 0, stdDev: 0 }
  const mean = values.reduce((sum, v) => sum + v, 0) / values.length
  const variance = values.reduce((sum, v) => sum + Math.pow(v - mean, 2), 0) / values.length
  const stdDev = Math.sqrt(variance)
  return { mean, stdDev }
}

function calculateGiniCoefficient(values) {
  if (values.length === 0) return 0
  const sorted = [...values].sort((a, b) => a - b)
  const n = sorted.length
  let sum = 0
  for (let i = 0; i < n; i++) {
    sum += (2 * (i + 1) - n - 1) * sorted[i]
  }
  const mean = sorted.reduce((a, b) => a + b, 0) / n
  return sum / (n * n * mean)
}

// Meeting type classification (keyword-based, expandable to embeddings later)
const MEETING_TYPE_KEYWORDS = {
  planning: ['planning', 'strategy', 'roadmap', 'quarterly', 'okr', 'goals'],
  standup: ['standup', 'daily', 'sync', 'check-in', 'status'],
  retrospective: ['retro', 'retrospective', 'postmortem', 'review'],
  brainstorm: ['brainstorm', 'ideation', 'workshop', 'design'],
  decision: ['decision', 'approval', 'sign-off', 'review']
}

function classifyMeeting(title) {
  if (!title) return 'other'
  const lower = title.toLowerCase()
  for (const [type, keywords] of Object.entries(MEETING_TYPE_KEYWORDS)) {
    if (keywords.some(kw => lower.includes(kw))) return type
  }
  return 'other'
}

// Filter to last 120 days (increased to capture full demo story from Nov 2025)
function filterRecent(items, dateField = 'createdAt', days = 120) {
  const cutoff = new Date()
  cutoff.setDate(cutoff.getDate() - days)
  cutoff.setHours(0, 0, 0, 0)
  
  return items.filter(item => {
    const dateStr = item[dateField]
    if (!dateStr) return false
    try {
      const date = new Date(dateStr)
      return date >= cutoff
    } catch {
      return false
    }
  })
}

// Pattern detection with statistical validity
function detectPatterns(meetings, actions) {
  const patterns = []
  
  // Minimum sample size requirement
  const MIN_MEETINGS = 5
  const MIN_ACTIONS = 10
  
  // Filter to last 120 days
  const recentMeetings = filterRecent(meetings)
  // For actions, use meetingDate instead of createdAt (actions inherit meeting date)
  const recentActions = filterRecent(actions, 'meetingDate')
  
  console.log('📊 Pattern Detection Filter Results:')
  console.log('  Recent meetings (120 days):', recentMeetings.length, '/', meetings.length)
  console.log('  Recent actions (120 days):', recentActions.length, '/', actions.length)
  console.log('  MIN_MEETINGS:', MIN_MEETINGS)
  console.log('  MIN_ACTIONS:', MIN_ACTIONS)
  
  if (recentMeetings.length < MIN_MEETINGS || recentActions.length < MIN_ACTIONS) {
    console.log('❌ Not enough data for pattern detection')
    console.log('  Need:', MIN_MEETINGS, 'meetings and', MIN_ACTIONS, 'actions')
    console.log('  Have:', recentMeetings.length, 'meetings and', recentActions.length, 'actions')
    return [] // Not enough data for meaningful analysis
  }
  
  console.log('✅ Enough data - proceeding with pattern detection')
  
  const sampleSize = `Based on ${recentMeetings.length} meetings and ${recentActions.length} actions in last 120 days`
  
  // Pattern 1: Planning Paralysis (statistically validated)
  const planningMeetings = recentMeetings.filter(m => classifyMeeting(m.title) === 'planning')
  if (planningMeetings.length >= 3) {
    const planningActions = recentActions.filter(a => 
      planningMeetings.some(m => m.meetingId === a.meetingId)
    )
    
    if (planningActions.length >= 5) {
      const completionRate = (planningActions.filter(a => a.completed).length / planningActions.length) * 100
      
      // Calculate team average completion rate for comparison
      const teamCompletionRate = (recentActions.filter(a => a.completed).length / recentActions.length) * 100
      
      // Detect if planning completion is significantly below team average
      if (completionRate < teamCompletionRate - 15) {
        patterns.push({
          id: 'planning-paralysis',
          name: 'Planning Paralysis',
          icon: '🔄',
          severity: 'high',
          color: '#e87a6a',
          symptoms: [
            `${planningMeetings.length} planning meetings in last 30 days`,
            `${Math.round(completionRate)}% completion vs ${Math.round(teamCompletionRate)}% team average`,
            'Planning actions underperforming team baseline'
          ],
          prescription: [
            'Set hard deadline for planning phase',
            'Limit planning meetings to 2 per month',
            'Require 1 executable action per planning meeting',
            'Use timeboxing: 25% plan, 75% execute'
          ],
          confidence: Math.min(planningActions.length / 20, 1),
          basedOn: sampleSize
        })
      }
    }
  }
  
  // Pattern 2: Action Item Amnesia (relative threshold)
  const incompleteRate = (recentActions.filter(a => !a.completed).length / recentActions.length) * 100
  
  // Industry benchmark: 67% completion rate (33% incomplete)
  const INDUSTRY_INCOMPLETE_RATE = 33
  
  if (incompleteRate > INDUSTRY_INCOMPLETE_RATE + 20) {
    patterns.push({
      id: 'action-amnesia',
      name: 'Action Item Amnesia',
      icon: '🧠',
      severity: 'critical',
      color: '#e87a6a',
      symptoms: [
        `${Math.round(incompleteRate)}% incomplete vs ${INDUSTRY_INCOMPLETE_RATE}% industry average`,
        'Significantly below industry completion standards',
        'Actions not being followed through'
      ],
      prescription: [
        'Send automated reminders 24h before deadline',
        'Review action items at start of each meeting',
        'Assign explicit owners (no "team" ownership)',
        'Use this tool\'s email notifications'
      ],
      confidence: Math.min(recentActions.length / 50, 1),
      basedOn: sampleSize
    })
  }
  
  // Pattern 3: Meeting Debt Spiral (statistical threshold)
  if (recentMeetings.length >= 8) {
    const actionsPerMeeting = recentMeetings.map(m => {
      return recentActions.filter(a => a.meetingId === m.meetingId).length
    })
    
    const { mean, stdDev } = calculateStats(actionsPerMeeting)
    
    // Detect if average is more than 1 std dev above mean
    if (mean > 4 && stdDev > 0 && mean > 3 + stdDev) {
      patterns.push({
        id: 'meeting-debt',
        name: 'Meeting Debt Spiral',
        icon: '�',
        severity: 'high',
        color: '#e8c06a',
        symptoms: [
          `Average ${mean.toFixed(1)} actions per meeting (σ=${stdDev.toFixed(1)})`,
          `${recentMeetings.length} meetings generating ${recentActions.length} actions`,
          'Action generation rate above sustainable threshold'
        ],
        prescription: [
          'Cancel recurring meetings with no outcomes',
          'Merge similar meetings',
          'Limit action items to 3 per meeting',
          'Use async updates instead of meetings'
        ],
        confidence: Math.min(recentMeetings.length / 15, 1),
        basedOn: sampleSize
      })
    }
  }
  
  // Pattern 4: Silent Majority (Gini coefficient)
  const ownerCounts = {}
  recentActions.forEach(a => {
    const owner = (a.owner || 'Unassigned').trim().toLowerCase()
    if (owner !== 'unassigned') {
      ownerCounts[owner] = (ownerCounts[owner] || 0) + 1
    }
  })
  
  const owners = Object.keys(ownerCounts)
  if (owners.length >= 3) {
    const counts = owners.map(o => ownerCounts[o])
    const gini = calculateGiniCoefficient(counts)
    
    // Gini > 0.4 indicates high inequality
    if (gini > 0.4) {
      const max = Math.max(...counts)
      const min = Math.min(...counts)
      
      patterns.push({
        id: 'silent-majority',
        name: 'Silent Majority',
        icon: '🤐',
        severity: 'medium',
        color: '#e8c06a',
        symptoms: [
          `Gini coefficient: ${gini.toFixed(2)} (>0.4 indicates high inequality)`,
          `Distribution: ${max} actions (most) vs ${min} actions (least)`,
          'Uneven contribution across team members'
        ],
        prescription: [
          'Round-robin action assignment',
          'Explicitly ask quiet members for input',
          'Rotate meeting facilitator role',
          'Use anonymous voting for decisions'
        ],
        confidence: Math.min(owners.length / 5, 1),
        basedOn: sampleSize
      })
    }
  }
  
  // Pattern 5: Chronic Blocker (exact string match only - semantic similarity needs backend)
  const taskCounts = {}
  recentActions.forEach(a => {
    const task = a.task?.toLowerCase().trim()
    if (task && task.length > 10) { // Ignore very short tasks
      taskCounts[task] = (taskCounts[task] || 0) + 1
    }
  })
  
  const duplicates = Object.entries(taskCounts)
    .filter(([_, count]) => count >= 3)
    .sort((a, b) => b[1] - a[1])
  
  if (duplicates.length > 0) {
    const [topTask, topCount] = duplicates[0]
    patterns.push({
      id: 'chronic-blocker',
      name: 'Chronic Blocker',
      icon: '🚧',
      severity: 'critical',
      color: '#e87a6a',
      symptoms: [
        `"${topTask.substring(0, 50)}${topTask.length > 50 ? '...' : ''}" repeated ${topCount} times`,
        'Same task appearing across multiple meetings',
        'Underlying issue not being resolved'
      ],
      prescription: [
        'Break down vague tasks into specific sub-tasks',
        'Identify root cause (resources? requirements? dependencies?)',
        'Escalate blockers to leadership',
        'Use 5 Whys technique to find real problem'
      ],
      confidence: Math.min(topCount / 5, 1),
      basedOn: sampleSize
    })
  }
  
  // Pattern 6: Ghost Meeting (zero output meetings)
  const ghostMeetings = recentMeetings.filter(m => {
    const meetingActions = recentActions.filter(a => a.meetingId === m.meetingId)
    const decisions = m.decisions || []
    return decisions.length === 0 && meetingActions.length === 0
  })
  
  if (ghostMeetings.length >= 2) {
    // Calculate cost: assume 5 attendees, 1 hour, $75/hour per person
    const avgAttendeesPerMeeting = 5
    const avgDurationHours = 1
    const costPerPersonPerHour = 75
    const totalCost = ghostMeetings.length * avgAttendeesPerMeeting * avgDurationHours * costPerPersonPerHour
    
    const ghostRate = (ghostMeetings.length / recentMeetings.length) * 100
    
    patterns.push({
      id: 'ghost-meeting',
      name: 'Ghost Meeting',
      icon: '👻',
      severity: 'high',
      color: '#8a8a74',
      symptoms: [
        `${ghostMeetings.length} meetings with zero decisions AND zero actions`,
        `${Math.round(ghostRate)}% of meetings produced nothing`,
        `Estimated cost: $${totalCost.toLocaleString()} in wasted time`
      ],
      prescription: [
        'Require agenda with clear objectives before meeting',
        'Cancel meetings that could be emails',
        'End meetings early if objectives are met',
        'Track meeting ROI: output value vs time cost'
      ],
      confidence: Math.min(ghostMeetings.length / 5, 1),
      basedOn: sampleSize
    })
  }
  
  return patterns
}

export default function PatternCards({ meetings }) {
  const [patterns, setPatterns] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [expanded, setExpanded] = useState({})
  const abortControllerRef = useRef(null)

  useEffect(() => {
    detectPatternsFromData()
    
    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort()
      }
    }
  }, [meetings])

  async function detectPatternsFromData() {
    try {
      abortControllerRef.current = new AbortController()
      const data = await getAllActions()
      const actions = data.actions || []
      
      // DEBUG: Log pattern detection inputs
      console.log('🔍 Pattern Detection Debug:')
      console.log('  Meetings passed:', meetings.length)
      console.log('  Actions fetched:', actions.length)
      console.log('  Sample meeting:', meetings[0])
      console.log('  Sample action:', actions[0])
      
      const detected = detectPatterns(meetings, actions)
      
      console.log('  Patterns detected:', detected.length)
      if (detected.length > 0) {
        console.log('  Pattern IDs:', detected.map(p => p.id))
      }
      
      setPatterns(detected)
    } catch (e) {
      if (e.name !== 'AbortError') {
        console.error('Pattern detection error:', e)
        setError('Failed to detect patterns')
      }
    } finally {
      setLoading(false)
    }
  }
  
  // Memoize pattern detection
  const memoizedPatterns = useMemo(() => patterns, [patterns])

  function toggleExpanded(patternId) {
    setExpanded(prev => ({
      ...prev,
      [patternId]: !prev[patternId]
    }))
  }

  if (loading) {
    return (
      <div style={s.loading}>
        <div style={s.spin}/>
      </div>
    )
  }

  if (error) {
    return <div style={s.error}>{error}</div>
  }

  if (memoizedPatterns.length === 0) {
    return (
      <div style={s.empty}>
        <p style={s.emptyIcon}>✨</p>
        <p style={s.emptyText}>No toxic patterns detected</p>
        <p style={s.emptySub}>Your meeting culture is healthy!</p>
      </div>
    )
  }

  return (
    <div style={s.root}>
      <div style={s.header}>
        <h3 style={s.title}>🔍 Pattern Detection</h3>
        <p style={s.subtitle}>Toxic meeting patterns identified</p>
      </div>
      
      <div style={s.list}>
        {memoizedPatterns.map((pattern, idx) => {
          const isExpanded = expanded[pattern.id]
          
          return (
            <div key={pattern.id} style={{...s.card,
              borderColor: pattern.color,
              animationDelay:`${idx*0.05}s`}}
              className="patterncard">
              <div style={s.cardHeader} onClick={() => toggleExpanded(pattern.id)}>
                <div style={s.cardLeft}>
                  <span style={s.icon}>{pattern.icon}</span>
                  <div>
                    <div style={s.nameRow}>
                      <span style={s.name}>{pattern.name}</span>
                      <span style={{...s.severity,
                        background: pattern.severity === 'critical' ? '#1a0e0e' :
                                   pattern.severity === 'high' ? '#1a140e' : '#1a1a0e',
                        color: pattern.color}}>
                        {pattern.severity.toUpperCase()}
                      </span>
                    </div>
                    <p style={s.symptom}>{pattern.symptoms[0]}</p>
                  </div>
                </div>
                <button style={s.expandBtn}>
                  {isExpanded ? '−' : '+'}
                </button>
              </div>
              
              {isExpanded && (
                <div style={s.cardBody}>
                  <div style={s.section}>
                    <p style={s.sectionTitle}>Symptoms</p>
                    <ul style={s.ul}>
                      {pattern.symptoms.map((symptom, i) => (
                        <li key={i} style={s.li}>{symptom}</li>
                      ))}
                    </ul>
                  </div>
                  
                  <div style={s.section}>
                    <p style={s.sectionTitle}>Prescription</p>
                    <ul style={s.ul}>
                      {pattern.prescription.map((rx, i) => (
                        <li key={i} style={s.li}>{rx}</li>
                      ))}
                    </ul>
                  </div>
                  
                  <div style={s.footer}>
                    <div style={s.footerItem}>
                      <span style={s.footerLabel}>Confidence:</span>
                      <span style={{...s.footerValue, color: pattern.confidence > 0.7 ? '#c8f04a' : '#e8c06a'}}>
                        {Math.round(pattern.confidence * 100)}%
                      </span>
                    </div>
                    <div style={s.footerItem}>
                      <span style={s.footerLabel}>Data:</span>
                      <span style={s.footerValue}>{pattern.basedOn}</span>
                    </div>
                  </div>
                </div>
              )}
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
        animation:'spin 1s linear infinite'},
  error:{padding:'12px', background:'#1a0e0e', border:'1px solid #4a2a2a',
         borderRadius:4, color:'#e87a6a', fontSize:11},
  empty:{padding:'40px 0', textAlign:'center'},
  emptyIcon:{fontSize:32, marginBottom:12},
  emptyText:{fontSize:13, color:'#8a8a74', marginBottom:4},
  emptySub:{fontSize:11, color:'#6b7260'},
  list:{display:'flex', flexDirection:'column', gap:12},
  card:{background:'#0f0f0c', border:'2px solid #2e2e22', borderRadius:6,
        overflow:'hidden', transition:'all 0.2s',
        animation:'fadeUp 0.3s ease both'},
  cardHeader:{padding:'14px 16px', display:'flex', justifyContent:'space-between',
              alignItems:'center', cursor:'pointer'},
  cardLeft:{display:'flex', alignItems:'flex-start', gap:12, flex:1},
  icon:{fontSize:24, lineHeight:1},
  nameRow:{display:'flex', alignItems:'center', gap:8, marginBottom:4},
  name:{fontSize:13, color:'#e8e4d0', letterSpacing:'0.01em', fontWeight:500},
  severity:{fontSize:8, letterSpacing:'0.15em', padding:'3px 8px',
            borderRadius:3, border:'1px solid'},
  symptom:{fontSize:11, color:'#8a8a74', lineHeight:1.5},
  expandBtn:{background:'none', border:'1px solid #3a3a2e', borderRadius:3,
             width:24, height:24, color:'#8a8a74', fontSize:16,
             cursor:'pointer', display:'flex', alignItems:'center',
             justifyContent:'center', lineHeight:1},
  cardBody:{padding:'0 16px 16px', borderTop:'1px solid #2a2a20'},
  section:{marginTop:16},
  sectionTitle:{fontSize:10, letterSpacing:'0.12em', color:'#c8f04a',
                textTransform:'uppercase', marginBottom:8},
  ul:{listStyle:'none', paddingLeft:0, display:'flex', flexDirection:'column', gap:6},
  li:{fontSize:11, color:'#8a8a74', lineHeight:1.6, paddingLeft:16,
      position:'relative'},
  footer:{marginTop:16, paddingTop:12, borderTop:'1px solid #2a2a20',
          display:'flex', flexDirection:'column', gap:12},
  footerItem:{display:'flex', flexDirection:'column', gap:4},
  footerLabel:{fontSize:9, letterSpacing:'0.1em', color:'#6b7260',
               textTransform:'uppercase'},
  footerValue:{fontSize:11, color:'#e8e4d0'},
}

// Add CSS for animations and pseudo-elements
const styleSheet = document.createElement('style')
styleSheet.textContent = `
  @keyframes spin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
  }
  
  @keyframes fadeUp {
    from {
      opacity: 0;
      transform: translateY(10px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }
  
  .patterncard li::before {
    content: '•';
    position: absolute;
    left: 0;
    color: #6b7260;
  }
`
if (!document.head.querySelector('style[data-pattern-cards]')) {
  styleSheet.setAttribute('data-pattern-cards', 'true')
  document.head.appendChild(styleSheet)
}
