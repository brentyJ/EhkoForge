"""
ReCog Scheduler v1.0

Manages automatic ReCog processing with user confirmation for costly operations.

Behaviour:
- Tier 0: Automatic, silent, free (signal annotation)
- Tier 1-3: Queued with cost estimate, requires user confirmation

Usage:
    scheduler = RecogScheduler(db_path, config_path)
    
    # Check for work and queue it
    pending = scheduler.check_and_queue()
    
    # Get pending confirmations
    awaiting = scheduler.get_pending_confirmations()
    
    # User confirms
    scheduler.confirm_operation(operation_id)
    
    # Process confirmed operations
    results = scheduler.process_confirmed()
"""

import json
import logging
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum

# ReCog components
from recog_engine import (
    Document,
    RecogConfig,
    Extractor,
    Correlator,
    Synthesizer,
    EhkoForgeAdapter,
)
from recog_engine.core.signal import SignalProcessor
from recog_engine.core.ehko_llm import create_recog_provider

logger = logging.getLogger(__name__)


# =============================================================================
# CONSTANTS
# =============================================================================

class OperationType(Enum):
    EXTRACT = "extract"                 # Tier 1 from sessions
    EXTRACT_DOCS = "extract_docs"       # Tier 1 from document chunks
    CORRELATE = "correlate"             # Tier 2
    SYNTHESISE = "synthesise"           # Tier 3
    FULL_SWEEP = "full_sweep"           # All tiers


# Mana costs per operation (configurable)
MANA_COSTS = {
    OperationType.EXTRACT: 2,       # Per session
    OperationType.EXTRACT_DOCS: 1,  # Per chunk (cheaper, higher volume)
    OperationType.CORRELATE: 8,     # Per batch
    OperationType.SYNTHESISE: 12,   # Per synthesis run
    OperationType.FULL_SWEEP: 20,   # Discounted bundle
}

# Token estimates for cost calculation
TOKEN_ESTIMATES = {
    OperationType.EXTRACT: 4000,      # Per session
    OperationType.EXTRACT_DOCS: 3000, # Per chunk
    OperationType.CORRELATE: 10000,   # Per batch
    OperationType.SYNTHESISE: 12000,  # Per run
}

# Batch sizes for document processing
DOC_CHUNK_BATCH_SIZE = 20  # Process 20 chunks at a time

# Thresholds for auto-queuing
HOT_TIER_MAX_AGE_HOURS = 48  # Sessions older than this need processing
MIN_SESSIONS_FOR_CORRELATION = 3
MIN_INSIGHTS_FOR_SYNTHESIS = 5


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class PendingOperation:
    """An operation awaiting user confirmation."""
    id: int
    operation_type: str
    source_type: Optional[str]
    source_count: int
    estimated_mana: int
    estimated_tokens: int
    queued_at: str
    description: str
    status: str = "pending"
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "operation_type": self.operation_type,
            "source_type": self.source_type,
            "source_count": self.source_count,
            "estimated_mana": self.estimated_mana,
            "estimated_tokens": self.estimated_tokens,
            "queued_at": self.queued_at,
            "description": self.description,
            "status": self.status,
        }


@dataclass
class ProcessingResult:
    """Result of a processing operation."""
    operation_id: int
    operation_type: str
    success: bool
    insights_created: int = 0
    patterns_found: int = 0
    syntheses_generated: int = 0
    mana_spent: int = 0
    tokens_used: int = 0
    error: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return {
            "operation_id": self.operation_id,
            "operation_type": self.operation_type,
            "success": self.success,
            "insights_created": self.insights_created,
            "patterns_found": self.patterns_found,
            "syntheses_generated": self.syntheses_generated,
            "mana_spent": self.mana_spent,
            "tokens_used": self.tokens_used,
            "error": self.error,
        }


# =============================================================================
# SCHEDULER CLASS
# =============================================================================

class RecogScheduler:
    """
    Manages ReCog processing pipeline with user confirmation.
    """
    
    def __init__(self, db_path: Path, config_path: Path = None):
        """
        Initialise scheduler.
        
        Args:
            db_path: Path to ehko_index.db
            config_path: Path to Config directory (for LLM keys)
        """
        self.db_path = db_path
        self.config_path = config_path
        self.config = RecogConfig.for_production()
        self.signal_processor = SignalProcessor()
        
        # LLM provider (lazy init)
        self._llm = None
        self._adapter = None
    
    @property
    def llm(self):
        """Lazy-load LLM provider."""
        if self._llm is None:
            self._llm = create_recog_provider(self.config_path)
        return self._llm
    
    @property
    def adapter(self):
        """Get fresh EhkoForge adapter (thread-safe)."""
        # Always create fresh adapter for thread safety
        return EhkoForgeAdapter(self.db_path, run_migrations_on_init=False)
    
    def get_db(self) -> sqlite3.Connection:
        """Get database connection (thread-safe)."""
        conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn
    
    # =========================================================================
    # TIER 0: AUTOMATIC SIGNAL PROCESSING
    # =========================================================================
    
    def run_tier0_automatic(self) -> Dict[str, int]:
        """
        Run Tier 0 signal processing on unprocessed content.
        This is FREE and runs automatically.
        
        Returns:
            Stats: {"sessions_processed": N, "signals_extracted": N}
        """
        conn = self.get_db()
        cursor = conn.cursor()
        
        stats = {"sessions_processed": 0, "signals_extracted": 0}
        
        # Find sessions not yet processed by Tier 0
        cursor.execute("""
            SELECT fs.id, fs.created_at
            FROM forge_sessions fs
            LEFT JOIN recog_processing_log rpl 
                ON rpl.source_type = 'session' 
                AND rpl.source_id = fs.id 
                AND rpl.tier = 0
            WHERE rpl.id IS NULL
            ORDER BY fs.created_at DESC
            LIMIT 20
        """)
        
        sessions = cursor.fetchall()
        now = datetime.utcnow().isoformat() + "Z"
        
        for session in sessions:
            session_id = session["id"]
            
            # Get session content
            cursor.execute("""
                SELECT role, content FROM forge_messages
                WHERE session_id = ?
                ORDER BY timestamp ASC
            """, (session_id,))
            messages = cursor.fetchall()
            
            if not messages:
                continue
            
            # Combine messages
            content = "\n\n".join(
                f"[{m['role']}]: {m['content']}" for m in messages
            )
            
            # Run signal processing
            doc = Document.create(
                content=content,
                source_type="session",
                source_ref=session_id,
            )
            self.signal_processor.process(doc)
            
            # Log processing
            cursor.execute("""
                INSERT INTO recog_processing_log 
                (source_type, source_id, tier, processed_at, tokens_used, mana_cost, result_summary)
                VALUES (?, ?, 0, ?, 0, 0, ?)
            """, (
                "session",
                session_id,
                now,
                json.dumps(doc.signals) if doc.signals else "{}",
            ))
            
            stats["sessions_processed"] += 1
            stats["signals_extracted"] += len(doc.signals.get("questions", [])) if doc.signals else 0
        
        conn.commit()
        conn.close()
        
        if stats["sessions_processed"] > 0:
            logger.info(f"Tier 0: Processed {stats['sessions_processed']} sessions")
        
        return stats
    
    # =========================================================================
    # QUEUE MANAGEMENT
    # =========================================================================
    
    def check_and_queue(self) -> List[PendingOperation]:
        """
        Check for content needing processing and queue operations.
        
        Returns:
            List of newly queued operations
        """
        # Skip Tier 0 for now - debugging threading
        # self.run_tier0_automatic()
        
        queued = []
        
        # Check for session extraction (Tier 1)
        extract_op = self._check_extraction_needed()
        if extract_op:
            queued.append(extract_op)
        
        # Check for document chunk extraction (Tier 1)
        doc_extract_op = self._check_doc_extraction_needed()
        if doc_extract_op:
            queued.append(doc_extract_op)
        
        # Check for correlation opportunities (Tier 2)
        correlate_op = self._check_correlation_needed()
        if correlate_op:
            queued.append(correlate_op)
        
        # Check for synthesis opportunities (Tier 3)
        synthesise_op = self._check_synthesis_needed()
        if synthesise_op:
            queued.append(synthesise_op)
        
        return queued
    
    def _check_extraction_needed(self) -> Optional[PendingOperation]:
        """Check if Tier 1 extraction should be queued."""
        conn = self.get_db()
        cursor = conn.cursor()
        
        # Find sessions with Tier 0 done but not Tier 1
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM recog_processing_log t0
            LEFT JOIN recog_processing_log t1 
                ON t1.source_type = t0.source_type 
                AND t1.source_id = t0.source_id 
                AND t1.tier = 1
            WHERE t0.tier = 0 
                AND t0.source_type = 'session'
                AND t1.id IS NULL
        """)
        
        result = cursor.fetchone()
        pending_count = result["count"] if result else 0
        
        # Check for existing pending/ready extract OR recent completion
        cursor.execute("""
            SELECT id, status, completed_at FROM recog_queue 
            WHERE operation_type = 'extract' 
            ORDER BY queued_at DESC
            LIMIT 1
        """)
        existing = cursor.fetchone()
        
        conn.close()
        
        # Don't queue if pending/ready exists
        if existing and existing["status"] in ('pending', 'ready', 'processing'):
            return None
        
        # Don't queue if completed within last hour
        if existing and existing["status"] == 'complete' and existing["completed_at"]:
            completed = datetime.fromisoformat(existing["completed_at"].replace("Z", ""))
            hours_since = (datetime.utcnow() - completed).total_seconds() / 3600
            if hours_since < 1:
                return None
        
        if pending_count > 0:
            # Queue extraction
            return self._queue_operation(
                operation_type=OperationType.EXTRACT,
                source_type="session",
                source_ids=[],  # Will be determined at processing time
                source_count=pending_count,
            )
        
        return None
    
    def _check_doc_extraction_needed(self) -> Optional[PendingOperation]:
        """Check if document chunk extraction should be queued."""
        # Get unprocessed chunk count from adapter
        unprocessed_count = self.adapter.get_unprocessed_chunk_count()
        
        if unprocessed_count == 0:
            return None
        
        conn = self.get_db()
        cursor = conn.cursor()
        
        # Check for existing pending/ready extract_docs OR recent completion
        cursor.execute("""
            SELECT id, status, completed_at FROM recog_queue 
            WHERE operation_type = 'extract_docs' 
            ORDER BY queued_at DESC
            LIMIT 1
        """)
        existing = cursor.fetchone()
        
        conn.close()
        
        # Don't queue if pending/ready exists
        if existing and existing["status"] in ('pending', 'ready', 'processing'):
            return None
        
        # Don't queue if completed within last hour
        if existing and existing["status"] == 'complete' and existing["completed_at"]:
            completed = datetime.fromisoformat(existing["completed_at"].replace("Z", ""))
            hours_since = (datetime.utcnow() - completed).total_seconds() / 3600
            if hours_since < 1:
                return None
        
        # Batch size for processing
        batch_count = min(unprocessed_count, DOC_CHUNK_BATCH_SIZE)
        
        return self._queue_operation(
            operation_type=OperationType.EXTRACT_DOCS,
            source_type="document_chunk",
            source_ids=[],
            source_count=batch_count,
        )
    
    def _check_correlation_needed(self) -> Optional[PendingOperation]:
        """Check if Tier 2 correlation should be queued."""
        conn = self.get_db()
        cursor = conn.cursor()
        
        # Count unprocessed insights (have Tier 1 but not Tier 2)
        cursor.execute("""
            SELECT COUNT(*) as count FROM ingots 
            WHERE status IN ('raw', 'refined')
            AND recog_insight_id IS NOT NULL
        """)
        result = cursor.fetchone()
        insight_count = result["count"] if result else 0
        
        # Check for existing pending/ready correlate OR recent completion
        cursor.execute("""
            SELECT id, status, completed_at FROM recog_queue 
            WHERE operation_type = 'correlate' 
            ORDER BY queued_at DESC
            LIMIT 1
        """)
        existing = cursor.fetchone()
        
        conn.close()
        
        # Don't queue if pending/ready exists
        if existing and existing["status"] in ('pending', 'ready', 'processing'):
            return None
        
        # Don't queue if completed within last hour
        if existing and existing["status"] == 'complete' and existing["completed_at"]:
            completed = datetime.fromisoformat(existing["completed_at"].replace("Z", ""))
            hours_since = (datetime.utcnow() - completed).total_seconds() / 3600
            if hours_since < 1:
                return None
        
        if insight_count >= MIN_INSIGHTS_FOR_SYNTHESIS:
            return self._queue_operation(
                operation_type=OperationType.CORRELATE,
                source_type="insights",
                source_ids=[],
                source_count=insight_count,
            )
        
        return None
    
    def _check_synthesis_needed(self) -> Optional[PendingOperation]:
        """Check if Tier 3 synthesis should be queued."""
        conn = self.get_db()
        cursor = conn.cursor()
        
        # Count patterns not yet synthesised
        cursor.execute("""
            SELECT COUNT(*) as count FROM ingot_patterns
        """)
        result = cursor.fetchone()
        pattern_count = result["count"] if result else 0
        
        # Check for existing pending/ready synthesise OR recent completion
        cursor.execute("""
            SELECT id, status, completed_at FROM recog_queue 
            WHERE operation_type = 'synthesise' 
            ORDER BY queued_at DESC
            LIMIT 1
        """)
        existing = cursor.fetchone()
        
        conn.close()
        
        # Don't queue if pending/ready exists
        if existing and existing["status"] in ('pending', 'ready', 'processing'):
            return None
        
        # Don't queue if completed within last hour
        if existing and existing["status"] == 'complete' and existing["completed_at"]:
            completed = datetime.fromisoformat(existing["completed_at"].replace("Z", ""))
            hours_since = (datetime.utcnow() - completed).total_seconds() / 3600
            if hours_since < 1:
                return None
        
        if pattern_count > 0:
            return self._queue_operation(
                operation_type=OperationType.SYNTHESISE,
                source_type="patterns",
                source_ids=[],
                source_count=pattern_count,
            )
        
        return None
    
    def _queue_operation(self, 
                         operation_type: OperationType,
                         source_type: str,
                         source_ids: List[str],
                         source_count: int) -> PendingOperation:
        """Add operation to queue."""
        conn = self.get_db()
        cursor = conn.cursor()
        
        now = datetime.utcnow().isoformat() + "Z"
        
        # Estimate costs
        base_mana = MANA_COSTS.get(operation_type, 5)
        estimated_mana = base_mana * max(1, source_count // 5)  # Scale with volume
        estimated_tokens = TOKEN_ESTIMATES.get(operation_type, 5000) * max(1, source_count // 3)
        
        # Build description
        descriptions = {
            OperationType.EXTRACT: f"Extract insights from {source_count} session(s)",
            OperationType.EXTRACT_DOCS: f"Extract insights from {source_count} document chunk(s)",
            OperationType.CORRELATE: f"Find patterns across {source_count} insight(s)",
            OperationType.SYNTHESISE: f"Synthesise personality from {source_count} pattern(s)",
            OperationType.FULL_SWEEP: f"Full analysis of {source_count} item(s)",
        }
        description = descriptions.get(operation_type, f"Process {source_count} items")
        
        cursor.execute("""
            INSERT INTO recog_queue 
            (operation_type, source_type, source_ids_json, queued_at, status,
             estimated_tokens, estimated_mana, requires_confirmation)
            VALUES (?, ?, ?, ?, 'pending', ?, ?, 1)
        """, (
            operation_type.value,
            source_type,
            json.dumps(source_ids),
            now,
            estimated_tokens,
            estimated_mana,
        ))
        
        op_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        logger.info(f"Queued {operation_type.value}: {description} (est. {estimated_mana} mana)")
        
        return PendingOperation(
            id=op_id,
            operation_type=operation_type.value,
            source_type=source_type,
            source_count=source_count,
            estimated_mana=estimated_mana,
            estimated_tokens=estimated_tokens,
            queued_at=now,
            description=description,
        )
    
    # =========================================================================
    # CONFIRMATION FLOW
    # =========================================================================
    
    def get_pending_confirmations(self) -> List[PendingOperation]:
        """Get operations awaiting user confirmation or ready for processing."""
        conn = self.get_db()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, operation_type, source_type, source_ids_json,
                   estimated_tokens, estimated_mana, queued_at, status
            FROM recog_queue
            WHERE status IN ('pending', 'ready') AND requires_confirmation = 1
            ORDER BY queued_at ASC
        """)
        
        operations = []
        for row in cursor.fetchall():
            source_ids = json.loads(row["source_ids_json"]) if row["source_ids_json"] else []
            
            # Build description
            op_type = row["operation_type"]
            source_count = len(source_ids) if source_ids else self._count_pending_sources(cursor, op_type)
            
            descriptions = {
                "extract": f"Extract insights from {source_count} session(s)",
                "extract_docs": f"Extract insights from {source_count} document chunk(s)",
                "correlate": f"Find patterns across {source_count} insight(s)",
                "synthesise": f"Synthesise personality from {source_count} pattern(s)",
                "full_sweep": f"Full analysis sweep",
            }
            
            operations.append(PendingOperation(
                id=row["id"],
                operation_type=op_type,
                source_type=row["source_type"],
                source_count=source_count,
                estimated_mana=row["estimated_mana"],
                estimated_tokens=row["estimated_tokens"],
                queued_at=row["queued_at"],
                description=descriptions.get(op_type, f"Process {op_type}"),
                status=row["status"],
            ))
        
        conn.close()
        return operations
    
    def _count_pending_sources(self, cursor, op_type: str) -> int:
        """Count sources for an operation type."""
        if op_type == "extract":
            cursor.execute("""
                SELECT COUNT(*) FROM recog_processing_log t0
                LEFT JOIN recog_processing_log t1 
                    ON t1.source_type = t0.source_type 
                    AND t1.source_id = t0.source_id 
                    AND t1.tier = 1
                WHERE t0.tier = 0 AND t1.id IS NULL
            """)
        elif op_type == "extract_docs":
            cursor.execute("SELECT COUNT(*) FROM document_chunks WHERE recog_processed = 0")
        elif op_type == "correlate":
            cursor.execute("SELECT COUNT(*) FROM ingots WHERE status IN ('raw', 'refined')")
        elif op_type == "synthesise":
            cursor.execute("SELECT COUNT(*) FROM ingot_patterns")
        else:
            return 0
        
        result = cursor.fetchone()
        return result[0] if result else 0
    
    def confirm_operation(self, operation_id: int) -> bool:
        """
        User confirms an operation. Marks it ready for processing.
        
        Args:
            operation_id: ID of the queued operation
            
        Returns:
            True if confirmed successfully
        """
        conn = self.get_db()
        cursor = conn.cursor()
        
        now = datetime.utcnow().isoformat() + "Z"
        
        cursor.execute("""
            UPDATE recog_queue
            SET status = 'ready', confirmed_at = ?
            WHERE id = ? AND status = 'pending'
        """, (now, operation_id))
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        if success:
            logger.info(f"Operation {operation_id} confirmed")
        
        return success
    
    def cancel_operation(self, operation_id: int) -> bool:
        """
        User cancels an operation.
        
        Args:
            operation_id: ID of the queued operation
            
        Returns:
            True if cancelled successfully
        """
        conn = self.get_db()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE recog_queue
            SET status = 'cancelled'
            WHERE id = ? AND status = 'pending'
        """, (operation_id,))
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        if success:
            logger.info(f"Operation {operation_id} cancelled")
        
        return success
    
    # =========================================================================
    # PROCESSING
    # =========================================================================
    
    def process_confirmed(self) -> List[ProcessingResult]:
        """
        Process all confirmed (ready) operations.
        
        Returns:
            List of processing results
        """
        conn = self.get_db()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, operation_type, source_type, source_ids_json,
                   estimated_mana
            FROM recog_queue
            WHERE status = 'ready'
            ORDER BY confirmed_at ASC
        """)
        
        operations = cursor.fetchall()
        conn.close()
        
        results = []
        for op in operations:
            result = self._process_operation(dict(op))
            results.append(result)
        
        return results
    
    def _process_operation(self, operation: Dict) -> ProcessingResult:
        """Process a single confirmed operation."""
        op_id = operation["id"]
        op_type = operation["operation_type"]
        
        logger.info(f"Processing operation {op_id}: {op_type}")
        
        # Mark as processing
        conn = self.get_db()
        cursor = conn.cursor()
        now = datetime.utcnow().isoformat() + "Z"
        
        cursor.execute("""
            UPDATE recog_queue SET status = 'processing', started_at = ?
            WHERE id = ?
        """, (now, op_id))
        conn.commit()
        conn.close()
        
        try:
            if op_type == "extract":
                result = self._run_extraction(op_id)
            elif op_type == "extract_docs":
                result = self._run_doc_extraction(op_id)
            elif op_type == "correlate":
                result = self._run_correlation(op_id)
            elif op_type == "synthesise":
                result = self._run_synthesis(op_id)
            elif op_type == "full_sweep":
                result = self._run_full_sweep(op_id)
            else:
                result = ProcessingResult(
                    operation_id=op_id,
                    operation_type=op_type,
                    success=False,
                    error=f"Unknown operation type: {op_type}",
                )
            
            # Mark complete
            self._complete_operation(op_id, result)
            
        except Exception as e:
            logger.error(f"Operation {op_id} failed: {e}")
            result = ProcessingResult(
                operation_id=op_id,
                operation_type=op_type,
                success=False,
                error=str(e),
            )
            self._complete_operation(op_id, result)
        
        return result
    
    def _run_extraction(self, op_id: int) -> ProcessingResult:
        """Run Tier 1 extraction."""
        if not self.llm:
            return ProcessingResult(op_id, "extract", False, error="No LLM configured")
        
        conn = self.get_db()
        cursor = conn.cursor()
        
        # Get sessions needing extraction
        cursor.execute("""
            SELECT t0.source_id
            FROM recog_processing_log t0
            LEFT JOIN recog_processing_log t1 
                ON t1.source_type = t0.source_type 
                AND t1.source_id = t0.source_id 
                AND t1.tier = 1
            WHERE t0.tier = 0 
                AND t0.source_type = 'session'
                AND t1.id IS NULL
            LIMIT 10
        """)
        session_ids = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        if not session_ids:
            return ProcessingResult(op_id, "extract", True, insights_created=0)
        
        # Load documents
        documents = []
        for session_id in session_ids:
            for doc in self.adapter.load_documents(source_type="session", limit=1):
                if doc.source_ref == session_id:
                    documents.append(doc)
                    break
        
        # Extract
        extractor = Extractor(llm=self.llm, config=self.config)
        all_insights = []
        
        for doc in documents:
            insights = extractor.extract(doc)
            for insight in insights:
                self.adapter.save_insight(insight)
                all_insights.append(insight)
            
            # Log Tier 1 processing
            self._log_processing(
                source_type="session",
                source_id=doc.source_ref,
                tier=1,
                result=f"{len(insights)} insights",
            )
        
        return ProcessingResult(
            operation_id=op_id,
            operation_type="extract",
            success=True,
            insights_created=len(all_insights),
            mana_spent=MANA_COSTS[OperationType.EXTRACT] * len(documents),
        )
    
    def _run_doc_extraction(self, op_id: int) -> ProcessingResult:
        """Run Tier 1 extraction on document chunks."""
        if not self.llm:
            return ProcessingResult(op_id, "extract_docs", False, error="No LLM configured")
        
        # Load unprocessed chunks
        documents = list(self.adapter.load_unprocessed_chunks(limit=DOC_CHUNK_BATCH_SIZE))
        
        if not documents:
            return ProcessingResult(op_id, "extract_docs", True, insights_created=0)
        
        logger.info(f"Processing {len(documents)} document chunks")
        
        # Extract insights from each chunk
        extractor = Extractor(llm=self.llm, config=self.config)
        all_insights = []
        
        for doc in documents:
            try:
                # Run Tier 0 signal processing first
                self.signal_processor.process(doc)
                
                # Extract insights (Tier 1)
                insights = extractor.extract(doc)
                
                # Get chunk_id from metadata
                chunk_id = doc.metadata.get("chunk_id")
                
                for insight in insights:
                    # Save insight linked to chunk
                    if chunk_id:
                        self.adapter.save_chunk_insight(chunk_id, insight)
                    else:
                        self.adapter.save_insight(insight)
                    all_insights.append(insight)
                
                # Mark chunk as processed (even if no insights extracted)
                if chunk_id and not insights:
                    self.adapter.mark_chunk_processed(
                        chunk_id,
                        tier0_signals=doc.signals,
                        insight_id=None
                    )
                
                logger.debug(f"Chunk {chunk_id}: {len(insights)} insights")
                
            except Exception as e:
                logger.error(f"Error processing chunk {doc.id}: {e}")
                # Mark as processed anyway to avoid infinite retries
                chunk_id = doc.metadata.get("chunk_id")
                if chunk_id:
                    self.adapter.mark_chunk_processed(chunk_id)
        
        # Log processing
        self._log_processing(
            source_type="document_batch",
            source_id=f"doc_extract_{op_id}",
            tier=1,
            result=f"{len(all_insights)} insights from {len(documents)} chunks",
        )
        
        logger.info(f"Document extraction complete: {len(all_insights)} insights from {len(documents)} chunks")
        
        return ProcessingResult(
            operation_id=op_id,
            operation_type="extract_docs",
            success=True,
            insights_created=len(all_insights),
            mana_spent=MANA_COSTS[OperationType.EXTRACT_DOCS] * len(documents),
        )
    
    def _run_correlation(self, op_id: int) -> ProcessingResult:
        """Run Tier 2 correlation."""
        if not self.llm:
            return ProcessingResult(op_id, "correlate", False, error="No LLM configured")
        
        # Get insights
        adapter = self.adapter  # Cache single adapter for consistency
        insights = list(adapter.get_insights(limit=50))
        
        if len(insights) < 2:
            return ProcessingResult(op_id, "correlate", True, patterns_found=0)
        
        logger.info(f"Correlating {len(insights)} insights")
        
        # Correlate
        correlator = Correlator(llm=self.llm, config=self.config)
        patterns, stats = correlator.correlate(insights)
        
        logger.info(f"Correlation found {len(patterns)} patterns: {stats}")
        
        # Save patterns using same adapter
        for i, pattern in enumerate(patterns):
            logger.debug(f"Saving pattern {i+1}/{len(patterns)}: {pattern.id[:8]} - {pattern.summary[:50]}")
            adapter.save_pattern(pattern)
        
        # Log
        self._log_processing(
            source_type="batch",
            source_id=f"correlation_{op_id}",
            tier=2,
            result=f"{len(patterns)} patterns from {len(insights)} insights",
        )
        
        return ProcessingResult(
            operation_id=op_id,
            operation_type="correlate",
            success=True,
            patterns_found=len(patterns),
            mana_spent=MANA_COSTS[OperationType.CORRELATE],
        )
    
    def _run_synthesis(self, op_id: int) -> ProcessingResult:
        """Run Tier 3 synthesis."""
        if not self.llm:
            return ProcessingResult(op_id, "synthesise", False, error="No LLM configured")
        
        # Get patterns and insights
        patterns = list(self.adapter.get_patterns())
        insights = list(self.adapter.get_insights(limit=100))
        
        if not patterns:
            return ProcessingResult(op_id, "synthesise", True, syntheses_generated=0)
        
        # Synthesise
        synthesizer = Synthesizer(llm=self.llm, config=self.config)
        syntheses, stats = synthesizer.synthesise(patterns, insights)
        
        for synth in syntheses:
            self.adapter.save_synthesis(synth)
        
        # Log
        self._log_processing(
            source_type="batch",
            source_id=f"synthesis_{op_id}",
            tier=3,
            result=f"{len(syntheses)} syntheses from {len(patterns)} patterns",
        )
        
        # Create report
        self._create_report(syntheses, patterns, insights)
        
        return ProcessingResult(
            operation_id=op_id,
            operation_type="synthesise",
            success=True,
            syntheses_generated=len(syntheses),
            mana_spent=MANA_COSTS[OperationType.SYNTHESISE],
        )
    
    def _run_full_sweep(self, op_id: int) -> ProcessingResult:
        """Run full pipeline (Tier 1-3)."""
        # Run each tier in sequence
        extract_result = self._run_extraction(op_id)
        correlate_result = self._run_correlation(op_id)
        synth_result = self._run_synthesis(op_id)
        
        return ProcessingResult(
            operation_id=op_id,
            operation_type="full_sweep",
            success=all([
                extract_result.success,
                correlate_result.success,
                synth_result.success,
            ]),
            insights_created=extract_result.insights_created,
            patterns_found=correlate_result.patterns_found,
            syntheses_generated=synth_result.syntheses_generated,
            mana_spent=MANA_COSTS[OperationType.FULL_SWEEP],
        )
    
    def _log_processing(self, source_type: str, source_id: str, tier: int, result: str):
        """Log a processing event."""
        conn = self.get_db()
        cursor = conn.cursor()
        now = datetime.utcnow().isoformat() + "Z"
        
        cursor.execute("""
            INSERT OR REPLACE INTO recog_processing_log
            (source_type, source_id, tier, processed_at, result_summary)
            VALUES (?, ?, ?, ?, ?)
        """, (source_type, source_id, tier, now, result))
        
        conn.commit()
        conn.close()
    
    def _complete_operation(self, op_id: int, result: ProcessingResult):
        """Mark operation as complete."""
        conn = self.get_db()
        cursor = conn.cursor()
        now = datetime.utcnow().isoformat() + "Z"
        
        status = "complete" if result.success else "failed"
        
        cursor.execute("""
            UPDATE recog_queue
            SET status = ?, completed_at = ?, actual_mana = ?, 
                result_summary = ?, error = ?
            WHERE id = ?
        """, (
            status,
            now,
            result.mana_spent,
            f"Created: {result.insights_created}i/{result.patterns_found}p/{result.syntheses_generated}s",
            result.error,
            op_id,
        ))
        
        conn.commit()
        conn.close()
    
    def _create_report(self, syntheses, patterns, insights):
        """Create a ReCog report snapshot."""
        conn = self.get_db()
        cursor = conn.cursor()
        now = datetime.utcnow().isoformat() + "Z"
        
        # Build conclusions - distinguish between full syntheses and emerging themes
        conclusions = []
        emerging_count = 0
        for synth in syntheses:
            is_emerging = synth.metadata.get("emerging", False)
            if is_emerging:
                emerging_count += 1
            conclusions.append({
                "type": synth.synthesis_type.value,
                "summary": synth.summary,
                "significance": synth.significance,
                "emerging": is_emerging,
            })
        
        # Generate appropriate summary
        if emerging_count == len(syntheses) and emerging_count > 0:
            summary = f"Identified {emerging_count} emerging themes from {len(patterns)} patterns and {len(insights)} insights. More data needed for full personality synthesis."
        elif emerging_count > 0:
            full_count = len(syntheses) - emerging_count
            summary = f"Synthesised {full_count} personality components plus {emerging_count} emerging themes from {len(patterns)} patterns and {len(insights)} insights."
        else:
            summary = f"Synthesised {len(syntheses)} personality components from {len(patterns)} patterns and {len(insights)} insights."
        
        cursor.execute("""
            INSERT INTO recog_reports
            (report_type, created_at, summary, insights_count, patterns_count, syntheses_count,
             conclusions_json, status)
            VALUES ('synthesis', ?, ?, ?, ?, ?, ?, 'current')
        """, (
            now,
            summary,
            len(insights),
            len(patterns),
            len(syntheses),
            json.dumps(conclusions),
        ))
        
        # Supersede previous current reports
        report_id = cursor.lastrowid
        cursor.execute("""
            UPDATE recog_reports
            SET status = 'superseded', superseded_by = ?
            WHERE status = 'current' AND id != ?
        """, (report_id, report_id))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Created ReCog report #{report_id}")
    
    # =========================================================================
    # STATUS
    # =========================================================================
    
    def get_status(self) -> Dict[str, Any]:
        """Get current scheduler status."""
        conn = self.get_db()
        cursor = conn.cursor()
        
        # Queue status
        cursor.execute("""
            SELECT status, COUNT(*) as count
            FROM recog_queue
            GROUP BY status
        """)
        queue_status = {row["status"]: row["count"] for row in cursor.fetchall()}
        
        # Last processing times
        cursor.execute("""
            SELECT tier, MAX(processed_at) as last
            FROM recog_processing_log
            GROUP BY tier
        """)
        last_processed = {f"tier_{row['tier']}": row["last"] for row in cursor.fetchall()}
        
        # Content counts
        cursor.execute("SELECT COUNT(*) FROM forge_sessions WHERE memory_tier = 'hot'")
        hot_sessions = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM ingots WHERE status IN ('raw', 'refined')")
        pending_insights = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM ingot_patterns")
        patterns = cursor.fetchone()[0]
        
        # Document ingestion counts
        try:
            cursor.execute("SELECT COUNT(*) FROM document_chunks WHERE recog_processed = 0")
            unprocessed_chunks = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM ingested_documents")
            ingested_docs = cursor.fetchone()[0]
        except:
            unprocessed_chunks = 0
            ingested_docs = 0
        
        # Current report
        cursor.execute("""
            SELECT id, created_at, summary
            FROM recog_reports
            WHERE status = 'current'
            ORDER BY created_at DESC
            LIMIT 1
        """)
        current_report = cursor.fetchone()
        
        conn.close()
        
        return {
            "queue": queue_status,
            "last_processed": last_processed,
            "hot_sessions": hot_sessions,
            "pending_insights": pending_insights,
            "patterns": patterns,
            "ingested_documents": ingested_docs,
            "unprocessed_chunks": unprocessed_chunks,
            "current_report": dict(current_report) if current_report else None,
            "llm_available": self.llm is not None,
        }


# =============================================================================
# MODULE EXPORTS
# =============================================================================

__all__ = [
    "RecogScheduler",
    "PendingOperation",
    "ProcessingResult",
    "OperationType",
    "MANA_COSTS",
    "DOC_CHUNK_BATCH_SIZE",
]
