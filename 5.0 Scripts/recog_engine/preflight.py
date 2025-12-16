"""
Preflight Session Manager v0.1

Orchestrates the preflight context system:
- Creates preflight sessions for batch processing
- Runs Tier 0 scans on content
- Collects entity questions
- Estimates costs
- Manages the review workflow

Copyright (c) 2025 Brent
Licensed under AGPLv3
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

from .tier0 import Tier0Processor, preprocess_text
from .entity_registry import (
    register_entities_from_tier0,
    resolve_entities_for_prompt,
    get_unknown_entities,
    get_entity_stats,
)

# Database path
DB_PATH = Path(__file__).parent.parent.parent / "_data" / "ehko_index.db"

# Cost estimation (cents per 1K tokens)
COST_PER_1K_INPUT = 0.015   # gpt-4o-mini input
COST_PER_1K_OUTPUT = 0.060  # gpt-4o-mini output
OVERHEAD_MULTIPLIER = 1.5   # Account for prompts, retries


# =============================================================================
# PREFLIGHT SESSION MANAGEMENT
# =============================================================================

def get_connection():
    """Get database connection."""
    return sqlite3.connect(str(DB_PATH))


def create_preflight_session(
    session_type: str,
    source_files: List[str] = None,
) -> int:
    """
    Create a new preflight session.
    
    Args:
        session_type: 'single_file', 'batch', 'chatgpt_import', etc.
        source_files: List of file paths being processed
        
    Returns:
        session_id
    """
    now = datetime.utcnow().isoformat() + "Z"
    
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO preflight_sessions (
                session_type, status, source_files_json, source_count,
                created_at, updated_at
            ) VALUES (?, 'pending', ?, ?, ?, ?)
        """, (
            session_type,
            json.dumps(source_files or []),
            len(source_files or []),
            now, now
        ))
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def get_preflight_session(session_id: int) -> Optional[Dict]:
    """Get a preflight session by ID."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT id, session_type, status, source_files_json, source_count,
                   total_word_count, total_entities_found, unknown_entities_count,
                   estimated_tokens, estimated_cost_cents, filters_json,
                   items_after_filter, entity_questions_json, entity_answers_json,
                   started_at, completed_at, recog_operations_created,
                   created_at, updated_at
            FROM preflight_sessions
            WHERE id = ?
        """, (session_id,))
        row = cursor.fetchone()
        if row:
            return {
                'id': row[0],
                'session_type': row[1],
                'status': row[2],
                'source_files': json.loads(row[3]) if row[3] else [],
                'source_count': row[4],
                'total_word_count': row[5],
                'total_entities_found': row[6],
                'unknown_entities_count': row[7],
                'estimated_tokens': row[8],
                'estimated_cost_cents': row[9],
                'filters': json.loads(row[10]) if row[10] else {},
                'items_after_filter': row[11],
                'entity_questions': json.loads(row[12]) if row[12] else [],
                'entity_answers': json.loads(row[13]) if row[13] else {},
                'started_at': row[14],
                'completed_at': row[15],
                'recog_operations_created': row[16],
                'created_at': row[17],
                'updated_at': row[18],
            }
        return None
    finally:
        conn.close()


def update_preflight_session(session_id: int, **kwargs) -> bool:
    """Update preflight session fields."""
    now = datetime.utcnow().isoformat() + "Z"
    
    # Map complex types to JSON
    json_fields = ['filters', 'entity_questions', 'entity_answers', 'source_files']
    
    updates = []
    values = []
    
    for key, value in kwargs.items():
        db_key = key
        if key in json_fields:
            db_key = f"{key}_json" if not key.endswith('_json') else key
            value = json.dumps(value)
        updates.append(f"{db_key} = ?")
        values.append(value)
    
    updates.append("updated_at = ?")
    values.append(now)
    values.append(session_id)
    
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(f"""
            UPDATE preflight_sessions
            SET {', '.join(updates)}
            WHERE id = ?
        """, values)
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()


# =============================================================================
# PREFLIGHT ITEMS (Individual content pieces in a session)
# =============================================================================

def add_preflight_item(
    preflight_session_id: int,
    source_type: str,
    source_id: str = None,
    title: str = None,
    content: str = None,
) -> int:
    """
    Add an item to a preflight session and run Tier 0 scan.
    
    Returns:
        item_id
    """
    now = datetime.utcnow().isoformat() + "Z"
    
    # Run Tier 0 scan if content provided
    pre_annotation = {}
    entities_found = {}
    word_count = 0
    
    if content:
        pre_annotation = preprocess_text(content)
        word_count = pre_annotation.get('word_count', 0)
        entities_found = pre_annotation.get('entities', {})
        
        # Register entities
        register_entities_from_tier0(
            entities_found,
            source_type=source_type,
            source_id=source_id,
        )
    
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO preflight_items (
                preflight_session_id, source_type, source_id, title,
                word_count, pre_annotation_json, entities_found_json,
                content, included, processed, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1, 0, ?)
        """, (
            preflight_session_id, source_type, source_id, title,
            word_count, json.dumps(pre_annotation), json.dumps(entities_found),
            content, now
        ))
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def get_preflight_items(
    preflight_session_id: int,
    included_only: bool = False,
) -> List[Dict]:
    """Get all items in a preflight session."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        conditions = ["preflight_session_id = ?"]
        values = [preflight_session_id]
        
        if included_only:
            conditions.append("included = 1")
        
        cursor.execute(f"""
            SELECT id, source_type, source_id, title, word_count, message_count,
                   date_range_start, date_range_end, pre_annotation_json,
                   entities_found_json, included, exclusion_reason, processed
            FROM preflight_items
            WHERE {' AND '.join(conditions)}
            ORDER BY id
        """, values)
        
        return [{
            'id': row[0],
            'source_type': row[1],
            'source_id': row[2],
            'title': row[3],
            'word_count': row[4],
            'message_count': row[5],
            'date_range_start': row[6],
            'date_range_end': row[7],
            'pre_annotation': json.loads(row[8]) if row[8] else {},
            'entities_found': json.loads(row[9]) if row[9] else {},
            'included': bool(row[10]),
            'exclusion_reason': row[11],
            'processed': bool(row[12]),
        } for row in cursor.fetchall()]
    finally:
        conn.close()


def exclude_preflight_item(item_id: int, reason: str = 'manual') -> bool:
    """Exclude an item from processing."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE preflight_items
            SET included = 0, exclusion_reason = ?
            WHERE id = ?
        """, (reason, item_id))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()


def include_preflight_item(item_id: int) -> bool:
    """Re-include an excluded item."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE preflight_items
            SET included = 1, exclusion_reason = NULL
            WHERE id = ?
        """, (item_id,))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()


# =============================================================================
# PREFLIGHT SCANNING & ANALYSIS
# =============================================================================

def scan_preflight_session(session_id: int) -> Dict:
    """
    Analyse a preflight session after all items are added.
    
    Returns summary with:
    - Total word count
    - Entity counts
    - Unknown entities needing review
    - Cost estimate
    - Questions for user
    """
    items = get_preflight_items(session_id, included_only=True)
    
    total_words = sum(item.get('word_count', 0) for item in items)
    
    # Aggregate entities
    all_phones = []
    all_emails = []
    all_people = []
    
    for item in items:
        entities = item.get('entities_found', {})
        all_phones.extend(entities.get('phone_numbers', []))
        all_emails.extend(entities.get('email_addresses', []))
        all_people.extend(entities.get('people', []))
    
    # Dedupe
    unique_phones = list({p.get('normalised', p.get('raw', '')): p for p in all_phones}.values())
    unique_emails = list({e.get('normalised', e.get('raw', '')): e for e in all_emails}.values())
    unique_people = list(set(all_people))
    
    total_entities = len(unique_phones) + len(unique_emails) + len(unique_people)
    
    # Get unknown entities from registry
    unknown = get_unknown_entities(limit=100)
    unknown_count = len(unknown)
    
    # Estimate tokens and cost
    # Rough: 1 word ≈ 1.3 tokens, plus prompt overhead
    estimated_tokens = int(total_words * 1.3 * OVERHEAD_MULTIPLIER)
    estimated_cost_cents = int(
        (estimated_tokens / 1000) * (COST_PER_1K_INPUT + COST_PER_1K_OUTPUT)
    )
    
    # Build questions for unknown entities
    questions = []
    for entity in unknown[:20]:  # Cap at 20 questions
        if entity.get('entity_type') == 'phone':
            questions.append({
                'entity_id': entity['id'],
                'type': 'phone',
                'value': entity['raw_value'],
                'question': f"Who is {entity['raw_value']}?",
                'options': ['Skip', 'Enter name...'],
            })
        elif entity.get('entity_type') == 'email':
            questions.append({
                'entity_id': entity['id'],
                'type': 'email',
                'value': entity['raw_value'],
                'question': f"Who is {entity['raw_value']}?",
                'options': ['Skip', 'Enter name...'],
            })
    
    # Update session
    update_preflight_session(
        session_id,
        status='scanned',
        total_word_count=total_words,
        total_entities_found=total_entities,
        unknown_entities_count=unknown_count,
        estimated_tokens=estimated_tokens,
        estimated_cost_cents=estimated_cost_cents,
        items_after_filter=len(items),
        entity_questions=questions,
    )
    
    return {
        'session_id': session_id,
        'status': 'scanned',
        'item_count': len(items),
        'total_words': total_words,
        'total_entities': total_entities,
        'unknown_entities': unknown_count,
        'estimated_tokens': estimated_tokens,
        'estimated_cost_cents': estimated_cost_cents,
        'estimated_cost_dollars': estimated_cost_cents / 100,
        'questions': questions,
        'entities': {
            'phones': len(unique_phones),
            'emails': len(unique_emails),
            'people': len(unique_people),
        },
    }


def get_preflight_summary(session_id: int) -> Dict:
    """Get a summary of a preflight session for display."""
    session = get_preflight_session(session_id)
    if not session:
        return {'error': 'Session not found'}
    
    items = get_preflight_items(session_id)
    included = [i for i in items if i['included']]
    
    return {
        'session_id': session_id,
        'session_type': session['session_type'],
        'status': session['status'],
        'source_count': session['source_count'],
        'items': {
            'total': len(items),
            'included': len(included),
            'excluded': len(items) - len(included),
        },
        'total_words': session['total_word_count'],
        'total_entities': session['total_entities_found'],
        'unknown_entities': session['unknown_entities_count'],
        'estimated_tokens': session['estimated_tokens'],
        'estimated_cost_cents': session['estimated_cost_cents'],
        'estimated_cost_dollars': (session['estimated_cost_cents'] or 0) / 100,
        'questions_pending': len(session.get('entity_questions', [])),
        'created_at': session['created_at'],
    }


# =============================================================================
# FILTERING
# =============================================================================

def apply_filters(
    session_id: int,
    min_words: int = None,
    min_messages: int = None,
    date_after: str = None,
    date_before: str = None,
    keywords: List[str] = None,
) -> Dict:
    """
    Apply filters to preflight items.
    Items not matching filters are excluded.
    
    Returns:
        Summary of filtering results
    """
    items = get_preflight_items(session_id)
    
    excluded_count = 0
    filters_applied = {}
    
    for item in items:
        exclude = False
        reason = None
        
        # Word count filter
        if min_words and item.get('word_count', 0) < min_words:
            exclude = True
            reason = f'words < {min_words}'
            filters_applied['min_words'] = min_words
        
        # Message count filter
        if min_messages and item.get('message_count', 0) < min_messages:
            exclude = True
            reason = f'messages < {min_messages}'
            filters_applied['min_messages'] = min_messages
        
        # Date filters
        if date_after and item.get('date_range_end'):
            if item['date_range_end'] < date_after:
                exclude = True
                reason = f'before {date_after}'
                filters_applied['date_after'] = date_after
        
        if date_before and item.get('date_range_start'):
            if item['date_range_start'] > date_before:
                exclude = True
                reason = f'after {date_before}'
                filters_applied['date_before'] = date_before
        
        # Keyword filter (include only if ANY keyword matches)
        if keywords:
            pre_annotation = item.get('pre_annotation', {})
            title = (item.get('title') or '').lower()
            # Check if any keyword appears in title or emotion keywords
            emotion_kws = pre_annotation.get('emotion_signals', {}).get('keywords_found', [])
            all_text = title + ' ' + ' '.join(emotion_kws)
            
            if not any(kw.lower() in all_text for kw in keywords):
                exclude = True
                reason = 'no keyword match'
                filters_applied['keywords'] = keywords
        
        if exclude and item['included']:
            exclude_preflight_item(item['id'], reason)
            excluded_count += 1
    
    # Update session with filters
    update_preflight_session(session_id, filters=filters_applied)
    
    # Rescan to update counts
    return scan_preflight_session(session_id)


# =============================================================================
# MODULE EXPORTS
# =============================================================================

__all__ = [
    'create_preflight_session',
    'get_preflight_session',
    'update_preflight_session',
    'add_preflight_item',
    'get_preflight_items',
    'exclude_preflight_item',
    'include_preflight_item',
    'scan_preflight_session',
    'get_preflight_summary',
    'apply_filters',
    'confirm_preflight_session',
]


# =============================================================================
# CONFIRMATION & PROCESSING
# =============================================================================

def confirm_preflight_session(session_id: int) -> Dict:
    """
    Confirm a preflight session and create ReCog operations.
    
    This transfers included items to the document_chunks table
    and queues them for ReCog processing.
    
    Returns:
        dict with document_id, chunks_created, status
    """
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Get session info
    cursor.execute("""
        SELECT id, session_type, source_files_json, status
        FROM preflight_sessions WHERE id = ?
    """, (session_id,))
    session = cursor.fetchone()
    
    if not session:
        conn.close()
        return {'success': False, 'error': 'Session not found'}
    
    if session['status'] not in ('scanned', 'reviewing'):
        conn.close()
        return {'success': False, 'error': f'Session not ready: {session["status"]}'}
    
    # Get included items WITH content
    cursor.execute("""
        SELECT id, source_type, source_id, title, word_count,
               pre_annotation_json, entities_found_json, content
        FROM preflight_items
        WHERE preflight_session_id = ? AND included = 1
    """, (session_id,))
    items = cursor.fetchall()
    
    if not items:
        conn.close()
        return {'success': False, 'error': 'No items to process'}
    
    now = datetime.utcnow().isoformat() + 'Z'
    source_files = json.loads(session['source_files_json']) if session['source_files_json'] else []
    filename = source_files[0] if source_files else f'preflight_{session_id}'
    
    # Create ingested_document entry
    cursor.execute("""
        INSERT INTO ingested_documents (
            filename, file_type, source_path, total_chunks, 
            status, ingested_at, doc_subject, metadata
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        filename,
        session['session_type'],
        f'preflight:{session_id}',
        len(items),
        'processing',
        now,
        f'Preflight Import - {session["session_type"]}',
        json.dumps({'preflight_session_id': session_id})
    ))
    document_id = cursor.lastrowid
    
    # Create document_chunks for each item
    chunks_created = 0
    for idx, item in enumerate(items):
        # Get content - stored in preflight_items
        content = item['content'] or ''
        
        # Fallback to title if no content
        if not content:
            pre_annotation = json.loads(item['pre_annotation_json']) if item['pre_annotation_json'] else {}
            content = pre_annotation.get('summary', item['title'] or '')
        
        # Estimate tokens (rough: 1 word = 1.3 tokens)
        token_count = int(item['word_count'] * 1.3) if item['word_count'] else 100
        
        cursor.execute("""
            INSERT INTO document_chunks (
                document_id, chunk_index, content, token_count,
                recog_processed, tier0_signals, metadata
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            document_id,
            idx,
            content,
            token_count,
            0,  # Not processed by Tier 1 yet
            item['pre_annotation_json'],  # Tier 0 already done
            json.dumps({
                'preflight_item_id': item['id'],
                'original_source_type': item['source_type'],
                'original_source_id': item['source_id'],
                'title': item['title'],
            })
        ))
        chunk_id = cursor.lastrowid
        
        # Link preflight item to chunk
        cursor.execute("""
            UPDATE preflight_items 
            SET processed = 1, recog_operation_id = ?
            WHERE id = ?
        """, (chunk_id, item['id']))
        
        chunks_created += 1
    
    # Update session status
    cursor.execute("""
        UPDATE preflight_sessions
        SET status = 'processing', recog_operations_created = ?
        WHERE id = ?
    """, (chunks_created, session_id))
    
    # Queue a ReCog operation for document extraction
    cursor.execute("""
        INSERT INTO recog_queue (
            operation_type, source_type, source_ids_json, queued_at, status,
            estimated_tokens, estimated_mana, requires_confirmation
        ) VALUES (?, ?, ?, ?, 'ready', ?, ?, 0)
    """, (
        'extract_docs',
        'document_chunk',
        json.dumps([document_id]),
        now,
        sum(int(i['word_count'] * 1.3) for i in items if i['word_count']),
        len(items),  # 1 mana per item
    ))
    operation_id = cursor.lastrowid
    
    conn.commit()
    conn.close()
    
    return {
        'success': True,
        'document_id': document_id,
        'chunks_created': chunks_created,
        'operation_id': operation_id,
        'status': 'queued'
    }
