import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { login, checkSession } from '../utils/auth.js'
import { Mic, Zap, Brain } from 'lucide-react'

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
      setError(err.message || 'Sign in failed. Check your credentials.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={styles.root}>
      {/* Background grid */}
      <div style={styles.grid} />

      {/* Glow orb */}
      <div style={styles.orb} />

      <div style={styles.card}>
        {/* Logo */}
        <div style={styles.logo}>
          <div style={styles.logoIcon}>
            <Mic size={22} color="#3b82f6" />
          </div>
          <span style={styles.logoText}>MeetingMind</span>
        </div>

        <h1 style={styles.heading}>Welcome back</h1>
        <p style={styles.sub}>Sign in to access your meeting intelligence</p>

        {error && (
          <div style={styles.errorBox}>
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} style={styles.form}>
          <div style={styles.field}>
            <label style={styles.label}>Email</label>
            <input
              type="email"
              value={email}
              onChange={e => setEmail(e.target.value)}
              placeholder="you@company.com"
              required
              style={styles.input}
              onFocus={e => e.target.style.borderColor = '#3b82f6'}
              onBlur={e  => e.target.style.borderColor = '#1e2f50'}
            />
          </div>

          <div style={styles.field}>
            <label style={styles.label}>Password</label>
            <input
              type="password"
              value={password}
              onChange={e => setPassword(e.target.value)}
              placeholder="••••••••"
              required
              style={styles.input}
              onFocus={e => e.target.style.borderColor = '#3b82f6'}
              onBlur={e  => e.target.style.borderColor = '#1e2f50'}
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            style={{...styles.btn, opacity: loading ? 0.7 : 1}}
          >
            {loading ? 'Signing in…' : 'Sign in →'}
          </button>
        </form>

        {/* Features strip */}
        <div style={styles.features}>
          {[
            { icon: <Mic size={14}/>,   text: 'Auto transcription' },
            { icon: <Brain size={14}/>, text: 'AI insights'        },
            { icon: <Zap size={14}/>,   text: 'Action tracking'    },
          ].map(f => (
            <div key={f.text} style={styles.featureItem}>
              <span style={styles.featureIcon}>{f.icon}</span>
              <span style={styles.featureText}>{f.text}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

const styles = {
  root: {
    minHeight: '100vh',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    background: '#070d1a',
    position: 'relative',
    overflow: 'hidden',
  },
  grid: {
    position: 'absolute', inset: 0,
    backgroundImage: `
      linear-gradient(rgba(59,130,246,0.04) 1px, transparent 1px),
      linear-gradient(90deg, rgba(59,130,246,0.04) 1px, transparent 1px)
    `,
    backgroundSize: '40px 40px',
  },
  orb: {
    position: 'absolute',
    width: 600, height: 600,
    borderRadius: '50%',
    background: 'radial-gradient(circle, rgba(59,130,246,0.12) 0%, transparent 70%)',
    top: '50%', left: '50%',
    transform: 'translate(-50%, -50%)',
    pointerEvents: 'none',
  },
  card: {
    position: 'relative', zIndex: 1,
    background: '#0d1629',
    border: '1px solid #1e2f50',
    borderRadius: 20,
    padding: '48px 44px',
    width: '100%', maxWidth: 420,
    boxShadow: '0 8px 48px rgba(0,0,0,0.6)',
  },
  logo: {
    display: 'flex', alignItems: 'center', gap: 10,
    marginBottom: 32,
  },
  logoIcon: {
    width: 40, height: 40,
    background: 'rgba(59,130,246,0.12)',
    border: '1px solid rgba(59,130,246,0.3)',
    borderRadius: 10,
    display: 'flex', alignItems: 'center', justifyContent: 'center',
  },
  logoText: {
    fontFamily: 'Syne, sans-serif',
    fontSize: 20, fontWeight: 700,
    color: '#f0f4ff',
    letterSpacing: '-0.3px',
  },
  heading: {
    fontFamily: 'Syne, sans-serif',
    fontSize: 28, fontWeight: 800,
    color: '#f0f4ff',
    marginBottom: 8,
    letterSpacing: '-0.5px',
  },
  sub: {
    color: '#8da0c4', fontSize: 14,
    marginBottom: 32,
  },
  errorBox: {
    background: 'rgba(239,68,68,0.1)',
    border: '1px solid rgba(239,68,68,0.3)',
    borderRadius: 8, padding: '10px 14px',
    color: '#fca5a5', fontSize: 13,
    marginBottom: 20,
  },
  form: { display: 'flex', flexDirection: 'column', gap: 18 },
  field: { display: 'flex', flexDirection: 'column', gap: 6 },
  label: { fontSize: 13, fontWeight: 500, color: '#8da0c4', letterSpacing: '0.3px' },
  input: {
    background: '#111e35',
    border: '1px solid #1e2f50',
    borderRadius: 8, padding: '11px 14px',
    color: '#f0f4ff', fontSize: 14,
    outline: 'none', transition: 'border-color 0.18s',
    fontFamily: 'DM Sans, sans-serif',
  },
  btn: {
    marginTop: 4,
    background: '#3b82f6',
    border: 'none', borderRadius: 8,
    padding: '13px 20px',
    color: '#fff', fontSize: 15, fontWeight: 600,
    cursor: 'pointer', transition: 'background 0.18s',
    fontFamily: 'Syne, sans-serif',
    letterSpacing: '-0.2px',
  },
  features: {
    display: 'flex', justifyContent: 'space-between',
    marginTop: 36,
    paddingTop: 24,
    borderTop: '1px solid #1e2f50',
  },
  featureItem: { display: 'flex', alignItems: 'center', gap: 6 },
  featureIcon: { color: '#3b82f6' },
  featureText: { fontSize: 12, color: '#4a5f84' },
}
