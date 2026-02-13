import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { login, checkSession } from '../utils/auth.js'

export default function LoginPage() {
  const navigate  = useNavigate()
  const [email,    setEmail]    = useState('')
  const [password, setPassword] = useState('')
  const [error,    setError]    = useState('')
  const [loading,  setLoading]  = useState(false)

  useEffect(() => {
    checkSession().then(u => { if (u) navigate('/') })
  }, [])

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await login(email, password)
      await checkSession()
      navigate('/')
    } catch (err) {
      setError(err.message || 'Invalid credentials.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={s.root}>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,700;0,900;1,400&family=DM+Mono:wght@300;400&display=swap');
        *{box-sizing:border-box;margin:0;padding:0;}
        body{background:#0c0c09;}
        @keyframes fadeUp{from{opacity:0;transform:translateY(16px)}to{opacity:1;transform:translateY(0)}}
        @keyframes ticker{0%{transform:translateX(0)}100%{transform:translateX(-50%)}}
        .inp:focus{outline:none;}
        .inp::placeholder{color:#555548;}
        input:-webkit-autofill{
          -webkit-box-shadow:0 0 0 100px #1a1a14 inset !important;
          -webkit-text-fill-color:#f5f0e8 !important;
        }
        .submit-btn:hover:not(:disabled){background:#d4f55a !important;}
        .submit-btn:disabled{opacity:0.5;cursor:not-allowed;}
      `}</style>

      {/* ── LEFT: brand panel ── */}
      <div style={s.left}>

        <div style={s.topLabel}>
          <span style={s.dot}/> AI Meeting Intelligence — ap-south-1
        </div>

        <div style={s.hero}>
          <div style={{...s.h, animationDelay:'0.05s'}}>Every</div>
          <div style={{...s.h, animationDelay:'0.15s'}}>meeting,</div>
          <div style={{...s.hi, animationDelay:'0.25s'}}>remembered.</div>
        </div>

        <div style={s.stats}>
          {[
            {n:'5 hrs', l:'saved per person weekly'},
            {n:'100%',  l:'action items captured'},
            {n:'< 90s', l:'to structured summary'},
          ].map(({n,l}) => (
            <div key={n} style={s.stat}>
              <span style={s.statN}>{n}</span>
              <span style={s.statL}>{l}</span>
            </div>
          ))}
        </div>

        {/* sample meeting card — shows outcome */}
        <div style={s.sampleCard}>
          <div style={s.sampleTop}>
            <span style={s.sampleLabel}>LATEST SUMMARY</span>
            <span style={s.sampleDone}>● DONE</span>
          </div>
          <p style={s.sampleTitle}>Q1 Planning — Product &amp; Eng</p>
          <div style={s.sampleItems}>
            {[
              {done:true,  t:'Finalize API contract',   o:'Ashhar'},
              {done:true,  t:'Review cost projections',  o:'Priya'},
              {done:false, t:'Send updated roadmap deck', o:'Unassigned'},
            ].map((a,i) => (
              <div key={i} style={s.sampleItem}>
                <span style={{...s.sampleCheck, color: a.done ? '#c8f04a' : '#333328'}}>
                  {a.done ? '✓' : '○'}
                </span>
                <span style={{...s.sampleText, textDecoration: a.done ? 'line-through' : 'none',
                  color: a.done ? '#444438' : '#888878'}}>
                  {a.t}
                </span>
                <span style={s.sampleOwner}>{a.o}</span>
              </div>
            ))}
          </div>
        </div>

        <div style={s.tickerWrap}>
          <div style={s.tickerTrack}>
            {[0,1].map(i => (
              <span key={i} style={{display:'inline-flex',gap:0}}>
                {['TRANSCRIBE','ANALYZE','EXTRACT','REMIND','TRACK','SUMMARIZE'].map(w => (
                  <span key={w} style={s.tw}>{w} <span style={{color:'#c8f04a',marginLeft:20}}>◆</span>&nbsp;&nbsp;&nbsp;&nbsp;</span>
                ))}
              </span>
            ))}
          </div>
        </div>
      </div>

      {/* ── RIGHT: form panel ── */}
      <div style={s.right}>
        <div style={s.formWrap}>

          <div style={s.logo}>
            <span style={s.logoAccent}>M</span>
            <span style={s.logoRest}>eetingMind</span>
          </div>

          <h2 style={s.formH}>Sign in</h2>
          <p style={s.formSub}>Access your meeting workspace</p>

          {error && <div style={s.err}>{error}</div>}

          <form onSubmit={handleSubmit} style={s.form}>

            <div style={s.fGroup}>
              <label style={s.label}>EMAIL ADDRESS</label>
              <input
                className="inp"
                type="email"
                value={email}
                onChange={e => setEmail(e.target.value)}
                placeholder="you@company.com"
                required
                style={s.input}
              />
            </div>

            <div style={s.fGroup}>
              <label style={s.label}>PASSWORD</label>
              <input
                className="inp"
                type="password"
                value={password}
                onChange={e => setPassword(e.target.value)}
                placeholder="Enter your password"
                required
                style={s.input}
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="submit-btn"
              style={s.btn}
            >
              {loading ? 'Signing in…' : 'Sign in →'}
            </button>

          </form>

          {/* trust anchor */}
          <div style={s.trust}>
            <div style={s.trustRow}>
              <span style={s.trustIcon}>🔒</span>
              <span style={s.trustText}>Private by default. Audio processed and discarded.</span>
            </div>
            <div style={s.trustRow}>
              <span style={s.trustIcon}>⚡</span>
              <span style={s.trustText}>Powered by AWS Bedrock · Runs on ap-south-1</span>
            </div>
          </div>

        </div>
      </div>
    </div>
  )
}

const s = {
  root:    {display:'flex', minHeight:'100vh', background:'#0c0c09', fontFamily:"'DM Mono',monospace"},

  /* LEFT */
  left:    {flex:1, background:'#0e0e0b', borderRight:'1px solid #222218',
            display:'flex', flexDirection:'column', justifyContent:'space-between',
            padding:'44px 48px', overflow:'hidden'},
  topLabel:{display:'flex', alignItems:'center', gap:8, fontSize:10,
            letterSpacing:'0.14em', color:'#38382e', textTransform:'uppercase',
            animation:'fadeUp 0.5s ease both'},
  dot:     {width:6, height:6, borderRadius:'50%', background:'#c8f04a', flexShrink:0},

  hero:    {flex:1, display:'flex', flexDirection:'column', justifyContent:'center', paddingTop:32},
  h:       {fontFamily:"'Playfair Display',serif", fontSize:'clamp(56px,7vw,108px)',
            fontWeight:900, color:'#f5f0e8', lineHeight:0.93, letterSpacing:'-2px',
            animation:'fadeUp 0.65s ease both'},
  hi:      {fontFamily:"'Playfair Display',serif", fontStyle:'italic',
            fontSize:'clamp(56px,7vw,108px)', fontWeight:400, color:'#c8f04a',
            lineHeight:1.05, letterSpacing:'-2px', animation:'fadeUp 0.65s ease both'},

  stats:   {display:'flex', gap:36, paddingBottom:28, animation:'fadeUp 0.65s ease 0.3s both'},
  stat:    {display:'flex', flexDirection:'column', gap:3},
  statN:   {fontFamily:"'Playfair Display',serif", fontSize:26, fontWeight:700,
            color:'#f5f0e8', letterSpacing:'-0.5px'},
  statL:   {fontSize:10, letterSpacing:'0.08em', color:'#38382e', textTransform:'uppercase'},

  /* sample card */
  sampleCard: {background:'#131310', border:'1px solid #222218', borderRadius:8,
               padding:'16px 18px', marginBottom:24,
               animation:'fadeUp 0.65s ease 0.4s both'},
  sampleTop:  {display:'flex', justifyContent:'space-between', alignItems:'center', marginBottom:10},
  sampleLabel:{fontSize:9, letterSpacing:'0.15em', color:'#38382e', textTransform:'uppercase'},
  sampleDone: {fontSize:9, letterSpacing:'0.1em', color:'#c8f04a'},
  sampleTitle:{fontSize:13, color:'#888878', marginBottom:12, letterSpacing:'0.02em'},
  sampleItems:{display:'flex', flexDirection:'column', gap:7},
  sampleItem: {display:'flex', alignItems:'center', gap:8},
  sampleCheck:{fontSize:12, fontWeight:700, width:14, flexShrink:0},
  sampleText: {flex:1, fontSize:11, letterSpacing:'0.02em'},
  sampleOwner:{fontSize:9, color:'#333328', letterSpacing:'0.08em'},

  tickerWrap: {overflow:'hidden', borderTop:'1px solid #1a1a14', paddingTop:14},
  tickerTrack:{display:'flex', whiteSpace:'nowrap', animation:'ticker 22s linear infinite'},
  tw:         {fontSize:10, letterSpacing:'0.14em', color:'#222218', textTransform:'uppercase'},

  /* RIGHT */
  right:   {width:460, display:'flex', alignItems:'center', justifyContent:'center',
            padding:'48px 44px', background:'#111110'},
  formWrap:{width:'100%', maxWidth:340, animation:'fadeUp 0.7s ease 0.15s both'},

  logo:     {display:'flex', alignItems:'baseline', gap:1, marginBottom:44},
  logoAccent:{fontFamily:"'Playfair Display',serif", fontSize:28, fontWeight:900, color:'#c8f04a'},
  logoRest:  {fontFamily:"'Playfair Display',serif", fontSize:22, fontWeight:700, color:'#f5f0e8'},

  formH:   {fontFamily:"'Playfair Display',serif", fontSize:30, fontWeight:700,
            color:'#f5f0e8', letterSpacing:'-0.5px', marginBottom:6},
  formSub: {fontSize:11, letterSpacing:'0.08em', color:'#666658', marginBottom:32,
            textTransform:'uppercase'},

  err:     {background:'rgba(239,68,68,0.08)', border:'1px solid rgba(239,68,68,0.18)',
            borderRadius:4, padding:'9px 12px', color:'#fca5a5',
            fontSize:11, marginBottom:20, letterSpacing:'0.03em'},

  form:    {display:'flex', flexDirection:'column', gap:24},
  fGroup:  {display:'flex', flexDirection:'column', gap:8},
  label:   {fontSize:9, letterSpacing:'0.15em', color:'#666658', textTransform:'uppercase'},
  input:   {width:'100%', background:'#1a1a14', border:'1px solid #2e2e26',
            borderRadius:4, padding:'12px 14px', color:'#f5f0e8',
            fontSize:14, fontFamily:"'DM Mono',monospace",
            outline:'none', transition:'border-color 0.2s',
            caretColor:'#c8f04a'},

  btn:     {background:'#c8f04a', border:'none', borderRadius:4,
            padding:'14px 20px', color:'#0c0c09', fontSize:12,
            fontFamily:"'DM Mono',monospace", letterSpacing:'0.1em',
            textTransform:'uppercase', cursor:'pointer',
            transition:'background 0.2s', width:'100%', fontWeight:400},

  trust:   {marginTop:36, paddingTop:24, borderTop:'1px solid #1e1e18',
            display:'flex', flexDirection:'column', gap:10},
  trustRow:{display:'flex', alignItems:'flex-start', gap:10},
  trustIcon:{fontSize:12, flexShrink:0, marginTop:1},
  trustText:{fontSize:10, color:'#444438', letterSpacing:'0.05em', lineHeight:1.5},
}
