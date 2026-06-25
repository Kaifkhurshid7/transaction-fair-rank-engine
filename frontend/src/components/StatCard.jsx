import React from 'react'

export default function StatCard({ title, value, icon }) {
  return (
    <div className="glass-effect rounded-xl p-6 border border-white border-opacity-20">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-white text-opacity-70 text-sm font-medium">{title}</p>
          <p className="text-white text-2xl font-bold mt-2">{value}</p>
        </div>
        <div className="text-4xl">{icon}</div>
      </div>
    </div>
  )
}
