import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { login, signup, checkSession } from '../utils/auth.js'

export default function LoginPage() {
  const navigate  = useNavigate()
  const [email,    setEmail]    = useState('')
  const [password, setPassword] = useState('')
  const [name,     setName]     = useState('')
  const [error,    setError]    = useState('')
  const [loading,  setLoading]  = useState(false)
  const [isSignup, setIsSignup] = useState(false)
  const [signupSuccess, setSignupSuccess] = useState(false)

  useEffect(() => {
    checkSession().then(u => { if (u) navigate('/') })
  }, [])

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      if (isSignup) {
        await signup(email, password, name)
        setSignupSuccess(true)
      } else {
        await login(email, password)
        await checkSession()
        navigate('/')
      }
    } catch (err) {
      if (err.name === 'UserNotConfirmedException') {
        setError('Your account is pending approval. We will email you when approved.')
      } else if (err.name === 'NotAuthorizedException') {
        setError('Invalid credentials or account not approved yet.')
      } else {
        setError(err.message || (isSignup ? 'Signup failed.' : 'Invalid credentials.'))
      }
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
        .inp{outline:none;transition:border-color 0.2s;}
        .inp:focus{border-color:#c8f04a !important;}
        .inp::placeholder{color:#6b7260;}
        input:-webkit-autofill{
          -webkit-box-shadow:0 0 0 100px #1e1e16 inset !important;
          -webkit-text-fill-color:#f0ece0 !important;
        }
        .submit-btn:hover:not(:disabled){background:#d4f55a !important;}
        .submit-btn:disabled{opacity:0.5;cursor:not-allowed;}
      `}</style>

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

        <div style={s.sampleCard}>
          <div style={s.sampleTop}>
            <span style={s.sampleLabel}>LATEST SUMMARY</span>
            <span style={s.sampleDone}>● DONE</span>
          </div>
          <p style={s.sampleTitle}>Q1 Planning — Product &amp; Eng</p>
          <div style={s.sampleItems}>
            {[
              {done:true,  t:'Finalize API contract',    o:'Ashhar'},
              {done:true,  t:'Review cost projections',  o:'Priya'},
              {done:false, t:'Send updated roadmap deck', o:'Unassigned'},
            ].map((a,i) => (
              <div key={i} style={s.sampleItem}>
                <span style={{color: a.done ? '#c8f04a' : '#6b7260', fontSize:12, width:14}}>
                  {a.done ? '✓' : '○'}
                </span>
                <span style={{
                  flex:1, fontSize:11, letterSpacing:'0.02em',
                  color: a.done ? '#7a7a68' : '#a8a894',
                  textDecoration: a.done ? 'line-through' : 'none',
                }}>
                  {a.t}
                </span>
                <span style={{fontSize:9, color:'#555548', letterSpacing:'0.08em'}}>{a.o}</span>
              </div>
            ))}
          </div>
        </div>

        <div style={s.tickerWrap}>
          <div style={s.tickerTrack}>
            {[0,1].map(i => (
              <span key={i} style={{display:'inline-flex'}}>
                {['TRANSCRIBE','ANALYZE','EXTRACT','REMIND','TRACK','SUMMARIZE'].map(w => (
                  <span key={w} style={s.tw}>
                    {w} <span style={{color:'#c8f04a', margin:'0 20px'}}>◆</span>
                  </span>
                ))}
              </span>
            ))}
          </div>
        </div>
      </div>

      <div style={s.right}>
        <div style={s.formWrap}>
          <div style={s.logo}>
            <span style={s.logoM}>M</span>
            <span style={s.logoRest}>eetingMind</span>
          </div>

          <h2 style={s.formH}>{isSignup ? 'Sign up' : 'Sign in'}</h2>
          <p style={s.formSub}>{isSignup ? 'Create your meeting workspace' : 'Access your meeting workspace'}</p>

          {signupSuccess && (
            <div style={s.success}>
              <div style={{fontSize:13, marginBottom:6}}>✓ Registration received!</div>
              <div style={{fontSize:10, lineHeight:1.5}}>
                Thank you for registering. We'll send you an email once your account is approved. 
                This usually takes a few hours.
              </div>
            </div>
          )}

          {error && <div style={s.err}>{error}</div>}

          <form onSubmit={handleSubmit} style={s.form}>
            {isSignup && (
              <div style={s.fGroup}>
                <label style={s.label}>FULL NAME</label>
                <input
                  className="inp"
                  type="text"
                  value={name}
                  onChange={e => setName(e.target.value)}
                  placeholder="Ashhar Ahmad Khan"
                  required
                  style={s.input}
                />
              </div>
            )}

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

            <button type="submit" disabled={loading || signupSuccess}
              className="submit-btn" style={s.btn}>
              {loading ? (isSignup ? 'Creating account…' : 'Signing in…') : (isSignup ? 'Create account →' : 'Sign in →')}
            </button>
          </form>

          {!signupSuccess && (
            <div style={s.toggle}>
              <span style={s.toggleText}>
                {isSignup ? 'Already have an account?' : "Don't have an account?"}
              </span>
              <button 
                onClick={() => { setIsSignup(!isSignup); setError(''); }}
                style={s.toggleBtn}
              >
                {isSignup ? 'Sign in' : 'Sign up'}
              </button>
            </div>
          )}

          <div style={s.trust}>
            <div style={s.trustRow}>
              <span>🔒</span>
              <span style={s.trustText}>Private by default. Audio processed and discarded.</span>
            </div>
            <div style={s.trustRow}>
              <span>⚡</span>
              <span style={s.trustText}>Powered by AWS Bedrock · Runs on ap-south-1</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

const s = {
  root:   {display:'flex', minHeight:'100vh', background:'#0c0c09',
           fontFamily:"'DM Mono',monospace"},
  left:   {flex:1, background:'#0f0f0c', borderRight:'1px solid #2a2a20',
           display:'flex', flexDirection:'column', justifyContent:'space-between',
           padding:'44px 48px', overflow:'hidden'},
  topLabel:{display:'flex', alignItems:'center', gap:8, fontSize:10,
            letterSpacing:'0.14em', color:'#6b7260', textTransform:'uppercase',
            animation:'fadeUp 0.5s ease both'},
  dot:    {width:6, height:6, borderRadius:'50%', background:'#c8f04a', flexShrink:0},
  hero:   {flex:1, display:'flex', flexDirection:'column', justifyContent:'center', paddingTop:32},
  h:      {fontFamily:"'Playfair Display',serif",
           fontSize:'clamp(56px,7vw,108px)', fontWeight:900,
           color:'#f0ece0', lineHeight:0.93, letterSpacing:'-2px',
           animation:'fadeUp 0.65s ease both'},
  hi:     {fontFamily:"'Playfair Display',serif", fontStyle:'italic',
           fontSize:'clamp(56px,7vw,108px)', fontWeight:400, color:'#c8f04a',
           lineHeight:1.05, letterSpacing:'-2px',
           animation:'fadeUp 0.65s ease both'},
  stats:  {display:'flex', gap:36, paddingBottom:28,
           animation:'fadeUp 0.65s ease 0.3s both'},
  stat:   {display:'flex', flexDirection:'column', gap:3},
  statN:  {fontFamily:"'Playfair Display',serif", fontSize:26, fontWeight:700,
           color:'#f0ece0', letterSpacing:'-0.5px'},
  statL:  {fontSize:10, letterSpacing:'0.08em', color:'#6b7260', textTransform:'uppercase'},
  sampleCard:{background:'#181812', border:'1px solid #2a2a20', borderRadius:8,
              padding:'16px 18px', marginBottom:24,
              animation:'fadeUp 0.65s ease 0.4s both'},
  sampleTop: {display:'flex', justifyContent:'space-between', alignItems:'center', marginBottom:10},
  sampleLabel:{fontSize:9, letterSpacing:'0.15em', color:'#6b7260', textTransform:'uppercase'},
  sampleDone: {fontSize:9, letterSpacing:'0.1em', color:'#c8f04a'},
  sampleTitle:{fontSize:13, color:'#a8a894', marginBottom:12, letterSpacing:'0.02em'},
  sampleItems:{display:'flex', flexDirection:'column', gap:7},
  sampleItem: {display:'flex', alignItems:'center', gap:8},
  tickerWrap: {overflow:'hidden', borderTop:'1px solid #2a2a20', paddingTop:14},
  tickerTrack:{display:'flex', whiteSpace:'nowrap', animation:'ticker 22s linear infinite'},
  tw:         {fontSize:10, letterSpacing:'0.14em', color:'#3a3a30', textTransform:'uppercase'},

  right:   {width:460, display:'flex', alignItems:'center', justifyContent:'center',
            padding:'48px 44px', background:'#131310'},
  formWrap:{width:'100%', maxWidth:340, animation:'fadeUp 0.7s ease 0.15s both'},
  logo:    {display:'flex', alignItems:'baseline', gap:1, marginBottom:44},
  logoM:   {fontFamily:"'Playfair Display',serif", fontSize:28, fontWeight:900, color:'#c8f04a'},
  logoRest:{fontFamily:"'Playfair Display',serif", fontSize:22, fontWeight:700, color:'#f0ece0'},
  formH:   {fontFamily:"'Playfair Display',serif", fontSize:30, fontWeight:700,
            color:'#f0ece0', letterSpacing:'-0.5px', marginBottom:6},
  formSub: {fontSize:11, letterSpacing:'0.08em', color:'#8a8a74', marginBottom:32,
            textTransform:'uppercase'},
  err:     {background:'#1e1010', border:'1px solid #4a2020',
            borderRadius:4, padding:'10px 12px', color:'#e88080',
            fontSize:11, marginBottom:20, letterSpacing:'0.03em'},
  success: {background:'#101e10', border:'1px solid #204a20',
            borderRadius:4, padding:'10px 12px', color:'#80e880',
            fontSize:11, marginBottom:20, letterSpacing:'0.03em'},
  form:    {display:'flex', flexDirection:'column', gap:24},
  fGroup:  {display:'flex', flexDirection:'column', gap:8},
  label:   {fontSize:9, letterSpacing:'0.15em', color:'#8a8a74', textTransform:'uppercase'},
  input:   {width:'100%', background:'#1e1e16', border:'1px solid #3a3a2e',
            borderRadius:4, padding:'12px 14px', color:'#f0ece0',
            fontSize:14, fontFamily:"'DM Mono',monospace", caretColor:'#c8f04a'},
  btn:     {background:'#c8f04a', border:'none', borderRadius:4,
            padding:'14px 20px', color:'#0c0c09', fontSize:12,
            fontFamily:"'DM Mono',monospace", letterSpacing:'0.1em',
            textTransform:'uppercase', cursor:'pointer',
            transition:'background 0.2s', width:'100%'},
  toggle:  {marginTop:24, display:'flex', alignItems:'center', justifyContent:'center', gap:8},
  toggleText:{fontSize:11, color:'#6b7260'},
  toggleBtn:{background:'none', border:'none', color:'#c8f04a', fontSize:11,
             fontFamily:"'DM Mono',monospace", cursor:'pointer',
             textDecoration:'underline', padding:0},
  trust:   {marginTop:36, paddingTop:24, borderTop:'1px solid #2a2a20',
            display:'flex', flexDirection:'column', gap:10},
  trustRow:{display:'flex', alignItems:'flex-start', gap:10, fontSize:12},
  trustText:{fontSize:10, color:'#6b7260', letterSpacing:'0.05em', lineHeight:1.5},
}
