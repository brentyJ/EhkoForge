"""
EhkoForge - Authority & Mana System v0.1

Handles:
- Authority calculation (Ehko advancement metric)
- Mana regeneration and cost deduction
- Stage transitions

Authority Components (equal weight):
- Memory Depth: Reflection volume + Insite count
- Identity Clarity: Pillars populated
- Emotional Range: Tag diversity
- Temporal Coverage: Date range of reflections
- Core Density: Core memories flagged

Mana:
- Regenerates over time (configurable rate)
- Operations cost mana
- Zero mana = Ehko dormant
"""

import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional, Tuple

from .prompts import get_stage_for_authority


# =============================================================================
# AUTHORITY CALCULATION
# =============================================================================

def calculate_authority_components(db_path: Path) -> Dict[str, float]:
    """
    Calculate all Authority components from database state.
    
    Returns dict with component scores (0.0 - 1.0) and total Authority.
    """
    conn = sqlite3.connect(str(db_path), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    components = {
        'memory_depth': 0.0,
        'identity_clarity': 0.0,
        'emotional_range': 0.0,
        'temporal_coverage': 0.0,
        'core_density': 0.0,
    }
    
    try:
        # ---------------------------------------------------------------------
        # Memory Depth: Reflection count + Insite count (normalised)
        # Target: 100 reflections + 50 insites = 1.0
        # ---------------------------------------------------------------------
        cursor.execute("SELECT COUNT(*) FROM reflection_objects")
        reflection_count = cursor.fetchone()[0]
        
        # Check for insites table (may not exist yet)
        cursor.execute("""
            SELECT COUNT(*) FROM sqlite_master 
            WHERE type='table' AND name='insites'
        """)
        if cursor.fetchone()[0]:
            cursor.execute("SELECT COUNT(*) FROM insites WHERE status = 'forged'")
            insite_count = cursor.fetchone()[0]
        else:
            # Fall back to ingots table
            cursor.execute("""
                SELECT COUNT(*) FROM sqlite_master 
                WHERE type='table' AND name='ingots'
            """)
            if cursor.fetchone()[0]:
                cursor.execute("SELECT COUNT(*) FROM ingots WHERE status = 'forged'")
                insite_count = cursor.fetchone()[0]
            else:
                insite_count = 0
        
        # Normalise: reflections contribute 60%, insites 40%
        reflection_score = min(1.0, reflection_count / 100)
        insite_score = min(1.0, insite_count / 50)
        components['memory_depth'] = (reflection_score * 0.6) + (insite_score * 0.4)
        
        # ---------------------------------------------------------------------
        # Identity Clarity: Pillars populated (6 pillars)
        # Each pillar with content_count > 0 contributes 1/6
        # ---------------------------------------------------------------------
        cursor.execute("""
            SELECT COUNT(*) FROM sqlite_master 
            WHERE type='table' AND name='identity_pillars'
        """)
        if cursor.fetchone()[0]:
            cursor.execute("""
                SELECT COUNT(*) FROM identity_pillars 
                WHERE populated = 1 OR content_count > 0
            """)
            populated_pillars = cursor.fetchone()[0]
            components['identity_clarity'] = min(1.0, populated_pillars / 6)
        else:
            # Fall back: check if pillar documents exist in Mirrorwell
            cursor.execute("""
                SELECT COUNT(DISTINCT me.identity_pillar) 
                FROM mirrorwell_extensions me
                WHERE me.identity_pillar IS NOT NULL AND me.identity_pillar != ''
            """)
            result = cursor.fetchone()
            if result and result[0]:
                components['identity_clarity'] = min(1.0, result[0] / 6)
        
        # ---------------------------------------------------------------------
        # Emotional Range: Diversity of emotional tags
        # Target: 15+ unique emotions = 1.0
        # ---------------------------------------------------------------------
        cursor.execute("SELECT COUNT(DISTINCT emotion) FROM emotional_tags")
        emotion_count = cursor.fetchone()[0]
        components['emotional_range'] = min(1.0, emotion_count / 15)
        
        # ---------------------------------------------------------------------
        # Temporal Coverage: Years of life represented
        # Target: 10+ years of life events = 1.0
        # Uses created dates from reflections
        # ---------------------------------------------------------------------
        cursor.execute("""
            SELECT MIN(created), MAX(created) FROM reflection_objects
            WHERE created IS NOT NULL AND created != ''
        """)
        row = cursor.fetchone()
        if row and row[0] and row[1]:
            try:
                # Parse dates (handle various formats)
                min_date = _parse_date(row[0])
                max_date = _parse_date(row[1])
                if min_date and max_date:
                    years_covered = (max_date - min_date).days / 365.25
                    components['temporal_coverage'] = min(1.0, years_covered / 10)
            except (ValueError, TypeError):
                pass
        
        # ---------------------------------------------------------------------
        # Core Density: Ratio of core memories to total reflections
        # Target: 10% of reflections flagged as core = 1.0
        # ---------------------------------------------------------------------
        if reflection_count > 0:
            cursor.execute("""
                SELECT COUNT(*) FROM mirrorwell_extensions 
                WHERE core_memory = 1
            """)
            core_count = cursor.fetchone()[0]
            core_ratio = core_count / reflection_count
            # 10% core memories = 1.0
            components['core_density'] = min(1.0, core_ratio / 0.1)
        
    except sqlite3.Error as e:
        print(f"[AUTHORITY] Database error: {e}")
    finally:
        conn.close()
    
    return components


def _parse_date(date_str: str) -> Optional[datetime]:
    """Parse date string in various formats."""
    formats = [
        "%Y-%m-%d",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%S.%f",
        "%Y-%m-%d %H:%M:%S",
    ]
    for fmt in formats:
        try:
            return datetime.strptime(date_str[:len("YYYY-MM-DDTHH:MM:SS.ffffff")], fmt)
        except (ValueError, TypeError):
            continue
    return None


def calculate_total_authority(components: Dict[str, float]) -> float:
    """
    Calculate total Authority from components.
    
    Currently equal weighting. Can be adjusted later.
    """
    weights = {
        'memory_depth': 1.0,
        'identity_clarity': 1.0,
        'emotional_range': 1.0,
        'temporal_coverage': 1.0,
        'core_density': 1.0,
    }
    
    total_weight = sum(weights.values())
    weighted_sum = sum(
        components.get(k, 0.0) * w 
        for k, w in weights.items()
    )
    
    return weighted_sum / total_weight


def update_authority(db_path: Path) -> Dict[str, float]:
    """
    Recalculate and store Authority in database.
    
    Returns full authority state including stage.
    """
    components = calculate_authority_components(db_path)
    authority_total = calculate_total_authority(components)
    stage = get_stage_for_authority(authority_total)
    
    conn = sqlite3.connect(str(db_path), check_same_thread=False)
    cursor = conn.cursor()
    
    try:
        now = datetime.utcnow().isoformat() + "Z"
        
        # Ensure table exists
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ehko_authority (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                memory_depth REAL DEFAULT 0.0,
                identity_clarity REAL DEFAULT 0.0,
                emotional_range REAL DEFAULT 0.0,
                temporal_coverage REAL DEFAULT 0.0,
                core_density REAL DEFAULT 0.0,
                authority_total REAL DEFAULT 0.0,
                advancement_stage TEXT DEFAULT 'nascent',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Upsert authority row
        cursor.execute("""
            INSERT INTO ehko_authority (id, memory_depth, identity_clarity, emotional_range,
                                        temporal_coverage, core_density, authority_total,
                                        advancement_stage, updated_at)
            VALUES (1, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                memory_depth = excluded.memory_depth,
                identity_clarity = excluded.identity_clarity,
                emotional_range = excluded.emotional_range,
                temporal_coverage = excluded.temporal_coverage,
                core_density = excluded.core_density,
                authority_total = excluded.authority_total,
                advancement_stage = excluded.advancement_stage,
                updated_at = excluded.updated_at
        """, (
            components['memory_depth'],
            components['identity_clarity'],
            components['emotional_range'],
            components['temporal_coverage'],
            components['core_density'],
            authority_total,
            stage,
            now,
        ))
        
        conn.commit()
        
    except sqlite3.Error as e:
        print(f"[AUTHORITY] Failed to update: {e}")
    finally:
        conn.close()
    
    return {
        **components,
        'authority_total': authority_total,
        'advancement_stage': stage,
    }


def get_current_authority(db_path: Path) -> Dict[str, float]:
    """
    Get current Authority state from database.
    
    If not calculated yet, calculates and stores it.
    """
    conn = sqlite3.connect(str(db_path), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT * FROM ehko_authority WHERE id = 1
        """)
        row = cursor.fetchone()
        
        if row:
            return {
                'memory_depth': row['memory_depth'],
                'identity_clarity': row['identity_clarity'],
                'emotional_range': row['emotional_range'],
                'temporal_coverage': row['temporal_coverage'],
                'core_density': row['core_density'],
                'authority_total': row['authority_total'],
                'advancement_stage': row['advancement_stage'],
            }
    except sqlite3.Error:
        pass
    finally:
        conn.close()
    
    # Not found or error — calculate fresh
    return update_authority(db_path)


# =============================================================================
# MANA SYSTEM
# =============================================================================

def get_mana_state(db_path: Path) -> Dict[str, float]:
    """
    Get current mana state, applying regeneration.
    
    Regeneration is calculated based on time since last update.
    """
    conn = sqlite3.connect(str(db_path), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        # Ensure tables exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS mana_state (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                current_mana REAL DEFAULT 100.0,
                max_mana REAL DEFAULT 100.0,
                regen_rate REAL DEFAULT 1.0,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("INSERT OR IGNORE INTO mana_state (id) VALUES (1)")
        
        cursor.execute("SELECT * FROM mana_state WHERE id = 1")
        row = cursor.fetchone()
        
        if not row:
            conn.commit()
            return {
                'current_mana': 100.0,
                'max_mana': 100.0,
                'regen_rate': 1.0,
                'is_dormant': False,
            }
        
        # Calculate regeneration
        last_updated = _parse_date(row['last_updated'])
        now = datetime.utcnow()
        
        if last_updated:
            hours_elapsed = (now - last_updated).total_seconds() / 3600
            regenerated = hours_elapsed * row['regen_rate']
            new_mana = min(row['max_mana'], row['current_mana'] + regenerated)
        else:
            new_mana = row['current_mana']
        
        # Update if changed significantly
        if abs(new_mana - row['current_mana']) > 0.01:
            cursor.execute("""
                UPDATE mana_state 
                SET current_mana = ?, last_updated = ?
                WHERE id = 1
            """, (new_mana, now.isoformat() + "Z"))
            conn.commit()
        
        return {
            'current_mana': new_mana,
            'max_mana': row['max_mana'],
            'regen_rate': row['regen_rate'],
            'is_dormant': new_mana < 1.0,
        }
        
    except sqlite3.Error as e:
        print(f"[MANA] Database error: {e}")
        return {
            'current_mana': 100.0,
            'max_mana': 100.0,
            'regen_rate': 1.0,
            'is_dormant': False,
        }
    finally:
        conn.close()


def get_mana_cost(db_path: Path, operation: str) -> float:
    """Get mana cost for an operation."""
    conn = sqlite3.connect(str(db_path), check_same_thread=False)
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS mana_costs (
                operation TEXT PRIMARY KEY,
                cost REAL NOT NULL,
                description TEXT
            )
        """)
        
        cursor.execute("""
            SELECT cost FROM mana_costs WHERE operation = ?
        """, (operation,))
        row = cursor.fetchone()
        
        if row:
            return row[0]
        
        # Default costs if not in table
        defaults = {
            'terminal_message': 1.0,
            'reflection_message': 3.0,
            'recog_sweep': 20.0,
            'flag_for_processing': 0.0,
        }
        return defaults.get(operation, 1.0)
        
    except sqlite3.Error:
        return 1.0
    finally:
        conn.close()


def spend_mana(db_path: Path, operation: str, amount: Optional[float] = None) -> Tuple[bool, str]:
    """
    Attempt to spend mana for an operation.
    
    Args:
        db_path: Path to database
        operation: Operation name (for cost lookup and logging)
        amount: Override amount (if None, looks up from mana_costs)
    
    Returns:
        (success, message) tuple
    """
    # Get current state (with regeneration applied)
    state = get_mana_state(db_path)
    
    # Get cost
    if amount is None:
        amount = get_mana_cost(db_path, operation)
    
    # Check if enough mana
    if state['current_mana'] < amount:
        return (False, f"Not enough mana. Need {amount:.1f}, have {state['current_mana']:.1f}")
    
    # Deduct mana
    new_mana = state['current_mana'] - amount
    
    conn = sqlite3.connect(str(db_path), check_same_thread=False)
    cursor = conn.cursor()
    
    try:
        now = datetime.utcnow().isoformat() + "Z"
        
        cursor.execute("""
            UPDATE mana_state 
            SET current_mana = ?, last_updated = ?
            WHERE id = 1
        """, (new_mana, now))
        
        # Log transaction
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS mana_transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                operation TEXT NOT NULL,
                amount REAL NOT NULL,
                balance_after REAL NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                details TEXT
            )
        """)
        
        cursor.execute("""
            INSERT INTO mana_transactions (operation, amount, balance_after, timestamp)
            VALUES (?, ?, ?, ?)
        """, (operation, -amount, new_mana, now))
        
        conn.commit()
        
        return (True, f"Spent {amount:.1f} mana on {operation}. {new_mana:.1f} remaining.")
        
    except sqlite3.Error as e:
        return (False, f"Database error: {e}")
    finally:
        conn.close()


def check_mana_available(db_path: Path, operation: str) -> Tuple[bool, float, float]:
    """
    Check if enough mana is available for an operation.
    
    Returns:
        (can_afford, current_mana, cost) tuple
    """
    state = get_mana_state(db_path)
    cost = get_mana_cost(db_path, operation)
    can_afford = state['current_mana'] >= cost
    
    return (can_afford, state['current_mana'], cost)


def get_dormant_response() -> str:
    """Get the response to show when Ehko is dormant (out of mana)."""
    return (
        "I need to rest. My mana has been depleted.\n\n"
        "Come back when I've had time to recover, or add more mana to continue."
    )


# =============================================================================
# MANA CONFIGURATION
# =============================================================================

def set_mana_config(db_path: Path, max_mana: float = None, regen_rate: float = None):
    """
    Update mana configuration (for BYOK users).
    
    Args:
        max_mana: Maximum mana capacity
        regen_rate: Mana regeneration per hour
    """
    conn = sqlite3.connect(str(db_path), check_same_thread=False)
    cursor = conn.cursor()
    
    try:
        updates = []
        params = []
        
        if max_mana is not None:
            updates.append("max_mana = ?")
            params.append(max_mana)
        
        if regen_rate is not None:
            updates.append("regen_rate = ?")
            params.append(regen_rate)
        
        if updates:
            now = datetime.utcnow().isoformat() + "Z"
            updates.append("last_updated = ?")
            params.append(now)
            params.append(1)  # WHERE id = 1
            
            cursor.execute(f"""
                UPDATE mana_state 
                SET {', '.join(updates)}
                WHERE id = ?
            """, params)
            
            conn.commit()
            
    except sqlite3.Error as e:
        print(f"[MANA] Config update error: {e}")
    finally:
        conn.close()


def refill_mana(db_path: Path, amount: float = None):
    """
    Refill mana (manually or via mana-core purchase).
    
    Args:
        amount: Amount to add (if None, fills to max)
    """
    state = get_mana_state(db_path)
    
    if amount is None:
        new_mana = state['max_mana']
    else:
        new_mana = min(state['max_mana'], state['current_mana'] + amount)
    
    conn = sqlite3.connect(str(db_path), check_same_thread=False)
    cursor = conn.cursor()
    
    try:
        now = datetime.utcnow().isoformat() + "Z"
        
        cursor.execute("""
            UPDATE mana_state 
            SET current_mana = ?, last_updated = ?
            WHERE id = 1
        """, (new_mana, now))
        
        # Log refill
        added = new_mana - state['current_mana']
        cursor.execute("""
            INSERT INTO mana_transactions (operation, amount, balance_after, timestamp, details)
            VALUES (?, ?, ?, ?, ?)
        """, ('refill', added, new_mana, now, 'Manual refill'))
        
        conn.commit()
        
    except sqlite3.Error as e:
        print(f"[MANA] Refill error: {e}")
    finally:
        conn.close()


# =============================================================================
# MODULE EXPORTS
# =============================================================================

__all__ = [
    # Authority
    'calculate_authority_components',
    'calculate_total_authority',
    'update_authority',
    'get_current_authority',
    # Mana
    'get_mana_state',
    'get_mana_cost',
    'spend_mana',
    'check_mana_available',
    'get_dormant_response',
    'set_mana_config',
    'refill_mana',
]
