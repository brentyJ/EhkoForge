"""
ReCog Engine - Smelt Processor v0.1

Copyright (c) 2025 Brent
Licensed under AGPLv3 - See LICENSE in this directory
Commercial licenses available: brent@ehkolabs.io

Batch job for extracting ingots from queued content via Tier 2 LLM analysis.
Handles queue management, ingot creation/update, similarity detection,
and surfacing logic.
"""

import json
import logging
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from uuid import uuid4

# LLM infrastructure (MIT-licensed ehkoforge.llm)
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from ehkoforge.llm import create_default_config, get_provider_for_processing

# ReCog components (AGPL)
from recog_engine.tier0 import preprocess_text, summarise_for_prompt

logger = logging.getLogger(__name__)


# =============================================================================
# CONSTANTS
# =============================================================================

SMELT_EXTRACTION_PROMPT = """You are analysing reflective content to extract meaningful insights (called "ingots") for a digital identity preservation system.

## Context
This content comes from {source_type}: {source_description}
Word count: {word_count}

## CRITICAL: Speaker Attribution
The content below contains messages from TWO speakers:
- <USER_MESSAGE> tags contain what the USER (the person whose identity we're preserving) said
- <EHKO_MESSAGE> tags contain what the AI ASSISTANT said

**ONLY extract insights from USER_MESSAGE content.** The Ehko/assistant messages are context only — never attribute the assistant's words or ideas to the user.

## Pre-Annotation Signals
{pre_annotation_summary}

## User Annotations
{user_annotations}

## Raw Content
{raw_content}

## Your Task
Extract 0-5 ingots from this content. An ingot is a distilled insight worth preserving — a pattern, realisation, value, memory, or emotional truth.

NOT every piece of content yields ingots. Mundane chat, logistics, or surface-level content should yield 0 ingots.

**IMPORTANT:** Only extract insights based on what the USER said (inside <USER_MESSAGE> tags). Do not extract insights from EHKO_MESSAGE content.

For each ingot, provide:
1. **summary**: 1-3 sentences capturing the insight (not a quote — a distillation)
2. **themes**: 2-5 theme tags (lowercase, hyphenated)
3. **emotional_tags**: 0-3 emotional tags from: anger, fear, sadness, shame, disgust, joy, pride, love, gratitude, hope, confusion, loneliness, nostalgia, ambivalence
4. **patterns**: 0-3 behavioural/cognitive patterns identified
5. **significance**: 0.0-1.0 score based on:
   - Emotional intensity (weight: 0.3)
   - Theme recurrence potential (weight: 0.3)
   - Self-insight depth (weight: 0.4)
6. **confidence**: 0.0-1.0 how certain you are this is a valid insight
7. **excerpt**: The most relevant 1-2 sentences FROM THE USER'S WORDS (from <USER_MESSAGE> only)
8. **layer_type**: What kind of personality component is this? One of: trait, memory, pattern, value, voice

## Output Format
Return valid JSON only. No markdown, no explanation, no backticks.

{{
  "ingots": [
    {{
      "summary": "...",
      "themes": ["...", "..."],
      "emotional_tags": ["..."],
      "patterns": ["..."],
      "significance": 0.0,
      "confidence": 0.0,
      "excerpt": "...",
      "layer_type": "..."
    }}
  ],
  "meta": {{
    "content_quality": "high|medium|low|empty",
    "suggested_reprocess": false,
    "notes": "..."
  }}
}}

If no ingots are extractable, return:
{{
  "ingots": [],
  "meta": {{
    "content_quality": "low",
    "suggested_reprocess": false,
    "notes": "Content is logistical/surface-level, no insights detected."
  }}
}}
"""

SURFACING_SIGNIFICANCE_THRESHOLD = 0.4
SURFACING_PASS_THRESHOLD = 2
SIMILARITY_THRESHOLD = 0.7


# =============================================================================
# SMELT PROCESSOR CLASS
# =============================================================================

class SmeltProcessor:
    """
    Batch processor for extracting ingots from queued content.
    """
    
    def __init__(self, db_path: Path, config_path: Path, mirrorwell_path: Path):
        """
        Initialise the smelt processor.
        
        Args:
            db_path: Path to ehko_index.db
            config_path: Path to Config directory containing llm_config.json
            mirrorwell_path: Path to Mirrorwell vault root
        """
        self.db_path = db_path
        self.mirrorwell_path = mirrorwell_path
        
        # LLM setup via provider factory
        self.llm_config = create_default_config(config_path)
        self.llm = get_provider_for_processing(self.llm_config)
        
        if self.llm:
            logger.info(f"Smelt processor initialised with {self.llm.PROVIDER_NAME}:{self.llm.model}")
        else:
            logger.warning("No LLM configured — smelt processor disabled")
    
    def get_db(self) -> sqlite3.Connection:
        """Get database connection with row factory."""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn
    
    def run(self, limit: int = 10) -> Dict[str, Any]:
        """
        Process pending queue entries.
        
        Args:
            limit: Maximum entries to process in this run
            
        Returns:
            Summary of processing results
        """
        if not self.llm:
            return {"success": False, "error": "No LLM configured"}
        
        results = {
            "success": True,
            "processed": 0,
            "ingots_created": 0,
            "ingots_updated": 0,
            "surfaced": 0,
            "errors": [],
        }
        
        # Fetch pending entries
        entries = self._fetch_pending_entries(limit)
        logger.info(f"Found {len(entries)} pending entries to process")
        
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
        
        # Check for surfacing after all processing
        surfaced = self._check_surfacing()
        results["surfaced"] = surfaced
        
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
            logger.warning(f"No content found for {entry['source_type']}:{entry['source_id']}")
            self._mark_entry_complete(entry["id"], conn, entry["pass_count"] + 1)
            conn.close()
            return {"created": 0, "updated": 0}
        
        # Ensure pre-annotation exists
        pre_annotation = entry.get("pre_annotation_json")
        if not pre_annotation:
            pre_annotation_data = preprocess_text(raw_content)
            pre_annotation = json.dumps(pre_annotation_data)
            cursor.execute("""
                UPDATE smelt_queue SET pre_annotation_json = ? WHERE id = ?
            """, (pre_annotation, entry["id"]))
            conn.commit()
        else:
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
        logger.info(f"Calling LLM for entry {entry['id']}")
        response = self.llm.generate(
            prompt=prompt,
            system_prompt="You are an insight extraction system. Return valid JSON only, no markdown formatting.",
            max_tokens=2000,
            temperature=0.3,
        )
        
        if not response.success:
            raise Exception(f"LLM error: {response.error}")
        
        # Parse response - handle potential markdown wrapping
        response_text = response.content.strip()
        if response_text.startswith("```"):
            # Remove markdown code blocks
            lines = response_text.split("\n")
            lines = [l for l in lines if not l.startswith("```")]
            response_text = "\n".join(lines)
        
        try:
            extraction = json.loads(response_text)
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON from LLM: {response_text[:200]}")
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
        conn.close()
        
        logger.info(f"Entry {entry['id']} complete: {created} created, {updated} updated")
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
                # Use clear XML-style markers to distinguish speakers
                if msg["role"] == "user":
                    parts.append(f"<USER_MESSAGE>\n{msg['content']}\n</USER_MESSAGE>")
                else:
                    parts.append(f"<EHKO_MESSAGE>\n{msg['content']}\n</EHKO_MESSAGE>")
            
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
            conn.close()
            if filepath.exists():
                return filepath.read_text(encoding="utf-8")
            return None
        
        conn.close()
        return None
    
    def _load_annotations(self, source_type: str, source_id: str) -> str:
        """Load user annotations for source."""
        conn = self.get_db()
        cursor = conn.cursor()
        
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
        pre_summary = summarise_for_prompt(pre_annotation)
        
        # Truncate content if too long
        max_content_chars = 8000
        if len(raw_content) > max_content_chars:
            raw_content = raw_content[:max_content_chars] + "\n\n[... content truncated ...]"
        
        return SMELT_EXTRACTION_PROMPT.format(
            source_type=source_type,
            source_description=source_id,
            word_count=pre_annotation.get("word_count", len(raw_content.split())),
            pre_annotation_summary=pre_summary,
            user_annotations=user_annotations,
            raw_content=raw_content,
        )
    
    def _create_or_update_ingot(self, ingot_data: Dict, source_type: str,
                                 source_id: str, pass_count: int) -> str:
        """Create new ingot or update existing similar one."""
        conn = self.get_db()
        cursor = conn.cursor()
        
        summary = ingot_data.get("summary", "")
        themes = ingot_data.get("themes", [])
        
        if not summary:
            conn.close()
            return "skipped"
        
        # Check for similar existing ingot
        similar_id = self._find_similar_ingot(cursor, summary, themes)
        
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
            
            # Update status to refined if multiple sources
            new_status = "refined" if new_source_count >= 2 else "raw"
            
            cursor.execute("""
                UPDATE ingots SET
                    updated_at = ?,
                    status = ?,
                    significance = ?,
                    source_count = ?,
                    themes_json = ?,
                    emotional_tags_json = ?,
                    patterns_json = ?,
                    latest_source_date = ?,
                    last_analysis_at = ?,
                    analysis_pass = ?
                WHERE id = ?
            """, (
                now,
                new_status,
                new_significance,
                new_source_count,
                json.dumps(merged_themes),
                json.dumps(merged_emotions),
                json.dumps(merged_patterns),
                now,
                now,
                pass_count,
                similar_id,
            ))
            
            # Add source link
            cursor.execute("""
                INSERT OR IGNORE INTO ingot_sources (ingot_id, source_type, source_id, excerpt, added_at)
                VALUES (?, ?, ?, ?, ?)
            """, (similar_id, source_type, str(source_id), ingot_data.get("excerpt", ""), now))
            
            # Log history
            cursor.execute("""
                INSERT INTO ingot_history (ingot_id, event_type, event_at, new_value, trigger)
                VALUES (?, 'source_added', ?, ?, 'smelt_pass')
            """, (similar_id, now, json.dumps({"source_type": source_type, "source_id": source_id})))
            
            conn.commit()
            conn.close()
            logger.info(f"Updated ingot {similar_id} with new source")
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
            """, (ingot_id, source_type, str(source_id), ingot_data.get("excerpt", ""), now))
            
            # Log history
            cursor.execute("""
                INSERT INTO ingot_history (ingot_id, event_type, event_at, new_value, trigger)
                VALUES (?, 'created', ?, ?, 'smelt_pass')
            """, (ingot_id, now, json.dumps(ingot_data)))
            
            conn.commit()
            conn.close()
            logger.info(f"Created new ingot {ingot_id}")
            return "created"
    
    def _find_similar_ingot(self, cursor, candidate_summary: str, candidate_themes: List[str]) -> Optional[str]:
        """
        Find existing ingot similar to candidate.
        Returns ingot_id if found, None otherwise.
        """
        # Get non-merged, non-rejected ingots
        cursor.execute("""
            SELECT id, summary, themes_json 
            FROM ingots 
            WHERE status NOT IN ('rejected', 'merged')
        """)
        
        candidates = cursor.fetchall()
        
        if not candidates:
            return None
        
        best_match = None
        best_score = 0.0
        
        candidate_themes_set = set(t.lower() for t in candidate_themes)
        candidate_words = set(candidate_summary.lower().split())
        
        for row in candidates:
            existing_themes = json.loads(row["themes_json"]) if row["themes_json"] else []
            existing_themes_set = set(t.lower() for t in existing_themes)
            
            # Jaccard similarity on themes
            if candidate_themes_set or existing_themes_set:
                theme_intersection = len(candidate_themes_set & existing_themes_set)
                theme_union = len(candidate_themes_set | existing_themes_set)
                jaccard = theme_intersection / theme_union if theme_union > 0 else 0.0
            else:
                jaccard = 0.0
            
            # Keyword overlap in summary
            existing_words = set(row["summary"].lower().split())
            if candidate_words or existing_words:
                word_intersection = len(candidate_words & existing_words)
                word_union = len(candidate_words | existing_words)
                word_overlap = word_intersection / word_union if word_union > 0 else 0.0
            else:
                word_overlap = 0.0
            
            # Combined score
            score = (jaccard * 0.6) + (word_overlap * 0.4)
            
            if score > best_score:
                best_score = score
                best_match = row["id"]
        
        if best_score >= SIMILARITY_THRESHOLD:
            logger.info(f"Found similar ingot {best_match} with score {best_score:.2f}")
            return best_match
        
        return None
    
    def _mark_entry_complete(self, entry_id: int, conn: sqlite3.Connection, pass_count: int = 1):
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
    
    def _check_surfacing(self) -> int:
        """
        Check all raw/refined ingots against surfacing threshold.
        
        Surfacing criteria:
        - significance >= 0.4 on first pass (immediate surface for high-quality)
        - OR (significance >= 0.3 AND pass_count >= 2)
        - OR source_count >= 3
        
        Returns count of newly surfaced ingots.
        """
        conn = self.get_db()
        cursor = conn.cursor()
        
        now = datetime.utcnow().isoformat() + "Z"
        
        # Surface ingots that meet any threshold
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
        
        if surfaced_count > 0:
            logger.info(f"Surfaced {surfaced_count} ingots")
        
        conn.commit()
        conn.close()
        
        return surfaced_count


# =============================================================================
# QUEUE MANAGEMENT FUNCTIONS
# =============================================================================

def queue_for_smelt(db_path: Path, source_type: str, source_id: str, 
                    priority: int = 0, word_count: int = None, 
                    pre_annotation: Dict = None) -> int:
    """
    Add content to smelt queue.
    
    Args:
        db_path: Path to database
        source_type: Type of source ('chat_session', 'transcript', etc.)
        source_id: ID or path of source
        priority: Processing priority (higher = sooner)
        word_count: Word count if known
        pre_annotation: Pre-computed Tier 0 annotation
        
    Returns:
        Queue entry ID
    """
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    now = datetime.utcnow().isoformat() + "Z"
    pre_json = json.dumps(pre_annotation) if pre_annotation else None
    
    cursor.execute("""
        INSERT INTO smelt_queue (source_type, source_id, queued_at, priority, word_count, pre_annotation_json)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (source_type, str(source_id), now, priority, word_count, pre_json))
    
    entry_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    logger.info(f"Queued {source_type}:{source_id} for smelt (entry {entry_id})")
    return entry_id


def get_queue_stats(db_path: Path) -> Dict:
    """Get smelt queue statistics."""
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT status, COUNT(*) as count, COALESCE(SUM(word_count), 0) as words
        FROM smelt_queue
        GROUP BY status
    """)
    
    stats = {row["status"]: {"count": row["count"], "words": row["words"]} 
             for row in cursor.fetchall()}
    
    conn.close()
    return stats


def should_auto_smelt(db_path: Path) -> bool:
    """Check if automatic smelting should trigger."""
    stats = get_queue_stats(db_path)
    pending = stats.get("pending", {"count": 0, "words": 0})
    
    # Threshold: 5+ entries OR 2000+ words
    return pending["count"] >= 5 or pending["words"] >= 2000


# =============================================================================
# MODULE EXPORTS
# =============================================================================

__all__ = [
    "SmeltProcessor",
    "queue_for_smelt",
    "get_queue_stats",
    "should_auto_smelt",
]
