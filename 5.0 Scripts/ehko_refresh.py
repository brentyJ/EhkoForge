#!/usr/bin/env python3
"""
ehko_refresh.py — EhkoForge Indexing + Transcription Processing Script v2.1

Scans EhkoForge and Mirrorwell vaults:
1. Detects transcription-style files (with Short Summary, Long Summary, Transcriptions sections)
2. Converts transcriptions → Mirrorwell reflection entries
3. Archives originals to _processed/
4. Indexes all markdown files into SQLite
5. Performs vault health checks

Usage:
    python ehko_refresh.py                  # Incremental update + process transcriptions
    python ehko_refresh.py --full           # Full rebuild + process all transcriptions
    python ehko_refresh.py --report         # Show stats only
    python ehko_refresh.py --no-process     # Index only, skip transcription processing
    python ehko_refresh.py --health         # Run vault health checks, generate report

Dependencies:
    pip install pyyaml

Author: Brent Lefebure / EhkoForge
Created: 2025-11-26
Updated: 2025-12-08 — v2.1: Added vault health checks (broken refs, orphaned files, missing versions, stale drafts)
"""

import argparse
import hashlib
import json
import os
import re
import shutil
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML not installed. Run: pip install pyyaml")
    exit(1)


# =============================================================================
# CONFIGURATION
# =============================================================================

# Vault root — parent directory containing EhkoForge and Mirrorwell
VAULT_ROOT = Path(__file__).parent.parent.parent  # Goes up from 5.0 Scripts → EhkoForge → Obsidian root

# Vaults to scan
VAULTS = {
    "EhkoForge": VAULT_ROOT / "EhkoForge",
    "Mirrorwell": VAULT_ROOT / "Mirrorwell",
}

# Database location
DB_PATH = VAULT_ROOT / "EhkoForge" / "_data" / "ehko_index.db"

# Processed transcriptions archive (stays with transcripts)
PROCESSED_DIR = VAULT_ROOT / "Mirrorwell" / "2_Reflection Library" / "2.2 Transcripts" / "_processed"

# Journals output directory (where processed reflections go)
REFLECTIONS_DIR = VAULT_ROOT / "Mirrorwell" / "2_Reflection Library" / "2.1 Journals"

# Directories to skip
SKIP_DIRS = {".obsidian", "_inbox", "attachments", "archive", "_data", "_ledger", "Templates", "_processed"}

# File patterns to skip
SKIP_PATTERNS = {"index.md", "README.md", "Start Here.md"}


# =============================================================================
# TRANSCRIPTION DETECTION & PROCESSING
# =============================================================================

def is_transcription_file(content: str) -> bool:
    """
    Detect if a file is a transcription-style document.
    Must have all three:
    - ## Short Summary
    - ## Long Summary (or ## Transcriptions)
    - Timestamped entries like ### A - Nov 27, 2025 18:12:18
    """
    has_short_summary = re.search(r"^##\s+Short Summary", content, re.MULTILINE | re.IGNORECASE)
    has_long_summary = re.search(r"^##\s+(Long Summary|Transcriptions)", content, re.MULTILINE | re.IGNORECASE)
    has_timestamps = re.search(r"^###\s+[A-Z]\s+-\s+\w+\s+\d+,\s+\d{4}\s+\d{2}:\d{2}:\d{2}", content, re.MULTILINE)
    
    return bool(has_short_summary and has_long_summary and has_timestamps)


def extract_transcription_data(content: str) -> dict:
    """
    Extract structured data from a transcription file.
    Returns dict with:
    - title (from filename or first heading)
    - short_summary
    - long_summary
    - themes (bullet section headers)
    - transcriptions (list of timestamped raw text)
    - first_timestamp (for created date)
    """
    data = {
        "title": "",
        "short_summary": "",
        "long_summary": "",
        "themes": [],
        "transcriptions": [],
        "first_timestamp": None,
    }
    
    # Extract title (first # heading)
    title_match = re.search(r"^#\s+(.+?)$", content, re.MULTILINE)
    if title_match:
        data["title"] = title_match.group(1).strip()
    
    # Extract Short Summary
    short_summary_match = re.search(
        r"^##\s+Short Summary\s*\n(.+?)(?=\n##|\Z)",
        content,
        re.MULTILINE | re.DOTALL | re.IGNORECASE
    )
    if short_summary_match:
        data["short_summary"] = short_summary_match.group(1).strip()
    
    # Extract Long Summary
    long_summary_match = re.search(
        r"^##\s+Long Summary\s*\n(.+?)(?=\n##|\Z)",
        content,
        re.MULTILINE | re.DOTALL | re.IGNORECASE
    )
    if long_summary_match:
        data["long_summary"] = long_summary_match.group(1).strip()
    
    # Extract themed sections (## Heading with bullets)
    # Find content between Long Summary and Transcriptions
    long_summary_end = re.search(r"^##\s+Long Summary\s*\n.+?(?=\n##)", content, re.MULTILINE | re.DOTALL | re.IGNORECASE)
    transcriptions_start = re.search(r"^##\s+Transcriptions", content, re.MULTILINE | re.IGNORECASE)
    
    if long_summary_end and transcriptions_start:
        # Get the text between Long Summary section and Transcriptions section
        start_pos = long_summary_end.end()
        end_pos = transcriptions_start.start()
        themes_text = content[start_pos:end_pos]
        
        # Extract each themed section
        for theme_match in re.finditer(
            r"^#\s+(.+?)\n((?:^-.+?\n?)+)",
            themes_text,
            re.MULTILINE
        ):
            theme_title = theme_match.group(1).strip()
            theme_bullets = theme_match.group(2).strip()
            data["themes"].append({
                "title": theme_title,
                "content": theme_bullets
            })
    
    # Extract transcriptions (timestamped entries)
    transcription_section = re.search(
        r"^##\s+Transcriptions\s*\n(.+?)\Z",
        content,
        re.MULTILINE | re.DOTALL | re.IGNORECASE
    )
    if transcription_section:
        trans_text = transcription_section.group(1)
        # Extract each timestamped entry
        for trans_match in re.finditer(
            r"^###\s+([A-Z])\s+-\s+(\w+\s+\d+,\s+\d{4}\s+\d{2}:\d{2}:\d{2})\s*\n(.+?)(?=\n###|\Z)",
            trans_text,
            re.MULTILINE | re.DOTALL
        ):
            label = trans_match.group(1)
            timestamp_str = trans_match.group(2)
            text = trans_match.group(3).strip()
            
            data["transcriptions"].append({
                "label": label,
                "timestamp": timestamp_str,
                "text": text
            })
            
            # Capture first timestamp for created date
            if not data["first_timestamp"]:
                data["first_timestamp"] = timestamp_str
    
    return data


def parse_timestamp(timestamp_str: str) -> str:
    """
    Convert 'Nov 27, 2025 18:12:18' to 'YYYY-MM-DD' format.
    """
    try:
        dt = datetime.strptime(timestamp_str, "%b %d, %Y %H:%M:%S")
        return dt.strftime("%Y-%m-%d")
    except ValueError:
        return datetime.now().strftime("%Y-%m-%d")


def generate_mirrorwell_entry(data: dict, original_filename: str) -> str:
    """
    Generate a Mirrorwell reflection entry from transcription data.
    Uses Mirrorwell Reflection Template v1.2 structure.
    """
    title = data["title"] or original_filename.replace(".md", "").replace("_", " ").title()
    created_date = parse_timestamp(data["first_timestamp"]) if data["first_timestamp"] else datetime.now().strftime("%Y-%m-%d")
    updated_date = datetime.now().strftime("%Y-%m-%d")
    
    # Build raw input section from all transcriptions
    raw_input_lines = []
    for trans in data["transcriptions"]:
        raw_input_lines.append(f"### {trans['label']} - {trans['timestamp']}")
        raw_input_lines.append(trans["text"])
        raw_input_lines.append("")
    raw_input = "\n".join(raw_input_lines)
    
    # Build context from summaries
    context_parts = []
    if data["short_summary"]:
        context_parts.append(f"**Brief:** {data['short_summary']}")
    if data["long_summary"]:
        context_parts.append(f"\n**Detail:** {data['long_summary']}")
    if data["first_timestamp"]:
        context_parts.append(f"\n**Recorded:** {data['first_timestamp']}")
    context = "\n".join(context_parts)
    
    # Build reflection from themed sections
    reflection_parts = []
    for theme in data["themes"]:
        reflection_parts.append(f"### {theme['title']}")
        reflection_parts.append(theme["content"])
        reflection_parts.append("")
    reflection = "\n".join(reflection_parts) if reflection_parts else "*(Themes to be extracted)*"
    
    # Generate entry
    entry = f"""---
title: "{title}"
vault: Mirrorwell
type: reflection
category: journaling
status: active
version: 1.0
created: {created_date}
updated: {updated_date}
tags: [transcription, voice-note]
related: []
source: voice-dictation
confidence: 0.95
revealed: true
---

# {title}

## 0. Raw Input (Preserved)
{raw_input}

---

## 1. Context
{context}

---

## 2. Observations
*(To be extracted from raw input)*

---

## 3. Reflection / Interpretation
{reflection}

---

## 4. Actions / Updates
*(To be identified)*

---

## 5. Cross-References
*(To be added)*

---

**Changelog**
- v1.0 — {updated_date} — Entry created from voice transcription
"""
    
    return entry


def process_transcription_file(file_path: Path) -> Optional[Path]:
    """
    Process a transcription file:
    1. Extract data
    2. Generate Mirrorwell entry
    3. Write to reflections/
    4. Move original to _processed/
    
    Returns path to generated reflection file, or None if failed.
    """
    try:
        content = file_path.read_text(encoding="utf-8")
        
        if not is_transcription_file(content):
            return None
        
        print(f"  PROCESSING TRANSCRIPTION: {file_path.name}")
        
        # Extract data
        data = extract_transcription_data(content)
        
        if not data["transcriptions"]:
            print(f"    WARNING: No transcriptions found, skipping")
            return None
        
        # Generate reflection entry
        entry = generate_mirrorwell_entry(data, file_path.stem)
        
        # Determine output filename
        created_date = parse_timestamp(data["first_timestamp"]) if data["first_timestamp"] else datetime.now().strftime("%Y-%m-%d")
        safe_title = re.sub(r'[^\w\s-]', '', data["title"] or file_path.stem).strip().lower()
        safe_title = re.sub(r'[-\s]+', '_', safe_title)
        output_filename = f"{created_date}_{safe_title}.md"
        output_path = REFLECTIONS_DIR / output_filename
        
        # Ensure reflections directory exists
        REFLECTIONS_DIR.mkdir(parents=True, exist_ok=True)
        
        # Write reflection entry
        output_path.write_text(entry, encoding="utf-8")
        print(f"    CREATED: {output_path.name}")
        
        # Archive original
        PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
        archive_path = PROCESSED_DIR / file_path.name
        shutil.move(str(file_path), str(archive_path))
        print(f"    ARCHIVED: {archive_path.name}")
        
        return output_path
        
    except Exception as e:
        print(f"    ERROR processing transcription: {e}")
        return None


# =============================================================================
# DATABASE SCHEMA (unchanged from v1.1)
# =============================================================================

SCHEMA_SQL = """
-- Core reflection objects table
CREATE TABLE IF NOT EXISTS reflection_objects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_path TEXT UNIQUE NOT NULL,
    vault TEXT NOT NULL,
    type TEXT NOT NULL,
    title TEXT NOT NULL,
    category TEXT,
    status TEXT NOT NULL,
    version TEXT NOT NULL,
    created DATE NOT NULL,
    updated DATE NOT NULL,
    source TEXT,
    confidence REAL,
    revealed BOOLEAN DEFAULT 1,
    raw_input_hash TEXT,
    content_hash TEXT,
    indexed_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Tags table (folksonomy)
CREATE TABLE IF NOT EXISTS tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    object_id INTEGER NOT NULL,
    tag TEXT NOT NULL,
    FOREIGN KEY (object_id) REFERENCES reflection_objects(id) ON DELETE CASCADE
);

-- Cross-references (wiki-links)
CREATE TABLE IF NOT EXISTS cross_references (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    object_id INTEGER NOT NULL,
    target_path TEXT NOT NULL,
    FOREIGN KEY (object_id) REFERENCES reflection_objects(id) ON DELETE CASCADE
);

-- Changelog entries
CREATE TABLE IF NOT EXISTS changelog_entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    object_id INTEGER NOT NULL,
    version TEXT NOT NULL,
    change_date DATE NOT NULL,
    description TEXT,
    FOREIGN KEY (object_id) REFERENCES reflection_objects(id) ON DELETE CASCADE
);

-- Mirrorwell-specific extensions
CREATE TABLE IF NOT EXISTS mirrorwell_extensions (
    object_id INTEGER PRIMARY KEY,
    core_memory BOOLEAN DEFAULT 0,
    identity_pillar TEXT,
    FOREIGN KEY (object_id) REFERENCES reflection_objects(id) ON DELETE CASCADE
);

-- Emotional tags (Mirrorwell)
CREATE TABLE IF NOT EXISTS emotional_tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    object_id INTEGER NOT NULL,
    emotion TEXT NOT NULL,
    FOREIGN KEY (object_id) REFERENCES reflection_objects(id) ON DELETE CASCADE
);

-- Shared with friends (for authentication)
CREATE TABLE IF NOT EXISTS shared_with_friends (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    object_id INTEGER NOT NULL,
    friend_name TEXT NOT NULL,
    FOREIGN KEY (object_id) REFERENCES reflection_objects(id) ON DELETE CASCADE
);

-- Friend registry (authentication)
CREATE TABLE IF NOT EXISTS friend_registry (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    relationship_type TEXT,
    email TEXT UNIQUE NOT NULL,
    phone TEXT,
    access_level TEXT DEFAULT 'standard',
    blacklisted BOOLEAN DEFAULT 0,
    blacklist_reason TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_authenticated DATETIME,
    authentication_count INTEGER DEFAULT 0
);

-- Shared memories (for contextual authentication)
CREATE TABLE IF NOT EXISTS shared_memories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    friend_id INTEGER NOT NULL,
    memory_file_path TEXT NOT NULL,
    specificity_score REAL,
    challenge_eligible BOOLEAN DEFAULT 1,
    times_used INTEGER DEFAULT 0,
    last_used DATETIME,
    FOREIGN KEY (friend_id) REFERENCES friend_registry(id) ON DELETE CASCADE
);

-- Authentication tokens
CREATE TABLE IF NOT EXISTS authentication_tokens (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    token TEXT UNIQUE NOT NULL,
    friend_id INTEGER NOT NULL,
    claimed_identity TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    expires_at DATETIME NOT NULL,
    used BOOLEAN DEFAULT 0,
    used_at DATETIME,
    ip_address TEXT,
    user_agent TEXT,
    FOREIGN KEY (friend_id) REFERENCES friend_registry(id) ON DELETE CASCADE
);

-- Authentication logs
CREATE TABLE IF NOT EXISTS authentication_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    claimed_identity TEXT NOT NULL,
    friend_id INTEGER,
    authentication_method TEXT,
    success BOOLEAN NOT NULL,
    confidence_score REAL,
    challenge_memory_path TEXT,
    user_response TEXT,
    suspicious BOOLEAN DEFAULT 0,
    custodian_notified BOOLEAN DEFAULT 0,
    ip_address TEXT,
    user_agent TEXT,
    FOREIGN KEY (friend_id) REFERENCES friend_registry(id) ON DELETE SET NULL
);

-- Custodians
CREATE TABLE IF NOT EXISTS custodians (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    relationship TEXT,
    email TEXT UNIQUE NOT NULL,
    phone TEXT,
    priority INTEGER,
    active BOOLEAN DEFAULT 1,
    handoff_date DATE,
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Prepared messages
CREATE TABLE IF NOT EXISTS prepared_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_path TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    addressed_to TEXT NOT NULL,
    trigger_type TEXT NOT NULL,
    trigger_conditions TEXT,
    delivery_priority INTEGER DEFAULT 5,
    one_time_delivery BOOLEAN DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Message deliveries
CREATE TABLE IF NOT EXISTS message_deliveries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    message_id INTEGER NOT NULL,
    friend_id INTEGER NOT NULL,
    delivered_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    trigger_context TEXT,
    session_id TEXT,
    FOREIGN KEY (message_id) REFERENCES prepared_messages(id) ON DELETE CASCADE,
    FOREIGN KEY (friend_id) REFERENCES friend_registry(id) ON DELETE CASCADE
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_reflection_vault_type ON reflection_objects(vault, type, status);
CREATE INDEX IF NOT EXISTS idx_reflection_created ON reflection_objects(created);
CREATE INDEX IF NOT EXISTS idx_reflection_updated ON reflection_objects(updated);
CREATE INDEX IF NOT EXISTS idx_tags_lookup ON tags(tag);
CREATE INDEX IF NOT EXISTS idx_tags_object ON tags(object_id);
CREATE INDEX IF NOT EXISTS idx_crossref_object ON cross_references(object_id);
CREATE INDEX IF NOT EXISTS idx_friend_email ON friend_registry(email);
CREATE INDEX IF NOT EXISTS idx_friend_name ON friend_registry(name);
CREATE INDEX IF NOT EXISTS idx_shared_memory_friend ON shared_memories(friend_id);
CREATE INDEX IF NOT EXISTS idx_shared_memory_eligible ON shared_memories(challenge_eligible);
CREATE INDEX IF NOT EXISTS idx_token ON authentication_tokens(token);
CREATE INDEX IF NOT EXISTS idx_token_expiry ON authentication_tokens(expires_at);
CREATE INDEX IF NOT EXISTS idx_auth_log_timestamp ON authentication_logs(timestamp);
CREATE INDEX IF NOT EXISTS idx_auth_log_suspicious ON authentication_logs(suspicious);
CREATE INDEX IF NOT EXISTS idx_prepared_addressed ON prepared_messages(addressed_to);
CREATE INDEX IF NOT EXISTS idx_prepared_trigger ON prepared_messages(trigger_type);
CREATE INDEX IF NOT EXISTS idx_delivery_message ON message_deliveries(message_id);
CREATE INDEX IF NOT EXISTS idx_delivery_friend ON message_deliveries(friend_id);
"""


# =============================================================================
# UTILITY FUNCTIONS (unchanged from v1.1)
# =============================================================================

def compute_hash(content: str) -> str:
    """Compute SHA256 hash of content."""
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def extract_frontmatter(content: str) -> tuple[Optional[dict], str]:
    """
    Extract YAML frontmatter and body from markdown content.
    Returns (frontmatter_dict, body_text) or (None, full_content) if no frontmatter.
    """
    # Match YAML frontmatter between --- delimiters
    pattern = r"^---\s*\n(.*?)\n---\s*\n(.*)$"
    match = re.match(pattern, content, re.DOTALL)
    
    if match:
        try:
            frontmatter = yaml.safe_load(match.group(1))
            body = match.group(2)
            return frontmatter, body
        except yaml.YAMLError as e:
            print(f"  WARNING: YAML parse error: {e}")
            return None, content
    
    return None, content


def extract_raw_input(body: str) -> Optional[str]:
    """Extract the Raw Input section from markdown body."""
    # Look for ## 0. Raw Input section
    pattern = r"##\s*0\.\s*Raw Input.*?\n(.*?)(?=\n---|\n##|$)"
    match = re.search(pattern, body, re.DOTALL | re.IGNORECASE)
    
    if match:
        return match.group(1).strip()
    return None


def extract_wiki_links(body: str) -> list[str]:
    """Extract all wiki-links [[target]] from body."""
    pattern = r"\[\[([^\]|]+)(?:\|[^\]]+)?\]\]"
    return re.findall(pattern, body)


def extract_changelog(body: str) -> list[dict]:
    """Extract changelog entries from markdown body."""
    entries = []
    
    # Look for changelog section
    changelog_pattern = r"\*\*Changelog\*\*\s*\n(.*?)$"
    changelog_match = re.search(changelog_pattern, body, re.DOTALL | re.IGNORECASE)
    
    if changelog_match:
        changelog_text = changelog_match.group(1)
        # Parse individual entries: - vX.Y — YYYY-MM-DD — Description
        entry_pattern = r"-\s*v?([\d.]+)\s*[—–-]\s*(\d{4}-\d{2}-\d{2})\s*[—–-]\s*(.+?)(?=\n-|\n\n|$)"
        for match in re.finditer(entry_pattern, changelog_text):
            entries.append({
                "version": match.group(1),
                "date": match.group(2),
                "description": match.group(3).strip()
            })
    
    return entries


# =============================================================================
# DATABASE OPERATIONS (unchanged from v1.1)
# =============================================================================

class EhkoDatabase:
    """Database handler for ehko_index.db"""
    
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.conn = None
    
    def connect(self):
        """Open database connection."""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON")
    
    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
            self.conn = None
    
    def initialize_schema(self):
        """Create tables if they don't exist."""
        self.conn.executescript(SCHEMA_SQL)
        self.conn.commit()
    
    def get_existing_hashes(self) -> dict[str, str]:
        """Get file_path -> content_hash mapping for all indexed files."""
        cursor = self.conn.execute(
            "SELECT file_path, content_hash FROM reflection_objects"
        )
        return {row["file_path"]: row["content_hash"] for row in cursor}
    
    def delete_object(self, file_path: str):
        """Delete a reflection object and all related records."""
        cursor = self.conn.execute(
            "SELECT id FROM reflection_objects WHERE file_path = ?",
            (file_path,)
        )
        row = cursor.fetchone()
        if row:
            obj_id = row["id"]
            # Cascade deletes handle related tables
            self.conn.execute("DELETE FROM reflection_objects WHERE id = ?", (obj_id,))
    
    def upsert_reflection(self, data: dict) -> int:
        """Insert or update a reflection object. Returns object ID."""
        # Check if exists
        cursor = self.conn.execute(
            "SELECT id FROM reflection_objects WHERE file_path = ?",
            (data["file_path"],)
        )
        row = cursor.fetchone()
        
        if row:
            # Update existing
            obj_id = row["id"]
            self.conn.execute("""
                UPDATE reflection_objects SET
                    vault = ?, type = ?, title = ?, category = ?,
                    status = ?, version = ?, created = ?, updated = ?,
                    source = ?, confidence = ?, revealed = ?,
                    raw_input_hash = ?, content_hash = ?, indexed_at = ?
                WHERE id = ?
            """, (
                data["vault"], data["type"], data["title"], data.get("category"),
                data["status"], data["version"], data["created"], data["updated"],
                data.get("source"), data.get("confidence", 0.95), data.get("revealed", True),
                data.get("raw_input_hash"), data["content_hash"], datetime.now().isoformat(),
                obj_id
            ))
            
            # Clear related tables for re-population
            self.conn.execute("DELETE FROM tags WHERE object_id = ?", (obj_id,))
            self.conn.execute("DELETE FROM cross_references WHERE object_id = ?", (obj_id,))
            self.conn.execute("DELETE FROM changelog_entries WHERE object_id = ?", (obj_id,))
            self.conn.execute("DELETE FROM emotional_tags WHERE object_id = ?", (obj_id,))
            self.conn.execute("DELETE FROM shared_with_friends WHERE object_id = ?", (obj_id,))
        else:
            # Insert new
            cursor = self.conn.execute("""
                INSERT INTO reflection_objects (
                    file_path, vault, type, title, category,
                    status, version, created, updated,
                    source, confidence, revealed,
                    raw_input_hash, content_hash, indexed_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                data["file_path"], data["vault"], data["type"], data["title"], data.get("category"),
                data["status"], data["version"], data["created"], data["updated"],
                data.get("source"), data.get("confidence", 0.95), data.get("revealed", True),
                data.get("raw_input_hash"), data["content_hash"], datetime.now().isoformat()
            ))
            obj_id = cursor.lastrowid
        
        return obj_id
    
    def insert_tags(self, object_id: int, tags: list[str]):
        """Insert tags for an object."""
        for tag in tags:
            self.conn.execute(
                "INSERT INTO tags (object_id, tag) VALUES (?, ?)",
                (object_id, tag.lower().strip())
            )
    
    def insert_emotional_tags(self, object_id: int, emotions: list[str]):
        """Insert emotional tags for an object."""
        for emotion in emotions:
            self.conn.execute(
                "INSERT INTO emotional_tags (object_id, emotion) VALUES (?, ?)",
                (object_id, emotion.lower().strip())
            )
    
    def insert_cross_references(self, object_id: int, targets: list[str]):
        """Insert cross-references for an object."""
        for target in targets:
            self.conn.execute(
                "INSERT INTO cross_references (object_id, target_path) VALUES (?, ?)",
                (object_id, target)
            )
    
    def insert_changelog_entries(self, object_id: int, entries: list[dict]):
        """Insert changelog entries for an object."""
        for entry in entries:
            self.conn.execute(
                "INSERT INTO changelog_entries (object_id, version, change_date, description) VALUES (?, ?, ?, ?)",
                (object_id, entry["version"], entry["date"], entry["description"])
            )
    
    def insert_shared_with(self, object_id: int, friends: list[str]):
        """Insert shared_with_friends records."""
        for friend in friends:
            self.conn.execute(
                "INSERT INTO shared_with_friends (object_id, friend_name) VALUES (?, ?)",
                (object_id, friend.lower().strip())
            )
    
    def upsert_mirrorwell_extension(self, object_id: int, core_memory: bool, identity_pillar: Optional[str]):
        """Insert or update Mirrorwell extension data."""
        self.conn.execute("""
            INSERT INTO mirrorwell_extensions (object_id, core_memory, identity_pillar)
            VALUES (?, ?, ?)
            ON CONFLICT(object_id) DO UPDATE SET
                core_memory = excluded.core_memory,
                identity_pillar = excluded.identity_pillar
        """, (object_id, core_memory, identity_pillar))
    
    def upsert_prepared_message(self, data: dict):
        """Insert or update a prepared message."""
        self.conn.execute("""
            INSERT INTO prepared_messages (
                file_path, title, addressed_to, trigger_type,
                trigger_conditions, delivery_priority, one_time_delivery
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(file_path) DO UPDATE SET
                title = excluded.title,
                addressed_to = excluded.addressed_to,
                trigger_type = excluded.trigger_type,
                trigger_conditions = excluded.trigger_conditions,
                delivery_priority = excluded.delivery_priority,
                one_time_delivery = excluded.one_time_delivery
        """, (
            data["file_path"], data["title"],
            json.dumps(data["addressed_to"]),
            data["trigger_type"],
            json.dumps(data.get("trigger_conditions", {})),
            data.get("delivery_priority", 5),
            data.get("one_time_delivery", True)
        ))
    
    def update_shared_memories(self):
        """
        Populate shared_memories table from shared_with_friends.
        Links memories to friends in friend_registry.
        """
        # Get all friends
        friends = self.conn.execute("SELECT id, name FROM friend_registry").fetchall()
        
        for friend in friends:
            friend_id = friend["id"]
            friend_name = friend["name"].lower()
            
            # Find all memories shared with this friend
            cursor = self.conn.execute("""
                SELECT DISTINCT ro.file_path, ro.id
                FROM reflection_objects ro
                JOIN shared_with_friends swf ON ro.id = swf.object_id
                WHERE LOWER(swf.friend_name) = ?
            """, (friend_name,))
            
            for row in cursor:
                # Check if already in shared_memories
                existing = self.conn.execute(
                    "SELECT id FROM shared_memories WHERE friend_id = ? AND memory_file_path = ?",
                    (friend_id, row["file_path"])
                ).fetchone()
                
                if not existing:
                    # Calculate specificity score
                    # Would need to re-read file here, so we'll use a default for now
                    # In production, this should be calculated during indexing
                    self.conn.execute("""
                        INSERT INTO shared_memories (friend_id, memory_file_path, specificity_score, challenge_eligible)
                        VALUES (?, ?, 0.5, 1)
                    """, (friend_id, row["file_path"]))
    
    def clear_all_objects(self):
        """Delete all reflection objects (for full rebuild)."""
        self.conn.execute("DELETE FROM reflection_objects")
        self.conn.execute("DELETE FROM prepared_messages")
        self.conn.commit()
    
    def commit(self):
        """Commit current transaction."""
        self.conn.commit()
    
    def get_stats(self) -> dict:
        """Get index statistics."""
        stats = {}
        
        stats["total_objects"] = self.conn.execute(
            "SELECT COUNT(*) FROM reflection_objects"
        ).fetchone()[0]
        
        stats["by_vault"] = {}
        for row in self.conn.execute(
            "SELECT vault, COUNT(*) as count FROM reflection_objects GROUP BY vault"
        ):
            stats["by_vault"][row["vault"]] = row["count"]
        
        stats["by_type"] = {}
        for row in self.conn.execute(
            "SELECT type, COUNT(*) as count FROM reflection_objects GROUP BY type"
        ):
            stats["by_type"][row["type"]] = row["count"]
        
        stats["total_tags"] = self.conn.execute(
            "SELECT COUNT(DISTINCT tag) FROM tags"
        ).fetchone()[0]
        
        stats["total_cross_refs"] = self.conn.execute(
            "SELECT COUNT(*) FROM cross_references"
        ).fetchone()[0]
        
        stats["friends_registered"] = self.conn.execute(
            "SELECT COUNT(*) FROM friend_registry"
        ).fetchone()[0]
        
        stats["prepared_messages"] = self.conn.execute(
            "SELECT COUNT(*) FROM prepared_messages"
        ).fetchone()[0]
        
        return stats


# =============================================================================
# INDEXING ENGINE
# =============================================================================

class EhkoIndexer:
    """Main indexing engine with transcription processing."""
    
    def __init__(self, db: EhkoDatabase, incremental: bool = True, process_transcriptions: bool = True):
        self.db = db
        self.incremental = incremental
        self.process_transcriptions = process_transcriptions
        self.stats = {
            "scanned": 0,
            "indexed": 0,
            "skipped": 0,
            "errors": 0,
            "deleted": 0,
            "transcriptions_processed": 0,
        }
    
    def should_skip_path(self, path: Path) -> bool:
        """Check if path should be skipped."""
        # Skip hidden directories and files
        for part in path.parts:
            if part.startswith("."):
                return True
            if part in SKIP_DIRS:
                return True
        
        # Skip specific files
        if path.name in SKIP_PATTERNS:
            return True
        
        # Only process .md files
        if path.suffix.lower() != ".md":
            return True
        
        return False
    
    def scan_vault(self, vault_name: str, vault_path: Path) -> list[Path]:
        """Scan vault directory for markdown files."""
        files = []
        
        for path in vault_path.rglob("*.md"):
            if not self.should_skip_path(path):
                files.append(path)
        
        return files
    
    def index_file(self, file_path: Path, vault_name: str, existing_hashes: dict) -> bool:
        """
        Index a single markdown file.
        Returns True if indexed, False if skipped.
        """
        self.stats["scanned"] += 1
        relative_path = str(file_path)
        
        try:
            # Read file content
            content = file_path.read_text(encoding="utf-8")
            content_hash = compute_hash(content)
            
            # Check if unchanged (incremental mode)
            if self.incremental and relative_path in existing_hashes:
                if existing_hashes[relative_path] == content_hash:
                    self.stats["skipped"] += 1
                    return False
            
            # Parse frontmatter
            frontmatter, body = extract_frontmatter(content)
            
            if not frontmatter:
                print(f"  SKIP (no frontmatter): {file_path.name}")
                self.stats["skipped"] += 1
                return False
            
            # Validate required fields
            required = ["title", "vault", "type", "status", "version", "created", "updated"]
            missing = [f for f in required if f not in frontmatter]
            if missing:
                print(f"  SKIP (missing fields {missing}): {file_path.name}")
                self.stats["skipped"] += 1
                return False
            
            # Extract raw input and calculate hash
            raw_input = extract_raw_input(body)
            raw_input_hash = compute_hash(raw_input) if raw_input else None
            
            # Build data dict
            data = {
                "file_path": relative_path,
                "vault": frontmatter.get("vault", vault_name),
                "type": frontmatter["type"],
                "title": frontmatter["title"],
                "category": frontmatter.get("category"),
                "status": frontmatter["status"],
                "version": str(frontmatter["version"]),
                "created": str(frontmatter["created"]),
                "updated": str(frontmatter["updated"]),
                "source": frontmatter.get("source"),
                "confidence": frontmatter.get("confidence", 0.95),
                "revealed": frontmatter.get("revealed", True),
                "raw_input_hash": raw_input_hash,
                "content_hash": content_hash,
            }
            
            # Insert/update reflection object
            obj_id = self.db.upsert_reflection(data)
            
            # Process tags
            tags = frontmatter.get("tags", [])
            if tags:
                self.db.insert_tags(obj_id, tags)
            
            # Process emotional tags (Mirrorwell)
            emotional_tags = frontmatter.get("emotional_tags", [])
            if emotional_tags:
                self.db.insert_emotional_tags(obj_id, emotional_tags)
            
            # Process shared_with (Mirrorwell)
            shared_with = frontmatter.get("shared_with", [])
            if shared_with:
                self.db.insert_shared_with(obj_id, shared_with)
            
            # Process cross-references
            wiki_links = extract_wiki_links(body)
            related = frontmatter.get("related", [])
            # Parse wiki-links from related field too
            for item in related:
                links = extract_wiki_links(item)
                wiki_links.extend(links)
            
            if wiki_links:
                self.db.insert_cross_references(obj_id, list(set(wiki_links)))
            
            # Process changelog
            changelog = extract_changelog(body)
            if changelog:
                self.db.insert_changelog_entries(obj_id, changelog)
            
            # Mirrorwell extensions
            if vault_name == "Mirrorwell" or frontmatter.get("vault") == "Mirrorwell":
                core_memory = frontmatter.get("core_memory", False)
                identity_pillar = frontmatter.get("identity_pillar")
                self.db.upsert_mirrorwell_extension(obj_id, core_memory, identity_pillar)
            
            # Prepared messages
            if frontmatter.get("type") == "prepared_message":
                pm_data = {
                    "file_path": relative_path,
                    "title": frontmatter["title"],
                    "addressed_to": frontmatter.get("addressed_to", ["*"]),
                    "trigger_type": frontmatter.get("trigger_type", "manual"),
                    "trigger_conditions": frontmatter.get("trigger_conditions", {}),
                    "delivery_priority": frontmatter.get("delivery_priority", 5),
                    "one_time_delivery": frontmatter.get("one_time_delivery", True),
                }
                self.db.upsert_prepared_message(pm_data)
            
            self.stats["indexed"] += 1
            return True
            
        except Exception as e:
            print(f"  ERROR indexing {file_path.name}: {e}")
            self.stats["errors"] += 1
            return False
    
    def cleanup_deleted(self, existing_hashes: dict, current_files: set[str]):
        """Remove index entries for deleted files."""
        for file_path in existing_hashes:
            if file_path not in current_files:
                print(f"  REMOVING: {Path(file_path).name}")
                self.db.delete_object(file_path)
                self.stats["deleted"] += 1
    
    def run(self) -> dict:
        """Run the full indexing process."""
        print("=" * 60)
        print("EHKO REFRESH v2.0 — Indexing + Transcription Processing")
        print("=" * 60)
        print(f"Mode: {'Incremental' if self.incremental else 'Full Rebuild'}")
        print(f"Transcription Processing: {'Enabled' if self.process_transcriptions else 'Disabled'}")
        print(f"Database: {DB_PATH}")
        print()
        
        # Get existing hashes for incremental mode
        existing_hashes = self.db.get_existing_hashes() if self.incremental else {}
        
        all_current_files = set()
        
        # Process each vault
        for vault_name, vault_path in VAULTS.items():
            if not vault_path.exists():
                print(f"WARNING: Vault not found: {vault_path}")
                continue
            
            print(f"Scanning {vault_name}...")
            files = self.scan_vault(vault_name, vault_path)
            print(f"  Found {len(files)} files")
            
            # First pass: process transcriptions
            if self.process_transcriptions:
                print(f"  Processing transcriptions...")
                for file_path in files[:]:  # Copy list to allow modification
                    try:
                        content = file_path.read_text(encoding="utf-8")
                        if is_transcription_file(content):
                            result_path = process_transcription_file(file_path)
                            if result_path:
                                self.stats["transcriptions_processed"] += 1
                                # Remove from files list (it's been moved)
                                files.remove(file_path)
                                # Add generated reflection to files list
                                if result_path.exists():
                                    files.append(result_path)
                    except Exception as e:
                        print(f"    ERROR checking transcription: {e}")
            
            # Second pass: index all remaining files
            print(f"  Indexing files...")
            for file_path in files:
                all_current_files.add(str(file_path))
                result = self.index_file(file_path, vault_name, existing_hashes)
                if result:
                    print(f"  INDEXED: {file_path.name}")
            
            print()
        
        # Cleanup deleted files
        if self.incremental:
            self.cleanup_deleted(existing_hashes, all_current_files)
        
        # Update shared memories linkage
        print("Updating shared memories linkage...")
        self.db.update_shared_memories()
        
        # Commit all changes
        self.db.commit()
        
        return self.stats


# =============================================================================
# REPORTING
# =============================================================================

def print_report(db: EhkoDatabase, indexer_stats: Optional[dict] = None):
    """Print index statistics report."""
    stats = db.get_stats()
    
    print("=" * 60)
    print("EHKO INDEX REPORT")
    print("=" * 60)
    print()
    
    if indexer_stats:
        print("Indexing Results:")
        print(f"  Scanned:        {indexer_stats['scanned']}")
        print(f"  Indexed:        {indexer_stats['indexed']}")
        print(f"  Skipped:        {indexer_stats['skipped']}")
        print(f"  Deleted:        {indexer_stats['deleted']}")
        print(f"  Transcriptions: {indexer_stats['transcriptions_processed']}")
        print(f"  Errors:         {indexer_stats['errors']}")
        print()
    
    print("Index Contents:")
    print(f"  Total Objects:    {stats['total_objects']}")
    print(f"  Unique Tags:      {stats['total_tags']}")
    print(f"  Cross-References: {stats['total_cross_refs']}")
    print(f"  Friends:          {stats['friends_registered']}")
    print(f"  Prepared Msgs:    {stats['prepared_messages']}")
    print()
    
    print("By Vault:")
    for vault, count in stats["by_vault"].items():
        print(f"  {vault}: {count}")
    print()
    
    print("By Type:")
    for obj_type, count in stats["by_type"].items():
        print(f"  {obj_type}: {count}")
    print()
    
    print("=" * 60)


# =============================================================================
# VAULT HEALTH CHECKS
# =============================================================================

def check_health(db: EhkoDatabase) -> dict:
    """
    Perform vault health checks and return results.
    Checks for:
    - Broken cross-references (links to non-existent files)
    - Orphaned files (files on disk not in database)
    - Missing version numbers
    - Stale status flags (draft files older than 30 days)
    """
    issues = {
        "broken_references": [],
        "orphaned_files": [],
        "missing_versions": [],
        "stale_drafts": [],
    }
    
    conn = db.conn
    cursor = conn.cursor()
    
    # 1. Check for broken cross-references
    cursor.execute("""
        SELECT DISTINCT ro1.file_path, cr.target_file
        FROM reflection_objects ro1
        JOIN cross_references cr ON ro1.id = cr.source_id
        LEFT JOIN reflection_objects ro2 ON cr.target_file = ro2.file_path
        WHERE ro2.id IS NULL
    """)
    
    for source_path, target_file in cursor.fetchall():
        issues["broken_references"].append({
            "source": source_path,
            "target": target_file
        })
    
    # 2. Check for orphaned files (files on disk but not in DB)
    indexed_files = set()
    cursor.execute("SELECT file_path FROM reflection_objects")
    for (path,) in cursor.fetchall():
        indexed_files.add(path)
    
    for vault_name, vault_path in VAULTS.items():
        for md_file in vault_path.rglob("*.md"):
            # Skip excluded directories
            if any(skip_dir in md_file.parts for skip_dir in SKIP_DIRS):
                continue
            if md_file.name in SKIP_PATTERNS:
                continue
            
            relative_path = str(md_file.relative_to(vault_path))
            full_path = f"{vault_name}/{relative_path}"
            
            if full_path not in indexed_files:
                issues["orphaned_files"].append(full_path)
    
    # 3. Check for missing version numbers
    cursor.execute("""
        SELECT file_path, frontmatter
        FROM reflection_objects
        WHERE frontmatter IS NOT NULL
    """)
    
    for file_path, frontmatter_json in cursor.fetchall():
        try:
            frontmatter = json.loads(frontmatter_json) if frontmatter_json else {}
            if "version" not in frontmatter or not frontmatter["version"]:
                issues["missing_versions"].append(file_path)
        except:
            pass
    
    # 4. Check for stale drafts (status: draft, updated > 30 days ago)
    cursor.execute("""
        SELECT file_path, updated
        FROM reflection_objects
        WHERE frontmatter LIKE '%"status": "draft"%'
    """)
    
    from datetime import datetime, timedelta
    thirty_days_ago = datetime.now() - timedelta(days=30)
    
    for file_path, updated_str in cursor.fetchall():
        try:
            if updated_str:
                updated = datetime.fromisoformat(updated_str)
                if updated < thirty_days_ago:
                    issues["stale_drafts"].append({
                        "path": file_path,
                        "updated": updated_str
                    })
        except:
            pass
    
    return issues


def write_health_report(issues: dict, report_path: Path):
    """Write health check results to markdown file."""
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("---\n")
        f.write("title: \"Vault Health Report\"\n")
        f.write("vault: \"EhkoForge\"\n")
        f.write("type: \"system\"\n")
        f.write("category: \"_data\"\n")
        f.write(f"generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("tags: [system, health, diagnostics]\n")
        f.write("---\n\n")
        f.write("# VAULT HEALTH REPORT\n\n")
        
        # Summary
        total_issues = sum(len(v) for v in issues.values())
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"**Total Issues:** {total_issues}\n\n")
        f.write("---\n\n")
        
        # Broken references
        f.write("## Broken Cross-References\n\n")
        if issues["broken_references"]:
            f.write(f"Found {len(issues['broken_references'])} broken links:\n\n")
            for ref in issues["broken_references"]:
                f.write(f"- `{ref['source']}` → `{ref['target']}` (not found)\n")
        else:
            f.write("✓ No broken cross-references found.\n")
        f.write("\n---\n\n")
        
        # Orphaned files
        f.write("## Orphaned Files\n\n")
        if issues["orphaned_files"]:
            f.write(f"Found {len(issues['orphaned_files'])} files not in index:\n\n")
            for path in issues["orphaned_files"]:
                f.write(f"- `{path}`\n")
        else:
            f.write("✓ No orphaned files found.\n")
        f.write("\n---\n\n")
        
        # Missing versions
        f.write("## Missing Version Numbers\n\n")
        if issues["missing_versions"]:
            f.write(f"Found {len(issues['missing_versions'])} files without version field:\n\n")
            for path in issues["missing_versions"]:
                f.write(f"- `{path}`\n")
        else:
            f.write("✓ All files have version numbers.\n")
        f.write("\n---\n\n")
        
        # Stale drafts
        f.write("## Stale Drafts\n\n")
        if issues["stale_drafts"]:
            f.write(f"Found {len(issues['stale_drafts'])} draft files older than 30 days:\n\n")
            for draft in issues["stale_drafts"]:
                f.write(f"- `{draft['path']}` (last updated: {draft['updated']})\n")
        else:
            f.write("✓ No stale drafts found.\n")
        f.write("\n---\n\n")
        
        f.write("## Recommendations\n\n")
        if total_issues == 0:
            f.write("✓ Vault is healthy. No issues found.\n")
        else:
            f.write("Review and fix the issues above to maintain vault integrity.\n")


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="EhkoForge Indexing + Transcription Processing Script"
    )
    parser.add_argument(
        "--full", action="store_true",
        help="Full rebuild (ignore existing hashes)"
    )
    parser.add_argument(
        "--report", action="store_true",
        help="Show index statistics only (no indexing)"
    )
    parser.add_argument(
        "--no-process", action="store_true",
        help="Skip transcription processing (index only)"
    )
    parser.add_argument(
        "--health", action="store_true",
        help="Run vault health checks and generate report"
    )
    
    args = parser.parse_args()
    
    # Ensure database directory exists
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    # Initialize database
    db = EhkoDatabase(DB_PATH)
    db.connect()
    db.initialize_schema()
    
    try:
        if args.health:
            # Run health checks
            print("Running vault health checks...")
            issues = check_health(db)
            
            # Write report
            report_path = DB_PATH.parent / "health_report.md"
            write_health_report(issues, report_path)
            
            # Print summary
            total_issues = sum(len(v) for v in issues.values())
            print(f"\nHealth check complete. Found {total_issues} issue(s).")
            print(f"Report written to: {report_path}")
            print("\nSummary:")
            print(f"  Broken references:   {len(issues['broken_references'])}")
            print(f"  Orphaned files:      {len(issues['orphaned_files'])}")
            print(f"  Missing versions:    {len(issues['missing_versions'])}")
            print(f"  Stale drafts (30d+): {len(issues['stale_drafts'])}")
            
        elif args.report:
            # Report only
            print_report(db)
        else:
            # Run indexing
            if args.full:
                print("Clearing existing index for full rebuild...")
                db.clear_all_objects()
            indexer = EhkoIndexer(
                db,
                incremental=not args.full,
                process_transcriptions=not args.no_process
            )
            stats = indexer.run()
            print_report(db, stats)
    
    finally:
        db.close()
    
    print("Done.")


if __name__ == "__main__":
    main()
