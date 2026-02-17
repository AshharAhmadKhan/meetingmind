import { useState, useEffect } from 'react'
import { listUserTeams, createTeam, joinTeam } from '../utils/api'

export default function TeamSelector({ selectedTeamId, onTeamChange }) {
  const [teams, setTeams] = useState([])
  const [loading, setLoading] = useState(true)
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [showJoinModal, setShowJoinModal] = useState(false)
  const [newTeamName, setNewTeamName] = useState('')
  const [inviteCode, setInviteCode] = useState('')
  const [error, setError] = useState('')

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

  async function handleCreateTeam() {
    if (!newTeamName.trim()) {
      setError('Team name is required')
      return
    }
    
    try {
      setError('')
      const data = await createTeam(newTeamName)
      alert(`Team created! Invite code: ${data.inviteCode}`)
      setShowCreateModal(false)
      setNewTeamName('')
      await loadTeams()
      onTeamChange(data.teamId)
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to create team')
    }
  }

  async function handleJoinTeam() {
    if (!inviteCode.trim()) {
      setError('Invite code is required')
      return
    }
    
    try {
      setError('')
      const data = await joinTeam(inviteCode.toUpperCase())
      alert(`Joined team: ${data.teamName}`)
      setShowJoinModal(false)
      setInviteCode('')
      await loadTeams()
      onTeamChange(data.teamId)
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to join team')
    }
  }

  if (loading) return <div style={s.loading}>Loading teams...</div>

  return (
    <div style={s.root}>
      <select
        value={selectedTeamId || ''}
        onChange={(e) => onTeamChange(e.target.value || null)}
        style={s.select}
      >
        <option value="">Personal (Just Me)</option>
        {teams.map(team => (
          <option key={team.teamId} value={team.teamId}>
            {team.teamName} ({team.memberCount} members)
          </option>
        ))}
      </select>

      <button onClick={() => setShowCreateModal(true)} style={s.createBtn}>
        Create Team
      </button>

      <button onClick={() => setShowJoinModal(true)} style={s.joinBtn}>
        Join Team
      </button>

      {/* Create Team Modal */}
      {showCreateModal && (
        <div style={s.modalOverlay}>
          <div style={s.modal}>
            <h3 style={s.modalTitle}>Create New Team</h3>
            {error && <div style={s.error}>{error}</div>}
            <input
              type="text"
              value={newTeamName}
              onChange={(e) => setNewTeamName(e.target.value)}
              placeholder="Team name"
              style={s.input}
            />
            <div style={s.modalButtons}>
              <button onClick={handleCreateTeam} style={s.modalCreateBtn}>
                Create
              </button>
              <button
                onClick={() => {
                  setShowCreateModal(false)
                  setNewTeamName('')
                  setError('')
                }}
                style={s.modalCancelBtn}
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Join Team Modal */}
      {showJoinModal && (
        <div style={s.modalOverlay}>
          <div style={s.modal}>
            <h3 style={s.modalTitle}>Join Team</h3>
            {error && <div style={s.error}>{error}</div>}
            <input
              type="text"
              value={inviteCode}
              onChange={(e) => setInviteCode(e.target.value.toUpperCase())}
              placeholder="Invite code (e.g., ABC123)"
              style={s.input}
              maxLength={6}
            />
            <div style={s.modalButtons}>
              <button onClick={handleJoinTeam} style={s.modalJoinBtn}>
                Join
              </button>
              <button
                onClick={() => {
                  setShowJoinModal(false)
                  setInviteCode('')
                  setError('')
                }}
                style={s.modalCancelBtn}
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
