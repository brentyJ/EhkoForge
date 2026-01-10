import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle, CardFooter } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import ComponentTest from '@/components/pages/ComponentTest'

function App() {
  const [status, setStatus] = useState(null)
  const [loading, setLoading] = useState(true)
  const [showTest, setShowTest] = useState(false)

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

  // Show component test page
  if (showTest) {
    return (
      <div className="min-h-screen bg-background">
        <div className="fixed top-4 right-4 z-50">
          <Button variant="outline" onClick={() => setShowTest(false)}>
            Back to Control Panel
          </Button>
        </div>
        <ComponentTest />
      </div>
    )
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
        <div className="mb-8 flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-foreground mb-2 font-mono">
              EHKOFORGE CONTROL PANEL
            </h1>
            <p className="text-muted-foreground">Web-based server management</p>
          </div>
          <Button variant="outline" size="sm" onClick={() => setShowTest(true)}>
            Component Test
          </Button>
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
        <Card className="mt-8">
          <CardHeader>
            <CardTitle>Quick Actions</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <Button>Refresh Vault</Button>
              <Button variant="secondary">Git Commit</Button>
              <Button variant="secondary">Git Push</Button>
              <Button variant="secondary">Open Logs</Button>
            </div>
          </CardContent>
        </Card>

        {/* Footer Info */}
        <div className="mt-8 text-center text-sm text-muted-foreground font-mono">
          Control Panel v2.0 • Port 5001 • {status?.timestamp && new Date(status.timestamp).toLocaleTimeString()}
        </div>
      </div>
    </div>
  )
}

function ServerCard({ name, server, port, status, onStart, onStop }) {
  const isRunning = status?.running

  return (
    <Card className="terminal-glow">
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg">{name}</CardTitle>
          <Badge variant={isRunning ? 'default' : 'secondary'}>
            {isRunning ? 'ACTIVE' : 'STOPPED'}
          </Badge>
        </div>
      </CardHeader>
      <CardContent className="space-y-2 text-sm">
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
      </CardContent>
      <CardFooter className="gap-2">
        {isRunning ? (
          <>
            <Button variant="destructive" size="sm" className="flex-1" onClick={onStop}>
              Stop
            </Button>
            <Button size="sm" className="flex-1" onClick={() => window.open(`http://localhost:${port}`, '_blank')}>
              Open
            </Button>
          </>
        ) : (
          <Button size="sm" className="w-full" onClick={onStart}>
            Start
          </Button>
        )}
      </CardFooter>
    </Card>
  )
}

export default App
