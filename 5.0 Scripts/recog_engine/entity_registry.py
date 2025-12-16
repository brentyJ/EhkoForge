"""
Entity Registry Manager v0.1

Manages the entity registry for preflight context system.
Stores and retrieves known entities (people, phones, emails) with user-provided context.

Copyright (c) 2025 Brent
Licensed under AGPLv3
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

# Database path
DB_PATH = Path(__file__).parent.parent.parent / "_data" / "ehko_index.db"


# =============================================================================
# ENTITY REGISTRY CRUD
# =============================================================================

def get_connection():
    """Get database connection."""
    return sqlite3.connect(str(DB_PATH))


def normalise_phone(raw: str) -> str:
    """Normalise phone number for matching."""
    import re
    # Remove all non-digit chars except leading +
    normalised = re.sub(r'[^\d+]', '', raw)
    # Ensure + is only at start
    if '+' in normalised[1:]:
        normalised = normalised[0] + normalised[1:].replace('+', '')
    return normalised


def normalise_email(raw: str) -> str:
    """Normalise email for matching."""
    return raw.lower().strip()


def get_entity(entity_type: str, normalised_value: str) -> Optional[Dict]:
    """Get an entity by type and normalised value."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT id, entity_type, raw_value, normalised_value, display_name,
                   relationship, notes, anonymise_in_prompts, placeholder_name,
                   first_seen_at, last_seen_at, occurrence_count, source_types,
                   confirmed, merged_into_id, created_at, updated_at
            FROM entity_registry
            WHERE entity_type = ? AND normalised_value = ? AND merged_into_id IS NULL
        """, (entity_type, normalised_value))
        row = cursor.fetchone()
        if row:
            return {
                'id': row[0],
                'entity_type': row[1],
                'raw_value': row[2],
                'normalised_value': row[3],
                'display_name': row[4],
                'relationship': row[5],
                'notes': row[6],
                'anonymise_in_prompts': bool(row[7]),
                'placeholder_name': row[8],
                'first_seen_at': row[9],
                'last_seen_at': row[10],
                'occurrence_count': row[11],
                'source_types': json.loads(row[12]) if row[12] else [],
                'confirmed': bool(row[13]),
                'merged_into_id': row[14],
                'created_at': row[15],
                'updated_at': row[16],
            }
        return None
    finally:
        conn.close()


def get_entity_by_id(entity_id: int) -> Optional[Dict]:
    """Get an entity by ID."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT id, entity_type, raw_value, normalised_value, display_name,
                   relationship, notes, anonymise_in_prompts, placeholder_name,
                   first_seen_at, last_seen_at, occurrence_count, source_types,
                   confirmed, merged_into_id, created_at, updated_at
            FROM entity_registry
            WHERE id = ?
        """, (entity_id,))
        row = cursor.fetchone()
        if row:
            return {
                'id': row[0],
                'entity_type': row[1],
                'raw_value': row[2],
                'normalised_value': row[3],
                'display_name': row[4],
                'relationship': row[5],
                'notes': row[6],
                'anonymise_in_prompts': bool(row[7]),
                'placeholder_name': row[8],
                'first_seen_at': row[9],
                'last_seen_at': row[10],
                'occurrence_count': row[11],
                'source_types': json.loads(row[12]) if row[12] else [],
                'confirmed': bool(row[13]),
                'merged_into_id': row[14],
                'created_at': row[15],
                'updated_at': row[16],
            }
        return None
    finally:
        conn.close()


def register_entity(
    entity_type: str,
    raw_value: str,
    normalised_value: str = None,
    display_name: str = None,
    relationship: str = None,
    source_type: str = None,
) -> Tuple[int, bool]:
    """
    Register an entity. Creates new or updates existing.
    
    Returns: (entity_id, is_new)
    """
    now = datetime.utcnow().isoformat() + "Z"
    
    # Normalise if not provided
    if normalised_value is None:
        if entity_type == 'phone':
            normalised_value = normalise_phone(raw_value)
        elif entity_type == 'email':
            normalised_value = normalise_email(raw_value)
        else:
            normalised_value = raw_value.strip()
    
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Check if exists
        cursor.execute("""
            SELECT id, occurrence_count, source_types 
            FROM entity_registry 
            WHERE entity_type = ? AND normalised_value = ? AND merged_into_id IS NULL
        """, (entity_type, normalised_value))
        existing = cursor.fetchone()
        
        if existing:
            # Update existing
            entity_id = existing[0]
            occurrence_count = existing[1] + 1
            source_types = json.loads(existing[2]) if existing[2] else []
            
            if source_type and source_type not in source_types:
                source_types.append(source_type)
            
            cursor.execute("""
                UPDATE entity_registry
                SET last_seen_at = ?, occurrence_count = ?, source_types = ?, updated_at = ?
                WHERE id = ?
            """, (now, occurrence_count, json.dumps(source_types), now, entity_id))
            
            conn.commit()
            return (entity_id, False)
        else:
            # Create new
            source_types = [source_type] if source_type else []
            
            cursor.execute("""
                INSERT INTO entity_registry (
                    entity_type, raw_value, normalised_value, display_name, relationship,
                    first_seen_at, last_seen_at, occurrence_count, source_types,
                    confirmed, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, 1, ?, 0, ?, ?)
            """, (
                entity_type, raw_value, normalised_value, display_name, relationship,
                now, now, json.dumps(source_types), now, now
            ))
            
            conn.commit()
            return (cursor.lastrowid, True)
    finally:
        conn.close()


def update_entity(
    entity_id: int,
    display_name: str = None,
    relationship: str = None,
    notes: str = None,
    anonymise_in_prompts: bool = None,
    placeholder_name: str = None,
    confirmed: bool = None,
) -> bool:
    """Update entity with user-provided context."""
    now = datetime.utcnow().isoformat() + "Z"
    
    updates = []
    values = []
    
    if display_name is not None:
        updates.append("display_name = ?")
        values.append(display_name)
    if relationship is not None:
        updates.append("relationship = ?")
        values.append(relationship)
    if notes is not None:
        updates.append("notes = ?")
        values.append(notes)
    if anonymise_in_prompts is not None:
        updates.append("anonymise_in_prompts = ?")
        values.append(1 if anonymise_in_prompts else 0)
    if placeholder_name is not None:
        updates.append("placeholder_name = ?")
        values.append(placeholder_name)
    if confirmed is not None:
        updates.append("confirmed = ?")
        values.append(1 if confirmed else 0)
    
    if not updates:
        return False
    
    updates.append("updated_at = ?")
    values.append(now)
    values.append(entity_id)
    
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(f"""
            UPDATE entity_registry
            SET {', '.join(updates)}
            WHERE id = ?
        """, values)
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()


def list_entities(
    entity_type: str = None,
    confirmed_only: bool = False,
    unconfirmed_only: bool = False,
    limit: int = 100,
) -> List[Dict]:
    """List entities with optional filtering."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        conditions = ["merged_into_id IS NULL"]
        values = []
        
        if entity_type:
            conditions.append("entity_type = ?")
            values.append(entity_type)
        if confirmed_only:
            conditions.append("confirmed = 1")
        if unconfirmed_only:
            conditions.append("confirmed = 0")
        
        values.append(limit)
        
        cursor.execute(f"""
            SELECT id, entity_type, raw_value, normalised_value, display_name,
                   relationship, occurrence_count, confirmed
            FROM entity_registry
            WHERE {' AND '.join(conditions)}
            ORDER BY occurrence_count DESC, last_seen_at DESC
            LIMIT ?
        """, values)
        
        return [{
            'id': row[0],
            'entity_type': row[1],
            'raw_value': row[2],
            'normalised_value': row[3],
            'display_name': row[4],
            'relationship': row[5],
            'occurrence_count': row[6],
            'confirmed': bool(row[7]),
        } for row in cursor.fetchall()]
    finally:
        conn.close()


def get_unknown_entities(limit: int = 50) -> List[Dict]:
    """Get entities that need user identification."""
    return list_entities(unconfirmed_only=True, limit=limit)


# =============================================================================
# BULK OPERATIONS
# =============================================================================

def register_entities_from_tier0(
    tier0_entities: Dict,
    source_type: str,
    source_id: str = None,
) -> Dict[str, List[Tuple[int, bool]]]:
    """
    Register all entities from Tier 0 extraction.
    
    Args:
        tier0_entities: The 'entities' dict from Tier 0 preprocess_text()
        source_type: Type of source (e.g., 'chat_session', 'document')
        source_id: Optional ID of source
        
    Returns:
        Dict mapping entity_type to list of (entity_id, is_new) tuples
    """
    results = {
        'phone': [],
        'email': [],
        'person': [],
    }
    
    # Phone numbers
    for phone in tier0_entities.get('phone_numbers', []):
        entity_id, is_new = register_entity(
            entity_type='phone',
            raw_value=phone.get('raw', ''),
            normalised_value=phone.get('normalised'),
            source_type=source_type,
        )
        results['phone'].append((entity_id, is_new))
    
    # Email addresses
    for email in tier0_entities.get('email_addresses', []):
        entity_id, is_new = register_entity(
            entity_type='email',
            raw_value=email.get('raw', ''),
            normalised_value=email.get('normalised'),
            source_type=source_type,
        )
        results['email'].append((entity_id, is_new))
    
    # People (from name detection)
    for person in tier0_entities.get('people', []):
        entity_id, is_new = register_entity(
            entity_type='person',
            raw_value=person,
            source_type=source_type,
        )
        results['person'].append((entity_id, is_new))
    
    return results


# =============================================================================
# ENTITY RESOLUTION FOR PROMPTS
# =============================================================================

def resolve_entities_for_prompt(tier0_entities: Dict) -> Dict:
    """
    Resolve entities against registry and return enriched data.
    
    For known entities:
    - If anonymise_in_prompts=True: use placeholder_name
    - Else: use display_name or raw_value
    
    For unknown entities:
    - Flag for user review
    - Use raw value with [UNKNOWN] marker
    
    Returns dict with:
    - resolved: List of resolved entity dicts
    - unknown: List of unknown entity dicts needing review
    - prompt_context: Formatted string for LLM prompts
    """
    resolved = []
    unknown = []
    context_parts = []
    
    # Process phone numbers
    for phone in tier0_entities.get('phone_numbers', []):
        normalised = phone.get('normalised', normalise_phone(phone.get('raw', '')))
        entity = get_entity('phone', normalised)
        
        if entity and entity.get('confirmed'):
            # Known entity
            display = entity.get('placeholder_name') if entity.get('anonymise_in_prompts') else entity.get('display_name', normalised)
            resolved.append({
                'type': 'phone',
                'raw': phone.get('raw'),
                'display': display,
                'relationship': entity.get('relationship'),
                'entity_id': entity.get('id'),
            })
            if display and entity.get('relationship'):
                context_parts.append(f"{display} ({entity.get('relationship')})")
        else:
            # Unknown entity
            unknown.append({
                'type': 'phone',
                'raw': phone.get('raw'),
                'normalised': normalised,
                'context': phone.get('context', ''),
                'entity_id': entity.get('id') if entity else None,
            })
    
    # Process email addresses
    for email in tier0_entities.get('email_addresses', []):
        normalised = email.get('normalised', normalise_email(email.get('raw', '')))
        entity = get_entity('email', normalised)
        
        if entity and entity.get('confirmed'):
            display = entity.get('placeholder_name') if entity.get('anonymise_in_prompts') else entity.get('display_name', normalised)
            resolved.append({
                'type': 'email',
                'raw': email.get('raw'),
                'display': display,
                'relationship': entity.get('relationship'),
                'entity_id': entity.get('id'),
            })
            if display and entity.get('relationship'):
                context_parts.append(f"{display} ({entity.get('relationship')})")
        else:
            unknown.append({
                'type': 'email',
                'raw': email.get('raw'),
                'normalised': normalised,
                'context': email.get('context', ''),
                'entity_id': entity.get('id') if entity else None,
            })
    
    # Build prompt context
    prompt_context = ""
    if context_parts:
        prompt_context = "Known entities in this content:\n" + "\n".join(f"- {p}" for p in context_parts)
    if unknown:
        prompt_context += f"\n\nNote: {len(unknown)} unidentified contact(s) present."
    
    return {
        'resolved': resolved,
        'unknown': unknown,
        'prompt_context': prompt_context.strip(),
    }


# =============================================================================
# STATISTICS
# =============================================================================

def get_entity_stats() -> Dict:
    """Get statistics about the entity registry."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        stats = {}
        
        # Total counts by type
        cursor.execute("""
            SELECT entity_type, COUNT(*), SUM(CASE WHEN confirmed = 1 THEN 1 ELSE 0 END)
            FROM entity_registry
            WHERE merged_into_id IS NULL
            GROUP BY entity_type
        """)
        for row in cursor.fetchall():
            stats[row[0]] = {
                'total': row[1],
                'confirmed': row[2],
                'unconfirmed': row[1] - row[2],
            }
        
        # Overall
        cursor.execute("""
            SELECT COUNT(*), SUM(CASE WHEN confirmed = 1 THEN 1 ELSE 0 END)
            FROM entity_registry
            WHERE merged_into_id IS NULL
        """)
        row = cursor.fetchone()
        stats['total'] = {
            'total': row[0] or 0,
            'confirmed': row[1] or 0,
            'unconfirmed': (row[0] or 0) - (row[1] or 0),
        }
        
        return stats
    finally:
        conn.close()


# =============================================================================
# MODULE EXPORTS
# =============================================================================

__all__ = [
    'get_entity',
    'get_entity_by_id',
    'register_entity',
    'update_entity',
    'list_entities',
    'get_unknown_entities',
    'register_entities_from_tier0',
    'resolve_entities_for_prompt',
    'get_entity_stats',
    'normalise_phone',
    'normalise_email',
]
