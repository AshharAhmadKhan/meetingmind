import React from 'react'

// Reusable skeleton components for loading states

export function MeetingCardSkeleton() {
  return (
    <div style={s.card}>
      <div style={s.top}>
        <div style={{...s.bar, width:'60%'}}/>
        <div style={{...s.circle}}/>
      </div>
      <div style={s.bottom}>
        <div style={{...s.bar, width:'30%', height:8}}/>
        <div style={{...s.bar, width:'25%', height:8}}/>
      </div>
      <div style={{...s.bar, width:'85%', height:10, marginTop:12}}/>
      <div style={{...s.bar, width:'70%', height:10, marginTop:6}}/>
    </div>
  )
}

export function ActionItemSkeleton() {
  return (
    <div style={s.actionCard}>
      <div style={s.actionTop}>
        <div style={s.actionLeft}>
          <div style={s.checkbox}/>
          <div style={{flex:1}}>
            <div style={{...s.bar, width:'70%', marginBottom:8}}/>
            <div style={s.metaRow}>
              <div style={{...s.bar, width:80, height:8}}/>
              <div style={{...s.bar, width:100, height:8}}/>
            </div>
          </div>
        </div>
        <div style={{...s.badge}}/>
      </div>
    </div>
  )
}

export function EpitaphCardSkeleton() {
  return (
    <div style={s.tombstone}>
      <div style={s.tombTop}>
        <div style={s.tombIcon}/>
        <div style={{...s.bar, width:60, height:12}}/>
      </div>
      <div style={s.tombBody}>
        <div style={{...s.bar, width:'40%', height:10, marginBottom:12}}/>
        <div style={{...s.bar, width:'90%', height:12, marginBottom:8}}/>
        <div style={{...s.bar, width:'75%', height:12, marginBottom:16}}/>
        <div style={s.metaGrid}>
          <div style={{...s.bar, width:'100%', height:8}}/>
          <div style={{...s.bar, width:'100%', height:8}}/>
          <div style={{...s.bar, width:'100%', height:8}}/>
          <div style={{...s.bar, width:'100%', height:8}}/>
        </div>
      </div>
    </div>
  )
}

export function StatsCardSkeleton() {
  return (
    <div style={s.statItem}>
      <div style={{...s.bar, width:40, height:32, marginBottom:4}}/>
      <div style={{...s.bar, width:60, height:8}}/>
    </div>
  )
}

const s = {
  card: {
    background:'#141410', border:'1px solid #2e2e22', borderRadius:6,
    padding:'14px 16px', animation:'pulse 1.5s ease-in-out infinite'
  },
  top: {display:'flex', justifyContent:'space-between', alignItems:'center', marginBottom:8},
  bottom: {display:'flex', justifyContent:'space-between', alignItems:'center'},
  bar: {
    height:14, background:'#2a2a24', borderRadius:3,
    animation:'shimmer 1.5s ease-in-out infinite'
  },
  circle: {
    width:20, height:20, background:'#2a2a24', borderRadius:'50%',
    animation:'shimmer 1.5s ease-in-out infinite'
  },
  actionCard: {
    background:'#141410', border:'1px solid #2e2e22', borderRadius:6,
    padding:'12px 14px', animation:'pulse 1.5s ease-in-out infinite'
  },
  actionTop: {display:'flex', justifyContent:'space-between', alignItems:'flex-start'},
  actionLeft: {display:'flex', gap:12, flex:1},
  checkbox: {
    width:16, height:16, background:'#2a2a24', borderRadius:3,
    animation:'shimmer 1.5s ease-in-out infinite'
  },
  metaRow: {display:'flex', gap:12},
  badge: {
    width:50, height:20, background:'#2a2a24', borderRadius:3,
    animation:'shimmer 1.5s ease-in-out infinite'
  },
  tombstone: {
    background:'#111108', border:'1px solid #2a2a20', borderRadius:8,
    padding:'20px', animation:'pulse 1.5s ease-in-out infinite'
  },
  tombTop: {display:'flex', justifyContent:'space-between', alignItems:'center', marginBottom:16},
  tombIcon: {
    width:32, height:32, background:'#2a2a24', borderRadius:'50%',
    animation:'shimmer 1.5s ease-in-out infinite'
  },
  tombBody: {marginBottom:16},
  metaGrid: {
    display:'grid', gridTemplateColumns:'1fr 1fr', gap:8,
    paddingTop:12, borderTop:'1px solid #2a2a20'
  },
  statItem: {display:'flex', flexDirection:'column', alignItems:'center'},
}

// Add CSS animations
const style = document.createElement('style')
style.textContent = `
  @keyframes shimmer {
    0%, 100% { opacity: 0.4; }
    50% { opacity: 0.7; }
  }
  @keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.8; }
  }
`
document.head.appendChild(style)
