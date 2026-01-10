const API_BASE = 'http://localhost:5001'

export class ForgeAPI {
  static async fetch(endpoint, options = {}) {
    const response = await fetch(`${API_BASE}${endpoint}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    })

    if (!response.ok) {
      throw new Error(`API error: ${response.statusText}`)
    }

    return response.json()
  }

  // Status endpoint
  static async getStatus() {
    return this.fetch('/api/status')
  }

  // Server control
  static async startServer(server) {
    return this.fetch(`/api/server/${server}/start`, { method: 'POST' })
  }

  static async stopServer(server) {
    return this.fetch(`/api/server/${server}/stop`, { method: 'POST' })
  }

  // Mana endpoints
  static async getManaStatus() {
    return this.fetch('/api/mana/status')
  }

  static async purchaseMana(amount) {
    return this.fetch('/api/mana/purchase', {
      method: 'POST',
      body: JSON.stringify({ amount }),
    })
  }

  // Tether endpoints
  static async getTethers() {
    return this.fetch('/api/tethers')
  }

  static async createTether(data) {
    return this.fetch('/api/tethers', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }

  static async deleteTether(provider) {
    return this.fetch(`/api/tethers/${provider}`, { method: 'DELETE' })
  }

  // ReCog endpoints
  static async getRecogStatus() {
    return this.fetch('/api/recog/status')
  }

  static async getRecogPending() {
    return this.fetch('/api/recog/pending')
  }

  static async confirmRecogOperation(id) {
    return this.fetch(`/api/recog/confirm/${id}`, { method: 'POST' })
  }

  static async cancelRecogOperation(id) {
    return this.fetch(`/api/recog/cancel/${id}`, { method: 'POST' })
  }

  static async processRecog() {
    return this.fetch('/api/recog/process', { method: 'POST' })
  }

  // Git operations
  static async gitCommit(message) {
    return this.fetch('/api/git/commit', {
      method: 'POST',
      body: JSON.stringify({ message }),
    })
  }

  static async gitPush() {
    return this.fetch('/api/git/push', { method: 'POST' })
  }

  // Vault operations
  static async refreshVault() {
    return this.fetch('/api/vault/refresh', { method: 'POST' })
  }
}

// Convenience hook for React
export function useAPI() {
  return ForgeAPI
}
