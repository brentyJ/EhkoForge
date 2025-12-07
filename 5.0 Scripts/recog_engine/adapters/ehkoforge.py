"""
ReCog Adapters - EhkoForge Adapter v1.0

Copyright (c) 2025 Brent Lefebure
Licensed under AGPLv3 - See LICENSE in repository root

Bridges ReCog engine to EhkoForge's SQLite database.
Maps ReCog types to existing EhkoForge tables:
- Document ← reflection_objects, forge_sessions
- Insight → ingots table
- Pattern → ingot_patterns table (new)
- Synthesis → ehko_personality_layers table
"""

import sqlite3
import json
import logging
from pathlib import Path
from typing import List, Optional, Iterator, Dict, Any
from datetime import datetime
from uuid import uuid4

from .base import RecogAdapter
from recog_engine.core.types import (
    Document,
    Insight,
    Pattern,
    PatternType,
    Synthesis,
    SynthesisType,
    ProcessingState,
    ProcessingStatus,
)


logger = logging.getLogger(__name__)


# =============================================================================
# DATABASE PATH
# =============================================================================

def get_default_db_path() -> Path:
    """Get the default database path for EhkoForge."""
    # Standard location relative to this file
    base = Path(__file__).parent.parent.parent.parent
    return base / "_data" / "ehko_index.db"


# =============================================================================
# SCHEMA MIGRATIONS
# =============================================================================

MIGRATIONS = [
    # Migration 1: Create ingot_patterns table for ReCog patterns
    """
    CREATE TABLE IF NOT EXISTS ingot_patterns (
        id TEXT PRIMARY KEY,
        summary TEXT NOT NULL,
        pattern_type TEXT NOT NULL,
        strength REAL DEFAULT 0.5,
        metadata TEXT,
        created_at TEXT NOT NULL
    );
    """,
    # Migration 2: Link table for pattern -> insights
    """
    CREATE TABLE IF NOT EXISTS ingot_pattern_insights (
        pattern_id TEXT NOT NULL,
        ingot_id TEXT NOT NULL,
        PRIMARY KEY (pattern_id, ingot_id),
        FOREIGN KEY (pattern_id) REFERENCES ingot_patterns(id),
        FOREIGN KEY (ingot_id) REFERENCES ingots(id)
    );
    """,
    # Migration 3: Add recog fields to ingots if not present
    """
    -- Add recog_insight_id column to track ReCog origin
    ALTER TABLE ingots ADD COLUMN recog_insight_id TEXT;
    """,
]


def run_migrations(conn: sqlite3.Connection) -> None:
    """Run schema migrations for ReCog adapter."""
    cursor = conn.cursor()
    
    for i, migration in enumerate(MIGRATIONS):
        try:
            cursor.executescript(migration)
            logger.debug(f"Migration {i+1} applied")
        except sqlite3.OperationalError as e:
            # Likely already applied (e.g., column already exists)
            if "duplicate column" in str(e).lower() or "already exists" in str(e).lower():
                logger.debug(f"Migration {i+1} already applied: {e}")
            else:
                logger.warning(f"Migration {i+1} error: {e}")
    
    conn.commit()


# =============================================================================
# EHKOFORGE ADAPTER
# =============================================================================

class EhkoForgeAdapter(RecogAdapter):
    """
    Adapter connecting ReCog engine to EhkoForge's SQLite database.
    
    Maps ReCog types to existing EhkoForge tables:
    - Document: Loaded from reflection_objects and forge_sessions
    - Insight: Saved to ingots table
    - Pattern: Saved to ingot_patterns table (new)
    - Synthesis: Saved to ehko_personality_layers table
    
    Usage:
        adapter = EhkoForgeAdapter()  # Uses default db path
        # or
        adapter = EhkoForgeAdapter(db_path=Path("/path/to/ehko_index.db"))
        
        # Load documents from EhkoForge
        for doc in adapter.load_documents(source_type="reflection"):
            process(doc)
        
        # Save insights back
        adapter.save_insight(insight)
    """
    
    def __init__(self, db_path: Path = None, run_migrations_on_init: bool = True):
        """
        Initialise the adapter.
        
        Args:
            db_path: Path to ehko_index.db (uses default if not provided)
            run_migrations_on_init: Whether to run schema migrations
        """
        self.db_path = db_path or get_default_db_path()
        
        if not self.db_path.exists():
            raise FileNotFoundError(f"Database not found: {self.db_path}")
        
        self._conn = None
        self._context = None
        
        if run_migrations_on_init:
            with self._get_connection() as conn:
                run_migrations(conn)
    
    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection (thread-safe)."""
        # Always create fresh connection for thread safety
        conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn
    
    def close(self) -> None:
        """Close database connection."""
        if self._conn:
            self._conn.close()
            self._conn = None
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
    
    # =========================================================================
    # DOCUMENT LOADING
    # =========================================================================
    
    def load_documents(self, **filters) -> Iterator[Document]:
        """
        Load documents from EhkoForge database.
        
        Supported filters:
            source_type: "reflection" | "session" | "transcript"
            vault: Filter by vault name
            since: Filter by created_at >= datetime
            until: Filter by created_at <= datetime
            limit: Maximum documents to return
        """
        source_type = filters.get("source_type")
        
        if source_type == "session":
            yield from self._load_session_documents(**filters)
        elif source_type == "transcript":
            yield from self._load_transcript_documents(**filters)
        else:
            # Default: load from reflection_objects
            yield from self._load_reflection_documents(**filters)
    
    def _load_reflection_documents(self, **filters) -> Iterator[Document]:
        """Load documents from reflection_objects table."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT ro.id, ro.file_path, ro.title, ro.vault, ro.type, ro.created, ro.updated
            FROM reflection_objects ro
            WHERE 1=1
        """
        params = []
        
        if filters.get("vault"):
            query += " AND ro.vault = ?"
            params.append(filters["vault"])
        
        if filters.get("since"):
            query += " AND ro.created >= ?"
            params.append(filters["since"].isoformat())
        
        if filters.get("until"):
            query += " AND ro.created <= ?"
            params.append(filters["until"].isoformat())
        
        if filters.get("limit"):
            query += " LIMIT ?"
            params.append(filters["limit"])
        
        cursor.execute(query, params)
        
        for row in cursor:
            # Read the actual file content
            content = self._read_reflection_content(row["file_path"])
            if content:
                yield Document(
                    id=str(row["id"]),
                    content=content,
                    source_type="reflection",
                    source_ref=row["file_path"],
                    metadata={
                        "title": row["title"],
                        "vault": row["vault"],
                        "type": row["type"],
                    },
                    created_at=datetime.fromisoformat(row["created"]) if row["created"] else datetime.utcnow(),
                )
    
    def _load_session_documents(self, **filters) -> Iterator[Document]:
        """Load documents from forge_sessions/forge_messages."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT fs.id, fs.title, fs.created_at,
                   GROUP_CONCAT(fm.content, '\n\n') as messages
            FROM forge_sessions fs
            JOIN forge_messages fm ON fm.session_id = fs.id
            WHERE 1=1
        """
        params = []
        
        if filters.get("since"):
            query += " AND fs.created_at >= ?"
            params.append(filters["since"].isoformat())
        
        query += " GROUP BY fs.id ORDER BY fs.created_at DESC"
        
        if filters.get("limit"):
            query += " LIMIT ?"
            params.append(filters["limit"])
        
        cursor.execute(query, params)
        
        for row in cursor:
            if row["messages"]:
                yield Document(
                    id=row["id"],
                    content=row["messages"],
                    source_type="session",
                    source_ref=f"session:{row['id']}",
                    metadata={
                        "title": row["title"],
                    },
                    created_at=datetime.fromisoformat(row["created_at"]) if row["created_at"] else datetime.utcnow(),
                )
    
    def _load_transcript_documents(self, **filters) -> Iterator[Document]:
        """Load documents from transcript_segments."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT ts.transcript_id, ts.segment_index, ts.content
            FROM transcript_segments ts
            ORDER BY ts.transcript_id, ts.segment_index
        """
        
        if filters.get("limit"):
            query += f" LIMIT {filters['limit']}"
        
        cursor.execute(query)
        
        # Group segments by transcript
        current_transcript = None
        segments = []
        
        for row in cursor:
            if current_transcript != row["transcript_id"]:
                if segments:
                    yield Document(
                        id=current_transcript,
                        content="\n\n".join(segments),
                        source_type="transcript",
                        source_ref=f"transcript:{current_transcript}",
                        metadata={},
                        created_at=datetime.utcnow(),
                    )
                current_transcript = row["transcript_id"]
                segments = []
            segments.append(row["content"])
        
        # Yield last transcript
        if segments:
            yield Document(
                id=current_transcript,
                content="\n\n".join(segments),
                source_type="transcript",
                source_ref=f"transcript:{current_transcript}",
                metadata={},
                created_at=datetime.utcnow(),
            )
    
    def _read_reflection_content(self, path: str) -> Optional[str]:
        """Read content from a reflection file."""
        try:
            # Path is relative to vault root
            vault_root = self.db_path.parent.parent
            full_path = vault_root / path
            
            if full_path.exists():
                return full_path.read_text(encoding="utf-8")
            else:
                logger.warning(f"Reflection file not found: {full_path}")
                return None
        except Exception as e:
            logger.error(f"Error reading reflection {path}: {e}")
            return None
    
    def get_document(self, doc_id: str) -> Optional[Document]:
        """Get a specific document by ID."""
        for doc in self.load_documents():
            if doc.id == doc_id:
                return doc
        return None
    
    # =========================================================================
    # INSIGHT MANAGEMENT (-> ingots table)
    # =========================================================================
    
    def save_insight(self, insight: Insight) -> None:
        """
        Save insight to ingots table.
        
        Maps ReCog Insight to EhkoForge ingot schema.
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Check if ingot with this recog_insight_id exists
        cursor.execute(
            "SELECT id FROM ingots WHERE recog_insight_id = ?",
            (insight.id,)
        )
        existing = cursor.fetchone()
        
        if existing:
            # Update existing
            cursor.execute("""
                UPDATE ingots SET
                    summary = ?,
                    themes_json = ?,
                    significance = ?,
                    confidence = ?,
                    updated_at = ?
                WHERE recog_insight_id = ?
            """, (
                insight.summary,
                json.dumps(insight.themes),
                insight.significance,
                insight.confidence,
                datetime.utcnow().isoformat(),
                insight.id,
            ))
        else:
            # Insert new
            ingot_id = str(uuid4())
            cursor.execute("""
                INSERT INTO ingots (
                    id, summary, themes_json, significance, 
                    confidence, status, created_at, updated_at, recog_insight_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                ingot_id,
                insight.summary,
                json.dumps(insight.themes),
                insight.significance,
                insight.confidence,
                "raw",
                insight.created_at.isoformat(),
                datetime.utcnow().isoformat(),
                insight.id,
            ))
            
            # Link to sources
            for source_id in insight.source_ids:
                try:
                    cursor.execute("""
                        INSERT OR IGNORE INTO ingot_sources (ingot_id, source_type, source_id, added_at)
                        VALUES (?, ?, ?, ?)
                    """, (ingot_id, "document", source_id, datetime.utcnow().isoformat()))
                except sqlite3.OperationalError:
                    pass  # Table might not exist
        
        conn.commit()
    
    def get_insights(self, **filters) -> List[Insight]:
        """
        Get insights from ingots table.
        
        Supported filters:
            min_significance: Filter by significance >= threshold
            themes: Filter by theme match
            status: Filter by status
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT id, summary, themes_json, significance, confidence, 
                   created_at, recog_insight_id
            FROM ingots
            WHERE 1=1
        """
        params = []
        
        if filters.get("min_significance"):
            query += " AND significance >= ?"
            params.append(filters["min_significance"])
        
        if filters.get("status"):
            query += " AND status = ?"
            params.append(filters["status"])
        
        cursor.execute(query, params)
        
        insights = []
        for row in cursor:
            themes = json.loads(row["themes_json"]) if row["themes_json"] else []
            
            # Apply theme filter in Python (JSON field)
            if filters.get("themes"):
                if not set(filters["themes"]) & set(themes):
                    continue
            
            insights.append(Insight(
                id=row["recog_insight_id"] or row["id"],
                summary=row["summary"],
                themes=themes,
                significance=row["significance"] or 0.5,
                confidence=row["confidence"] or 0.5,
                source_ids=[],  # Would need join to get these
                excerpts=[],
                created_at=datetime.fromisoformat(row["created_at"]) if row["created_at"] else datetime.utcnow(),
                updated_at=datetime.utcnow(),
            ))
        
        return insights
    
    # =========================================================================
    # PATTERN MANAGEMENT (-> ingot_patterns table)
    # =========================================================================
    
    def save_pattern(self, pattern: Pattern) -> None:
        """Save pattern to ingot_patterns table."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Upsert pattern
        cursor.execute("""
            INSERT OR REPLACE INTO ingot_patterns (
                id, summary, pattern_type, strength, metadata, created_at
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, (
            pattern.id,
            pattern.summary,
            pattern.pattern_type.value,
            pattern.strength,
            json.dumps(pattern.metadata),
            pattern.created_at.isoformat(),
        ))
        
        # Update insight links
        cursor.execute(
            "DELETE FROM ingot_pattern_insights WHERE pattern_id = ?",
            (pattern.id,)
        )
        
        for insight_id in pattern.insight_ids:
            # Find the ingot ID for this insight
            cursor.execute(
                "SELECT id FROM ingots WHERE recog_insight_id = ?",
                (insight_id,)
            )
            row = cursor.fetchone()
            ingot_id = row["id"] if row else insight_id
            
            cursor.execute("""
                INSERT OR IGNORE INTO ingot_pattern_insights (pattern_id, ingot_id)
                VALUES (?, ?)
            """, (pattern.id, ingot_id))
        
        conn.commit()
    
    def get_patterns(self, **filters) -> List[Pattern]:
        """Get patterns from ingot_patterns table."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        query = "SELECT * FROM ingot_patterns WHERE 1=1"
        params = []
        
        if filters.get("pattern_type"):
            query += " AND pattern_type = ?"
            params.append(filters["pattern_type"].value if isinstance(filters["pattern_type"], PatternType) else filters["pattern_type"])
        
        if filters.get("min_strength"):
            query += " AND strength >= ?"
            params.append(filters["min_strength"])
        
        cursor.execute(query, params)
        
        patterns = []
        for row in cursor:
            # Get linked insight IDs
            cursor.execute("""
                SELECT i.recog_insight_id, i.id
                FROM ingot_pattern_insights ipi
                JOIN ingots i ON i.id = ipi.ingot_id
                WHERE ipi.pattern_id = ?
            """, (row["id"],))
            insight_ids = [r["recog_insight_id"] or r["id"] for r in cursor.fetchall()]
            
            patterns.append(Pattern(
                id=row["id"],
                summary=row["summary"],
                pattern_type=PatternType(row["pattern_type"]),
                insight_ids=insight_ids,
                strength=row["strength"],
                metadata=json.loads(row["metadata"]) if row["metadata"] else {},
                created_at=datetime.fromisoformat(row["created_at"]),
            ))
        
        return patterns
    
    # =========================================================================
    # SYNTHESIS MANAGEMENT (-> ehko_personality_layers table)
    # =========================================================================
    
    def save_synthesis(self, synthesis: Synthesis) -> None:
        """
        Save synthesis to ehko_personality_layers table.
        
        Maps SynthesisType to layer_type:
        - TRAIT → "trait"
        - BELIEF → "value"
        - TENDENCY → "pattern"
        - THEME → "trait" (fallback)
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Map synthesis type to layer type
        layer_type_map = {
            SynthesisType.TRAIT: "trait",
            SynthesisType.BELIEF: "value",
            SynthesisType.TENDENCY: "pattern",
            SynthesisType.THEME: "trait",
        }
        layer_type = layer_type_map.get(synthesis.synthesis_type, "trait")
        
        # Use significance as weight
        weight = synthesis.significance
        
        # Check if exists
        cursor.execute(
            "SELECT id FROM ehko_personality_layers WHERE ingot_id = ?",
            (synthesis.id,)
        )
        existing = cursor.fetchone()
        
        if existing:
            cursor.execute("""
                UPDATE ehko_personality_layers SET
                    layer_type = ?,
                    content = ?,
                    weight = ?
                WHERE ingot_id = ?
            """, (layer_type, synthesis.summary, weight, synthesis.id))
        else:
            cursor.execute("""
                INSERT INTO ehko_personality_layers (
                    ingot_id, layer_type, content, weight, active, integrated_at
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                synthesis.id,
                layer_type,
                synthesis.summary,
                weight,
                1,  # active
                synthesis.created_at.isoformat(),
            ))
        
        conn.commit()
    
    def get_syntheses(self, **filters) -> List[Synthesis]:
        """Get syntheses from ehko_personality_layers table."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Reverse map layer_type to SynthesisType
        type_map = {
            "trait": SynthesisType.TRAIT,
            "value": SynthesisType.BELIEF,
            "pattern": SynthesisType.TENDENCY,
            "memory": SynthesisType.THEME,
            "voice": SynthesisType.TRAIT,
        }
        
        query = "SELECT * FROM ehko_personality_layers WHERE active = 1"
        params = []
        
        if filters.get("synthesis_type"):
            layer_type_map = {
                SynthesisType.TRAIT: "trait",
                SynthesisType.BELIEF: "value",
                SynthesisType.TENDENCY: "pattern",
                SynthesisType.THEME: "memory",
            }
            st = filters["synthesis_type"]
            if isinstance(st, SynthesisType):
                query += " AND layer_type = ?"
                params.append(layer_type_map.get(st, "trait"))
        
        cursor.execute(query, params)
        
        syntheses = []
        for row in cursor:
            syntheses.append(Synthesis(
                id=row["ingot_id"],
                summary=row["content"],
                synthesis_type=type_map.get(row["layer_type"], SynthesisType.THEME),
                pattern_ids=[],
                significance=row["weight"] or 0.5,
                confidence=0.5,
                metadata={},
                created_at=datetime.fromisoformat(row["integrated_at"]) if row["integrated_at"] else datetime.utcnow(),
            ))
        
        return syntheses
    
    # =========================================================================
    # CONTEXT MANAGEMENT
    # =========================================================================
    
    def set_context(self, context: str) -> None:
        """Set domain context for prompts."""
        self._context = context
    
    def get_context(self) -> Optional[str]:
        """Get domain context."""
        if self._context:
            return self._context
        
        # Default context for EhkoForge
        return (
            "This is a personal digital identity preservation system. "
            "Content includes reflections, journals, chat transcripts, and voice notes. "
            "The goal is to extract meaningful patterns about the person's identity, "
            "values, beliefs, and personality traits."
        )
    
    def get_existing_themes(self) -> List[str]:
        """Get themes from existing ingots."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT DISTINCT themes_json FROM ingots WHERE themes_json IS NOT NULL")
        
        all_themes = set()
        for row in cursor:
            try:
                themes = json.loads(row["themes_json"])
                all_themes.update(themes)
            except:
                pass
        
        return list(all_themes)
    
    # =========================================================================
    # STATE MANAGEMENT
    # =========================================================================
    
    def save_state(self, state: ProcessingState) -> None:
        """Save processing state (not implemented for EhkoForge)."""
        # Could store in a processing_runs table if needed
        pass
    
    def load_state(self, corpus_id: str) -> Optional[ProcessingState]:
        """Load processing state (not implemented for EhkoForge)."""
        return None
    
    # =========================================================================
    # UTILITY
    # =========================================================================
    
    def stats(self) -> Dict[str, int]:
        """Get database statistics."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        stats = {}
        
        cursor.execute("SELECT COUNT(*) FROM reflection_objects")
        stats["reflections"] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM ingots")
        stats["insights"] = cursor.fetchone()[0]
        
        try:
            cursor.execute("SELECT COUNT(*) FROM ingot_patterns")
            stats["patterns"] = cursor.fetchone()[0]
        except:
            stats["patterns"] = 0
        
        cursor.execute("SELECT COUNT(*) FROM ehko_personality_layers")
        stats["syntheses"] = cursor.fetchone()[0]
        
        # Document ingestion stats
        try:
            cursor.execute("SELECT COUNT(*) FROM ingested_documents")
            stats["ingested_documents"] = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM document_chunks WHERE recog_processed = 0")
            stats["unprocessed_chunks"] = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM document_chunks WHERE recog_processed = 1")
            stats["processed_chunks"] = cursor.fetchone()[0]
        except:
            stats["ingested_documents"] = 0
            stats["unprocessed_chunks"] = 0
            stats["processed_chunks"] = 0
        
        return stats
    
    # =========================================================================
    # DOCUMENT CHUNK METHODS
    # =========================================================================
    
    def load_unprocessed_chunks(self, limit: int = 50) -> List[Document]:
        """
        Load unprocessed document chunks as ReCog Documents.
        
        Args:
            limit: Maximum chunks to return
            
        Returns:
            List of Document objects ready for ReCog processing
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                c.id, c.document_id, c.chunk_index, c.content, c.token_count,
                c.preceding_context, c.following_context,
                d.filename, d.file_type, d.doc_subject, d.doc_date, d.doc_author,
                d.metadata as doc_metadata
            FROM document_chunks c
            JOIN ingested_documents d ON c.document_id = d.id
            WHERE c.recog_processed = 0
            ORDER BY d.ingested_at ASC, c.chunk_index ASC
            LIMIT ?
        """, (limit,))
        
        # Collect all results before returning (thread safety)
        rows = cursor.fetchall()
        conn.close()
        
        documents = []
        for row in rows:
            # Build content with context
            content_parts = []
            if row["preceding_context"]:
                content_parts.append(f"[...] {row['preceding_context']}")
            content_parts.append(row["content"])
            if row["following_context"]:
                content_parts.append(f"{row['following_context']} [...]")
            
            full_content = "\n".join(content_parts)
            
            # Parse doc metadata
            doc_meta = {}
            if row["doc_metadata"]:
                try:
                    doc_meta = json.loads(row["doc_metadata"])
                except:
                    pass
            
            documents.append(Document(
                id=f"chunk:{row['id']}",
                content=full_content,
                source_type="document_chunk",
                source_ref=f"doc:{row['document_id']}:chunk:{row['chunk_index']}",
                metadata={
                    "chunk_id": row["id"],
                    "document_id": row["document_id"],
                    "chunk_index": row["chunk_index"],
                    "filename": row["filename"],
                    "file_type": row["file_type"],
                    "title": row["doc_subject"] or row["filename"],
                    "author": row["doc_author"],
                    "date": row["doc_date"],
                    **doc_meta,
                },
                created_at=datetime.utcnow(),
            ))
        
        return documents
    
    def get_unprocessed_chunk_count(self) -> int:
        """Get count of unprocessed document chunks."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM document_chunks WHERE recog_processed = 0")
        result = cursor.fetchone()[0]
        conn.close()
        return result
    
    def get_chunk_token_estimate(self, limit: int = 50) -> int:
        """Estimate total tokens for unprocessed chunks."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT COALESCE(SUM(token_count), 0) 
            FROM (
                SELECT token_count FROM document_chunks 
                WHERE recog_processed = 0 
                ORDER BY document_id, chunk_index 
                LIMIT ?
            )
        """, (limit,))
        result = cursor.fetchone()[0]
        conn.close()
        return result
    
    def mark_chunk_processed(
        self, 
        chunk_id: int, 
        tier0_signals: Dict = None,
        insight_id: str = None
    ) -> None:
        """
        Mark a document chunk as processed.
        
        Args:
            chunk_id: The chunk ID (from metadata)
            tier0_signals: Tier 0 signals extracted
            insight_id: ID of insight created from this chunk
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE document_chunks SET
                recog_processed = 1,
                tier0_signals = ?,
                recog_insight_id = ?
            WHERE id = ?
        """, (
            json.dumps(tier0_signals) if tier0_signals else None,
            insight_id,
            chunk_id,
        ))
        conn.commit()
        conn.close()
    
    def mark_document_complete(self, document_id: int) -> None:
        """Mark a document as fully processed if all chunks are done."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Check if all chunks are processed
        cursor.execute("""
            SELECT COUNT(*) FROM document_chunks 
            WHERE document_id = ? AND recog_processed = 0
        """, (document_id,))
        unprocessed = cursor.fetchone()[0]
        
        if unprocessed == 0:
            # Count insights extracted
            cursor.execute("""
                SELECT COUNT(*) FROM document_chunks 
                WHERE document_id = ? AND recog_insight_id IS NOT NULL
            """, (document_id,))
            insights = cursor.fetchone()[0]
            
            cursor.execute("""
                UPDATE ingested_documents SET
                    status = 'complete',
                    insights_extracted = ?,
                    completed_at = ?
                WHERE id = ?
            """, (insights, datetime.utcnow().isoformat(), document_id))
            conn.commit()
        
        conn.close()
    
    def save_chunk_insight(self, chunk_id: int, insight: Insight) -> str:
        """
        Save insight from a document chunk and link it.
        
        Args:
            chunk_id: Source chunk ID
            insight: The insight to save
            
        Returns:
            The ingot ID
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Get chunk metadata for source tracking
        cursor.execute("""
            SELECT c.document_id, d.filename 
            FROM document_chunks c
            JOIN ingested_documents d ON c.document_id = d.id
            WHERE c.id = ?
        """, (chunk_id,))
        row = cursor.fetchone()
        document_id = row["document_id"] if row else None
        filename = row["filename"] if row else "unknown"
        
        # Create ingot
        ingot_id = str(uuid4())
        cursor.execute("""
            INSERT INTO ingots (
                id, summary, themes_json, significance, 
                confidence, status, created_at, updated_at, recog_insight_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            ingot_id,
            insight.summary,
            json.dumps(insight.themes),
            insight.significance,
            insight.confidence,
            "raw",
            insight.created_at.isoformat(),
            datetime.utcnow().isoformat(),
            insight.id,
        ))
        
        # Link to document source
        cursor.execute("""
            INSERT OR IGNORE INTO ingot_sources (ingot_id, source_type, source_id, added_at)
            VALUES (?, ?, ?, ?)
        """, (ingot_id, "document_chunk", str(chunk_id), datetime.utcnow().isoformat()))
        
        # Mark chunk as processed with insight link
        cursor.execute("""
            UPDATE document_chunks SET
                recog_processed = 1,
                recog_insight_id = ?
            WHERE id = ?
        """, (ingot_id, chunk_id))
        
        conn.commit()
        conn.close()
        
        # Check if document is complete
        if document_id:
            self.mark_document_complete(document_id)
        
        return ingot_id


# =============================================================================
# MODULE EXPORTS
# =============================================================================

__all__ = ["EhkoForgeAdapter", "get_default_db_path", "run_migrations"]
