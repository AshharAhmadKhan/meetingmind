import React from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import LoginPage     from './pages/LoginPage.jsx'
import Dashboard     from './pages/Dashboard.jsx'
import MeetingDetail from './pages/MeetingDetail.jsx'
import { getUser }   from './utils/auth.js'

function ProtectedRoute({ children }) {
  const user = getUser()
  return user ? children : <Navigate to="/login" replace />
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/" element={
          <ProtectedRoute><Dashboard /></ProtectedRoute>
        }/>
        <Route path="/meeting/:meetingId" element={
          <ProtectedRoute><MeetingDetail /></ProtectedRoute>
        }/>
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  )
}
