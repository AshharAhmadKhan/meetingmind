import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { logout, checkSession, getUser } from '../utils/auth.js'
import { getDebtAnalytics } from '../utils/api.js'
import TeamSelector from '../components/TeamSelector.jsx'

function CountUp({ target, duration = 1500 }) {
  const [count, setCount] = useState(0)
  useEffect(() => {
    let start = 0
    const increment = target / (duration / 16)
    const timer = setInterval(() => {
      start += increment
      if (start >= target) {
        setCount(target)
        clearInterval(timer)
      } else {
        setCount(Math.floor(start))
      }
    }, 16)
    return () => clearInterval(timer)
  }, [target, duration])
  return <>{count.toLocaleString('en-US')}</>
}

function PieChart({ data }) {
  const total = Object.values(data).reduce((a, b) => a + b, 0)
  if (total === 0) return <div style={s.emptyChart}>No debt data</div>
  
  const colors = {
    forgotten: '#e87a6a',
    overdue: '#e8c06a',
    unassigned: '#8a8a74',
    atRisk: '#6a9ae8'
  }
  
  let currentAngle = 0
  const segments = Object.entries(data).map(([key, value]) => {
    const percentage = (value / total) * 100
    const angle = (value / total) * 360
    const startAngle = currentAngle
    currentAngle += angle
    
    return { key, value, percentage, startAngle, angle, color: colors[key] }
  })
  
  return (
    <div style={s.pieWrap}>
      <svg viewBox="0 0 200 200" style={s.pieSvg}>
        {segments.map((seg, i) => {
          const x1 = 100 + 90 * Math.cos((seg.startAngle - 90) * Math.PI / 180)
          const y1 = 100 + 90 * Math.sin((seg.startAngle - 90) * Math.PI / 180)
          const x2 = 100 + 90 * Math.cos((seg.startAngle + seg.angle - 90) * Math.PI / 180)
          const y2 = 100 + 90 * Math.sin((seg.startAngle + seg.angle - 90) * Math.PI / 180)
          const largeArc = seg.angle > 180 ? 1 : 0
          
          return (
            <path
              key={seg.key}
              d={`M 100 100 L ${x1} ${y1} A 90 90 0 ${largeArc} 1 ${x2} ${y2} Z`}
              fill={seg.color}
              opacity={0.9}
              style={{animation: `fadeIn 0.5s ease ${i * 0.1}s both`}}
            />
          )
        })}
        <circle cx="100" cy="100" r="50" fill="#0c0c09"/>
      </svg>
      <div style={s.pieLegend}>
        {segments.map(seg => (
          <div key={seg.key} style={s.legendItem}>
            <span style={{...s.legendDot, background: seg.color}}/>
            <span style={s.legendLabel}>{seg.key}</span>
            <span style={s.legendValue}>${seg.value.toLocaleString()}</span>
          </div>
        ))}
      </div>
    </div>
  )
}

function TrendChart({ data }) {
  if (!data || data.length === 0) return <div style={s.emptyChart}>No trend data</div>
  
  const max = Math.max(...data.map(d => d.debt), 1)
  const points = data.map((d, i) => {
    const x = (i / (data.length - 1)) * 280
    const y = 100 - (d.debt / max) * 80
    return { x, y, debt: d.debt, date: d.date }
  })
  
  const pathD = points.map((p, i) => 
    `${i === 0 ? 'M' : 'L'} ${p.x} ${p.y}`
  ).join(' ')
  
  return (
    <div style={s.trendWrap}>
      <svg viewBox="0 0 280 100" style={s.trendSvg}>
        <path d={pathD} stroke="#c8f04a" strokeWidth="2" fill="none"
          style={{animation: 'drawLine 1.5s ease both'}}/>
        {points.map((p, i) => (
          <circle key={i} cx={p.x} cy={p.y} r="3" fill="#c8f04a"
            style={{animation: `fadeIn 0.3s ease ${0.5 + i * 0.1}s both`}}/>
        ))}
      </svg>
      <div style={s.trendLabels}>
        {data.map((d, i) => (
          <span key={i} style={s.trendLabel}>
            {new Date(d.date).toLocaleDateString('en-US', {month: 'short', day: 'numeric'})}
          </span>
        ))}
      </div>
    </div>
  )
}

export default function DebtDashboard() {
  const navigate = useNavigate()
  const [user, setUser] = useState('')
  const [loading, setLoading] = useState(true)
  const [data, setData] = useState(null)
  const [error, setError] = useState('')
  const [selectedTeamId, setSelectedTeamId] = useState(null)

  useEffect(() => {
    checkSession().then(u => {
      if (!u) { navigate('/login'); return }
      setUser(getUser() || '')
      fetchData()
    })
  }, [selectedTeamId])

  async function fetchData() {
    try {
      const analytics = await getDebtAnalytics(selectedTeamId)
      setData(analytics)
    } catch (e) {
      setError(e.response?.data?.error || e.message || 'Failed to load analytics')
    } finally {
      setLoading(false)
    }
  }

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
          <button onClick={() => navigate('/')} style={s.backBtn}>
            ← Back to Meetings
          </button>
        </div>
        <div style={s.hdrR}>
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

        {loading ? (
          <div style={s.center}>
            <div style={{...s.spin, animation:'spin 1s linear infinite'}}/>
          </div>
        ) : error ? (
          <div style={s.errBox}>{error}</div>
        ) : data ? (
          <>
            <section style={s.hero}>
              <div style={s.heroContent}>
                <h1 style={s.heroTitle}>Meeting Debt Dashboard</h1>
                <p style={s.heroSub}>
                  Track the hidden cost of incomplete action items
                </p>
              </div>
              <div style={s.debtCard}>
                <div style={s.debtLabel}>TOTAL MEETING DEBT</div>
                <div style={s.debtAmount}>
                  $<CountUp target={data.totalDebt} />
                </div>
                <div style={s.debtMeta}>
                  {data.incompleteActions} incomplete action{data.incompleteActions !== 1 ? 's' : ''} × 
                  $240 avg cost
                </div>
              </div>
            </section>

            <div style={s.grid}>
              <div style={s.card}>
                <h3 style={s.cardTitle}>Debt Breakdown</h3>
                <PieChart data={data.breakdown} />
              </div>

              <div style={s.card}>
                <h3 style={s.cardTitle}>8-Week Trend</h3>
                <TrendChart data={data.trend} />
                <div style={s.velocity}>
                  <span style={s.velLabel}>Debt Velocity:</span>
                  <span style={{...s.velValue, color: data.debtVelocity > 0 ? '#e87a6a' : '#c8f04a'}}>
                    {data.debtVelocity > 0 ? '+' : ''}{data.debtVelocity.toLocaleString()}/week
                  </span>
                </div>
              </div>

              <div style={s.card}>
                <h3 style={s.cardTitle}>Completion Rate</h3>
                <div style={s.compWrap}>
                  <div style={s.compBar}>
                    <div style={s.compLabel}>Your Team</div>
                    <div style={s.compTrack}>
                      <div style={{...s.compFill, width: `${data.completionRate * 100}%`, background: '#c8f04a'}}/>
                    </div>
                    <div style={s.compPct}>{Math.round(data.completionRate * 100)}%</div>
                  </div>
                  <div style={s.compBar}>
                    <div style={s.compLabel}>Industry Avg</div>
                    <div style={s.compTrack}>
                      <div style={{...s.compFill, width: `${data.industryBenchmark * 100}%`, background: '#8a8a74'}}/>
                    </div>
                    <div style={s.compPct}>{Math.round(data.industryBenchmark * 100)}%</div>
                  </div>
                </div>
                {data.completionRate > data.industryBenchmark && (
                  <div style={s.badge}>
                    ✓ Above industry average
                  </div>
                )}
              </div>

              <div style={s.card}>
                <h3 style={s.cardTitle}>Action Items Summary</h3>
                <div style={s.stats}>
                  <div style={s.stat}>
                    <div style={s.statNum}>{data.totalActions}</div>
                    <div style={s.statLabel}>Total Actions</div>
                  </div>
                  <div style={s.stat}>
                    <div style={{...s.statNum, color: '#c8f04a'}}>{data.completedActions}</div>
                    <div style={s.statLabel}>Completed</div>
                  </div>
                  <div style={s.stat}>
                    <div style={{...s.statNum, color: '#e87a6a'}}>{data.incompleteActions}</div>
                    <div style={s.statLabel}>Incomplete</div>
                  </div>
                </div>
              </div>

              <div style={{...s.card, gridColumn: '1 / -1'}}>
                <h3 style={s.cardTitle}>Quick Wins</h3>
                <div style={s.wins}>
                  {data.breakdown.forgotten > 0 && (
                    <div style={s.win}>
                      <span style={s.winIcon}>⚠️</span>
                      <div>
                        <div style={s.winTitle}>Address Forgotten Items</div>
                        <div style={s.winDesc}>
                          ${data.breakdown.forgotten.toLocaleString()} in debt from items over 30 days old
                        </div>
                      </div>
                    </div>
                  )}
                  {data.breakdown.unassigned > 0 && (
                    <div style={s.win}>
                      <span style={s.winIcon}>👤</span>
                      <div>
                        <div style={s.winTitle}>Assign Owners</div>
                        <div style={s.winDesc}>
                          ${data.breakdown.unassigned.toLocaleString()} in unassigned action items
                        </div>
                      </div>
                    </div>
                  )}
                  {data.breakdown.overdue > 0 && (
                    <div style={s.win}>
                      <span style={s.winIcon}>⏰</span>
                      <div>
                        <div style={s.winTitle}>Clear Overdue Tasks</div>
                        <div style={s.winDesc}>
                          ${data.breakdown.overdue.toLocaleString()} in past-deadline items
                        </div>
                      </div>
                    </div>
                  )}
                  {data.breakdown.forgotten === 0 && data.breakdown.unassigned === 0 && data.breakdown.overdue === 0 && (
                    <div style={s.win}>
                      <span style={s.winIcon}>✨</span>
                      <div>
                        <div style={s.winTitle}>Great Job!</div>
                        <div style={s.winDesc}>No critical debt items. Keep up the momentum.</div>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </>
        ) : null}
      </main>
    </div>
  )
}

const css = `
  @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=DM+Mono:wght@300;400&display=swap');
  *{box-sizing:border-box;margin:0;padding:0;}
  body{background:#0c0c09;}
  @keyframes fadeIn{from{opacity:0}to{opacity:1}}
  @keyframes spin{to{transform:rotate(360deg)}}
  @keyframes drawLine{from{stroke-dasharray:1000;stroke-dashoffset:1000}to{stroke-dasharray:1000;stroke-dashoffset:0}}
  .signout:hover{color:#f0ece0 !important;border-color:#6b7260 !important;}
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
  backBtn:{background:'none', border:'1px solid #3a3a2e', borderRadius:3,
           padding:'5px 12px', color:'#8a8a74', fontSize:10, letterSpacing:'0.1em',
           cursor:'pointer', fontFamily:"'DM Mono',monospace",
           transition:'color 0.15s, border-color 0.15s'},
  hdrR: {display:'flex', alignItems:'center', gap:14},
  userTxt:{fontSize:11, letterSpacing:'0.06em', color:'#8a8a74'},
  signOut:{background:'none', border:'1px solid #3a3a2e', borderRadius:3,
           padding:'5px 12px', color:'#8a8a74', fontSize:10, letterSpacing:'0.1em',
           cursor:'pointer', fontFamily:"'DM Mono',monospace",
           transition:'color 0.15s, border-color 0.15s'},
  main: {padding:'48px 36px', maxWidth:1400, margin:'0 auto'},
  center:{display:'flex', alignItems:'center', justifyContent:'center', padding:'80px 0'},
  spin:  {width:20, height:20, border:'2px solid #2a2a20',
          borderTopColor:'#c8f04a', borderRadius:'50%'},
  errBox:{background:'#1a0e0e', border:'1px solid #4a2a2a', borderRadius:4,
          padding:'10px 12px', color:'#e87a6a', fontSize:11, marginBottom:16},
  hero: {display:'flex', justifyContent:'space-between', alignItems:'center',
         marginBottom:48, gap:32},
  heroContent:{flex:1},
  heroTitle:{fontFamily:"'Playfair Display',serif", fontSize:42, fontWeight:900,
             color:'#f0ece0', marginBottom:8, letterSpacing:'-0.5px'},
  heroSub:{fontSize:14, color:'#8a8a74', letterSpacing:'0.02em'},
  debtCard:{background:'#141410', border:'2px solid #c8f04a', borderRadius:12,
            padding:'24px 28px', minWidth:320},
  debtLabel:{fontSize:9, letterSpacing:'0.15em', color:'#8a8a74',
             textTransform:'uppercase', marginBottom:12},
  debtAmount:{fontFamily:"'Playfair Display',serif", fontSize:52, fontWeight:900,
              color:'#c8f04a', lineHeight:1, marginBottom:8},
  debtMeta:{fontSize:11, color:'#6b7260', letterSpacing:'0.03em'},
  grid: {display:'grid', gridTemplateColumns:'repeat(2, 1fr)', gap:24},
  card: {background:'#111108', border:'1px solid #2a2a20', borderRadius:8,
         padding:'24px', animation:'fadeIn 0.5s ease both'},
  cardTitle:{fontFamily:"'Playfair Display',serif", fontSize:18, fontWeight:700,
             color:'#f0ece0', marginBottom:20},
  emptyChart:{padding:'40px 0', textAlign:'center', color:'#555548', fontSize:12},
  pieWrap:{display:'flex', gap:32, alignItems:'center'},
  pieSvg:{width:200, height:200, flexShrink:0},
  pieLegend:{flex:1, display:'flex', flexDirection:'column', gap:12},
  legendItem:{display:'flex', alignItems:'center', gap:10},
  legendDot:{width:12, height:12, borderRadius:'50%', flexShrink:0},
  legendLabel:{fontSize:11, color:'#8a8a74', textTransform:'capitalize', flex:1},
  legendValue:{fontSize:12, color:'#f0ece0', fontWeight:400},
  trendWrap:{},
  trendSvg:{width:'100%', height:100, marginBottom:12},
  trendLabels:{display:'flex', justifyContent:'space-between'},
  trendLabel:{fontSize:9, color:'#6b7260'},
  velocity:{marginTop:16, paddingTop:16, borderTop:'1px solid #2a2a20',
            display:'flex', justifyContent:'space-between', alignItems:'center'},
  velLabel:{fontSize:11, color:'#8a8a74'},
  velValue:{fontSize:13, fontWeight:400},
  compWrap:{display:'flex', flexDirection:'column', gap:20},
  compBar:{},
  compLabel:{fontSize:11, color:'#8a8a74', marginBottom:8},
  compTrack:{height:8, background:'#2a2a20', borderRadius:4, overflow:'hidden'},
  compFill:{height:'100%', borderRadius:4, transition:'width 1.5s ease'},
  compPct:{fontSize:12, color:'#f0ece0', marginTop:6},
  badge:{marginTop:16, padding:'8px 12px', background:'#141a09',
         border:'1px solid #3a4a18', borderRadius:4, color:'#c8f04a',
         fontSize:11, textAlign:'center'},
  stats:{display:'flex', gap:24},
  stat:{flex:1, textAlign:'center'},
  statNum:{fontFamily:"'Playfair Display',serif", fontSize:32, fontWeight:900,
           color:'#f0ece0', marginBottom:6},
  statLabel:{fontSize:10, color:'#8a8a74', letterSpacing:'0.1em', textTransform:'uppercase'},
  wins:{display:'flex', flexDirection:'column', gap:16},
  win:{display:'flex', gap:16, padding:'16px', background:'#0f0f0c',
       border:'1px solid #2a2a20', borderRadius:6},
  winIcon:{fontSize:24, flexShrink:0},
  winTitle:{fontSize:13, color:'#f0ece0', marginBottom:4},
  winDesc:{fontSize:11, color:'#8a8a74', lineHeight:1.5},
}
