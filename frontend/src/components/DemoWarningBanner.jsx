import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { logout } from '../utils/auth.js'

const DEMO_USER_EMAIL = 'demo@meetingmind.com'

export default function DemoWarningBanner({ userEmail }) {
  const navigate = useNavigate()
  const [isDemoUser, setIsDemoUser] = useState(false)
  const [dismissed, setDismissed] = useState(false)

  useEffect(() => {
    // Check if current user is the demo user
    console.log('DemoWarningBanner - userEmail:', userEmail) // Debug log
    console.log('DemoWarningBanner - DEMO_USER_EMAIL:', DEMO_USER_EMAIL) // Debug log
    const isDemo = userEmail === DEMO_USER_EMAIL
    console.log('DemoWarningBanner - isDemoUser:', isDemo) // Debug log
    console.log('DemoWarningBanner - comparison:', { userEmail, DEMO_USER_EMAIL, match: userEmail === DEMO_USER_EMAIL }) // Debug log
    setIsDemoUser(isDemo)
    
    // Check if banner was dismissed in this session
    const wasDismissed = sessionStorage.getItem('demoBannerDismissed') === 'true'
    console.log('DemoWarningBanner - dismissed:', wasDismissed) // Debug log
    setDismissed(wasDismissed)
  }, [userEmail])

  const handleDismiss = () => {
    setDismissed(true)
    sessionStorage.setItem('demoBannerDismissed', 'true')
  }

  const handleSignUp = async () => {
    // Log out the demo user first, then navigate to signup
    await logout()
    navigate('/login?signup=true')
  }

  console.log('DemoWarningBanner render - isDemoUser:', isDemoUser, 'dismissed:', dismissed) // Debug log

  if (!isDemoUser || dismissed) {
    console.log('DemoWarningBanner - not rendering because:', !isDemoUser ? 'not demo user' : 'dismissed') // Debug log
    return null
  }

  return (
    <div style={styles.banner}>
      <div style={styles.content}>
        <div style={styles.iconContainer}>
          <span style={styles.icon}>⚠️</span>
        </div>
        <div style={styles.textContainer}>
          <div style={styles.title}>Demo Mode Active</div>
          <div style={styles.message}>
            You're using a shared demo account. Your uploaded meetings will be automatically deleted after 30 minutes.
            {' '}
            <span style={styles.highlight}>Sign up for a free account to save your data permanently.</span>
          </div>
        </div>
        <div style={styles.actions}>
          <button onClick={handleSignUp} style={styles.signUpButton}>
            Sign Up Free
          </button>
          <button onClick={handleDismiss} style={styles.dismissButton}>
            ×
          </button>
        </div>
      </div>
    </div>
  )
}

const styles = {
  banner: {
    background: 'linear-gradient(135deg, #2a2a1f 0%, #1a1a12 100%)',
    border: '1px solid #e8c06a',
    borderRadius: 8,
    padding: '16px 20px',
    marginBottom: 24,
    boxShadow: '0 4px 12px rgba(232, 192, 106, 0.1)',
    animation: 'slideDown 0.3s ease-out',
  },
  content: {
    display: 'flex',
    alignItems: 'center',
    gap: 16,
  },
  iconContainer: {
    flexShrink: 0,
  },
  icon: {
    fontSize: 24,
    filter: 'drop-shadow(0 2px 4px rgba(232, 192, 106, 0.3))',
  },
  textContainer: {
    flex: 1,
    minWidth: 0,
  },
  title: {
    color: '#e8c06a',
    fontSize: 14,
    fontWeight: 600,
    marginBottom: 4,
    fontFamily: "'DM Mono', monospace",
    letterSpacing: '0.5px',
  },
  message: {
    color: '#d4d4c8',
    fontSize: 13,
    lineHeight: 1.5,
    fontFamily: "'DM Sans', sans-serif",
  },
  highlight: {
    color: '#c8f04a',
    fontWeight: 500,
  },
  actions: {
    display: 'flex',
    alignItems: 'center',
    gap: 12,
    flexShrink: 0,
  },
  signUpButton: {
    background: '#c8f04a',
    color: '#0c0c09',
    border: 'none',
    borderRadius: 6,
    padding: '8px 20px',
    fontSize: 13,
    fontWeight: 600,
    fontFamily: "'DM Mono', monospace",
    cursor: 'pointer',
    transition: 'all 0.2s',
    boxShadow: '0 2px 8px rgba(200, 240, 74, 0.2)',
  },
  dismissButton: {
    background: 'transparent',
    color: '#8a8a74',
    border: 'none',
    fontSize: 24,
    lineHeight: 1,
    cursor: 'pointer',
    padding: '4px 8px',
    transition: 'color 0.2s',
  },
}

// Add hover effects via CSS-in-JS
if (typeof document !== 'undefined') {
  const style = document.createElement('style')
  style.textContent = `
    @keyframes slideDown {
      from {
        opacity: 0;
        transform: translateY(-10px);
      }
      to {
        opacity: 1;
        transform: translateY(0);
      }
    }
    button:hover {
      transform: translateY(-1px);
    }
  `
  document.head.appendChild(style)
}
