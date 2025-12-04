#!/usr/bin/env python3
"""
EhkoForge Server v2.3
Flask application serving the Forge UI.
Phase 2 UI Consolidation: Single terminal interface with mode toggle.
Includes Authority/Mana systems, mana purchase (Stripe placeholder), and LLM integration.

Run: python forge_server.py
Access: http://localhost:5000

Routes:
    / -> Main terminal UI (consolidated)
    /forge -> Insite review page
    /reflect, /terminal -> Redirect to /
    /api/mana/* -> Mana management endpoints
"""

# Load environment variables FIRST, before any other imports
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("[OK] Loaded .env file")
except ImportError:
    pass  # python-dotenv not installed, rely on system env vars

import json
import random
import sqlite3
from datetime import datetime
from pathlib import Path
from uuid import uuid4

from flask import Flask, jsonify, request, send_from_directory, render_template, redirect
import logging

# LLM Integration
import sys
sys.path.insert(0, str(Path(__file__).parent))

from ehkoforge.llm import (
    EhkoContextBuilder,
    create_default_config,
    get_provider_for_conversation,
    ProviderFactory,
)

# ReCog Engine (AGPL-licensed)
from recog_engine.prompts import get_system_prompt, get_stage_for_authority
from recog_engine.tier0 import preprocess_text
from recog_engine.smelt import SmeltProcessor, queue_for_smelt, get_queue_stats, should_auto_smelt
from recog_engine.authority_mana import (
    get_current_authority,
    update_authority,
    get_mana_state,
    spend_mana,
    check_mana_available,
    get_dormant_response,
    refill_mana,
)
from recog_engine.mana_manager import (
    get_user_config,
    set_user_config,
    get_mana_balance,
    spend_mana_smart,
    get_pricing_tiers,
    record_purchase,
    get_purchase_history,
    get_usage_stats,
    check_spending_limits,
    set_api_keys,
    get_api_keys,
)

# =============================================================================
# CONFIGURATION
# =============================================================================

# Paths - adjust if your vault location differs
EHKOFORGE_ROOT = Path("G:/Other computers/Ehko/Obsidian/EhkoForge")
MIRRORWELL_ROOT = Path("G:/Other computers/Ehko/Obsidian/Mirrorwell")
DATABASE_PATH = EHKOFORGE_ROOT / "_data" / "ehko_index.db"
CONFIG_PATH = EHKOFORGE_ROOT / "Config" / "ui-preferences.json"
STATIC_PATH = EHKOFORGE_ROOT / "6.0 Frontend" / "static"
JOURNALS_PATH = MIRRORWELL_ROOT / "2_Reflection Library" / "2.1 Journals"

# Flask app
TEMPLATES_PATH = EHKOFORGE_ROOT / "6.0 Frontend" / "templates"
app = Flask(__name__, 
            static_folder=str(STATIC_PATH),
            template_folder=str(TEMPLATES_PATH))
app.logger.setLevel(logging.DEBUG)
logging.basicConfig(level=logging.DEBUG)

# =============================================================================
# LLM CONFIGURATION
# =============================================================================

LLM_CONFIG = create_default_config(EHKOFORGE_ROOT / "Config")
CONTEXT_BUILDER = EhkoContextBuilder(DATABASE_PATH, MIRRORWELL_ROOT)

_llm_provider = None


def get_llm_provider():
    """Get or create the LLM provider instance for conversation."""
    global _llm_provider
    
    if _llm_provider is None:
        try:
            _llm_provider = get_provider_for_conversation(LLM_CONFIG)
            if _llm_provider:
                print(f"[OK] Conversation provider initialised: {_llm_provider.PROVIDER_NAME}:{_llm_provider.model}")
            else:
                print("[WARN] No conversation provider configured. Using templated responses.")
        except Exception as e:
            print(f"[WARN] Could not initialise conversation provider: {e}")
    
    return _llm_provider


# =============================================================================
# DATABASE HELPERS
# =============================================================================

def get_db():
    """Get database connection with row factory."""
    conn = sqlite3.connect(str(DATABASE_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_session_tables():
    """Create session tables if they don't exist."""
    conn = get_db()
    cursor = conn.cursor()
    
    # Forge sessions table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS forge_sessions (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            session_tags TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            message_count INTEGER DEFAULT 0,
            is_archived INTEGER DEFAULT 0
        )
    """)
    
    # Session messages table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS forge_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            forged INTEGER DEFAULT 0,
            forged_path TEXT,
            FOREIGN KEY (session_id) REFERENCES forge_sessions(id)
        )
    """)
    
    # Index for fast message retrieval
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_messages_session 
        ON forge_messages(session_id, timestamp)
    """)
    
    conn.commit()
    conn.close()


def index_forged_reflection(filepath: Path, title: str, tags: list, 
                            emotional_tags: list, session_id: str):
    """
    Add a newly forged reflection to the SQLite index.
    
    This allows it to appear in context searches immediately.
    """
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        now = datetime.now().strftime("%Y-%m-%d")
        
        # Insert into reflection_objects
        cursor.execute("""
            INSERT OR REPLACE INTO reflection_objects 
            (file_path, vault, type, title, category, status, version, created, updated, 
             source, confidence, revealed)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            str(filepath),
            "Mirrorwell",
            "reflection",
            title,
            "Journals",
            "active",
            "1.0",
            now,
            now,
            "forge_session",
            0.8,
            1
        ))
        
        # Get the auto-generated object_id
        object_id = cursor.lastrowid
        
        # Insert tags using object_id
        for tag in tags:
            if tag and tag.strip():
                cursor.execute("""
                    INSERT OR IGNORE INTO tags (object_id, tag)
                    VALUES (?, ?)
                """, (object_id, tag.lower().strip()))
        
        # Insert emotional tags using object_id (column is 'emotion' not 'tag')
        for etag in emotional_tags:
            if etag and etag.strip():
                cursor.execute("""
                    INSERT OR IGNORE INTO emotional_tags (object_id, emotion)
                    VALUES (?, ?)
                """, (object_id, etag.lower().strip()))
        
        conn.commit()
        print(f"[FORGE] Indexed reflection: {title} (id={object_id})", flush=True)
        
    except sqlite3.Error as e:
        print(f"[FORGE] Failed to index reflection: {e}", flush=True)
    finally:
        conn.close()


# =============================================================================
# CONFIG HELPERS
# =============================================================================

DEFAULT_CONFIG = {
    "theme": "forge-dark",
    "avatar_visible": True,
    "low_motion_mode": False,
    "high_contrast_mode": False,
    "reduced_chroma_mode": False,
    "dyslexic_font": False,
    "last_session_id": None
}


def load_config():
    """Load UI preferences from config file."""
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return DEFAULT_CONFIG.copy()


def save_config(config):
    """Save UI preferences to config file."""
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)


# =============================================================================
# EHKO RESPONSE GENERATION
# =============================================================================

def generate_ehko_response(user_message: str, session_context: list = None, 
                           interaction_mode: str = "terminal") -> str:
    """
    Generate an Ehko response to user input.
    
    Uses Claude API if configured, falls back to templates.
    
    Args:
        user_message: The user's message
        session_context: Recent messages for context
        interaction_mode: 'terminal' or 'reflection'
    """
    print(f"[EHKO] generate_ehko_response called with: {user_message[:50]}...", flush=True)
    
    provider = get_llm_provider()
    print(f"[EHKO] Provider: {provider}", flush=True)
    
    # Fallback if no API key configured
    if provider is None:
        print("[EHKO] No provider, using templates", flush=True)
        return _generate_templated_response(user_message)
    
    try:
        # Get current Authority state for stage-based personality
        authority = get_current_authority(DATABASE_PATH)
        advancement_stage = authority.get('advancement_stage', 'nascent')
        print(f"[EHKO] Authority stage: {advancement_stage} ({authority.get('authority_total', 0):.1%})", flush=True)
        
        # Search reflections for relevant context
        print("[EHKO] Building context...", flush=True)
        reflection_context = CONTEXT_BUILDER.build_context(
            query=user_message,
            max_reflections=3 if interaction_mode == 'terminal' else 5,
            max_tokens_estimate=1500 if interaction_mode == 'terminal' else 2500,
        )
        print(f"[EHKO] Context length: {len(reflection_context)} chars", flush=True)
        
        # Get Ehko behaviour rules with stage-based personality dampener
        system_prompt = get_system_prompt(
            mode="forging",
            interaction_mode=interaction_mode,
            advancement_stage=advancement_stage,
            reflection_context=reflection_context,
        )
        
        # Call Claude
        print("[EHKO] Calling Claude API...", flush=True)
        response = provider.generate(
            prompt=user_message,
            system_prompt=system_prompt,
            max_tokens=512,
            temperature=0.7,
        )
        
        print(f"[EHKO] Response success: {response.success}", flush=True)
        if response.success:
            print(f"[EHKO] Response content: {response.content[:100]}...", flush=True)
            return response.content
        else:
            print(f"[EHKO] LLM error: {response.error}", flush=True)
            return _generate_templated_response(user_message)
            
    except Exception as e:
        print(f"[EHKO] LLM generation failed: {e}", flush=True)
        import traceback
        traceback.print_exc()
        return _generate_templated_response(user_message)


def _generate_templated_response(user_message: str) -> str:
    """
    Fallback templated responses when LLM unavailable.
    """
    message_lower = user_message.lower()
    
    if any(word in message_lower for word in ["thank", "thanks"]):
        responses = [
            "You're welcome. I'm here whenever you need to reflect.",
            "Of course. Take your time with whatever comes next.",
        ]
    elif any(word in message_lower for word in ["feel", "feeling", "felt"]):
        responses = [
            "Those feelings are worth sitting with. Would you like to explore them further?",
            "I hear you. What do you think is at the root of that feeling?",
            "Thank you for sharing that. Feelings often point to something deeper.",
        ]
    elif any(word in message_lower for word in ["remember", "memory", "memories"]):
        responses = [
            "Memories shape who we are. What made this one surface now?",
            "That memory sounds significant. Would you like to forge it into the vault?",
            "I've noted that. Memories like these often connect to core patterns.",
        ]
    elif any(word in message_lower for word in ["help", "stuck", "confused"]):
        responses = [
            "Let's slow down. What's the smallest piece you can name right now?",
            "Sometimes clarity comes from just getting words out. Keep going.",
            "I'm here. There's no rush to have it all figured out.",
        ]
    elif "?" in user_message:
        responses = [
            "That's a question worth holding. What does your gut tell you?",
            "I wonder what asking that question reveals about where you are right now.",
            "Good question. Let's sit with it rather than rush to an answer.",
        ]
    else:
        responses = [
            "I've noted that. What else is on your mind?",
            "Thank you for sharing. I'm here when you're ready to continue.",
            "That's worth sitting with. Would you like to explore it further?",
            "I hear you. Take whatever time you need.",
            "Noted. These threads often connect to something larger.",
        ]
    
    return random.choice(responses)


# =============================================================================
# STATS CALCULATION
# =============================================================================

def calculate_stats():
    """
    Calculate symbolic stats from reflection corpus.
    
    Returns dict with values 0.0-1.0 for each stat.
    """
    conn = get_db()
    cursor = conn.cursor()
    
    stats = {
        "identity_depth": 0.0,
        "clarity": 0.0,
        "resonance": 0.0,
        "anchors": 0.0
    }
    
    try:
        # Total reflections
        cursor.execute("SELECT COUNT(*) FROM reflection_objects")
        total = cursor.fetchone()[0]
        
        if total == 0:
            return stats
        
        # Identity depth: reflections tagged with identity-related tags
        cursor.execute("""
            SELECT COUNT(DISTINCT ro.id) FROM reflection_objects ro
            JOIN tags t ON ro.id = t.object_id
            WHERE t.tag IN ('identity', 'self', 'values', 'beliefs', 'pillar')
        """)
        identity_count = cursor.fetchone()[0]
        stats["identity_depth"] = min(1.0, identity_count / max(total, 1))
        
        # Clarity: reflections with high confidence scores
        cursor.execute("""
            SELECT AVG(CAST(confidence AS REAL)) FROM reflection_objects 
            WHERE confidence IS NOT NULL AND confidence != ''
        """)
        avg_confidence = cursor.fetchone()[0]
        stats["clarity"] = avg_confidence if avg_confidence else 0.5
        
        # Resonance: average based on emotional tag diversity
        cursor.execute("SELECT COUNT(DISTINCT emotion) FROM emotional_tags")
        emotional_diversity = cursor.fetchone()[0]
        stats["resonance"] = min(1.0, emotional_diversity / 20.0)  # Assume 20 is rich
        
        # Anchors: core memories ratio
        cursor.execute("""
            SELECT COUNT(*) FROM mirrorwell_extensions 
            WHERE core_memory = 1
        """)
        core_count = cursor.fetchone()[0]
        stats["anchors"] = min(1.0, core_count / max(total * 0.1, 1))  # 10% is high
        
    except sqlite3.Error:
        # Tables might not exist yet, return defaults
        pass
    finally:
        conn.close()
    
    return stats


# =============================================================================
# FORGE TO VAULT
# =============================================================================

def forge_to_vault(session_id: str, message_ids: list, title: str, 
                   tags: list = None, emotional_tags: list = None) -> dict:
    """
    Forge selected messages into a Mirrorwell reflection file.
    
    Returns dict with success status and file path.
    """
    print(f"[FORGE] Starting forge for session {session_id}, {len(message_ids)} messages", flush=True)
    
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        # Get messages
        placeholders = ",".join("?" * len(message_ids))
        cursor.execute(f"""
            SELECT id, role, content, timestamp FROM forge_messages
            WHERE id IN ({placeholders})
            ORDER BY timestamp ASC
        """, message_ids)
        messages = cursor.fetchall()
        
        if not messages:
            return {"success": False, "error": "No messages found"}
        
        # Build reflection content
        now = datetime.now()
        date_str = now.strftime("%Y-%m-%d")
        slug = title.lower().replace(" ", "-").replace("'", "")[:50]
        filename = f"{date_str}_{slug}.md"
        filepath = JOURNALS_PATH / filename
        
        # Combine message content for Raw Input
        raw_content = []
        for msg in messages:
            prefix = "**Me:**" if msg["role"] == "user" else "**Ehko:**"
            raw_content.append(f"{prefix} {msg['content']}")
        
        raw_input = "\n\n".join(raw_content)
        
        # Build YAML frontmatter
        tags_list = tags or ["reflection", "forged"]
        emotional_list = emotional_tags or []
        
        frontmatter = f"""---
title: "{title}"
vault: "Mirrorwell"
type: "reflection"
category: "Journals"
status: active
version: "1.0"
created: {date_str}
updated: {date_str}
tags: {json.dumps(tags_list)}
related: []
source: "forge_session"
confidence: 0.8
revealed: true
emotional_tags: {json.dumps(emotional_list)}
shared_with: []
core_memory: false
identity_pillar: null
forge_session_id: "{session_id}"
---"""

        # Build full document
        document = f"""{frontmatter}

# {title}

## 0. Raw Input (Preserved)

{raw_input}

---

## 1. Context

Forged from Forge UI session on {now.strftime("%Y-%m-%d at %H:%M")}.

---

## 2. Observations

*To be populated during review.*

---

## 3. Reflection / Interpretation

*To be populated during review.*

---

## 4. Actions / Updates

- [ ] Review and expand reflection sections
- [ ] Add cross-references to related entries
- [ ] Consider for Core Memory Index

---

## 5. Cross-References

*To be populated.*

---

**Changelog**
- v1.0 — {date_str} — Forged from session {session_id}
"""
        
        # Write file
        JOURNALS_PATH.mkdir(parents=True, exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(document)
        
        print(f"[FORGE] File written: {filepath}", flush=True)
        
        # Add to index immediately so it appears in searches
        index_forged_reflection(
            filepath=filepath,
            title=title,
            tags=tags_list,
            emotional_tags=emotional_list,
            session_id=session_id
        )
        
        # Mark messages as forged
        cursor.execute(f"""
            UPDATE forge_messages 
            SET forged = 1, forged_path = ?
            WHERE id IN ({placeholders})
        """, [str(filepath)] + message_ids)
        
        conn.commit()
        
        # Queue session for smelting (extracts ingots from the conversation)
        try:
            queue_for_smelt(
                db_path=DATABASE_PATH,
                source_type="chat_session",
                source_id=session_id,
                priority=5,
            )
            print(f"[FORGE] Queued session {session_id} for smelting", flush=True)
        except Exception as e:
            print(f"[FORGE] Failed to queue for smelt: {e}", flush=True)
        
        return {
            "success": True,
            "reflection_path": str(filepath.relative_to(MIRRORWELL_ROOT.parent)),
            "forged_count": len(messages),
            "queued_for_smelt": True
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}
    finally:
        conn.close()


# =============================================================================
# API ROUTES - SESSIONS
# =============================================================================

@app.route("/api/sessions", methods=["GET"])
def get_sessions():
    """List all sessions, newest first."""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, title, session_tags, created_at, updated_at, message_count
        FROM forge_sessions
        WHERE is_archived = 0
        ORDER BY updated_at DESC
    """)
    
    sessions = []
    for row in cursor.fetchall():
        sessions.append({
            "id": row["id"],
            "title": row["title"],
            "session_tags": json.loads(row["session_tags"]) if row["session_tags"] else [],
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
            "message_count": row["message_count"]
        })
    
    conn.close()
    return jsonify({"sessions": sessions})


@app.route("/api/sessions", methods=["POST"])
def create_session():
    """Create a new session."""
    data = request.get_json() or {}
    title = data.get("title", "New Session")
    
    session_id = f"session-{datetime.now().strftime('%Y-%m-%d')}-{uuid4().hex[:6]}"
    now = datetime.now().isoformat()
    
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO forge_sessions (id, title, session_tags, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?)
    """, (session_id, title, "[]", now, now))
    
    conn.commit()
    conn.close()
    
    return jsonify({
        "id": session_id,
        "title": title,
        "session_tags": [],
        "created_at": now,
        "updated_at": now,
        "message_count": 0
    }), 201


@app.route("/api/sessions/<session_id>", methods=["GET"])
def get_session(session_id):
    """Get single session details."""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, title, session_tags, created_at, updated_at, message_count
        FROM forge_sessions WHERE id = ?
    """, (session_id,))
    
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return jsonify({"error": "Session not found"}), 404
    
    return jsonify({
        "id": row["id"],
        "title": row["title"],
        "session_tags": json.loads(row["session_tags"]) if row["session_tags"] else [],
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
        "message_count": row["message_count"]
    })


@app.route("/api/sessions/<session_id>", methods=["DELETE"])
def archive_session(session_id):
    """Archive a session (soft delete)."""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        UPDATE forge_sessions SET is_archived = 1 WHERE id = ?
    """, (session_id,))
    
    conn.commit()
    conn.close()
    
    return jsonify({"success": True})


# =============================================================================
# API ROUTES - MESSAGES
# =============================================================================

@app.route("/api/sessions/<session_id>/messages", methods=["GET"])
def get_messages(session_id):
    """Get all messages in a session."""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, role, content, timestamp, forged, forged_path
        FROM forge_messages
        WHERE session_id = ?
        ORDER BY timestamp ASC
    """, (session_id,))
    
    messages = []
    for row in cursor.fetchall():
        messages.append({
            "id": row["id"],
            "role": row["role"],
            "content": row["content"],
            "timestamp": row["timestamp"],
            "forged": bool(row["forged"]),
            "forged_path": row["forged_path"]
        })
    
    conn.close()
    return jsonify({"session_id": session_id, "messages": messages})


@app.route("/api/sessions/<session_id>/messages", methods=["POST"])
def send_message(session_id):
    """
    Add a message to session.
    If role is 'user', also generates and adds Ehko response.
    Checks and spends mana based on interaction mode.
    """
    try:
        print(f"[ROUTE] POST /api/sessions/{session_id}/messages", flush=True)
        
        data = request.get_json() or {}
        content = data.get("content", "").strip()
        role = data.get("role", "user")
        interaction_mode = data.get("mode", "terminal")  # terminal or reflection
        
        print(f"[ROUTE] Message content: {content[:50]}... role: {role} mode: {interaction_mode}", flush=True)
        
        if not content:
            return jsonify({"error": "Empty message"}), 400
        
        # Check mana for user messages
        if role == "user":
            mana_op = "reflection_message" if interaction_mode == "reflection" else "terminal_message"
            can_afford, current_mana, cost = check_mana_available(DATABASE_PATH, mana_op)
            
            if not can_afford:
                return jsonify({
                    "error": "Not enough mana",
                    "dormant": True,
                    "current_mana": current_mana,
                    "required": cost,
                    "message": get_dormant_response(),
                }), 429
            
            # Spend mana
            success, msg = spend_mana(DATABASE_PATH, mana_op)
            print(f"[ROUTE] Mana: {msg}", flush=True)
        
        conn = get_db()
        cursor = conn.cursor()
        
        now = datetime.now().isoformat()
        
        # Insert user message
        cursor.execute("""
            INSERT INTO forge_messages (session_id, role, content, timestamp)
            VALUES (?, ?, ?, ?)
        """, (session_id, role, content, now))
        
        user_msg_id = cursor.lastrowid
        
        messages_added = [{
            "id": user_msg_id,
            "role": role,
            "content": content,
            "timestamp": now,
            "forged": False
        }]
        
        # If user message, generate Ehko response
        if role == "user":
            print("[ROUTE] Generating Ehko response...", flush=True)
            
            # Get session context (last few messages)
            cursor.execute("""
                SELECT content FROM forge_messages 
                WHERE session_id = ? 
                ORDER BY timestamp DESC LIMIT 5
            """, (session_id,))
            context = [row["content"] for row in cursor.fetchall()]
            
            ehko_response = generate_ehko_response(content, context, interaction_mode)
            print(f"[ROUTE] Ehko response: {ehko_response[:50]}...", flush=True)
            
            ehko_time = datetime.now().isoformat()
            
            cursor.execute("""
                INSERT INTO forge_messages (session_id, role, content, timestamp)
                VALUES (?, ?, ?, ?)
            """, (session_id, "ehko", ehko_response, ehko_time))
            
            ehko_msg_id = cursor.lastrowid
            
            messages_added.append({
                "id": ehko_msg_id,
                "role": "ehko",
                "content": ehko_response,
                "timestamp": ehko_time,
                "forged": False
            })
        
        # Update session message count and timestamp
        cursor.execute("""
            UPDATE forge_sessions 
            SET message_count = message_count + ?, updated_at = ?
            WHERE id = ?
        """, (len(messages_added), now, session_id))
        
        conn.commit()
        conn.close()
        
        print(f"[ROUTE] Returning {len(messages_added)} messages", flush=True)
        return jsonify({"messages": messages_added}), 201
        
    except Exception as e:
        print(f"[ROUTE] ERROR: {e}", flush=True)
        import traceback
        traceback.print_exc()
        return jsonify({"error": "Internal server error"}), 500


# =============================================================================
# API ROUTES - FORGE
# =============================================================================

@app.route("/api/forge", methods=["POST"])
def forge():
    """Forge selected messages into Mirrorwell vault."""
    data = request.get_json() or {}
    
    session_id = data.get("session_id")
    message_ids = data.get("message_ids", [])
    title = data.get("title", "Forged Reflection")
    tags = data.get("tags", [])
    emotional_tags = data.get("emotional_tags", [])
    
    if not session_id or not message_ids:
        return jsonify({"error": "Missing session_id or message_ids"}), 400
    
    result = forge_to_vault(session_id, message_ids, title, tags, emotional_tags)
    
    if result["success"]:
        return jsonify(result)
    else:
        return jsonify(result), 500


# =============================================================================
# API ROUTES - STATS
# =============================================================================

@app.route("/api/stats", methods=["GET"])
def get_stats():
    """Get symbolic stats for display."""
    stats = calculate_stats()
    return jsonify(stats)


# =============================================================================
# API ROUTES - CONFIG
# =============================================================================

@app.route("/api/config", methods=["GET"])
def get_config():
    """Get UI preferences."""
    config = load_config()
    return jsonify(config)


@app.route("/api/config", methods=["POST"])
def update_config():
    """Update UI preferences."""
    data = request.get_json() or {}
    config = load_config()
    config.update(data)
    save_config(config)
    return jsonify(config)


# =============================================================================
# API ROUTES - REFLECTIONS (READ-ONLY)
# =============================================================================

@app.route("/api/reflections", methods=["GET"])
def get_reflections():
    """Query indexed reflections."""
    tag = request.args.get("tag")
    core_memory = request.args.get("core_memory")
    search = request.args.get("search")
    limit = request.args.get("limit", 50, type=int)
    
    conn = get_db()
    cursor = conn.cursor()
    
    query = "SELECT DISTINCT ro.* FROM reflection_objects ro"
    joins = []
    conditions = []
    params = []
    
    if tag:
        joins.append("JOIN tags t ON ro.id = t.object_id")
        conditions.append("t.tag = ?")
        params.append(tag)
    
    if core_memory == "true":
        joins.append("JOIN mirrorwell_extensions me ON ro.id = me.object_id")
        conditions.append("me.core_memory = 1")
    
    if search:
        conditions.append("(ro.title LIKE ? OR ro.id IN (SELECT object_id FROM tags WHERE tag LIKE ?))")
        params.extend([f"%{search}%", f"%{search}%"])
    
    if joins:
        query += " " + " ".join(joins)
    
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    
    query += " ORDER BY ro.updated DESC LIMIT ?"
    params.append(limit)
    
    cursor.execute(query, params)
    
    reflections = []
    for row in cursor.fetchall():
        reflections.append({
            "id": row["id"],
            "title": row["title"],
            "vault": row["vault"],
            "type": row["type"],
            "created": row["created"],
            "updated": row["updated"]
        })
    
    conn.close()
    return jsonify({"reflections": reflections})


# =============================================================================
# API ROUTES - SMELT QUEUE
# =============================================================================

@app.route("/api/smelt/status", methods=["GET"])
def smelt_status():
    """Get smelt queue status."""
    stats = get_queue_stats(DATABASE_PATH)
    should_run = should_auto_smelt(DATABASE_PATH)
    
    return jsonify({
        "queue": stats,
        "should_auto_smelt": should_run,
    })


@app.route("/api/smelt/resurface", methods=["POST"])
def resurface_ingots():
    """Re-check surfacing criteria for existing insites. Costs mana."""
    # Check mana cost
    can_afford, current_mana, cost = check_mana_available(DATABASE_PATH, "recog_sweep")
    if not can_afford:
        return jsonify({
            "error": "Not enough mana for ReCog sweep",
            "dormant": True,
            "current_mana": current_mana,
            "required": cost,
            "message": get_dormant_response(),
        }), 429
    
    # Spend mana
    spend_mana(DATABASE_PATH, "recog_sweep")
    
    conn = get_db()
    cursor = conn.cursor()
    
    now = datetime.utcnow().isoformat() + "Z"
    
    # Apply same surfacing criteria as in smelt.py
    cursor.execute("""
        UPDATE ingots SET status = 'surfaced', updated_at = ?
        WHERE status IN ('raw', 'refined')
        AND (
            significance >= 0.4
            OR (significance >= 0.3 AND analysis_pass >= 2)
            OR source_count >= 3
        )
    """, (now,))
    
    surfaced_count = cursor.rowcount
    
    conn.commit()
    conn.close()
    
    return jsonify({"surfaced": surfaced_count, "success": True})


@app.route("/api/smelt/run", methods=["POST"])
def run_smelt():
    """Manually trigger smelt processing. Costs mana."""
    # Check mana cost
    can_afford, current_mana, cost = check_mana_available(DATABASE_PATH, "recog_sweep")
    if not can_afford:
        return jsonify({
            "error": "Not enough mana for ReCog sweep",
            "dormant": True,
            "current_mana": current_mana,
            "required": cost,
            "message": get_dormant_response(),
        }), 429
    
    # Spend mana
    spend_mana(DATABASE_PATH, "recog_sweep")
    
    data = request.get_json() or {}
    limit = data.get("limit", 10)
    
    try:
        processor = SmeltProcessor(
            db_path=DATABASE_PATH,
            config_path=EHKOFORGE_ROOT / "Config",
            mirrorwell_path=MIRRORWELL_ROOT,
        )
        
        results = processor.run(limit=limit)
        return jsonify(results)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/smelt/queue", methods=["POST"])
def add_to_smelt_queue():
    """Manually add content to smelt queue."""
    data = request.get_json() or {}
    
    source_type = data.get("source_type")
    source_id = data.get("source_id")
    priority = data.get("priority", 0)
    
    if not source_type or not source_id:
        return jsonify({"error": "Missing source_type or source_id"}), 400
    
    entry_id = queue_for_smelt(DATABASE_PATH, source_type, source_id, priority)
    
    return jsonify({"entry_id": entry_id, "success": True}), 201


@app.route("/api/smelt/queue-all", methods=["POST"])
def queue_all_sessions_for_smelt():
    """Queue all sessions that have forged messages but aren't in smelt queue."""
    conn = get_db()
    cursor = conn.cursor()
    
    # Find sessions with forged messages not yet in queue
    cursor.execute("""
        SELECT DISTINCT fm.session_id 
        FROM forge_messages fm
        WHERE fm.forged = 1
        AND fm.session_id NOT IN (
            SELECT source_id FROM smelt_queue WHERE source_type = 'chat_session'
        )
    """)
    
    sessions = [row[0] for row in cursor.fetchall()]
    conn.close()
    
    queued = []
    for session_id in sessions:
        try:
            entry_id = queue_for_smelt(
                db_path=DATABASE_PATH,
                source_type="chat_session",
                source_id=session_id,
                priority=5,
            )
            queued.append({"session_id": session_id, "entry_id": entry_id})
        except Exception as e:
            print(f"[SMELT] Failed to queue {session_id}: {e}")
    
    return jsonify({"queued": queued, "count": len(queued)})


@app.route("/api/sessions/<session_id>/smelt", methods=["POST"])
def queue_session_for_smelt(session_id):
    """Queue a chat session for smelting."""
    data = request.get_json() or {}
    priority = data.get("priority", 10)  # High priority for manual trigger
    
    # Get word count from session
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT SUM(LENGTH(content) - LENGTH(REPLACE(content, ' ', '')) + 1) as word_count
        FROM forge_messages WHERE session_id = ?
    """, (session_id,))
    row = cursor.fetchone()
    word_count = row["word_count"] if row and row["word_count"] else 0
    conn.close()
    
    entry_id = queue_for_smelt(
        db_path=DATABASE_PATH,
        source_type="chat_session",
        source_id=session_id,
        priority=priority,
        word_count=word_count,
    )
    
    return jsonify({"entry_id": entry_id, "success": True, "word_count": word_count}), 201


# =============================================================================
# API ROUTES - INGOTS
# =============================================================================

def get_significance_tier(significance: float) -> str:
    """Map significance score to tier name."""
    if significance >= 0.9:
        return "mythic"
    elif significance >= 0.75:
        return "gold"
    elif significance >= 0.5:
        return "silver"
    elif significance >= 0.25:
        return "iron"
    else:
        return "copper"


def get_source_title(cursor, source_type: str, source_id: str) -> str:
    """Get human-readable title for a source."""
    if source_type == "chat_session":
        cursor.execute("SELECT title FROM forge_sessions WHERE id = ?", (source_id,))
        row = cursor.fetchone()
        return row["title"] if row else source_id
    elif source_type == "transcript_segment":
        cursor.execute("SELECT transcript_path FROM transcript_segments WHERE id = ?", (source_id,))
        row = cursor.fetchone()
        return Path(row["transcript_path"]).stem if row else source_id
    elif source_type == "reflection":
        cursor.execute("SELECT title FROM reflection_objects WHERE file_path = ?", (source_id,))
        row = cursor.fetchone()
        return row["title"] if row else source_id
    return source_id


@app.route("/api/ingots/debug", methods=["GET"])
def debug_ingots():
    """Debug endpoint - show ALL ingots regardless of status."""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, status, significance, confidence, summary, analysis_pass, source_count
        FROM ingots
        ORDER BY created_at DESC
    """)
    
    ingots = []
    for row in cursor.fetchall():
        ingots.append({
            "id": row["id"],
            "status": row["status"],
            "significance": row["significance"],
            "confidence": row["confidence"],
            "summary": row["summary"][:100] if row["summary"] else None,
            "analysis_pass": row["analysis_pass"],
            "source_count": row["source_count"],
        })
    
    conn.close()
    return jsonify({"ingots": ingots, "total": len(ingots)})


@app.route("/api/ingots", methods=["GET"])
def get_ingots():
    """
    Get ingots for Forge UI.
    
    Query params:
    - status: filter by status (default: 'surfaced')
    - min_significance: minimum significance threshold
    - theme: filter by theme tag
    - limit: max results (default: 20)
    """
    status = request.args.get("status", "surfaced")
    min_sig = request.args.get("min_significance", 0.0, type=float)
    theme = request.args.get("theme")
    limit = request.args.get("limit", 20, type=int)
    
    conn = get_db()
    cursor = conn.cursor()
    
    query = """
        SELECT id, summary, themes_json, emotional_tags_json, patterns_json,
               significance, confidence, source_count, created_at, updated_at
        FROM ingots
        WHERE status = ?
        AND significance >= ?
    """
    params = [status, min_sig]
    
    if theme:
        query += " AND themes_json LIKE ?"
        params.append(f'%"{theme}"%')
    
    query += " ORDER BY significance DESC LIMIT ?"
    params.append(limit)
    
    cursor.execute(query, params)
    
    ingots = []
    for row in cursor.fetchall():
        ingots.append({
            "id": row["id"],
            "summary": row["summary"],
            "themes": json.loads(row["themes_json"]) if row["themes_json"] else [],
            "emotional_tags": json.loads(row["emotional_tags_json"]) if row["emotional_tags_json"] else [],
            "patterns": json.loads(row["patterns_json"]) if row["patterns_json"] else [],
            "significance": row["significance"],
            "significance_tier": get_significance_tier(row["significance"]),
            "confidence": row["confidence"],
            "source_count": row["source_count"],
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
        })
    
    conn.close()
    return jsonify({"ingots": ingots, "count": len(ingots)})


@app.route("/api/ingots/<ingot_id>", methods=["GET"])
def get_ingot_detail(ingot_id):
    """Get full ingot details including sources."""
    conn = get_db()
    cursor = conn.cursor()
    
    # Get ingot
    cursor.execute("SELECT * FROM ingots WHERE id = ?", (ingot_id,))
    row = cursor.fetchone()
    
    if not row:
        conn.close()
        return jsonify({"error": "Ingot not found"}), 404
    
    ingot = {
        "id": row["id"],
        "summary": row["summary"],
        "themes": json.loads(row["themes_json"]) if row["themes_json"] else [],
        "emotional_tags": json.loads(row["emotional_tags_json"]) if row["emotional_tags_json"] else [],
        "patterns": json.loads(row["patterns_json"]) if row["patterns_json"] else [],
        "significance": row["significance"],
        "significance_tier": get_significance_tier(row["significance"]),
        "confidence": row["confidence"],
        "source_count": row["source_count"],
        "status": row["status"],
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }
    
    # Get sources
    cursor.execute("""
        SELECT source_type, source_id, excerpt, added_at
        FROM ingot_sources
        WHERE ingot_id = ?
        ORDER BY added_at ASC
    """, (ingot_id,))
    
    sources = []
    for src in cursor.fetchall():
        source_title = get_source_title(cursor, src["source_type"], src["source_id"])
        sources.append({
            "type": src["source_type"],
            "id": src["source_id"],
            "title": source_title,
            "excerpt": src["excerpt"],
            "added_at": src["added_at"],
        })
    
    ingot["sources"] = sources
    
    conn.close()
    return jsonify(ingot)


@app.route("/api/ingots/<ingot_id>/forge", methods=["POST"])
def forge_ingot(ingot_id):
    """Accept and forge an ingot into the Ehko."""
    conn = get_db()
    cursor = conn.cursor()
    
    now = datetime.utcnow().isoformat() + "Z"
    
    # Get ingot data
    cursor.execute("SELECT * FROM ingots WHERE id = ?", (ingot_id,))
    ingot = cursor.fetchone()
    
    if not ingot:
        conn.close()
        return jsonify({"error": "Ingot not found"}), 404
    
    if ingot["status"] == "forged":
        conn.close()
        return jsonify({"error": "Ingot already forged"}), 400
    
    # Update ingot status
    cursor.execute("""
        UPDATE ingots SET status = 'forged', forged_at = ?, updated_at = ?
        WHERE id = ?
    """, (now, now, ingot_id))
    
    # Determine layer type
    patterns = json.loads(ingot["patterns_json"]) if ingot["patterns_json"] else []
    themes = json.loads(ingot["themes_json"]) if ingot["themes_json"] else []
    
    layer_type = "trait"  # default
    if any(p in ["behaviour", "tendency", "habit", "reaction"] for p in patterns):
        layer_type = "pattern"
    elif any(t in ["values", "beliefs", "principles"] for t in themes):
        layer_type = "value"
    elif any(t in ["memory", "childhood", "event", "experience"] for t in themes):
        layer_type = "memory"
    elif any(t in ["voice", "speech", "communication", "tone"] for t in themes):
        layer_type = "voice"
    
    # Build layer content
    layer_content = ingot["summary"]
    if patterns:
        layer_content += f" (Patterns: {', '.join(patterns)})"
    
    # Create personality layer
    cursor.execute("""
        INSERT INTO ehko_personality_layers (ingot_id, layer_type, content, weight, integrated_at)
        VALUES (?, ?, ?, ?, ?)
    """, (ingot_id, layer_type, layer_content, ingot["significance"], now))
    
    # Log history
    cursor.execute("""
        INSERT INTO ingot_history (ingot_id, event_type, event_at, trigger)
        VALUES (?, 'forged', ?, 'user_action')
    """, (ingot_id, now))
    
    conn.commit()
    conn.close()
    
    return jsonify({
        "success": True,
        "ingot_id": ingot_id,
        "layer_type": layer_type,
        "message": "Ingot forged into Ehko"
    })


@app.route("/api/ingots/<ingot_id>/reject", methods=["POST"])
def reject_ingot(ingot_id):
    """Reject an ingot."""
    conn = get_db()
    cursor = conn.cursor()
    
    now = datetime.utcnow().isoformat() + "Z"
    
    cursor.execute("""
        UPDATE ingots SET status = 'rejected', updated_at = ?
        WHERE id = ?
    """, (now, ingot_id))
    
    cursor.execute("""
        INSERT INTO ingot_history (ingot_id, event_type, event_at, trigger)
        VALUES (?, 'rejected', ?, 'user_action')
    """, (ingot_id, now))
    
    conn.commit()
    conn.close()
    
    return jsonify({"success": True, "ingot_id": ingot_id})


# =============================================================================
# API ROUTES - AUTHORITY & MANA
# =============================================================================

@app.route("/api/authority", methods=["GET"])
def get_authority():
    """Get current Authority state (Ehko advancement metric)."""
    authority = get_current_authority(DATABASE_PATH)
    return jsonify(authority)


@app.route("/api/authority/refresh", methods=["POST"])
def refresh_authority():
    """Recalculate Authority from current database state."""
    authority = update_authority(DATABASE_PATH)
    return jsonify(authority)


@app.route("/api/mana", methods=["GET"])
def get_mana():
    """Get current Mana state (resource economy)."""
    mana = get_mana_state(DATABASE_PATH)
    return jsonify(mana)


@app.route("/api/mana/refill", methods=["POST"])
def refill_mana_endpoint():
    """Refill mana (for BYOK users or mana-core purchase)."""
    data = request.get_json() or {}
    amount = data.get("amount")  # None = fill to max
    
    refill_mana(DATABASE_PATH, amount)
    mana = get_mana_state(DATABASE_PATH)
    
    return jsonify({
        "success": True,
        "mana": mana,
    })


@app.route("/api/mana/cost/<operation>", methods=["GET"])
def get_operation_cost(operation):
    """Get mana cost for a specific operation."""
    from recog_engine.authority_mana import get_mana_cost
    cost = get_mana_cost(DATABASE_PATH, operation)
    return jsonify({"operation": operation, "cost": cost})


# =============================================================================
# API ROUTES - EHKO STATUS
# =============================================================================

@app.route("/api/ehko/status", methods=["GET"])
def get_ehko_status():
    """Get Ehko's current status including Authority and Mana."""
    conn = get_db()
    cursor = conn.cursor()
    
    # Forged insite count (check both old and new table names)
    forged_count = 0
    try:
        cursor.execute("SELECT COUNT(*) FROM insites WHERE status = 'forged'")
        forged_count = cursor.fetchone()[0]
    except sqlite3.OperationalError:
        try:
            cursor.execute("SELECT COUNT(*) FROM ingots WHERE status = 'forged'")
            forged_count = cursor.fetchone()[0]
        except sqlite3.OperationalError:
            pass
    
    # Layer count
    try:
        cursor.execute("SELECT COUNT(*) FROM ehko_personality_layers WHERE active = 1")
        layer_count = cursor.fetchone()[0]
    except sqlite3.OperationalError:
        layer_count = 0
    
    conn.close()
    
    # Get Authority state
    authority = get_current_authority(DATABASE_PATH)
    
    # Get Mana state
    mana = get_mana_state(DATABASE_PATH)
    
    return jsonify({
        "forged_count": forged_count,
        "layer_count": layer_count,
        "authority": authority,
        "mana": mana,
    })


@app.route("/api/ehko/layers", methods=["GET"])
def get_ehko_layers():
    """Get all active personality layers."""
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT epl.id, epl.ingot_id, epl.layer_type, epl.content, epl.weight, epl.integrated_at,
                   i.summary as ingot_summary
            FROM ehko_personality_layers epl
            JOIN ingots i ON epl.ingot_id = i.id
            WHERE epl.active = 1
            ORDER BY epl.weight DESC, epl.integrated_at DESC
        """)
        
        layers = []
        for row in cursor.fetchall():
            layers.append({
                "id": row["id"],
                "ingot_id": row["ingot_id"],
                "ingot_summary": row["ingot_summary"],
                "layer_type": row["layer_type"],
                "content": row["content"],
                "weight": row["weight"],
                "integrated_at": row["integrated_at"],
            })
    except sqlite3.OperationalError:
        layers = []
    
    conn.close()
    return jsonify({"layers": layers, "count": len(layers)})


# =============================================================================
# LLM STATUS ENDPOINTS
# =============================================================================

@app.route("/api/llm/status", methods=["GET"])
def llm_status():
    """Check LLM provider status."""
    provider = get_llm_provider()
    
    if provider is None:
        return jsonify({
            "status": "offline",
            "provider": None,
            "message": "No LLM provider configured. Using templated responses.",
        })
    
    # Get available and configured providers
    available = ProviderFactory.list_available()
    configured = ProviderFactory.list_configured(LLM_CONFIG)
    
    return jsonify({
        "status": "online",
        "provider": provider.PROVIDER_NAME,
        "model": provider.model,
        "message": "LLM provider active.",
        "role_config": {
            "conversation": f"{LLM_CONFIG.conversation_provider}:{LLM_CONFIG.conversation_model}",
            "processing": f"{LLM_CONFIG.processing_provider}:{LLM_CONFIG.processing_model}",
            "ehko": f"{LLM_CONFIG.ehko_provider}:{LLM_CONFIG.ehko_model}",
        },
        "available_providers": available,
        "configured_providers": configured,
    })


# =============================================================================
# API ROUTES - JOURNAL
# =============================================================================

@app.route("/api/journal/entries", methods=["GET"])
def list_journal_entries():
    """List journal entries with optional date filters."""
    start_date = request.args.get("start")
    end_date = request.args.get("end")
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Check if table exists
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='journal_entries'
    """)
    if not cursor.fetchone():
        conn.close()
        return jsonify({"entries": []})
    
    query = "SELECT * FROM journal_entries WHERE 1=1"
    params = []
    
    if start_date:
        query += " AND entry_date >= ?"
        params.append(start_date)
    
    if end_date:
        query += " AND entry_date <= ?"
        params.append(end_date)
    
    query += " ORDER BY entry_date DESC"
    
    cursor.execute(query, params)
    
    entries = []
    for row in cursor.fetchall():
        entries.append({
            "id": row["id"],
            "title": row["title"],
            "content": row["content"],
            "entry_date": row["entry_date"],
            "original_date": row["original_date"],
            "tags": json.loads(row["tags"]) if row["tags"] else [],
            "emotional_tags": json.loads(row["emotional_tags"]) if row["emotional_tags"] else [],
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
        })
    
    conn.close()
    return jsonify({"entries": entries})


@app.route("/api/journal/entries", methods=["POST"])
def create_journal_entry():
    """Create a new journal entry."""
    data = request.get_json() or {}
    
    title = data.get("title", "Untitled")
    content = data.get("content", "")
    entry_date = data.get("entry_date", datetime.now().strftime("%Y-%m-%d"))
    original_date = data.get("original_date")
    tags = json.dumps(data.get("tags", []))
    emotional_tags = json.dumps(data.get("emotional_tags", []))
    
    now = datetime.now().isoformat()
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Create table if not exists
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS journal_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            content TEXT NOT NULL,
            entry_date DATE NOT NULL,
            original_date DATE,
            tags TEXT,
            emotional_tags TEXT,
            reflection_object_id TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("""
        INSERT INTO journal_entries (title, content, entry_date, original_date, tags, emotional_tags, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (title, content, entry_date, original_date, tags, emotional_tags, now, now))
    
    entry_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return jsonify({
        "id": entry_id,
        "title": title,
        "content": content,
        "entry_date": entry_date,
        "original_date": original_date,
        "tags": data.get("tags", []),
        "emotional_tags": data.get("emotional_tags", []),
        "created_at": now,
        "updated_at": now,
    }), 201


@app.route("/api/journal/entries/<int:entry_id>", methods=["GET"])
def get_journal_entry(entry_id):
    """Get a single journal entry."""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM journal_entries WHERE id = ?", (entry_id,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return jsonify({"error": "Entry not found"}), 404
    
    return jsonify({
        "id": row["id"],
        "title": row["title"],
        "content": row["content"],
        "entry_date": row["entry_date"],
        "original_date": row["original_date"],
        "tags": json.loads(row["tags"]) if row["tags"] else [],
        "emotional_tags": json.loads(row["emotional_tags"]) if row["emotional_tags"] else [],
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    })


@app.route("/api/journal/entries/<int:entry_id>", methods=["PUT"])
def update_journal_entry(entry_id):
    """Update a journal entry."""
    data = request.get_json() or {}
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Check exists
    cursor.execute("SELECT id FROM journal_entries WHERE id = ?", (entry_id,))
    if not cursor.fetchone():
        conn.close()
        return jsonify({"error": "Entry not found"}), 404
    
    now = datetime.now().isoformat()
    
    cursor.execute("""
        UPDATE journal_entries 
        SET title = ?, content = ?, entry_date = ?, original_date = ?, 
            tags = ?, emotional_tags = ?, updated_at = ?
        WHERE id = ?
    """, (
        data.get("title", "Untitled"),
        data.get("content", ""),
        data.get("entry_date"),
        data.get("original_date"),
        json.dumps(data.get("tags", [])),
        json.dumps(data.get("emotional_tags", [])),
        now,
        entry_id,
    ))
    
    conn.commit()
    
    # Fetch updated
    cursor.execute("SELECT * FROM journal_entries WHERE id = ?", (entry_id,))
    row = cursor.fetchone()
    conn.close()
    
    return jsonify({
        "id": row["id"],
        "title": row["title"],
        "content": row["content"],
        "entry_date": row["entry_date"],
        "original_date": row["original_date"],
        "tags": json.loads(row["tags"]) if row["tags"] else [],
        "emotional_tags": json.loads(row["emotional_tags"]) if row["emotional_tags"] else [],
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    })


# =============================================================================
# MANA MANAGEMENT API
# =============================================================================

@app.route("/api/mana/balance", methods=["GET"])
def api_mana_balance():
    """Get user's complete mana balance (regenerative + purchased)."""
    try:
        balance = get_mana_balance(DATABASE_PATH)
        limits = check_spending_limits(DATABASE_PATH)
        
        return jsonify({
            "success": True,
            "balance": balance,
            "limits": limits,
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/mana/config", methods=["GET", "POST"])
def api_mana_config():
    """Get or update mana configuration."""
    if request.method == "GET":
        try:
            config = get_user_config(DATABASE_PATH)
            return jsonify({"success": True, "config": config})
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500
    
    elif request.method == "POST":
        try:
            data = request.json
            success = set_user_config(DATABASE_PATH, **data)
            
            if success:
                config = get_user_config(DATABASE_PATH)
                return jsonify({"success": True, "config": config})
            else:
                return jsonify({"success": False, "error": "Update failed"}), 400
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/mana/pricing", methods=["GET"])
def api_mana_pricing():
    """Get available mana-core pricing tiers."""
    try:
        tiers = get_pricing_tiers(DATABASE_PATH)
        return jsonify({"success": True, "tiers": tiers})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/mana/purchase", methods=["POST"])
def api_mana_purchase():
    """
    Process mana-core purchase (Stripe integration).
    
    This is a placeholder - actual Stripe integration requires:
    1. Stripe SDK (pip install stripe)
    2. Publishable/Secret keys
    3. Webhook handling for payment confirmation
    
    For MVP, this endpoint simulates a purchase.
    """
    try:
        data = request.json
        tier_id = data.get('tier_id')
        
        if not tier_id:
            return jsonify({"success": False, "error": "Missing tier_id"}), 400
        
        # Simulate Stripe payment (replace with actual Stripe call)
        payment_intent_id = f"sim_pi_{uuid4().hex[:16]}"
        charge_id = f"sim_ch_{uuid4().hex[:16]}"
        
        purchase_id = record_purchase(
            DATABASE_PATH, 
            user_id=1, 
            tier_id=tier_id,
            stripe_payment_intent_id=payment_intent_id,
            stripe_charge_id=charge_id
        )
        
        if purchase_id:
            balance = get_mana_balance(DATABASE_PATH)
            return jsonify({
                "success": True,
                "purchase_id": purchase_id,
                "balance": balance,
            })
        else:
            return jsonify({"success": False, "error": "Purchase failed"}), 500
            
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/mana/history", methods=["GET"])
def api_mana_history():
    """Get purchase and usage history."""
    try:
        limit = request.args.get('limit', 10, type=int)
        days = request.args.get('days', 30, type=int)
        
        purchases = get_purchase_history(DATABASE_PATH, limit=limit)
        usage = get_usage_stats(DATABASE_PATH, days=days)
        
        return jsonify({
            "success": True,
            "purchases": purchases,
            "usage": usage,
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/mana/api-keys", methods=["GET", "POST"])
def api_mana_keys():
    """Manage BYOK API keys."""
    if request.method == "GET":
        try:
            keys = get_api_keys(DATABASE_PATH)
            # Mask keys for display (show last 4 chars only)
            masked = {}
            for provider, key in keys.items():
                if key:
                    masked[provider] = f"...{key[-4:]}"
                else:
                    masked[provider] = None
            
            return jsonify({"success": True, "keys": masked})
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500
    
    elif request.method == "POST":
        try:
            data = request.json
            claude_key = data.get('claude_key')
            openai_key = data.get('openai_key')
            
            success = set_api_keys(DATABASE_PATH, 
                                   claude_key=claude_key, 
                                   openai_key=openai_key)
            
            if success:
                return jsonify({"success": True, "message": "API keys updated"})
            else:
                return jsonify({"success": False, "error": "Update failed"}), 400
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500


# =============================================================================
# PAGE ROUTES
# =============================================================================

@app.route("/")
def index():
    """Serve main terminal UI (Phase 2 consolidated interface)."""
    return render_template("index.html")


@app.route("/reflect")
@app.route("/reflect/<submode>")
def reflect(submode="chat"):
    """Redirect to main UI (legacy route)."""
    return redirect("/")


@app.route("/forge")
def forge_page():
    """Serve Forge area (Insite review)."""
    return render_template("forge.html", area="forge", submode=None)


@app.route("/terminal")
def terminal():
    """Redirect to main UI (legacy route)."""
    return redirect("/")


# =============================================================================
# STATIC FILE SERVING
# =============================================================================

@app.route("/css/<path:filename>")
def serve_css(filename):
    """Serve CSS files."""
    return send_from_directory(str(STATIC_PATH / "css"), filename)


@app.route("/js/<path:filename>")
def serve_js(filename):
    """Serve JS files."""
    return send_from_directory(str(STATIC_PATH / "js"), filename)


@app.route("/<path:filename>")
def static_files(filename):
    """Serve other static files."""
    return send_from_directory(str(STATIC_PATH), filename)


# =============================================================================
# STARTUP
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("EHKOFORGE SERVER v2.3")
    print("Authority & Mana Purchase Systems Active")
    print("=" * 60)
    print(f"Database: {DATABASE_PATH}")
    print(f"Static files: {STATIC_PATH}")
    print(f"Mirrorwell: {MIRRORWELL_ROOT}")
    print("-" * 60)
    
    # Initialise session tables
    init_session_tables()
    print("[OK] Session tables initialised")
    
    # Ensure config exists
    if not CONFIG_PATH.exists():
        save_config(DEFAULT_CONFIG)
        print("[OK] Default config created")
    
    # Test LLM connection
    provider = get_llm_provider()
    if provider:
        print(f"[OK] LLM provider: {provider.PROVIDER_NAME} ({provider.model})")
    else:
        print("[WARN] No LLM provider - using templated responses")
    
    print("-" * 60)
    print("Starting server at http://localhost:5000")
    print("Press Ctrl+C to stop")
    print("=" * 60)
    
    app.run(host="127.0.0.1", port=5000, debug=True, use_reloader=False)
