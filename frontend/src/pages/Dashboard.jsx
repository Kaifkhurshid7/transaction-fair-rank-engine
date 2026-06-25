import React, { useState, useEffect } from 'react'
import StatCard from '../components/StatCard'
import { v4 as uuidv4 } from 'crypto-js'

export default function Dashboard({ userId, onShowToast, onUserCreated }) {
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [amount, setAmount] = useState('')
  const [summary, setSummary] = useState(null)
  const [loading, setLoading] = useState(false)

  const handleCreateUser = async (e) => {
    e.preventDefault()
    if (!name || !email) {
      onShowToast('Please fill in all fields', 'error')
      return
    }
    setLoading(true)
    try {
      const response = await fetch(`/api/v1/summary/users?name=${encodeURIComponent(name)}&email=${encodeURIComponent(email)}`, {
        method: 'POST'
      })
      const data = await response.json()
      onUserCreated(name, email)
      setName('')
      setEmail('')
      setSummary(null)
    } catch (error) {
      onShowToast('Error creating user', 'error')
    } finally {
      setLoading(false)
    }
  }

  const handleTransaction = async (e) => {
    e.preventDefault()
    if (!userId) {
      onShowToast('Please create a user first', 'error')
      return
    }
    if (!amount || parseFloat(amount) <= 0) {
      onShowToast('Please enter a valid amount', 'error')
      return
    }

    setLoading(true)
    try {
      const response = await fetch('/api/v1/transaction', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: userId,
          amount: parseFloat(amount),
          idempotency_key: `txn_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
        })
      })
      const data = await response.json()
      if (response.ok) {
        onShowToast(`Transaction created! Earned ${data.points_earned} points`, 'success')
        setAmount('')
        fetchSummary()
      } else {
        onShowToast(data.message || 'Error creating transaction', 'error')
      }
    } catch (error) {
      onShowToast('Error creating transaction', 'error')
    } finally {
      setLoading(false)
    }
  }

  const fetchSummary = async () => {
    if (!userId) return
    try {
      const response = await fetch(`/api/v1/summary/${userId}`)
      const data = await response.json()
      setSummary(data)
    } catch (error) {
      console.error('Error fetching summary:', error)
    }
  }

  useEffect(() => {
    if (userId) {
      fetchSummary()
      const interval = setInterval(fetchSummary, 5000)
      return () => clearInterval(interval)
    }
  }, [userId])

  return (
    <div className="space-y-8">
      {!userId ? (
        <div className="glass-effect rounded-2xl p-8 max-w-md mx-auto">
          <h2 className="text-2xl font-bold text-white mb-6">Create Account</h2>
          <form onSubmit={handleCreateUser} className="space-y-4">
            <input
              type="text"
              placeholder="Your Name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full px-4 py-3 rounded-lg bg-white bg-opacity-20 text-white placeholder-white placeholder-opacity-60 border border-white border-opacity-30 focus:outline-none focus:ring-2 focus:ring-white"
            />
            <input
              type="email"
              placeholder="Email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full px-4 py-3 rounded-lg bg-white bg-opacity-20 text-white placeholder-white placeholder-opacity-60 border border-white border-opacity-30 focus:outline-none focus:ring-2 focus:ring-white"
            />
            <button
              type="submit"
              disabled={loading}
              className="w-full px-4 py-3 bg-gradient-to-r from-pink-500 to-red-500 text-white font-bold rounded-lg hover:opacity-90 disabled:opacity-50"
            >
              {loading ? 'Creating...' : 'Create Account'}
            </button>
          </form>
        </div>
      ) : (
        <>
          {summary && (
            <>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <StatCard title="Rank" value={`#${summary.current_rank}`} icon="🏆" />
                <StatCard title="Total Points" value={summary.total_points.toFixed(2)} icon="⭐" />
                <StatCard title="Total Amount" value={`$${summary.total_amount.toFixed(2)}`} icon="💰" />
                <StatCard title="Transactions" value={summary.transaction_count} icon="📊" />
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="glass-effect rounded-2xl p-8">
                  <h3 className="text-xl font-bold text-white mb-4">Profile</h3>
                  <div className="space-y-3 text-white text-opacity-90">
                    <p><strong>Name:</strong> {summary.name}</p>
                    <p><strong>Email:</strong> {summary.email}</p>
                    <p><strong>Consistency:</strong> {(summary.consistency_score * 100).toFixed(1)}%</p>
                    <p><strong>Ranking Score:</strong> {summary.ranking_score.toFixed(2)}</p>
                  </div>
                </div>

                <div className="glass-effect rounded-2xl p-8">
                  <h3 className="text-xl font-bold text-white mb-4">New Transaction</h3>
                  <form onSubmit={handleTransaction} className="space-y-4">
                    <input
                      type="number"
                      placeholder="Amount"
                      value={amount}
                      onChange={(e) => setAmount(e.target.value)}
                      step="0.01"
                      min="0"
                      className="w-full px-4 py-3 rounded-lg bg-white bg-opacity-20 text-white placeholder-white placeholder-opacity-60 border border-white border-opacity-30 focus:outline-none focus:ring-2 focus:ring-white"
                    />
                    <button
                      type="submit"
                      disabled={loading}
                      className="w-full px-4 py-3 bg-gradient-to-r from-green-500 to-emerald-500 text-white font-bold rounded-lg hover:opacity-90 disabled:opacity-50"
                    >
                      {loading ? 'Processing...' : 'Submit Transaction'}
                    </button>
                  </form>
                </div>
              </div>
            </>
          )}
        </>
      )}
    </div>
  )
}
