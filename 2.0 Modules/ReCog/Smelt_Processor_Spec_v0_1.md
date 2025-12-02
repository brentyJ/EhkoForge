---
title: "Smelt Processor Specification"
vault: "EhkoForge"
type: "module"
category: "Data Processing"
status: draft
version: "0.1"
created: 2025-12-01
updated: 2025-12-01
tags: [ehkoforge, smelt, processing, ingots, llm]
related:
  - "Ingot_System_Schema_v0_1.md"
  - "Tier0_PreAnnotation_Spec_v0_1.md"
  - "1_4_Data_Model_v1_3.md"
---

# SMELT PROCESSOR SPECIFICATION v0.1

## 1. Overview

The Smelt Processor is a batch job that processes queued content through Tier 2 LLM analysis and extracts ingots. It transforms raw reflections into distilled insights ready for user review and eventual integration into an Ehko's personality.

### 1.1 Design Goals

1. **Batch-oriented** — processes queue entries, not real-time
2. **Multi-pass capable** — same content can be re-analysed as corpus grows
3. **Cost-aware** — uses Tier 2 (Sonnet) for extraction, reserves Tier 3 (Opus) for correlation
4. **Idempotent** — safe to re-run; updates existing ingots rather than duplicating
5. **Traceable** — full lineage from source → ingot → history

### 1.2 LLM Tier Usage

| Tier | Model | Purpose |
|------|-------|---------|
| Tier 2 | Claude Sonnet | Ingot extraction, pattern tagging |
| Tier 3 | Claude Opus | Cross-correlation (future), deep analysis |

---

## 2. Trigger Conditions

The smelt processor runs when ANY of:

| Trigger | Description |
|---------|-------------|
| **Manual** | User clicks "Smelt Now" in UI |
| **Threshold** | Queue has ≥5 pending entries OR ≥2000 words accumulated |
| **Scheduled** | Daily batch (configurable, default: 2am local) |
| **Session close** | User ends a chat session (optional, configurable) |

---

## 3. Processing Pipeline

```
┌─────────────────────────────────────────────────────────────┐
│                     SMELT PROCESSOR                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. QUEUE FETCH                                             │
│     └─→ Get pending entries, ordered by priority DESC       │
│                                                             │
│  2. PRE-CHECK                                               │
│     └─→ Verify pre-annotation exists (run Tier 0 if not)    │
│                                                             │
│  3. CONTENT ASSEMBLY                                        │
│     └─→ Load raw text + pre-annotation + user annotations   │
│                                                             │
│  4. TIER 2 EXTRACTION                                       │
│     └─→ LLM call: extract candidate ingots                  │
│                                                             │
│  5. INGOT CREATION/UPDATE                                   │
│     └─→ Create new ingots OR update existing if similar     │
│                                                             │
│  6. SOURCE LINKING                                          │
│     └─→ Link ingots to source material                      │
│                                                             │
│  7. HISTORY LOGGING                                         │
│     └─→ Record events in ingot_history                      │
│                                                             │
│  8. QUEUE UPDATE                                            │
│     └─→ Mark entry complete, increment pass_count           │
│                                                             │
│  9. SURFACING CHECK                                         │
│     └─→ Promote ingots meeting threshold to 'surfaced'      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 3.1 Surfacing Threshold

An ingot surfaces (becomes visible for user review) when:

```
(significance >= 0.4 AND pass_count >= 2) OR user_requested = true
```

---

## 4. Tier 2 Extraction Prompt

```python
SMELT_EXTRACTION_PROMPT = """You are analysing reflective content to extract meaningful insights (called "ingots") for a digital identity preservation system.

## Context
This content comes from {source_type}: {source_description}
Word count: {word_count}

## Pre-Annotation Signals
{pre_annotation_summary}

## User Annotations (if any)
{user_annotations}

## Raw Content
{raw_content}

## Your Task
Extract 0-5 ingots from this content. An ingot is a distilled insight worth preserving — a pattern, realisation, value, memory, or emotional truth.

NOT every piece of content yields ingots. Mundane chat, logistics, or surface-level content should yield 0 ingots.

For each ingot, provide:
1. **summary**: 1-3 sentences capturing the insight (not a quote — a distillation)
2. **themes**: 2-5 theme tags (lowercase, hyphenated)
3. **emotional_tags**: 0-3 emotional tags from this list: {emotion_lexicon}
4. **patterns**: 0-3 behavioural/cognitive patterns identified
5. **significance**: 0.0-1.0 score based on:
   - Emotional intensity (weight: 0.3)
   - Theme recurrence potential (weight: 0.3)
   - Self-insight depth (weight: 0.4)
6. **confidence**: 0.0-1.0 how certain you are this is a valid insight
7. **excerpt**: The most relevant 1-2 sentences from the source (for UI display)
8. **layer_type**: What kind of personality component is this? One of: trait, memory, pattern, value, voice

## Output Format
Return valid JSON only. No markdown, no explanation.

```json
{
  "ingots": [
    {
      "summary": "...",
      "themes": ["...", "..."],
      "emotional_tags": ["..."],
      "patterns": ["..."],
      "significance": 0.0,
      "confidence": 0.0,
      "excerpt": "...",
      "layer_type": "..."
    }
  ],
  "meta": {
    "content_quality": "high|medium|low|empty",
    "suggested_reprocess": false,
    "notes": "..."
  }
}
```

If no ingots are extractable, return:
```json
{
  "ingots": [],
  "meta": {
    "content_quality": "low",
    "suggested_reprocess": false,
    "notes": "Content is logistical/surface-level, no insights detected."
  }
}
```
"""
```

---

## 5. Ingot Similarity Detection

Before creating a new ingot, check for existing similar ingots. If found, update rather than duplicate.

```python
def find_similar_ingot(candidate_summary: str, candidate_themes: list, threshold: float = 0.7) -> Optional[str]:
    """
    Find existing ingot similar to candidate.
    Returns ingot_id if found, None otherwise.
    
    Similarity based on:
    - Theme overlap (Jaccard similarity)
    - Summary embedding similarity (if available)
    - Keyword overlap in summary
    """
    conn = get_db()
    cursor = conn.cursor()
    
    # Get non-merged, non-rejected ingots
    cursor.execute("""
        SELECT id, summary, themes_json 
        FROM ingots 
        WHERE status NOT IN ('rejected', 'merged')
    """)
    
    candidates = cursor.fetchall()
    conn.close()
    
    best_match = None
    best_score = 0.0
    
    for row in candidates:
        existing_themes = json.loads(row["themes_json"]) if row["themes_json"] else []
        
        # Jaccard similarity on themes
        set_a = set(candidate_themes)
        set_b = set(existing_themes)
        if set_a or set_b:
            jaccard = len(set_a & set_b) / len(set_a | set_b)
        else:
            jaccard = 0.0
        
        # Keyword overlap in summary (simple)
        candidate_words = set(candidate_summary.lower().split())
        existing_words = set(row["summary"].lower().split())
        if candidate_words or existing_words:
            word_overlap = len(candidate_words & existing_words) / len(candidate_words | existing_words)
        else:
            word_overlap = 0.0
        
        # Combined score
        score = (jaccard * 0.6) + (word_overlap * 0.4)
        
        if score > best_score:
            best_score = score
            best_match = row["id"]
    
    if best_score >= threshold:
        return best_match
    return None
```

---

## 6. Core Processor Class

```python
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from uuid import uuid4

from ehkoforge.llm import ClaudeProvider, create_default_config
from ehkoforge.preprocessing.tier0 import preprocess_text

logger = logging.getLogger(__name__)


class SmeltProcessor:
    """
    Batch processor for extracting ingots from queued content.
    """
    
    def __init__(self, db_path: Path, config_path: Path, mirrorwell_path: Path):
        self.db_path = db_path
        self.mirrorwell_path = mirrorwell_path
        
        # LLM setup
        self.llm_config = create_default_config(config_path)
        provider_config = self.llm_config.get_provider("claude")
        
        if provider_config and provider_config.api_key:
            self.llm = ClaudeProvider(
                api_key=provider_config.api_key,
                model="claude-sonnet-4-20250514",  # Tier 2
            )
        else:
            self.llm = None
            logger.warning("No LLM configured — smelt processor disabled")
        
        # Emotion lexicon for prompt
        self.emotion_lexicon = [
            "anger", "fear", "sadness", "shame", "disgust",
            "joy", "pride", "love", "gratitude", "hope",
            "confusion", "loneliness", "nostalgia", "ambivalence"
        ]
    
    def get_db(self):
        """Get database connection."""
        import sqlite3
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn
    
    def run(self, limit: int = 10) -> Dict[str, Any]:
        """
        Process pending queue entries.
        
        Returns summary of processing results.
        """
        if not self.llm:
            return {"success": False, "error": "No LLM configured"}
        
        results = {
            "processed": 0,
            "ingots_created": 0,
            "ingots_updated": 0,
            "errors": [],
        }
        
        # Fetch pending entries
        entries = self._fetch_pending_entries(limit)
        
        for entry in entries:
            try:
                entry_result = self._process_entry(entry)
                results["processed"] += 1
                results["ingots_created"] += entry_result.get("created", 0)
                results["ingots_updated"] += entry_result.get("updated", 0)
            except Exception as e:
                logger.error(f"Error processing entry {entry['id']}: {e}")
                results["errors"].append({
                    "entry_id": entry["id"],
                    "error": str(e)
                })
                self._mark_entry_failed(entry["id"], str(e))
        
        return results
    
    def _fetch_pending_entries(self, limit: int) -> List[Dict]:
        """Fetch pending smelt queue entries."""
        conn = self.get_db()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, source_type, source_id, pre_annotation_json, pass_count
            FROM smelt_queue
            WHERE status = 'pending'
            ORDER BY priority DESC, queued_at ASC
            LIMIT ?
        """, (limit,))
        
        entries = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return entries
    
    def _process_entry(self, entry: Dict) -> Dict:
        """Process a single queue entry."""
        conn = self.get_db()
        cursor = conn.cursor()
        
        # Mark as processing
        cursor.execute("""
            UPDATE smelt_queue SET status = 'processing' WHERE id = ?
        """, (entry["id"],))
        conn.commit()
        
        # Load content
        raw_content = self._load_content(entry["source_type"], entry["source_id"])
        
        if not raw_content:
            self._mark_entry_complete(entry["id"], conn)
            conn.close()
            return {"created": 0, "updated": 0}
        
        # Ensure pre-annotation exists
        pre_annotation = entry.get("pre_annotation_json")
        if not pre_annotation:
            pre_annotation = json.dumps(preprocess_text(raw_content))
            cursor.execute("""
                UPDATE smelt_queue SET pre_annotation_json = ? WHERE id = ?
            """, (pre_annotation, entry["id"]))
            conn.commit()
        
        pre_annotation_data = json.loads(pre_annotation)
        
        # Load user annotations
        user_annotations = self._load_annotations(entry["source_type"], entry["source_id"])
        
        # Build prompt
        prompt = self._build_extraction_prompt(
            source_type=entry["source_type"],
            source_id=entry["source_id"],
            raw_content=raw_content,
            pre_annotation=pre_annotation_data,
            user_annotations=user_annotations,
        )
        
        # Call LLM
        response = self.llm.generate(
            prompt=prompt,
            system_prompt="You are an insight extraction system. Return valid JSON only.",
            max_tokens=2000,
            temperature=0.3,
        )
        
        if not response.success:
            raise Exception(f"LLM error: {response.error}")
        
        # Parse response
        try:
            extraction = json.loads(response.content)
        except json.JSONDecodeError as e:
            raise Exception(f"Invalid JSON from LLM: {e}")
        
        # Process extracted ingots
        created = 0
        updated = 0
        
        for ingot_data in extraction.get("ingots", []):
            result = self._create_or_update_ingot(
                ingot_data=ingot_data,
                source_type=entry["source_type"],
                source_id=entry["source_id"],
                pass_count=entry["pass_count"] + 1,
            )
            if result == "created":
                created += 1
            elif result == "updated":
                updated += 1
        
        # Mark complete
        self._mark_entry_complete(entry["id"], conn, entry["pass_count"] + 1)
        
        # Check for surfacing
        self._check_surfacing()
        
        conn.close()
        
        return {"created": created, "updated": updated}
    
    def _load_content(self, source_type: str, source_id: str) -> Optional[str]:
        """Load raw content from source."""
        conn = self.get_db()
        cursor = conn.cursor()
        
        if source_type == "chat_session":
            cursor.execute("""
                SELECT role, content FROM forge_messages
                WHERE session_id = ?
                ORDER BY timestamp ASC
            """, (source_id,))
            messages = cursor.fetchall()
            conn.close()
            
            if not messages:
                return None
            
            parts = []
            for msg in messages:
                prefix = "**Me:**" if msg["role"] == "user" else "**Ehko:**"
                parts.append(f"{prefix} {msg['content']}")
            
            return "\n\n".join(parts)
        
        elif source_type == "transcript_segment":
            cursor.execute("""
                SELECT content FROM transcript_segments WHERE id = ?
            """, (source_id,))
            row = cursor.fetchone()
            conn.close()
            return row["content"] if row else None
        
        elif source_type == "transcript":
            # Full transcript file
            filepath = Path(source_id)
            if filepath.exists():
                conn.close()
                return filepath.read_text(encoding="utf-8")
            conn.close()
            return None
        
        conn.close()
        return None
    
    def _load_annotations(self, source_type: str, source_id: str) -> str:
        """Load user annotations for source."""
        conn = self.get_db()
        cursor = conn.cursor()
        
        # Map source types
        if source_type == "chat_session":
            # Get all message IDs for session
            cursor.execute("""
                SELECT id FROM forge_messages WHERE session_id = ?
            """, (source_id,))
            message_ids = [row["id"] for row in cursor.fetchall()]
            
            if not message_ids:
                conn.close()
                return "None"
            
            placeholders = ",".join("?" * len(message_ids))
            cursor.execute(f"""
                SELECT annotation_type, content FROM annotations
                WHERE source_type = 'chat_message' AND source_id IN ({placeholders})
            """, message_ids)
        else:
            cursor.execute("""
                SELECT annotation_type, content FROM annotations
                WHERE source_type = ? AND source_id = ?
            """, (source_type, source_id))
        
        annotations = cursor.fetchall()
        conn.close()
        
        if not annotations:
            return "None"
        
        parts = []
        for ann in annotations:
            if ann["content"]:
                parts.append(f"- {ann['annotation_type']}: {ann['content']}")
            else:
                parts.append(f"- {ann['annotation_type']}")
        
        return "\n".join(parts)
    
    def _build_extraction_prompt(self, source_type: str, source_id: str,
                                  raw_content: str, pre_annotation: Dict,
                                  user_annotations: str) -> str:
        """Build the extraction prompt for Tier 2."""
        
        # Summarise pre-annotation
        pa = pre_annotation
        pre_summary_parts = []
        
        if pa.get("emotion_signals", {}).get("keywords_found"):
            pre_summary_parts.append(
                f"Emotion keywords: {', '.join(pa['emotion_signals']['keywords_found'])}"
            )
        
        if pa.get("flags", {}).get("high_emotion"):
            pre_summary_parts.append("High emotion flag: TRUE")
        
        if pa.get("flags", {}).get("self_reflective"):
            pre_summary_parts.append("Self-reflective flag: TRUE")
        
        if pa.get("temporal_references", {}).get("past"):
            pre_summary_parts.append(
                f"Past references: {', '.join(pa['temporal_references']['past'][:3])}"
            )
        
        if pa.get("entities", {}).get("people"):
            pre_summary_parts.append(
                f"People mentioned: {', '.join(pa['entities']['people'][:5])}"
            )
        
        pre_summary = "\n".join(pre_summary_parts) if pre_summary_parts else "No significant signals detected."
        
        return SMELT_EXTRACTION_PROMPT.format(
            source_type=source_type,
            source_description=source_id,
            word_count=pa.get("word_count", len(raw_content.split())),
            pre_annotation_summary=pre_summary,
            user_annotations=user_annotations,
            raw_content=raw_content[:8000],  # Truncate for context limits
            emotion_lexicon=", ".join(self.emotion_lexicon),
        )
    
    def _create_or_update_ingot(self, ingot_data: Dict, source_type: str,
                                 source_id: str, pass_count: int) -> str:
        """Create new ingot or update existing similar one."""
        conn = self.get_db()
        cursor = conn.cursor()
        
        summary = ingot_data.get("summary", "")
        themes = ingot_data.get("themes", [])
        
        # Check for similar existing ingot
        similar_id = find_similar_ingot(summary, themes)
        
        now = datetime.utcnow().isoformat() + "Z"
        
        if similar_id:
            # Update existing ingot
            cursor.execute("""
                SELECT significance, source_count, themes_json, emotional_tags_json, patterns_json
                FROM ingots WHERE id = ?
            """, (similar_id,))
            existing = cursor.fetchone()
            
            # Merge data
            new_significance = min(1.0, (existing["significance"] + ingot_data.get("significance", 0.5)) / 2 + 0.05)
            new_source_count = existing["source_count"] + 1
            
            existing_themes = json.loads(existing["themes_json"]) if existing["themes_json"] else []
            merged_themes = list(set(existing_themes + themes))
            
            existing_emotions = json.loads(existing["emotional_tags_json"]) if existing["emotional_tags_json"] else []
            merged_emotions = list(set(existing_emotions + ingot_data.get("emotional_tags", [])))
            
            existing_patterns = json.loads(existing["patterns_json"]) if existing["patterns_json"] else []
            merged_patterns = list(set(existing_patterns + ingot_data.get("patterns", [])))
            
            cursor.execute("""
                UPDATE ingots SET
                    updated_at = ?,
                    significance = ?,
                    source_count = ?,
                    themes_json = ?,
                    emotional_tags_json = ?,
                    patterns_json = ?,
                    last_analysis_at = ?,
                    analysis_pass = ?
                WHERE id = ?
            """, (
                now,
                new_significance,
                new_source_count,
                json.dumps(merged_themes),
                json.dumps(merged_emotions),
                json.dumps(merged_patterns),
                now,
                pass_count,
                similar_id,
            ))
            
            # Add source link
            cursor.execute("""
                INSERT OR IGNORE INTO ingot_sources (ingot_id, source_type, source_id, excerpt, added_at)
                VALUES (?, ?, ?, ?, ?)
            """, (similar_id, source_type, source_id, ingot_data.get("excerpt", ""), now))
            
            # Log history
            cursor.execute("""
                INSERT INTO ingot_history (ingot_id, event_type, event_at, new_value, trigger)
                VALUES (?, 'source_added', ?, ?, 'smelt_pass')
            """, (similar_id, now, json.dumps({"source_type": source_type, "source_id": source_id})))
            
            conn.commit()
            conn.close()
            return "updated"
        
        else:
            # Create new ingot
            ingot_id = str(uuid4())
            
            cursor.execute("""
                INSERT INTO ingots (
                    id, created_at, updated_at, status, significance, confidence,
                    summary, themes_json, emotional_tags_json, patterns_json,
                    source_count, earliest_source_date, latest_source_date,
                    last_analysis_at, analysis_model, analysis_pass
                ) VALUES (?, ?, ?, 'raw', ?, ?, ?, ?, ?, ?, 1, ?, ?, ?, 'claude-sonnet', ?)
            """, (
                ingot_id,
                now,
                now,
                ingot_data.get("significance", 0.5),
                ingot_data.get("confidence", 0.5),
                summary,
                json.dumps(themes),
                json.dumps(ingot_data.get("emotional_tags", [])),
                json.dumps(ingot_data.get("patterns", [])),
                now,
                now,
                now,
                pass_count,
            ))
            
            # Add source link
            cursor.execute("""
                INSERT INTO ingot_sources (ingot_id, source_type, source_id, excerpt, added_at)
                VALUES (?, ?, ?, ?, ?)
            """, (ingot_id, source_type, source_id, ingot_data.get("excerpt", ""), now))
            
            # Log history
            cursor.execute("""
                INSERT INTO ingot_history (ingot_id, event_type, event_at, new_value, trigger)
                VALUES (?, 'created', ?, ?, 'smelt_pass')
            """, (ingot_id, now, json.dumps(ingot_data)))
            
            conn.commit()
            conn.close()
            return "created"
    
    def _mark_entry_complete(self, entry_id: int, conn, pass_count: int = 1):
        """Mark queue entry as complete."""
        cursor = conn.cursor()
        now = datetime.utcnow().isoformat() + "Z"
        
        cursor.execute("""
            UPDATE smelt_queue SET
                status = 'complete',
                last_processed_at = ?,
                pass_count = ?
            WHERE id = ?
        """, (now, pass_count, entry_id))
        conn.commit()
    
    def _mark_entry_failed(self, entry_id: int, error: str):
        """Mark queue entry as failed."""
        conn = self.get_db()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE smelt_queue SET status = 'failed', notes = ? WHERE id = ?
        """, (error, entry_id))
        
        conn.commit()
        conn.close()
    
    def _check_surfacing(self):
        """
        Check all raw/refined ingots against surfacing threshold.
        Threshold: (significance >= 0.4 AND pass_count >= 2) OR user requests
        """
        conn = self.get_db()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE ingots SET status = 'surfaced', updated_at = ?
            WHERE status IN ('raw', 'refined')
            AND significance >= 0.4
            AND analysis_pass >= 2
        """, (datetime.utcnow().isoformat() + "Z",))
        
        surfaced_count = cursor.rowcount
        
        if surfaced_count > 0:
            logger.info(f"Surfaced {surfaced_count} ingots")
        
        conn.commit()
        conn.close()
```

---

## 7. Queue Management Functions

```python
def queue_for_smelt(source_type: str, source_id: str, priority: int = 0,
                    word_count: int = None, pre_annotation: Dict = None) -> int:
    """
    Add content to smelt queue.
    Returns queue entry ID.
    """
    conn = get_db()
    cursor = conn.cursor()
    
    now = datetime.utcnow().isoformat() + "Z"
    pre_json = json.dumps(pre_annotation) if pre_annotation else None
    
    cursor.execute("""
        INSERT INTO smelt_queue (source_type, source_id, queued_at, priority, word_count, pre_annotation_json)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (source_type, source_id, now, priority, word_count, pre_json))
    
    entry_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return entry_id


def get_queue_stats() -> Dict:
    """Get smelt queue statistics."""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT status, COUNT(*) as count, SUM(word_count) as words
        FROM smelt_queue
        GROUP BY status
    """)
    
    stats = {row["status"]: {"count": row["count"], "words": row["words"] or 0} 
             for row in cursor.fetchall()}
    
    conn.close()
    return stats


def should_auto_smelt() -> bool:
    """Check if automatic smelting should trigger."""
    stats = get_queue_stats()
    pending = stats.get("pending", {"count": 0, "words": 0})
    
    # Threshold: 5+ entries OR 2000+ words
    return pending["count"] >= 5 or pending["words"] >= 2000
```

---

## 8. API Endpoints (Flask)

```python
@app.route("/api/smelt/status", methods=["GET"])
def smelt_status():
    """Get smelt queue status."""
    stats = get_queue_stats()
    should_run = should_auto_smelt()
    
    return jsonify({
        "queue": stats,
        "should_auto_smelt": should_run,
    })


@app.route("/api/smelt/run", methods=["POST"])
def run_smelt():
    """Manually trigger smelt processing."""
    data = request.get_json() or {}
    limit = data.get("limit", 10)
    
    processor = SmeltProcessor(
        db_path=DATABASE_PATH,
        config_path=EHKOFORGE_ROOT / "Config",
        mirrorwell_path=MIRRORWELL_ROOT,
    )
    
    results = processor.run(limit=limit)
    
    return jsonify(results)


@app.route("/api/smelt/queue", methods=["POST"])
def add_to_smelt_queue():
    """Manually add content to smelt queue."""
    data = request.get_json() or {}
    
    source_type = data.get("source_type")
    source_id = data.get("source_id")
    priority = data.get("priority", 0)
    
    if not source_type or not source_id:
        return jsonify({"error": "Missing source_type or source_id"}), 400
    
    entry_id = queue_for_smelt(source_type, source_id, priority)
    
    return jsonify({"entry_id": entry_id}), 201
```

---

## 9. Scheduled Execution

```python
# Optional: Background scheduler integration
# Using APScheduler or similar

from apscheduler.schedulers.background import BackgroundScheduler

def init_scheduler(app):
    """Initialise background smelt scheduler."""
    scheduler = BackgroundScheduler()
    
    # Daily smelt at 2am
    scheduler.add_job(
        func=run_scheduled_smelt,
        trigger="cron",
        hour=2,
        minute=0,
        id="daily_smelt",
    )
    
    # Check threshold every 30 minutes
    scheduler.add_job(
        func=check_and_run_smelt,
        trigger="interval",
        minutes=30,
        id="threshold_smelt",
    )
    
    scheduler.start()
    return scheduler


def run_scheduled_smelt():
    """Run scheduled smelt processing."""
    logger.info("Running scheduled smelt")
    processor = SmeltProcessor(DATABASE_PATH, CONFIG_PATH, MIRRORWELL_PATH)
    results = processor.run(limit=50)
    logger.info(f"Scheduled smelt complete: {results}")


def check_and_run_smelt():
    """Check threshold and run if needed."""
    if should_auto_smelt():
        logger.info("Threshold reached, running auto-smelt")
        processor = SmeltProcessor(DATABASE_PATH, CONFIG_PATH, MIRRORWELL_PATH)
        results = processor.run(limit=20)
        logger.info(f"Auto-smelt complete: {results}")
```

---

## 10. Module Location

**Recommended path:** `EhkoForge/5.0 Scripts/ehkoforge/processing/smelt.py`

**Imports:**
```python
from ehkoforge.processing.smelt import SmeltProcessor, queue_for_smelt, should_auto_smelt
```

---

## 11. Open Items

- [ ] Tier 3 correlation pass (cross-ingot pattern detection)
- [ ] Re-smelt scheduling (when to re-process old content with new context)
- [ ] Token budget tracking per run
- [ ] Batch size optimisation
- [ ] Parallel processing for large queues

---

**Changelog**
- v0.1 — 2025-12-01 — Initial specification
