import React from 'react'

// Reusable skeleton components with SUBTLE WHITE SHIMMER (minimal & elegant)

export function MeetingCardSkeleton() {
  return (
    <div style={s.card}>
      <div style={s.shimmerWave}/>
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
      <div style={s.shimmerWave}/>
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
      <div style={s.shimmerWave}/>
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
    background:'#1a1a14', 
    border:'1px solid #3a3a2e', 
    borderRadius:6,
    padding:'14px 16px',
    position:'relative',
    overflow:'hidden'
  },
  shimmerWave: {
    position:'absolute',
    top:0, left:'-100%', right:0, bottom:0,
    background:'linear-gradient(90deg, transparent, rgba(255,255,255,0.08), transparent)',
    animation:'shimmerSlide 2s infinite',
    zIndex:2,
    pointerEvents:'none'
  },
  top: {display:'flex', justifyContent:'space-between', alignItems:'center', marginBottom:8, position:'relative', zIndex:1},
  bottom: {display:'flex', justifyContent:'space-between', alignItems:'center', position:'relative', zIndex:1},
  bar: {
    height:14, 
    background:'#3a3a3a',
    borderRadius:3,
    position:'relative',
    zIndex:1
  },
  circle: {
    width:20, height:20, 
    background:'#3a3a3a',
    borderRadius:'50%',
    position:'relative',
    zIndex:1
  },
  actionCard: {
    background:'#1a1a14', 
    border:'1px solid #3a3a2e', 
    borderRadius:6,
    padding:'12px 14px',
    position:'relative',
    overflow:'hidden'
  },
  actionTop: {display:'flex', justifyContent:'space-between', alignItems:'flex-start', position:'relative', zIndex:1},
  actionLeft: {display:'flex', gap:12, flex:1},
  checkbox: {
    width:16, height:16, 
    background:'#3a3a3a',
    borderRadius:3,
    position:'relative',
    zIndex:1
  },
  metaRow: {display:'flex', gap:12},
  badge: {
    width:50, height:20, 
    background:'#3a3a3a',
    borderRadius:3,
    position:'relative',
    zIndex:1
  },
  tombstone: {
    background:'#1a1a14', 
    border:'1px solid #3a3a2e', 
    borderRadius:8,
    padding:'20px',
    position:'relative',
    overflow:'hidden'
  },
  tombTop: {display:'flex', justifyContent:'space-between', alignItems:'center', marginBottom:16, position:'relative', zIndex:1},
  tombIcon: {
    width:32, height:32, 
    background:'#3a3a3a',
    borderRadius:'50%',
    position:'relative',
    zIndex:1
  },
  tombBody: {marginBottom:16, position:'relative', zIndex:1},
  metaGrid: {
    display:'grid', gridTemplateColumns:'1fr 1fr', gap:8,
    paddingTop:12, borderTop:'1px solid #2a2a20'
  },
  statItem: {display:'flex', flexDirection:'column', alignItems:'center'},
}
