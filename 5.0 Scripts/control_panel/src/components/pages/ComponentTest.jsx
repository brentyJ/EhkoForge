import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Badge } from "@/components/ui/badge"
import { Textarea } from "@/components/ui/textarea"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"

export function ComponentTest() {
  const [dialogOpen, setDialogOpen] = useState(false)

  return (
    <div className="container mx-auto p-8 space-y-8">
      <h1 className="text-3xl font-bold font-mono">EhkoForge Component Test</h1>
      <p className="text-muted-foreground">All shadcn/ui components with EhkoForge terminal theme</p>

      {/* Button variants */}
      <Card className="terminal-glow">
        <CardHeader>
          <CardTitle>Buttons</CardTitle>
          <CardDescription>All button variants and sizes</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex gap-2 flex-wrap">
            <Button>Default</Button>
            <Button variant="destructive">Destructive</Button>
            <Button variant="outline">Outline</Button>
            <Button variant="secondary">Secondary</Button>
            <Button variant="ghost">Ghost</Button>
            <Button variant="link">Link</Button>
          </div>
          <div className="flex gap-2 flex-wrap items-center">
            <Button size="sm">Small</Button>
            <Button size="default">Default</Button>
            <Button size="lg">Large</Button>
            <Button size="icon">I</Button>
          </div>
        </CardContent>
      </Card>

      {/* Form inputs */}
      <Card>
        <CardHeader>
          <CardTitle>Form Elements</CardTitle>
          <CardDescription>Input, Label, Textarea, Select</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="email">Email</Label>
            <Input id="email" type="email" placeholder="ehko@ehkolabs.io" />
          </div>
          <div className="space-y-2">
            <Label htmlFor="message">Message</Label>
            <Textarea id="message" placeholder="Enter your message..." />
          </div>
          <div className="space-y-2">
            <Label>Select an option</Label>
            <Select>
              <SelectTrigger>
                <SelectValue placeholder="Select..." />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="option1">Option 1</SelectItem>
                <SelectItem value="option2">Option 2</SelectItem>
                <SelectItem value="option3">Option 3</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* Badges */}
      <Card>
        <CardHeader>
          <CardTitle>Badges</CardTitle>
        </CardHeader>
        <CardContent className="flex gap-2 flex-wrap">
          <Badge>Default</Badge>
          <Badge variant="secondary">Secondary</Badge>
          <Badge variant="destructive">Destructive</Badge>
          <Badge variant="outline">Outline</Badge>
        </CardContent>
      </Card>

      {/* Tabs */}
      <Card>
        <CardHeader>
          <CardTitle>Tabs</CardTitle>
        </CardHeader>
        <CardContent>
          <Tabs defaultValue="servers" className="w-full">
            <TabsList>
              <TabsTrigger value="servers">Servers</TabsTrigger>
              <TabsTrigger value="settings">Settings</TabsTrigger>
              <TabsTrigger value="logs">Logs</TabsTrigger>
            </TabsList>
            <TabsContent value="servers" className="p-4 border rounded-md mt-2">
              <p className="text-muted-foreground">Server management content here</p>
            </TabsContent>
            <TabsContent value="settings" className="p-4 border rounded-md mt-2">
              <p className="text-muted-foreground">Settings content here</p>
            </TabsContent>
            <TabsContent value="logs" className="p-4 border rounded-md mt-2">
              <p className="text-muted-foreground">Logs content here</p>
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>

      {/* Dialog */}
      <Card>
        <CardHeader>
          <CardTitle>Dialog</CardTitle>
        </CardHeader>
        <CardContent>
          <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
            <DialogTrigger asChild>
              <Button>Open Dialog</Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Confirm Action</DialogTitle>
                <DialogDescription>
                  This is a sample dialog with the EhkoForge terminal theme.
                </DialogDescription>
              </DialogHeader>
              <div className="py-4">
                <p className="text-sm text-muted-foreground">
                  Dialog content goes here. You can add forms, confirmations, or any other content.
                </p>
              </div>
              <DialogFooter>
                <Button variant="outline" onClick={() => setDialogOpen(false)}>Cancel</Button>
                <Button onClick={() => setDialogOpen(false)}>Confirm</Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        </CardContent>
      </Card>

      {/* Status Colors */}
      <Card>
        <CardHeader>
          <CardTitle>Status Colors</CardTitle>
          <CardDescription>EhkoForge-specific status indicators</CardDescription>
        </CardHeader>
        <CardContent className="flex gap-4">
          <div className="flex items-center gap-2">
            <span className="status-active">● Active</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="status-stopped">○ Stopped</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="status-error">● Error</span>
          </div>
        </CardContent>
      </Card>

      {/* Card with footer */}
      <Card className="terminal-glow">
        <CardHeader>
          <CardTitle>Server Status</CardTitle>
          <CardDescription>Example card with terminal glow effect</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            <div className="flex justify-between">
              <span className="text-muted-foreground">Status:</span>
              <span className="status-active font-mono">● RUNNING</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Port:</span>
              <span className="font-mono">5000</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">PID:</span>
              <span className="font-mono">12345</span>
            </div>
          </div>
        </CardContent>
        <CardFooter className="gap-2">
          <Button variant="destructive" size="sm">Stop</Button>
          <Button size="sm">Open</Button>
        </CardFooter>
      </Card>
    </div>
  )
}

export default ComponentTest
