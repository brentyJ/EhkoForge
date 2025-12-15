---
title: "Quick Commands Reference"
vault: "EhkoForge"
type: "system"
category: "_data"
status: "active"
version: "1.0"
created: 2025-12-08
updated: 2025-12-08
tags: [system, reference, commands]
---

# QUICK COMMANDS REFERENCE

**Purpose:** Fast lookup for common EhkoForge commands and workflows
**Load:** When you need a command reminder

---

## COMMIT WORKFLOWS

### ⚡ Quick Commit
**Use for:** Small changes, typo fixes, quick updates
**Method:** Control panel "⚡ Quick" button OR `quick_commit.bat "message"`
**Does:** `git add` → `git commit` → `git push` (all automatic)
**Example:** `quick_commit.bat "Fix typo in health check"`

### 📝 Session Commit
**Use for:** End of work session, documented changes
**Method:** Control panel "📝 Session" button OR `git_push.bat`
**Does:** Opens batch file for manual session number + summary entry
**Example:** Session 29 summary with detailed notes

---

## VAULT OPERATIONS

### 🔄 Index Vault
**Command:** `python ehko_refresh.py`
**Does:** Incremental index update + process transcriptions
**When:** After adding/editing markdown files

### 🩺 Health Check
**Command:** `python ehko_refresh.py --health`
**Does:** Scan for broken refs, orphaned files, missing versions, stale drafts
**Output:** `_data/health_report.md`
**When:** Weekly or after major changes

### 📊 System Status
**Command:** Control panel "📊 Status" OR API `/api/authority`, `/api/mana/balance`, `/api/recog/status`
**Shows:** Authority %, Mana balance, ReCog queue, progression stats

---

## RECOG ENGINE

### ⚙ Check for Work
**Command:** Control panel "⚙ Check" OR API `/api/recog/check`
**Does:** Scan for unprocessed content, queue operations

### ✓ Confirm All
**Command:** Control panel "✓ Confirm All" OR API `/api/recog/confirm/{id}`
**Does:** Approve all pending ReCog operations for processing

### ▶ Process
**Command:** Control panel "▶ Process" OR API `/api/recog/process`
**Does:** Execute confirmed ReCog operations (LLM calls)
**Note:** May take 1-2 minutes

### 📊 Pending
**Command:** Control panel "📊 Pending" OR API `/api/recog/pending`
**Shows:** List of pending ReCog operations with mana estimates

---

## SERVER CONTROL

### Start Server
**Command:** Control panel "▶ Start Server" OR `python forge_server.py`
**Access:** http://localhost:5000

### Stop Server
**Command:** Control panel "■ Stop"

### Open UI
**Command:** Control panel "🌐 Open UI"
**Opens:** Main terminal interface

### Open Studio
**Command:** Control panel "◆ Studio"
**Opens:** Evolution Studio (Ehko visual explorer)

---

## COMMON PATTERNS

### Session Start
1. Load `_data/session_state.md` (session tracking)
2. Check `PROJECT_STATUS.md` if implementation work
3. Review any open questions/blockers
4. Proceed with work

### Session End
1. Update `_data/session_state.md` (active work, next priorities)
2. Update `PROJECT_STATUS.md` if needed
3. Use "📝 Session" commit with session number + summary

### Quick Fix Workflow
1. Make change
2. "⚡ Quick" commit with simple message
3. Continue working

### Health Maintenance
1. Run "🩺 Health" check
2. Review `_data/health_report.md`
3. Fix issues flagged
4. Re-run to verify

---

## FILE LOCATIONS

| File | Path | Purpose |
|------|------|---------|
| session_state.md | `_data/` | Session tracking |
| quick_commands.md | `_data/` | This file - command reference |
| PROJECT_STATUS.md | Root | Implementation status |
| vault_map.md | `_data/` | Vault structure |
| health_report.md | `_data/` | Health check results (generated) |
| ehko_index.db | `_data/` | SQLite database |

---

## TIPS

- **Quick vs Session commits:** Quick = "save now", Session = "document work"
- **Health checks:** Run weekly or after structural changes
- **ReCog processing:** Check → Confirm → Process (don't skip confirmation)
- **Server logs:** Watch server panel for errors during development

---

**Changelog:**
- v1.0 — 2025-12-08 — Initial quick commands reference created
