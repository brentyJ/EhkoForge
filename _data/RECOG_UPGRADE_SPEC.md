# EhkoForge Upgrade Specification
## Based on ReCog Advancements

**Created:** 2026-01-18
**Purpose:** Backport relevant improvements from ReCog to EhkoForge
**Scope:** Frontend + Backend architectural upgrades

---

## Executive Summary

ReCog has evolved significantly with production-grade patterns that EhkoForge can benefit from. This spec identifies **relevant** upgrades—not wholesale replacement, but targeted improvements that align with EhkoForge's architecture and purpose.

### Key Differences (Context for Filtering)

| Aspect | EhkoForge | ReCog |
|--------|-----------|-------|
| **Primary UI** | Terminal chat interface | Dashboard analytics |
| **Core Loop** | Conversation → Reflection → Ingots | Upload → Extract → Analyse |
| **User Model** | Single user, personal vault | Multi-case investigation |
| **State Complexity** | Session-based chat | Multi-entity relationships |
| **Visual Identity** | Retro terminal aesthetic | Holographic/modern |

**Filtering Principle:** Only adopt patterns that enhance EhkoForge without compromising its terminal-first identity or adding unnecessary complexity.

---

## PART 1: BACKEND UPGRADES

### 1.1 Custom Exception Hierarchy (HIGH PRIORITY)

**ReCog Pattern:** `errors.py` (293 lines)
- Base `RecogError` with dual messaging (technical + user-friendly)
- HTTP status codes embedded in exceptions
- Centralized Flask error handler

**Current EhkoForge:** Bare `except Exception as e` with inline error messages

**Upgrade:**
```python
# New file: 5.0 Scripts/ehkoforge/errors.py

class EhkoForgeError(Exception):
    """Base exception with dual messaging."""
    def __init__(self, message: str, user_message: str = None, status_code: int = 500):
        super().__init__(message)
        self.user_message = user_message or message
        self.status_code = status_code

class ManaInsufficientError(EhkoForgeError):
    def __init__(self, required: int, available: int):
        super().__init__(
            f"Insufficient mana: need {required}, have {available}",
            f"Not enough mana. You need {required} but only have {available}.",
            402  # Payment Required
        )

class TetherConnectionError(EhkoForgeError):
    def __init__(self, provider: str, original_error: str):
        super().__init__(
            f"Tether to {provider} failed: {original_error}",
            f"Connection to {provider} unavailable. Check your API key.",
            503
        )

class SessionNotFoundError(EhkoForgeError):
    def __init__(self, session_id: str):
        super().__init__(
            f"Session {session_id} not found",
            "This conversation no longer exists.",
            404
        )

# ... LLMProviderError, IngotValidationError, VaultIndexError, etc.
```

**Flask Handler:**
```python
@app.errorhandler(EhkoForgeError)
def handle_ehkoforge_error(error: EhkoForgeError):
    logger.error(f"[{error.__class__.__name__}] {error}")
    return jsonify({
        "success": False,
        "error": error.user_message,
        "error_type": error.__class__.__name__
    }), error.status_code
```

**Effort:** 2-3 hours | **Impact:** High (debuggability, user experience)

---

### 1.2 Structured Logging with Context (HIGH PRIORITY)

**ReCog Pattern:** `logging_utils.py` (400+ lines)
- Context variables for request tracing (request_id, case_id, session_id)
- Secrets sanitisation filter (redacts API keys in logs)
- Dual output modes (JSON for production, text for development)
- Log rotation

**Current EhkoForge:** `print()` statements throughout

**Upgrade:**
```python
# New file: 5.0 Scripts/ehkoforge/logging_utils.py

from contextvars import ContextVar
import logging
import re

request_id_var: ContextVar[str] = ContextVar("request_id", default="")
session_id_var: ContextVar[str] = ContextVar("session_id", default="")

class SecretsSanitiser(logging.Filter):
    PATTERNS = [
        (re.compile(r'sk-[a-zA-Z0-9]{20,}'), '[OPENAI_KEY]'),
        (re.compile(r'sk-ant-[a-zA-Z0-9\-]{20,}'), '[ANTHROPIC_KEY]'),
        (re.compile(r'(api_key|password|token)\s*[:=]\s*\S+'), r'\1=[REDACTED]'),
    ]

    def filter(self, record):
        msg = record.getMessage()
        for pattern, replacement in self.PATTERNS:
            msg = pattern.sub(replacement, msg)
        record.msg = msg
        return True

def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.addFilter(SecretsSanitiser())
    return logger
```

**Request Middleware:**
```python
@app.before_request
def before_request_logging():
    request_id = request.headers.get("X-Request-ID", str(uuid4())[:8])
    set_request_id(request_id)
    request.start_time = time.time()

@app.after_request
def after_request_logging(response):
    duration_ms = (time.time() - request.start_time) * 1000
    logger.info(f"{request.method} {request.path} → {response.status_code} ({duration_ms:.0f}ms)")
    response.headers["X-Request-ID"] = get_request_id()
    return response
```

**Effort:** 3-4 hours | **Impact:** High (debugging, observability)

---

### 1.3 API Response Standardisation (MEDIUM PRIORITY)

**ReCog Pattern:** Consistent JSON envelope
```json
{
  "success": true|false,
  "timestamp": "2026-01-18T...",
  "data": { ... },
  "error": "Human-readable message (if success=false)"
}
```

**Current EhkoForge:** Inconsistent—some endpoints return `{"status": "ok"}`, others `{"success": true}`, others raw data

**Upgrade:**
```python
# Add to forge_server.py or new utils file

def api_response(data=None, error=None, status=200):
    """Standard API response wrapper."""
    response = {
        "success": error is None,
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }
    if data is not None:
        response["data"] = data
    if error is not None:
        response["error"] = error
    return jsonify(response), status

# Usage:
@app.route("/api/sessions/<session_id>")
def get_session(session_id):
    session = load_session(session_id)
    if not session:
        return api_response(error="Session not found", status=404)
    return api_response(data=session)
```

**Effort:** 2-3 hours (refactor existing endpoints) | **Impact:** Medium (consistency, frontend simplification)

---

### 1.4 Cost Tracking System (MEDIUM PRIORITY)

**ReCog Pattern:** `cost_tracker.py` (350+ lines)
- Per-request token counting and cost calculation
- Database logging for audit trail
- Summary queries by day/week/month/feature

**Current EhkoForge:** Mana system exists but no granular LLM cost tracking

**Upgrade:**
```python
# New file: 5.0 Scripts/ehkoforge/cost_tracker.py

PRICING = {
    "anthropic": {
        "claude-sonnet-4-20250514": {"input": 3.00, "output": 15.00},  # $/1M tokens
    },
    "openai": {
        "gpt-4o-mini": {"input": 0.15, "output": 0.60},
        "gpt-4o": {"input": 2.50, "output": 10.00},
    },
}

def log_llm_cost(db_path, feature: str, provider: str, model: str,
                 input_tokens: int, output_tokens: int, latency_ms: int):
    """Log LLM call cost to database for tracking."""
    pricing = PRICING.get(provider, {}).get(model, {"input": 0, "output": 0})
    input_cost = (input_tokens / 1_000_000) * pricing["input"]
    output_cost = (output_tokens / 1_000_000) * pricing["output"]
    total_cost = input_cost + output_cost

    conn = sqlite3.connect(str(db_path))
    conn.execute("""
        INSERT INTO cost_logs (feature, provider, model, input_tokens, output_tokens,
                               cost_cents, latency_ms, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'))
    """, (feature, provider, model, input_tokens, output_tokens, total_cost * 100, latency_ms))
    conn.commit()
    conn.close()
    return total_cost
```

**New Table:**
```sql
CREATE TABLE IF NOT EXISTS cost_logs (
    id INTEGER PRIMARY KEY,
    feature TEXT NOT NULL,        -- 'chat', 'extract', 'correlate', 'synthesise'
    provider TEXT NOT NULL,
    model TEXT NOT NULL,
    input_tokens INTEGER,
    output_tokens INTEGER,
    cost_cents REAL,
    latency_ms INTEGER,
    created_at TEXT DEFAULT (datetime('now'))
);
CREATE INDEX idx_cost_logs_feature ON cost_logs(feature);
CREATE INDEX idx_cost_logs_created ON cost_logs(created_at);
```

**Effort:** 2-3 hours | **Impact:** Medium (visibility into actual costs)

---

### 1.5 Response Caching (LOW-MEDIUM PRIORITY)

**ReCog Pattern:** `response_cache.py` (400+ lines)
- Content-hash based deduplication
- File-based cache with TTL
- Hit rate tracking

**EhkoForge Relevance:** Useful for repeated ReCog processing of same content (re-uploads, re-runs)

**Upgrade:** Adopt ReCog's pattern for the recog_engine module. Not needed for chat (each message is unique).

**Effort:** 2 hours (copy + adapt) | **Impact:** Low-Medium (saves mana on reprocessing)

---

### 1.6 Rate Limiting (LOW PRIORITY for single-user)

**ReCog Pattern:** Flask-Limiter with tiered limits

**EhkoForge Relevance:** Lower priority since EhkoForge is single-user. Consider if exposing API publicly later.

**Recommendation:** Defer unless multi-user support planned.

---

### 1.7 Provider Failover Configuration (MEDIUM PRIORITY)

**ReCog Pattern:** Primary + fallback provider with automatic switching

**Current EhkoForge:** Role-based routing exists but no failover chain

**Upgrade:**
```python
# Extend LLMConfig in config.py

@dataclass
class ProviderConfig:
    api_key: str
    default_model: str
    fallback_provider: Optional[str] = None  # NEW
    max_retries: int = 2                      # NEW

def get_provider_with_fallback(role: str, config: LLMConfig) -> LLMProvider:
    """Try primary provider, fall back if unavailable."""
    primary = get_provider_for_role(role, config)
    try:
        if primary and primary.test_connection():
            return primary
    except Exception as e:
        logger.warning(f"Primary provider for {role} failed: {e}")

    # Try fallback
    fallback_key = config.providers.get(role, {}).fallback_provider
    if fallback_key:
        fallback = get_provider(fallback_key, config)
        if fallback and fallback.test_connection():
            logger.info(f"Using fallback provider for {role}: {fallback_key}")
            return fallback

    return None
```

**Effort:** 1-2 hours | **Impact:** Medium (resilience)

---

## PART 2: FRONTEND UPGRADES

### 2.1 Centralised State Management (HIGH PRIORITY)

**ReCog Pattern:** `CypherContext.jsx` (377 lines)
- React Context with comprehensive state
- Event-driven updates via custom window events
- localStorage persistence for preferences

**Current EhkoForge:**
- `main.js`: Global state object mutated directly
- `control_panel`: Local useState per component, no shared state

**Upgrade for Control Panel:**
```jsx
// New file: control_panel/src/contexts/ForgeContext.jsx

import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';

const ForgeContext = createContext(null);

export function ForgeProvider({ children }) {
  const [servers, setServers] = useState({});
  const [manaBalance, setManaBalance] = useState({ current: 0, max: 100 });
  const [tethers, setTethers] = useState([]);
  const [recogStatus, setRecogStatus] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  // Centralised data fetching
  const refreshAll = useCallback(async () => {
    setIsLoading(true);
    try {
      const [statusRes, manaRes, tethersRes] = await Promise.all([
        ForgeAPI.getStatus(),
        ForgeAPI.getManaStatus(),
        ForgeAPI.getTethers(),
      ]);
      setServers(statusRes.data);
      setManaBalance(manaRes.data);
      setTethers(tethersRes.data);
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Polling
  useEffect(() => {
    refreshAll();
    const interval = setInterval(refreshAll, 5000);
    return () => clearInterval(interval);
  }, [refreshAll]);

  // Event listeners for cross-component communication
  useEffect(() => {
    const handleManaUpdate = (e) => setManaBalance(e.detail);
    const handleTetherUpdate = () => refreshAll();

    window.addEventListener('forge-mana-update', handleManaUpdate);
    window.addEventListener('forge-tether-update', handleTetherUpdate);

    return () => {
      window.removeEventListener('forge-mana-update', handleManaUpdate);
      window.removeEventListener('forge-tether-update', handleTetherUpdate);
    };
  }, [refreshAll]);

  const value = {
    servers, manaBalance, tethers, recogStatus,
    isLoading, error,
    refreshAll,
    // Actions
    startServer: async (name) => { /* ... */ },
    stopServer: async (name) => { /* ... */ },
  };

  return <ForgeContext.Provider value={value}>{children}</ForgeContext.Provider>;
}

export const useForge = () => useContext(ForgeContext);
```

**Effort:** 4-5 hours | **Impact:** High (maintainability, debugging)

---

### 2.2 Event-Driven Cross-Component Communication (HIGH PRIORITY)

**ReCog Pattern:** Custom window events
```javascript
window.dispatchEvent(new CustomEvent('recog-extraction-progress', { detail: {...} }));
window.dispatchEvent(new CustomEvent('refresh-entities'));
```

**Current EhkoForge:** Direct DOM manipulation and callback chains

**Upgrade for main.js:**
```javascript
// Define event types
const ForgeEvents = {
  MANA_UPDATE: 'forge-mana-update',
  TETHER_CHANGE: 'forge-tether-change',
  AUTHORITY_UPDATE: 'forge-authority-update',
  SESSION_CHANGE: 'forge-session-change',
  MESSAGE_SENT: 'forge-message-sent',
  MESSAGE_RECEIVED: 'forge-message-received',
  MODE_CHANGE: 'forge-mode-change',
};

// Emit events instead of direct DOM updates
function updateManaDisplay(manaData) {
  window.dispatchEvent(new CustomEvent(ForgeEvents.MANA_UPDATE, {
    detail: manaData
  }));
}

// Web Components listen for events
class EhkoManaBar extends HTMLElement {
  connectedCallback() {
    window.addEventListener('forge-mana-update', (e) => {
      this.setMana(e.detail.current, e.detail.max);
    });
  }
}
```

**Effort:** 3-4 hours | **Impact:** High (decoupling, testability)

---

### 2.3 API Client Enhancement (MEDIUM PRIORITY)

**ReCog Pattern:** `api.js` (550+ lines)
- Custom `APIError` class
- Centralised `fetchAPI` wrapper with error normalisation
- ~45+ typed API functions

**Current EhkoForge:** `ForgeAPI` static class—good start but missing:
- Custom error class
- Request/response interceptors
- Request cancellation (AbortController)
- Retry logic

**Upgrade:**
```javascript
// Enhance: control_panel/src/lib/api.js

class ForgeAPIError extends Error {
  constructor(message, status, data = null) {
    super(message);
    this.name = 'ForgeAPIError';
    this.status = status;
    this.data = data;
  }

  get isNetworkError() { return this.status === 0; }
  get isServerError() { return this.status >= 500; }
  get isClientError() { return this.status >= 400 && this.status < 500; }
}

async function fetchAPI(endpoint, options = {}) {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), options.timeout || 30000);

  try {
    const response = await fetch(`/api${endpoint}`, {
      ...options,
      signal: controller.signal,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    });

    clearTimeout(timeoutId);
    const data = await response.json();

    if (!response.ok || data.success === false) {
      throw new ForgeAPIError(
        data.error || `Request failed with status ${response.status}`,
        response.status,
        data
      );
    }

    return data;
  } catch (err) {
    clearTimeout(timeoutId);
    if (err.name === 'AbortError') {
      throw new ForgeAPIError('Request timed out', 0);
    }
    if (err instanceof ForgeAPIError) throw err;
    throw new ForgeAPIError(err.message, 0);
  }
}
```

**Effort:** 2-3 hours | **Impact:** Medium (error handling, reliability)

---

### 2.4 Error Boundaries (MEDIUM PRIORITY)

**ReCog Pattern:** `error-boundary.jsx`
- Class component wrapper with stack traces
- Reset button and navigation to dashboard
- Graceful degradation

**Current EhkoForge:** No error boundaries—React crashes show blank screen

**Upgrade:**
```jsx
// New file: control_panel/src/components/ui/error-boundary.jsx

import React from 'react';
import { Button } from './button';
import { AlertTriangle } from 'lucide-react';

export class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('ErrorBoundary caught:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="flex flex-col items-center justify-center p-8 text-center">
          <AlertTriangle className="h-12 w-12 text-orange-500 mb-4" />
          <h2 className="text-xl font-semibold mb-2">Something went wrong</h2>
          <p className="text-muted-foreground mb-4">
            {this.state.error?.message || 'An unexpected error occurred'}
          </p>
          <Button onClick={() => this.setState({ hasError: false, error: null })}>
            Try Again
          </Button>
        </div>
      );
    }

    return this.props.children;
  }
}
```

**Effort:** 1 hour | **Impact:** Medium (user experience on errors)

---

### 2.5 Loading & Empty States (MEDIUM PRIORITY)

**ReCog Pattern:** Reusable `LoadingState` and `EmptyState` components with variants

**Current EhkoForge:** Basic "Loading..." text

**Upgrade:**
```jsx
// New file: control_panel/src/components/ui/loading-state.jsx

export function LoadingState({ message = "Loading...", size = "default" }) {
  const sizes = {
    sm: "h-4 w-4",
    default: "h-8 w-8",
    lg: "h-12 w-12",
  };

  return (
    <div className="flex flex-col items-center justify-center p-8">
      <div className={`animate-spin rounded-full border-2 border-primary border-t-transparent ${sizes[size]}`} />
      <p className="mt-4 text-muted-foreground">{message}</p>
    </div>
  );
}

// New file: control_panel/src/components/ui/empty-state.jsx

export function EmptyState({ icon: Icon, title, description, action }) {
  return (
    <div className="flex flex-col items-center justify-center p-8 text-center">
      {Icon && <Icon className="h-12 w-12 text-muted-foreground mb-4" />}
      <h3 className="text-lg font-medium mb-2">{title}</h3>
      {description && <p className="text-muted-foreground mb-4">{description}</p>}
      {action}
    </div>
  );
}
```

**Effort:** 1-2 hours | **Impact:** Medium (polish)

---

### 2.6 main.js Modularisation (HIGH PRIORITY)

**Current State:** 1,630 lines in single file with mixed concerns

**ReCog Pattern:** Separated into contexts, hooks, api, components

**Upgrade Plan:**
```
6.0 Frontend/static/js/
├── main.js              # Reduced to ~200 lines (init + orchestration)
├── forge-api.js         # API calls (extracted)
├── forge-state.js       # State management (extracted)
├── forge-events.js      # Event system (new)
├── forge-ui.js          # DOM manipulation helpers (extracted)
└── forge-animations.js  # Animation utilities (extracted)
```

**Effort:** 4-6 hours | **Impact:** High (maintainability)

---

### 2.7 Progress Tracking with ETA (LOW-MEDIUM PRIORITY)

**ReCog Pattern:** `CypherProgress.jsx`
- Real-time ETA calculation
- Progress bar with gradient
- Current document display

**EhkoForge Relevance:** Useful for ReCog processing in EhkoForge

**Upgrade:** Adapt for EhkoForge's control panel when showing ReCog queue processing.

**Effort:** 2 hours | **Impact:** Low-Medium (UX during processing)

---

## PART 3: SHARED/INFRASTRUCTURE

### 3.1 Migration System (MEDIUM PRIORITY)

**ReCog Pattern:** `migrations/` folder with versioned SQL files
- Clear naming: `migration_v0_2_blacklist.sql`, `migration_v0_3_*.sql`
- `CREATE TABLE IF NOT EXISTS` for idempotency
- Applied via `db.py` init function

**Current EhkoForge:** Manual migration scripts (`run_*_migration.py`)

**Upgrade:** Consolidate into `migrations/` folder with version tracking table.

```sql
-- migrations/migration_v0_1_cost_logs.sql
CREATE TABLE IF NOT EXISTS cost_logs (...);

-- migrations/migration_v0_2_error_logs.sql
CREATE TABLE IF NOT EXISTS error_logs (...);
```

```python
# db_utils.py
def apply_migrations(db_path):
    """Apply pending migrations in order."""
    conn = sqlite3.connect(str(db_path))

    # Create tracking table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS _migrations (
            version TEXT PRIMARY KEY,
            applied_at TEXT DEFAULT (datetime('now'))
        )
    """)

    applied = {row[0] for row in conn.execute("SELECT version FROM _migrations")}

    for migration_file in sorted(MIGRATIONS_DIR.glob("migration_v*.sql")):
        version = migration_file.stem
        if version not in applied:
            conn.executescript(migration_file.read_text())
            conn.execute("INSERT INTO _migrations (version) VALUES (?)", (version,))
            conn.commit()

    conn.close()
```

**Effort:** 2-3 hours | **Impact:** Medium (maintainability)

---

### 3.2 Configuration Validation (MEDIUM PRIORITY)

**ReCog Pattern:** Startup validation of providers, paths, environment

**Current EhkoForge:** Environment variables loaded without validation

**Upgrade:**
```python
# New file: 5.0 Scripts/ehkoforge/config_validator.py

def validate_config():
    """Validate configuration on startup. Raises ConfigError if invalid."""
    errors = []

    # Check required env vars
    if not os.environ.get("ANTHROPIC_API_KEY") and not os.environ.get("OPENAI_API_KEY"):
        errors.append("At least one LLM API key required (ANTHROPIC_API_KEY or OPENAI_API_KEY)")

    # Check database path
    db_path = Path(os.environ.get("EHKO_DB_PATH", "_data/ehko_index.db"))
    if not db_path.parent.exists():
        errors.append(f"Database directory does not exist: {db_path.parent}")

    # Check vault path
    vault_path = Path(os.environ.get("EHKO_VAULT_PATH", ".."))
    if not vault_path.exists():
        errors.append(f"Vault path does not exist: {vault_path}")

    if errors:
        raise ConfigError("Configuration validation failed:\n" + "\n".join(f"  - {e}" for e in errors))
```

**Effort:** 1-2 hours | **Impact:** Medium (fail-fast on misconfiguration)

---

## PART 4: NOT RECOMMENDED

These ReCog features are **not recommended** for EhkoForge:

| Feature | Reason |
|---------|--------|
| **Virtual Scrolling** | EhkoForge doesn't have large lists (sessions capped, ingots manageable) |
| **Hash-based Routing** | Control panel is simple; React Router overkill |
| **Recharts Dashboard** | EhkoForge's terminal aesthetic doesn't suit charts |
| **Case Management** | EhkoForge is single-user, single-context |
| **Findings/Promotion** | Ingot system already handles this |
| **Preflight Batch UI** | ReCog's upload workflow doesn't apply |
| **Assistant Mode Toggle** | Ehko IS the assistant; no toggle needed |
| **PII Redactor** | EhkoForge is personal vault; user owns all data |

---

## IMPLEMENTATION PRIORITY

### Phase 1: Foundation (Week 1)
1. Custom Exception Hierarchy (backend)
2. Structured Logging (backend)
3. API Response Standardisation (backend)
4. Error Boundaries (frontend)

### Phase 2: State Management (Week 2)
5. ForgeContext (React control panel)
6. Event System (main.js)
7. API Client Enhancement (frontend)

### Phase 3: Observability (Week 3)
8. Cost Tracking System (backend)
9. Loading/Empty States (frontend)
10. main.js Modularisation (frontend)

### Phase 4: Infrastructure (Week 4)
11. Migration System (backend)
12. Configuration Validation (backend)
13. Provider Failover (backend)
14. Response Caching (backend - ReCog module only)

---

## FILE CHANGES SUMMARY

### New Files
```
5.0 Scripts/
├── ehkoforge/
│   ├── errors.py           # Exception hierarchy
│   ├── logging_utils.py    # Structured logging
│   ├── cost_tracker.py     # LLM cost tracking
│   └── config_validator.py # Startup validation
├── migrations/
│   ├── migration_v0_1_cost_logs.sql
│   └── ...
└── db_utils.py              # Migration runner

control_panel/src/
├── contexts/
│   └── ForgeContext.jsx    # Centralised state
├── components/ui/
│   ├── error-boundary.jsx
│   ├── loading-state.jsx
│   └── empty-state.jsx
└── lib/
    └── api.js              # Enhanced (not new)

6.0 Frontend/static/js/
├── forge-api.js            # Extracted from main.js
├── forge-state.js          # Extracted from main.js
├── forge-events.js         # New event system
├── forge-ui.js             # Extracted from main.js
└── forge-animations.js     # Extracted from main.js
```

### Modified Files
```
5.0 Scripts/
├── forge_server.py         # Error handlers, response wrapper, logging
└── recog_engine/
    ├── scheduler.py        # Cost tracking integration
    └── mana_manager.py     # Logging integration

control_panel/src/
├── App.jsx                 # Wrap with ForgeProvider, ErrorBoundary
└── main.jsx                # Add providers

6.0 Frontend/static/js/
└── main.js                 # Reduce to orchestration only
```

---

## ESTIMATED TOTAL EFFORT

| Phase | Effort | Files |
|-------|--------|-------|
| Phase 1 | 8-12 hours | 6 new, 2 modified |
| Phase 2 | 8-12 hours | 4 new, 3 modified |
| Phase 3 | 6-10 hours | 2 new, 6 modified |
| Phase 4 | 6-8 hours | 4 new, 2 modified |
| **Total** | **28-42 hours** | **16 new, 13 modified** |

---

## APPENDIX: RECOG PATTERNS NOT TRANSFERRED (Reference)

For future reference, these patterns exist in ReCog but were deemed not applicable:

1. **Cypher Conversational Interface** - ReCog-specific; Ehko chat serves this purpose
2. **Entity Network Graph** - ReCog's multi-entity relationships; Ehko is single-subject
3. **Synthesis Runs** - Already exists in EhkoForge's recog_engine
4. **Provider Verification UI** - Tether system already handles this
5. **Document Upload Flow** - EhkoForge uses vault indexing instead
6. **Anonymisation Toggle** - Personal vault doesn't need anonymisation
