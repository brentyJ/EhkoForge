import { useState, useEffect } from 'react'

function App() {
  const [status, setStatus] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchStatus()
    const interval = setInterval(fetchStatus, 3000)
    return () => clearInterval(interval)
  }, [])

  const fetchStatus = async () => {
    try {
      const res = await fetch('/api/status')
      const data = await res.json()
      setStatus(data)
      setLoading(false)
    } catch (err) {
      console.error('Failed to fetch status:', err)
      setLoading(false)
    }
  }

  const handleServerAction = async (server, action) => {
    try {
      await fetch(`/api/server/${server}/${action}`, { method: 'POST' })
      fetchStatus() // Refresh immediately
    } catch (err) {
      console.error(`Failed to ${action} ${server}:`, err)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-primary font-mono">Loading...</div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-background p-8">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-foreground mb-2 font-mono">
            ⚒ EHKOFORGE CONTROL PANEL
          </h1>
          <p className="text-muted-foreground">Web-based server management</p>
        </div>

        {/* Server Status Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* EhkoForge Server */}
          <ServerCard
            name="EhkoForge"
            server="forge"
            port={5000}
            status={status?.forge}
            onStart={() => handleServerAction('forge', 'start')}
            onStop={() => handleServerAction('forge', 'stop')}
          />

          {/* ReCog Server */}
          <ServerCard
            name="ReCog"
            server="recog"
            port={5100}
            status={status?.recog}
            onStart={() => handleServerAction('recog', 'start')}
            onStop={() => handleServerAction('recog', 'stop')}
          />

          {/* Website Server */}
          <ServerCard
            name="Website"
            server="website"
            port={4321}
            status={status?.website}
            onStart={() => handleServerAction('website', 'start')}
            onStop={() => handleServerAction('website', 'stop')}
          />
        </div>

        {/* Quick Actions */}
        <div className="mt-8 p-6 rounded-lg border border-border bg-card">
          <h2 className="text-xl font-semibold text-foreground mb-4">Quick Actions</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <button className="px-4 py-2 rounded-md bg-primary text-primary-foreground hover:bg-primary/90 transition-colors font-medium">
              Refresh Vault
            </button>
            <button className="px-4 py-2 rounded-md bg-secondary text-secondary-foreground hover:bg-secondary/80 transition-colors font-medium">
              Git Commit
            </button>
            <button className="px-4 py-2 rounded-md bg-secondary text-secondary-foreground hover:bg-secondary/80 transition-colors font-medium">
              Git Push
            </button>
            <button className="px-4 py-2 rounded-md bg-secondary text-secondary-foreground hover:bg-secondary/80 transition-colors font-medium">
              Open Logs
            </button>
          </div>
        </div>

        {/* Footer Info */}
        <div className="mt-8 text-center text-sm text-muted-foreground font-mono">
          Control Panel v1.0 • Port 5001 • {status?.timestamp && new Date(status.timestamp).toLocaleTimeString()}
        </div>
      </div>
    </div>
  )
}

function ServerCard({ name, server, port, status, onStart, onStop }) {
  const isRunning = status?.running
  const statusColor = isRunning ? 'text-[hsl(var(--success))]' : 'text-muted-foreground'

  return (
    <div className="p-6 rounded-lg border border-border bg-card terminal-glow">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-foreground">{name}</h3>
        <span className={`text-sm font-mono ${statusColor}`}>
          {isRunning ? '● ACTIVE' : '○ STOPPED'}
        </span>
      </div>
      
      <div className="space-y-2 mb-4 text-sm">
        <div className="flex justify-between text-muted-foreground">
          <span>Port:</span>
          <span className="font-mono">{port}</span>
        </div>
        {status?.pid && (
          <div className="flex justify-between text-muted-foreground">
            <span>PID:</span>
            <span className="font-mono">{status.pid}</span>
          </div>
        )}
      </div>

      <div className="flex gap-2">
        {isRunning ? (
          <>
            <button
              onClick={onStop}
              className="flex-1 px-3 py-2 rounded-md bg-destructive text-destructive-foreground hover:bg-destructive/90 transition-colors text-sm font-medium"
            >
              Stop
            </button>
            <button
              onClick={() => window.open(`http://localhost:${port}`, '_blank')}
              className="flex-1 px-3 py-2 rounded-md bg-primary text-primary-foreground hover:bg-primary/90 transition-colors text-sm font-medium"
            >
              Open
            </button>
          </>
        ) : (
          <button
            onClick={onStart}
            className="w-full px-3 py-2 rounded-md bg-primary text-primary-foreground hover:bg-primary/90 transition-colors text-sm font-medium"
          >
            Start
          </button>
        )}
      </div>
    </div>
  )
}

export default App
