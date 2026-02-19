import { useState, useEffect, useCallback } from 'react'
import { listUserTeams, createTeam, joinTeam } from '../utils/api'

export default function TeamSelector({ selectedTeamId, onTeamChange }) {
  const [teams, setTeams] = useState([])
  const [loading, setLoading] = useState(true)
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [showJoinModal, setShowJoinModal] = useState(false)
  const [newTeamName, setNewTeamName] = useState('')
  const [inviteCode, setInviteCode] = useState('')
  const [createdInviteCode, setCreatedInviteCode] = useState('')
  const [createError, setCreateError] = useState('')
  const [joinError, setJoinError] = useState('')
  const [submitting, setSubmitting] = useState(false)

  useEffect(() => {
    loadTeams()
  }, [])

  async function loadTeams() {
    try {
      const data = await listUserTeams()
      setTeams(data.teams || [])
    } catch (err) {
      console.error('Failed to load teams:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleCreateTeam = useCallback(async () => {
    if (!newTeamName.trim()) {
      setCreateError('Team name is required')
      return
    }
    
    if (submitting) return
    
    try {
      setSubmitting(true)
      setCreateError('')
      const data = await createTeam(newTeamName)
      
      // Optimistic update
      const newTeam = {
        teamId: data.teamId,
        teamName: newTeamName,
        memberCount: 1
      }
      setTeams(prev => [...prev, newTeam])
      
      // Show invite code in modal
      setCreatedInviteCode(data.inviteCode)
      setNewTeamName('')
      
      // Switch to new team
      onTeamChange(data.teamId)
      
      // Background refresh
      loadTeams()
    } catch (err) {
      setCreateError(err.response?.data?.error || 'Failed to create team')
    } finally {
      setSubmitting(false)
    }
  }, [newTeamName, submitting, onTeamChange])

  const handleJoinTeam = useCallback(async () => {
    if (!inviteCode.trim()) {
      setJoinError('Invite code is required')
      return
    }
    
    // Validate format
    const normalized = inviteCode.toUpperCase().trim()
    if (!/^[A-Z0-9]{6}$/.test(normalized)) {
      setJoinError('Invite code must be 6 alphanumeric characters')
      return
    }
    
    if (submitting) return
    
    try {
      setSubmitting(true)
      setJoinError('')
      const data = await joinTeam(normalized)
      
      // Optimistic update
      const joinedTeam = {
        teamId: data.teamId,
        teamName: data.teamName,
        memberCount: data.memberCount || 1
      }
      setTeams(prev => [...prev, joinedTeam])
      
      setShowJoinModal(false)
      setInviteCode('')
      
      // Switch to joined team
      onTeamChange(data.teamId)
      
      // Background refresh
      loadTeams()
    } catch (err) {
      setJoinError(err.response?.data?.error || 'Failed to join team')
    } finally {
      setSubmitting(false)
    }
  }, [inviteCode, submitting, onTeamChange])

  const copyInviteCode = useCallback(() => {
    navigator.clipboard.writeText(createdInviteCode)
  }, [createdInviteCode])

  const closeCreateModal = useCallback(() => {
    setShowCreateModal(false)
    setNewTeamName('')
    setCreateError('')
    setCreatedInviteCode('')
  }, [])

  const closeJoinModal = useCallback(() => {
    setShowJoinModal(false)
    setInviteCode('')
    setJoinError('')
  }, [])

  // Keyboard handlers
  useEffect(() => {
    const handleEscape = (e) => {
      if (e.key === 'Escape') {
        if (showCreateModal) closeCreateModal()
        if (showJoinModal) closeJoinModal()
      }
    }
    
    if (showCreateModal || showJoinModal) {
      document.addEventListener('keydown', handleEscape)
      return () => document.removeEventListener('keydown', handleEscape)
    }
  }, [showCreateModal, showJoinModal, closeCreateModal, closeJoinModal])

  if (loading) return <div style={s.loading}>Loading teams...</div>

  return (
    <div style={s.root}>
      <select
        value={selectedTeamId || ''}
        onChange={(e) => onTeamChange(e.target.value || null)}
        style={s.select}
      >
        <option value="">📋 Personal (Just Me)</option>
        {teams.length === 0 && (
          <option disabled>No teams yet - create or join one</option>
        )}
        {teams.map(team => {
          // Add emoji indicators for V1/V2 teams
          const isV1 = team.teamName.includes('V1') || team.teamName.includes('Legacy')
          const isV2 = team.teamName.includes('V2') || team.teamName.includes('Active')
          const emoji = isV1 ? '📦' : isV2 ? '🚀' : '👥'
          
          return (
            <option key={team.teamId} value={team.teamId}>
              {emoji} {team.teamName} ({team.memberCount} {team.memberCount === 1 ? 'member' : 'members'})
            </option>
          )
        })}
      </select>

      <button onClick={() => setShowCreateModal(true)} style={s.createBtn}>
        Create Team
      </button>

      <button onClick={() => setShowJoinModal(true)} style={s.joinBtn}>
        Join Team
      </button>

      {/* Create Team Modal */}
      {showCreateModal && (
        <div style={s.modalOverlay} onClick={closeCreateModal}>
          <div style={s.modal} onClick={(e) => e.stopPropagation()}>
            <h3 style={s.modalTitle}>Create New Team</h3>
            
            {createError && <div style={s.error}>{createError}</div>}
            
            {createdInviteCode ? (
              // Success state with invite code
              <div>
                <div style={s.successBox}>
                  <p style={s.successText}>Team created successfully!</p>
                  <p style={s.inviteLabel}>Share this invite code:</p>
                  <div style={s.inviteCodeBox}>
                    <span style={s.inviteCode}>{createdInviteCode}</span>
                    <button onClick={copyInviteCode} style={s.copyBtn}>
                      Copy
                    </button>
                  </div>
                  <p style={s.inviteNote}>
                    Invite codes are permanent and can be used multiple times
                  </p>
                </div>
                <button onClick={closeCreateModal} style={s.modalDoneBtn}>
                  Done
                </button>
              </div>
            ) : (
              // Input state
              <div>
                <input
                  type="text"
                  value={newTeamName}
                  onChange={(e) => setNewTeamName(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handleCreateTeam()}
                  placeholder="Team name"
                  style={s.input}
                  autoFocus
                  disabled={submitting}
                />
                <div style={s.modalButtons}>
                  <button 
                    onClick={handleCreateTeam} 
                    style={{...s.modalCreateBtn, opacity: submitting ? 0.5 : 1}}
                    disabled={submitting}
                  >
                    {submitting ? 'Creating...' : 'Create'}
                  </button>
                  <button
                    onClick={closeCreateModal}
                    style={s.modalCancelBtn}
                    disabled={submitting}
                  >
                    Cancel
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Join Team Modal */}
      {showJoinModal && (
        <div style={s.modalOverlay} onClick={closeJoinModal}>
          <div style={s.modal} onClick={(e) => e.stopPropagation()}>
            <h3 style={s.modalTitle}>Join Team</h3>
            {joinError && <div style={s.error}>{joinError}</div>}
            <input
              type="text"
              value={inviteCode}
              onChange={(e) => setInviteCode(e.target.value.toUpperCase())}
              onKeyDown={(e) => e.key === 'Enter' && handleJoinTeam()}
              placeholder="Invite code (e.g., ABC123)"
              style={s.input}
              maxLength={6}
              autoFocus
              disabled={submitting}
            />
            <div style={s.modalButtons}>
              <button 
                onClick={handleJoinTeam} 
                style={{...s.modalJoinBtn, opacity: submitting ? 0.5 : 1}}
                disabled={submitting}
              >
                {submitting ? 'Joining...' : 'Join'}
              </button>
              <button
                onClick={closeJoinModal}
                style={s.modalCancelBtn}
                disabled={submitting}
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

const s = {
  root: {
    display: 'flex',
    alignItems: 'center',
    gap: 12,
    padding: '16px 20px',
    background: '#111108',
    border: '1px solid #2a2a20',
    borderRadius: 8,
  },
  loading: {
    fontSize: 11,
    color: '#6b7260',
    padding: '16px 20px',
  },
  select: {
    background: '#1e1e16',
    border: '1px solid #3a3a2e',
    borderRadius: 4,
    padding: '8px 12px',
    color: '#f0ece0',
    fontSize: 12,
    fontFamily: "'DM Mono',monospace",
    cursor: 'pointer',
    outline: 'none',
    flex: 1,
  },
  createBtn: {
    background: '#6a9ae8',
    border: 'none',
    borderRadius: 4,
    padding: '8px 14px',
    color: '#0c0c09',
    fontSize: 11,
    letterSpacing: '0.05em',
    cursor: 'pointer',
    fontFamily: "'DM Mono',monospace",
    fontWeight: 400,
    transition: 'opacity 0.15s',
  },
  joinBtn: {
    background: '#c8f04a',
    border: 'none',
    borderRadius: 4,
    padding: '8px 14px',
    color: '#0c0c09',
    fontSize: 11,
    letterSpacing: '0.05em',
    cursor: 'pointer',
    fontFamily: "'DM Mono',monospace",
    fontWeight: 400,
    transition: 'opacity 0.15s',
  },
  modalOverlay: {
    position: 'fixed',
    inset: 0,
    background: 'rgba(0,0,0,0.7)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    zIndex: 1000,
  },
  modal: {
    background: '#111108',
    border: '1px solid #3a3a2e',
    borderRadius: 8,
    padding: '24px',
    maxWidth: 400,
    width: '90%',
  },
  modalTitle: {
    fontFamily: "'Playfair Display',serif",
    fontSize: 18,
    fontWeight: 700,
    color: '#f0ece0',
    marginBottom: 16,
  },
  error: {
    background: '#1a0e0e',
    border: '1px solid #4a2a2a',
    borderRadius: 4,
    padding: '8px 12px',
    color: '#e87a6a',
    fontSize: 11,
    marginBottom: 12,
  },
  successBox: {
    background: '#0e1a0e',
    border: '1px solid #2a4a2a',
    borderRadius: 6,
    padding: '16px',
    marginBottom: 16,
  },
  successText: {
    color: '#c8f04a',
    fontSize: 13,
    marginBottom: 12,
    fontWeight: 500,
  },
  inviteLabel: {
    color: '#8a8a74',
    fontSize: 11,
    marginBottom: 8,
  },
  inviteCodeBox: {
    display: 'flex',
    alignItems: 'center',
    gap: 8,
    background: '#1e1e16',
    border: '1px solid #3a3a2e',
    borderRadius: 4,
    padding: '10px 12px',
    marginBottom: 8,
  },
  inviteCode: {
    flex: 1,
    fontFamily: "'DM Mono',monospace",
    fontSize: 18,
    letterSpacing: '0.15em',
    color: '#c8f04a',
    fontWeight: 600,
  },
  copyBtn: {
    background: '#c8f04a',
    border: 'none',
    borderRadius: 3,
    padding: '6px 12px',
    color: '#0c0c09',
    fontSize: 10,
    letterSpacing: '0.05em',
    cursor: 'pointer',
    fontFamily: "'DM Mono',monospace",
    fontWeight: 500,
  },
  inviteNote: {
    color: '#6b7260',
    fontSize: 10,
    lineHeight: 1.4,
  },
  input: {
    width: '100%',
    background: '#1e1e16',
    border: '1px solid #3a3a2e',
    borderRadius: 4,
    padding: '10px 12px',
    color: '#f0ece0',
    fontSize: 13,
    fontFamily: "'DM Mono',monospace",
    marginBottom: 16,
    outline: 'none',
  },
  modalButtons: {
    display: 'flex',
    gap: 12,
  },
  modalCreateBtn: {
    flex: 1,
    background: '#6a9ae8',
    border: 'none',
    borderRadius: 4,
    padding: '10px',
    color: '#0c0c09',
    fontSize: 12,
    letterSpacing: '0.05em',
    cursor: 'pointer',
    fontFamily: "'DM Mono',monospace",
    fontWeight: 400,
    transition: 'opacity 0.15s',
  },
  modalJoinBtn: {
    flex: 1,
    background: '#c8f04a',
    border: 'none',
    borderRadius: 4,
    padding: '10px',
    color: '#0c0c09',
    fontSize: 12,
    letterSpacing: '0.05em',
    cursor: 'pointer',
    fontFamily: "'DM Mono',monospace",
    fontWeight: 400,
    transition: 'opacity 0.15s',
  },
  modalDoneBtn: {
    width: '100%',
    background: '#c8f04a',
    border: 'none',
    borderRadius: 4,
    padding: '10px',
    color: '#0c0c09',
    fontSize: 12,
    letterSpacing: '0.05em',
    cursor: 'pointer',
    fontFamily: "'DM Mono',monospace",
    fontWeight: 400,
  },
  modalCancelBtn: {
    flex: 1,
    background: '#2a2a20',
    border: '1px solid #3a3a2e',
    borderRadius: 4,
    padding: '10px',
    color: '#8a8a74',
    fontSize: 12,
    letterSpacing: '0.05em',
    cursor: 'pointer',
    fontFamily: "'DM Mono',monospace",
    fontWeight: 400,
  },
}
