import React, { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { getMeeting, updateAction } from '../utils/api.js'
import { ArrowLeft, CheckCircle, Circle, Clock,
         AlertTriangle, User, Calendar, Loader,
         Mic, Lightbulb, ListChecks, MessageSquare } from 'lucide-react'

function Section({ icon, title, children, accent = '#3b82f6' }) {
  return (
    <div style={sec.wrap}>
      <div style={sec.header}>
        <div style={{...sec.iconBox, background: `${accent}18`, border: `1px solid ${accent}30`}}>
          {React.cloneElement(icon, { size: 16, color: accent })}
        </div>
        <h2 style={sec.title}>{title}</h2>
      </div>
      {children}
    </div>
  )
}

const sec = {
  wrap:    { background: '#0d1629', border: '1px solid #1e2f50', borderRadius: 14, padding: 24, marginBottom: 20 },
  header:  { display: 'flex', alignItems: 'center', gap: 10, marginBottom: 18 },
  iconBox: { width: 32, height: 32, borderRadius: 8, display: 'flex', alignItems: 'center', justifyContent: 'center' },
  title:   { fontFamily: 'Syne, sans-serif', fontSize: 15, fontWeight: 700, color: '#f0f4ff' },
}

function ActionItem({ action, meetingId, onToggle }) {
  const [loading, setLoading] = useState(false)
  const isOverdue = action.deadline &&
    !action.completed &&
    new Date(action.deadline) < new Date()

  async function toggle() {
    setLoading(true)
    try { await onToggle(action.id, !action.completed) }
    finally { setLoading(false) }
  }

  return (
    <div style={{
      ...ai.item,
      opacity: action.completed ? 0.6 : 1,
      borderLeft: `3px solid ${action.completed ? '#10b981' : isOverdue ? '#ef4444' : '#1e2f50'}`,
    }}>
      <button onClick={toggle} disabled={loading} style={ai.check}>
        {loading
          ? <Loader size={18} color="#4a5f84" style={{animation:'spin 1s linear infinite'}}/>
          : action.completed
            ? <CheckCircle size={18} color="#10b981"/>
            : <Circle size={18} color="#4a5f84"/>
        }
      </button>

      <div style={ai.body}>
        <p style={{
          ...ai.task,
          textDecoration: action.completed ? 'line-through' : 'none',
          color: action.completed ? '#4a5f84' : '#f0f4ff',
        }}>
          {action.task}
        </p>
        <div style={ai.meta}>
          {action.owner && action.owner !== 'Unassigned' && (
            <span style={ai.tag}>
              <User size={10}/> {action.owner}
            </span>
          )}
          {action.deadline && (
            <span style={{...ai.tag, color: isOverdue && !action.completed ? '#fca5a5' : '#8da0c4'}}>
              {isOverdue && !action.completed && <AlertTriangle size={10}/>}
              <Calendar size={10}/> {action.deadline}
              {isOverdue && !action.completed && ' — Overdue'}
            </span>
          )}
          {action.completed && (
            <span style={{...ai.tag, color: '#6ee7b7'}}>
              <CheckCircle size={10}/> Completed
            </span>
          )}
        </div>
      </div>
    </div>
  )
}

const ai = {
  item:  { display: 'flex', alignItems: 'flex-start', gap: 12,
           background: '#111e35', borderRadius: 8, padding: '12px 14px',
           marginBottom: 8, transition: 'opacity 0.18s' },
  check: { background: 'none', border: 'none', cursor: 'pointer',
           padding: 0, marginTop: 2, flexShrink: 0 },
  body:  { flex: 1, minWidth: 0 },
  task:  { fontSize: 14, lineHeight: 1.5, marginBottom: 6, transition: 'all 0.18s' },
  meta:  { display: 'flex', flexWrap: 'wrap', gap: 8 },
  tag:   { display: 'flex', alignItems: 'center', gap: 4,
           fontSize: 11, color: '#8da0c4' },
}

export default function MeetingDetail() {
  const { meetingId } = useParams()
  const navigate      = useNavigate()
  const [meeting, setMeeting] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error,   setError]   = useState('')

  useEffect(() => {
    getMeeting(meetingId)
      .then(setMeeting)
      .catch(() => setError('Failed to load meeting'))
      .finally(() => setLoading(false))
  }, [meetingId])

  async function handleToggle(actionId, completed) {
    await updateAction(meetingId, actionId, completed)
    setMeeting(prev => ({
      ...prev,
      actionItems: prev.actionItems.map(a =>
        a.id === actionId ? { ...a, completed } : a
      )
    }))
  }

  if (loading) return (
    <div style={pg.center}>
      <Loader size={32} color="#3b82f6" style={{animation:'spin 1s linear infinite'}}/>
      <p style={{color:'#4a5f84', marginTop: 16}}>Loading meeting…</p>
      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
    </div>
  )

  if (error) return (
    <div style={pg.center}>
      <p style={{color:'#fca5a5'}}>{error}</p>
      <button onClick={() => navigate('/')} style={pg.backBtn}>← Back</button>
    </div>
  )

  const done    = meeting.actionItems?.filter(a => a.completed).length || 0
  const total   = meeting.actionItems?.length || 0

  return (
    <div style={pg.root}>
      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>

      {/* Header */}
      <header style={pg.header}>
        <div style={pg.headerInner}>
          <button onClick={() => navigate('/')} style={pg.backBtnTop}>
            <ArrowLeft size={16}/> Back
          </button>
          <div style={pg.headerTitle}>
            <div style={pg.logoIcon}><Mic size={16} color="#3b82f6"/></div>
            <span style={pg.logoText}>MeetingMind</span>
          </div>
        </div>
      </header>

      <main style={pg.main}>
        {/* Title block */}
        <div style={pg.titleBlock}>
          <h1 style={pg.meetingName}>{meeting.title}</h1>
          <div style={pg.titleMeta}>
            <span style={pg.metaItem}>
              <Calendar size={13}/>
              {new Date(meeting.createdAt).toLocaleDateString('en-US',
                {weekday:'long', year:'numeric', month:'long', day:'numeric'})}
            </span>
            {total > 0 && (
              <span style={pg.metaItem}>
                <ListChecks size={13}/>
                {done}/{total} actions complete
              </span>
            )}
          </div>
          {/* Progress bar */}
          {total > 0 && (
            <div style={pg.progressWrap}>
              <div style={{...pg.progressBar, width: `${(done/total)*100}%`}} />
            </div>
          )}
        </div>

        {/* Summary */}
        {meeting.summary && (
          <Section icon={<Mic/>} title="Summary" accent="#3b82f6">
            <p style={pg.summaryText}>{meeting.summary}</p>
          </Section>
        )}

        {/* Decisions */}
        {meeting.decisions?.length > 0 && (
          <Section icon={<Lightbulb/>} title="Key Decisions" accent="#f59e0b">
            <ol style={pg.decisionList}>
              {meeting.decisions.map((d, i) => (
                <li key={i} style={pg.decisionItem}>
                  <span style={pg.decisionNum}>{i+1}</span>
                  <span style={pg.decisionText}>{d}</span>
                </li>
              ))}
            </ol>
          </Section>
        )}

        {/* Action Items */}
        {meeting.actionItems?.length > 0 && (
          <Section icon={<ListChecks/>} title={`Action Items (${done}/${total} done)`} accent="#10b981">
            {meeting.actionItems.map(a => (
              <ActionItem
                key={a.id}
                action={a}
                meetingId={meetingId}
                onToggle={handleToggle}
              />
            ))}
          </Section>
        )}

        {/* Follow-ups */}
        {meeting.followUps?.length > 0 && (
          <Section icon={<MessageSquare/>} title="Follow-ups for Next Meeting" accent="#8b5cf6">
            <ul style={pg.followList}>
              {meeting.followUps.map((f, i) => (
                <li key={i} style={pg.followItem}>
                  <span style={pg.followDot}/>
                  <span style={pg.followText}>{f}</span>
                </li>
              ))}
            </ul>
          </Section>
        )}

        {/* Empty state */}
        {!meeting.summary && !meeting.decisions?.length &&
         !meeting.actionItems?.length && !meeting.followUps?.length && (
          <div style={pg.emptyInsights}>
            <Loader size={24} color="#3b82f6" style={{animation:'spin 1s linear infinite'}}/>
            <p style={{color:'#4a5f84', marginTop: 12}}>AI is analyzing this meeting…</p>
          </div>
        )}
      </main>
    </div>
  )
}

const pg = {
  root:        { minHeight: '100vh', background: '#070d1a' },
  center:      { minHeight: '100vh', display: 'flex', flexDirection: 'column',
                 alignItems: 'center', justifyContent: 'center' },
  header:      { background: '#0d1629', borderBottom: '1px solid #1e2f50',
                 padding: '0 32px', height: 60, position: 'sticky', top: 0, zIndex: 100 },
  headerInner: { maxWidth: 800, margin: '0 auto', height: '100%',
                 display: 'flex', alignItems: 'center', justifyContent: 'space-between' },
  backBtnTop:  { display: 'flex', alignItems: 'center', gap: 6,
                 background: 'none', border: 'none', color: '#8da0c4',
                 cursor: 'pointer', fontSize: 14, fontFamily: 'DM Sans, sans-serif' },
  backBtn:     { marginTop: 16, background: 'none', border: '1px solid #1e2f50',
                 borderRadius: 8, padding: '8px 16px', color: '#8da0c4',
                 cursor: 'pointer', fontFamily: 'DM Sans, sans-serif' },
  headerTitle: { display: 'flex', alignItems: 'center', gap: 8 },
  logoIcon:    { width: 30, height: 30, background: 'rgba(59,130,246,0.12)',
                 border: '1px solid rgba(59,130,246,0.25)', borderRadius: 7,
                 display: 'flex', alignItems: 'center', justifyContent: 'center' },
  logoText:    { fontFamily: 'Syne, sans-serif', fontSize: 15, fontWeight: 700, color: '#f0f4ff' },
  main:        { maxWidth: 800, margin: '0 auto', padding: '32px' },
  titleBlock:  { marginBottom: 28 },
  meetingName: { fontFamily: 'Syne, sans-serif', fontSize: 32, fontWeight: 800,
                 color: '#f0f4ff', letterSpacing: '-0.5px', marginBottom: 12, lineHeight: 1.2 },
  titleMeta:   { display: 'flex', alignItems: 'center', gap: 20, marginBottom: 14 },
  metaItem:    { display: 'flex', alignItems: 'center', gap: 6, fontSize: 13, color: '#8da0c4' },
  progressWrap:{ height: 4, background: '#111e35', borderRadius: 2 },
  progressBar: { height: '100%', background: '#10b981', borderRadius: 2, transition: 'width 0.4s ease' },
  summaryText: { fontSize: 15, color: '#c5d4f0', lineHeight: 1.75 },
  decisionList:{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: 10 },
  decisionItem:{ display: 'flex', alignItems: 'flex-start', gap: 12,
                 background: '#111e35', borderRadius: 8, padding: '12px 14px' },
  decisionNum: { width: 24, height: 24, background: 'rgba(245,158,11,0.12)',
                 border: '1px solid rgba(245,158,11,0.2)', borderRadius: 6,
                 display: 'flex', alignItems: 'center', justifyContent: 'center',
                 fontSize: 12, fontWeight: 700, color: '#f59e0b', flexShrink: 0 },
  decisionText:{ fontSize: 14, color: '#f0f4ff', lineHeight: 1.5 },
  followList:  { display: 'flex', flexDirection: 'column', gap: 8 },
  followItem:  { display: 'flex', alignItems: 'flex-start', gap: 10,
                 background: '#111e35', borderRadius: 8, padding: '10px 14px' },
  followDot:   { width: 6, height: 6, borderRadius: '50%', background: '#8b5cf6',
                 marginTop: 6, flexShrink: 0 },
  followText:  { fontSize: 14, color: '#c5d4f0', lineHeight: 1.5 },
  emptyInsights: { display: 'flex', flexDirection: 'column', alignItems: 'center',
                   padding: '60px 0' },
}
