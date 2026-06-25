import React, { useState, useEffect } from 'react'

export default function Leaderboard({ onShowToast }) {
  const [rankings, setRankings] = useState([])
  const [loading, setLoading] = useState(false)

  const fetchRankings = async () => {
    setLoading(true)
    try {
      const response = await fetch('/api/v1/ranking?limit=100')
      const data = await response.json()
      setRankings(data.rankings)
    } catch (error) {
      onShowToast('Error fetching rankings', 'error')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchRankings()
    const interval = setInterval(fetchRankings, 5000)
    return () => clearInterval(interval)
  }, [])

  if (loading && rankings.length === 0) {
    return <div className="text-white text-center py-8">Loading rankings...</div>
  }

  return (
    <div className="space-y-6">
      <h2 className="text-3xl font-bold text-white">🏆 Global Leaderboard</h2>
      
      <div className="glass-effect rounded-2xl overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-white bg-opacity-10 border-b border-white border-opacity-20">
              <tr>
                <th className="px-6 py-4 text-left text-white font-semibold">Rank</th>
                <th className="px-6 py-4 text-left text-white font-semibold">User</th>
                <th className="px-6 py-4 text-right text-white font-semibold">Points</th>
                <th className="px-6 py-4 text-right text-white font-semibold">Transactions</th>
                <th className="px-6 py-4 text-right text-white font-semibold">Consistency</th>
                <th className="px-6 py-4 text-right text-white font-semibold">Score</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white divide-opacity-10">
              {rankings.map((entry) => (
                <tr
                  key={entry.user_id}
                  className="hover:bg-white hover:bg-opacity-10 transition"
                >
                  <td className="px-6 py-4">
                    <span className="text-2xl font-bold">
                      {entry.rank === 1 && '🥇'}
                      {entry.rank === 2 && '🥈'}
                      {entry.rank === 3 && '🥉'}
                      {entry.rank > 3 && `#${entry.rank}`}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <div className="text-white font-semibold">{entry.name}</div>
                    <div className="text-white text-opacity-60 text-sm">{entry.email}</div>
                  </td>
                  <td className="px-6 py-4 text-right text-white">
                    {entry.total_points.toFixed(2)} ⭐
                  </td>
                  <td className="px-6 py-4 text-right text-white">
                    {entry.transaction_count}
                  </td>
                  <td className="px-6 py-4 text-right text-white">
                    {(entry.consistency_score * 100).toFixed(0)}%
                  </td>
                  <td className="px-6 py-4 text-right">
                    <span className="bg-white bg-opacity-20 text-white px-3 py-1 rounded-lg font-bold">
                      {entry.score.toFixed(0)}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {rankings.length === 0 && (
        <div className="glass-effect rounded-2xl p-8 text-center">
          <p className="text-white text-opacity-60">No rankings yet. Create an account and start transacting!</p>
        </div>
      )}
    </div>
  )
}
