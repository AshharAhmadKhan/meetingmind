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

  if (loading) return <div className="text-gray-400">Loading teams...</div>

  return (
    <div className="flex items-center gap-3">
      <select
        value={selectedTeamId || ''}
        onChange={(e) => onTeamChange(e.target.value || null)}
        className="bg-gray-800 text-white px-4 py-2 rounded-lg border border-gray-700 focus:border-blue-500 focus:outline-none"
      >
        <option value="">Personal (Just Me)</option>
        {teams.map(team => (
          <option key={team.teamId} value={team.teamId}>
            {team.teamName} ({team.memberCount} members)
          </option>
        ))}
      </select>

      <button
        onClick={() => setShowCreateModal(true)}
        className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition"
      >
        Create Team
      </button>

      <button
        onClick={() => setShowJoinModal(true)}
        className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg transition"
      >
        Join Team
      </button>

      {/* Create Team Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-gray-800 p-6 rounded-lg max-w-md w-full">
            <h3 className="text-xl font-bold mb-4">Create New Team</h3>
            {error && <div className="text-red-500 mb-3">{error}</div>}
            <input
              type="text"
              value={newTeamName}
              onChange={(e) => setNewTeamName(e.target.value)}
              placeholder="Team name"
              className="w-full bg-gray-700 text-white px-4 py-2 rounded-lg mb-4"
            />
            <div className="flex gap-3">
              <button
                onClick={handleCreateTeam}
                className="flex-1 bg-blue-600 hover:bg-blue-700 text-white py-2 rounded-lg"
              >
                Create
              </button>
              <button
                onClick={() => {
                  setShowCreateModal(false)
                  setNewTeamName('')
                  setError('')
                }}
                className="flex-1 bg-gray-600 hover:bg-gray-700 text-white py-2 rounded-lg"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Join Team Modal */}
      {showJoinModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-gray-800 p-6 rounded-lg max-w-md w-full">
            <h3 className="text-xl font-bold mb-4">Join Team</h3>
            {error && <div className="text-red-500 mb-3">{error}</div>}
            <input
              type="text"
              value={inviteCode}
              onChange={(e) => setInviteCode(e.target.value.toUpperCase())}
              placeholder="Invite code (e.g., ABC123)"
              className="w-full bg-gray-700 text-white px-4 py-2 rounded-lg mb-4"
              maxLength={6}
            />
            <div className="flex gap-3">
              <button
                onClick={handleJoinTeam}
                className="flex-1 bg-green-600 hover:bg-green-700 text-white py-2 rounded-lg"
              >
                Join
              </button>
              <button
                onClick={() => {
                  setShowJoinModal(false)
                  setInviteCode('')
                  setError('')
                }}
                className="flex-1 bg-gray-600 hover:bg-gray-700 text-white py-2 rounded-lg"
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
