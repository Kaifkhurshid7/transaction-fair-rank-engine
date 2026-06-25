import React, { useState } from 'react'
import Dashboard from './pages/Dashboard'
import Leaderboard from './pages/Leaderboard'
import Toast from './components/Toast'

function App() {
  const [currentPage, setCurrentPage] = useState('dashboard')
  const [toast, setToast] = useState(null)
  const [userId, setUserId] = useState(null)

  const showToast = (message, type = 'info') => {
    setToast({ message, type })
    setTimeout(() => setToast(null), 3000)
  }

  const handleCreateUser = async (name, email) => {
    try {
      const response = await fetch('/api/v1/summary/users?name=' + encodeURIComponent(name) + '&email=' + encodeURIComponent(email), {
        method: 'POST'
      })
      const data = await response.json()
      setUserId(data.user_id)
      showToast(`Welcome ${name}!`, 'success')
    } catch (error) {
      showToast(error.message || 'Error creating user', 'error')
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-600 to-indigo-900">
      <nav className="glass-effect sticky top-0 z-50 border-b border-white border-opacity-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <h1 className="text-white text-2xl font-bold">💎 Transaction Ranking</h1>
            <div className="flex space-x-4">
              <button
                onClick={() => setCurrentPage('dashboard')}
                className={`px-4 py-2 rounded-lg font-medium transition ${
                  currentPage === 'dashboard'
                    ? 'bg-white bg-opacity-30 text-white'
                    : 'text-white hover:bg-white hover:bg-opacity-10'
                }`}
              >
                Dashboard
              </button>
              <button
                onClick={() => setCurrentPage('leaderboard')}
                className={`px-4 py-2 rounded-lg font-medium transition ${
                  currentPage === 'leaderboard'
                    ? 'bg-white bg-opacity-30 text-white'
                    : 'text-white hover:bg-white hover:bg-opacity-10'
                }`}
              >
                Leaderboard
              </button>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {currentPage === 'dashboard' && (
          <Dashboard userId={userId} onShowToast={showToast} onUserCreated={handleCreateUser} />
        )}
        {currentPage === 'leaderboard' && (
          <Leaderboard onShowToast={showToast} />
        )}
      </main>

      {toast && <Toast message={toast.message} type={toast.type} />}
    </div>
  )
}

export default App
