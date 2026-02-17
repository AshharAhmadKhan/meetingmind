import React, { useState, useEffect } from 'react'
import { getAllActions } from '../utils/api.js'

// Pattern detection logic (mock - will use Bedrock later)
function detectPatterns(meetings, actions) {
  const patterns = []
  
  // Pattern 1: Planning Paralysis
  // Symptom: Many meetings with "planning" in title, low action completion
  const planningMeetings = meetings.filter(m => 
    m.title?.toLowerCase().includes('planning') || 
    m.title?.toLowerCase().includes('strategy')
  )
  if (planningMeetings.length >= 3) {
    const planningActions = actions.filter(a => 
      planningMeetings.some(m => m.meetingId === a.meetingId)
    )
    const completionRate = planningActions.length > 0
      ? (planningActions.filter(a => a.completed).length / planningActions.length) * 100
      : 0
    
    if (completionRate < 50) {
      patterns.push({
        id: 'planning-paralysis',
        name: 'Planning Paralysis',
        icon: '🔄',
        severity: 'high',
        color: '#e87a6a',
        symptoms: [
          `${planningMeetings.length} planning meetings detected`,
          `Only ${Math.round(completionRate)}% of planning actions completed`,
          'Team stuck in analysis mode'
        ],
        prescription: [
          'Set hard deadline for planning phase',
          'Limit planning meetings to 2 per quarter',
          'Require 1 executable action per planning meeting',
          'Use timeboxing: 25% plan, 75% execute'
        ],
        impact: 'High - Reduces time-to-market by 40%',
        successRate: 78
      })
    }
  }
  
  // Pattern 2: Action Item Amnesia
  // Symptom: High percentage of incomplete actions
  const incompleteRate = actions.length > 0
    ? (actions.filter(a => !a.completed).length / actions.length) * 100
    : 0
  
  if (incompleteRate > 70) {
    patterns.push({
      id: 'action-amnesia',
      name: 'Action Item Amnesia',
      icon: '🧠',
      severity: 'critical',
      color: '#e87a6a',
      symptoms: [
        `${Math.round(incompleteRate)}% of actions incomplete`,
        'Team forgets commitments after meetings',
        'No follow-through on decisions'
      ],
      prescription: [
        'Send automated reminders 24h before deadline',
        'Review action items at start of each meeting',
        'Assign explicit owners (no "team" ownership)',
        'Use this tool\'s email notifications'
      ],
      impact: 'Critical - Improves execution by 60%',
      successRate: 85
    })
  }
  
  // Pattern 3: Meeting Debt Spiral
  // Symptom: Many meetings, high debt
  if (meetings.length >= 10) {
    const avgActionsPerMeeting = actions.length / meetings.length
    if (avgActionsPerMeeting > 5) {
      patterns.push({
        id: 'meeting-debt',
        name: 'Meeting Debt Spiral',
        icon: '💸',
        severity: 'high',
        color: '#e8c06a',
        symptoms: [
          `${meetings.length} meetings generating ${actions.length} actions`,
          `Average ${Math.round(avgActionsPerMeeting)} actions per meeting`,
          'Team drowning in commitments'
        ],
        prescription: [
          'Cancel recurring meetings with no outcomes',
          'Merge similar meetings (e.g., all planning into one)',
          'Limit action items to 3 per meeting',
          'Use async updates instead of meetings'
        ],
        impact: 'High - Frees up 30% of calendar time',
        successRate: 72
      })
    }
  }
  
  // Pattern 4: Silent Majority
  // Symptom: Uneven action distribution
  const ownerCounts = {}
  actions.forEach(a => {
    const owner = a.owner || 'Unassigned'
    ownerCounts[owner] = (ownerCounts[owner] || 0) + 1
  })
  
  const owners = Object.keys(ownerCounts).filter(o => o !== 'Unassigned')
  if (owners.length >= 3) {
    const counts = owners.map(o => ownerCounts[o])
    const max = Math.max(...counts)
    const min = Math.min(...counts)
    const ratio = max / min
    
    if (ratio > 3) {
      patterns.push({
        id: 'silent-majority',
        name: 'Silent Majority',
        icon: '🤐',
        severity: 'medium',
        color: '#e8c06a',
        symptoms: [
          `Uneven distribution: ${max} actions for one person, ${min} for another`,
          'Some team members not contributing',
          'Same people always volunteering'
        ],
        prescription: [
          'Round-robin action assignment',
          'Explicitly ask quiet members for input',
          'Rotate meeting facilitator role',
          'Use anonymous voting for decisions'
        ],
        impact: 'Medium - Increases team engagement by 45%',
        successRate: 68
      })
    }
  }
  
  // Pattern 5: Chronic Blocker
  // Symptom: Duplicate actions (from Day 5 data)
  const taskCounts = {}
  actions.forEach(a => {
    const task = a.task?.toLowerCase().trim()
    if (task) {
      taskCounts[task] = (taskCounts[task] || 0) + 1
    }
  })
  
  const duplicates = Object.entries(taskCounts).filter(([_, count]) => count >= 3)
  if (duplicates.length > 0) {
    const [topTask, topCount] = duplicates[0]
    patterns.push({
      id: 'chronic-blocker',
      name: 'Chronic Blocker',
      icon: '🚧',
      severity: 'critical',
      color: '#e87a6a',
      symptoms: [
        `"${topTask}" repeated ${topCount} times`,
        'Same tasks keep appearing in meetings',
        'Underlying issue not being addressed'
      ],
      prescription: [
        'Break down vague tasks into specific sub-tasks',
        'Identify root cause (lack of resources? unclear requirements?)',
        'Escalate blockers to leadership',
        'Use 5 Whys technique to find real problem'
      ],
      impact: 'Critical - Unblocks 50% of stalled work',
      successRate: 82
    })
  }
  
  return patterns
}

export default function PatternCards({ meetings }) {
  const [patterns, setPatterns] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [expanded, setExpanded] = useState({})

  useEffect(() => {
    detectPatternsFromData()
  }, [meetings])

  async function detectPatternsFromData() {
    try {
      const data = await getAllActions()
      const actions = data.actions || []
      const detected = detectPatterns(meetings, actions)
      setPatterns(detected)
    } catch (e) {
      setError('Failed to detect patterns')
    } finally {
      setLoading(false)
    }
  }

  function toggleExpanded(patternId) {
    setExpanded(prev => ({
      ...prev,
      [patternId]: !prev[patternId]
    }))
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

  if (patterns.length === 0) {
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
        {patterns.map((pattern, idx) => {
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
                      <span style={s.footerLabel}>Impact:</span>
                      <span style={s.footerValue}>{pattern.impact}</span>
                    </div>
                    <div style={s.footerItem}>
                      <span style={s.footerLabel}>Success Rate:</span>
                      <span style={{...s.footerValue, color:'#c8f04a'}}>
                        {pattern.successRate}%
                      </span>
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
        borderTopColor:'#c8f04a', borderRadius:'50%'},
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
      position:'relative',
      '::before':{content:'"•"', position:'absolute', left:0, color:'#6b7260'}},
  footer:{marginTop:16, paddingTop:12, borderTop:'1px solid #2a2a20',
          display:'flex', gap:24},
  footerItem:{display:'flex', flexDirection:'column', gap:4},
  footerLabel:{fontSize:9, letterSpacing:'0.1em', color:'#6b7260',
               textTransform:'uppercase'},
  footerValue:{fontSize:11, color:'#e8e4d0'},
}
