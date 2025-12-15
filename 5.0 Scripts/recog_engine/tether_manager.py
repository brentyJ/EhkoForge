"""
EhkoForge - Tether Manager v0.1

Handles direct conduits to LLM Sources (BYOK).

Unlike mana, tethers never deplete. They represent a permanent connection
to an LLM provider through the user's own API key. While a tether is active,
operations route through it without consuming mana.

Tethers are conceptually styled like mana bars but display connection status
rather than resource level - always full when connected.
"""

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import os

# Optional: async HTTP for verification
try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False


# =============================================================================
# TETHER CRUD OPERATIONS
# =============================================================================

def get_tethers(db_path: Path, user_id: int = 1, active_only: bool = False) -> List[Dict]:
    """
    Get all tethers for a user.
    
    Returns list of tether objects (API keys masked for security).
    """
    conn = sqlite3.connect(str(db_path), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        query = """
            SELECT 
                t.id,
                t.provider,
                t.display_name,
                t.active,
                t.last_verified_at,
                t.verification_status,
                t.created_at,
                t.updated_at,
                tp.display_name as provider_display_name,
                tp.default_model,
                tp.supports_chat,
                tp.supports_processing,
                CASE WHEN t.api_key_encrypted IS NOT NULL THEN 1 ELSE 0 END as has_key
            FROM tethers t
            JOIN tether_providers tp ON t.provider = tp.provider_key
            WHERE t.user_id = ?
        """
        
        if active_only:
            query += " AND t.active = 1"
        
        query += " ORDER BY tp.display_order"
        
        cursor.execute(query, (user_id,))
        return [dict(row) for row in cursor.fetchall()]
        
    finally:
        conn.close()


def get_tether(db_path: Path, provider: str, user_id: int = 1) -> Optional[Dict]:
    """Get a specific tether by provider."""
    conn = sqlite3.connect(str(db_path), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT * FROM tethers WHERE user_id = ? AND provider = ?
        """, (user_id, provider))
        row = cursor.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def create_tether(db_path: Path, provider: str, api_key: str, 
                  user_id: int = 1, display_name: Optional[str] = None) -> Tuple[bool, str, Optional[int]]:
    """
    Create or update a tether (direct Source connection).
    
    Returns: (success, message, tether_id)
    """
    conn = sqlite3.connect(str(db_path), check_same_thread=False)
    cursor = conn.cursor()
    
    try:
        now = datetime.utcnow().isoformat() + "Z"
        
        # Check if provider is supported
        cursor.execute("""
            SELECT provider_key, display_name FROM tether_providers 
            WHERE provider_key = ? AND active = 1
        """, (provider,))
        provider_row = cursor.fetchone()
        
        if not provider_row:
            return (False, f"Unsupported provider: {provider}", None)
        
        if not display_name:
            display_name = provider_row[1]
        
        # Check if tether already exists
        cursor.execute("""
            SELECT id FROM tethers WHERE user_id = ? AND provider = ?
        """, (user_id, provider))
        existing = cursor.fetchone()
        
        if existing:
            # Update existing tether
            cursor.execute("""
                UPDATE tethers SET
                    api_key_encrypted = ?,
                    display_name = ?,
                    active = 1,
                    verification_status = 'pending',
                    updated_at = ?
                WHERE id = ?
            """, (api_key, display_name, now, existing[0]))
            tether_id = existing[0]
            action = "updated"
        else:
            # Create new tether
            cursor.execute("""
                INSERT INTO tethers (
                    user_id, provider, display_name, api_key_encrypted,
                    active, verification_status, created_at, updated_at
                ) VALUES (?, ?, ?, ?, 1, 'pending', ?, ?)
            """, (user_id, provider, display_name, api_key, now, now))
            tether_id = cursor.lastrowid
            action = "created"
        
        conn.commit()
        return (True, f"Tether {action} for {provider}", tether_id)
        
    except sqlite3.Error as e:
        return (False, f"Database error: {e}", None)
    finally:
        conn.close()


def delete_tether(db_path: Path, provider: str, user_id: int = 1) -> Tuple[bool, str]:
    """
    Remove a tether (disconnect from Source).
    
    This doesn't delete usage history, just removes the connection.
    """
    conn = sqlite3.connect(str(db_path), check_same_thread=False)
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            DELETE FROM tethers WHERE user_id = ? AND provider = ?
        """, (user_id, provider))
        
        if cursor.rowcount > 0:
            conn.commit()
            return (True, f"Tether disconnected: {provider}")
        else:
            return (False, f"No tether found for {provider}")
            
    except sqlite3.Error as e:
        return (False, f"Database error: {e}")
    finally:
        conn.close()


def toggle_tether(db_path: Path, provider: str, active: bool, user_id: int = 1) -> Tuple[bool, str]:
    """Activate or deactivate a tether without removing it."""
    conn = sqlite3.connect(str(db_path), check_same_thread=False)
    cursor = conn.cursor()
    
    try:
        now = datetime.utcnow().isoformat() + "Z"
        
        cursor.execute("""
            UPDATE tethers SET active = ?, updated_at = ?
            WHERE user_id = ? AND provider = ?
        """, (1 if active else 0, now, user_id, provider))
        
        if cursor.rowcount > 0:
            conn.commit()
            status = "connected" if active else "disconnected"
            return (True, f"Tether {status}: {provider}")
        else:
            return (False, f"No tether found for {provider}")
            
    except sqlite3.Error as e:
        return (False, f"Database error: {e}")
    finally:
        conn.close()


# =============================================================================
# TETHER VERIFICATION
# =============================================================================

def verify_tether(db_path: Path, provider: str, user_id: int = 1) -> Tuple[bool, str]:
    """
    Verify a tether's API key is still valid.
    
    Makes a lightweight API call to confirm the key works.
    """
    tether = get_tether(db_path, provider, user_id)
    if not tether:
        return (False, "Tether not found")
    
    api_key = tether['api_key_encrypted']  # TODO: Decrypt
    
    # Verification logic per provider
    try:
        if provider == 'claude':
            valid, message = _verify_claude_key(api_key)
        elif provider == 'openai':
            valid, message = _verify_openai_key(api_key)
        elif provider == 'gemini':
            valid, message = _verify_gemini_key(api_key)
        else:
            return (False, f"Unknown provider: {provider}")
        
        # Update verification status
        _update_verification_status(db_path, provider, user_id, valid)
        
        return (valid, message)
        
    except Exception as e:
        _update_verification_status(db_path, provider, user_id, False)
        return (False, f"Verification error: {e}")


def _verify_claude_key(api_key: str) -> Tuple[bool, str]:
    """Verify Anthropic API key."""
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
        # Minimal request to verify key
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1,
            messages=[{"role": "user", "content": "hi"}]
        )
        return (True, "Claude tether verified")
    except anthropic.AuthenticationError:
        return (False, "Invalid Claude API key")
    except Exception as e:
        return (False, f"Claude verification failed: {e}")


def _verify_openai_key(api_key: str) -> Tuple[bool, str]:
    """Verify OpenAI API key."""
    try:
        import openai
        client = openai.OpenAI(api_key=api_key)
        # List models to verify key (minimal cost)
        client.models.list()
        return (True, "OpenAI tether verified")
    except openai.AuthenticationError:
        return (False, "Invalid OpenAI API key")
    except Exception as e:
        return (False, f"OpenAI verification failed: {e}")


def _verify_gemini_key(api_key: str) -> Tuple[bool, str]:
    """Verify Google Gemini API key."""
    # Placeholder - implement when Gemini support added
    return (False, "Gemini verification not yet implemented")


def _update_verification_status(db_path: Path, provider: str, user_id: int, valid: bool):
    """Update tether verification status in database."""
    conn = sqlite3.connect(str(db_path), check_same_thread=False)
    cursor = conn.cursor()
    
    try:
        now = datetime.utcnow().isoformat() + "Z"
        status = 'valid' if valid else 'invalid'
        
        cursor.execute("""
            UPDATE tethers SET
                verification_status = ?,
                last_verified_at = ?,
                updated_at = ?
            WHERE user_id = ? AND provider = ?
        """, (status, now, now, user_id, provider))
        
        conn.commit()
    finally:
        conn.close()


# =============================================================================
# TETHER ROUTING
# =============================================================================

def get_active_tether_for_operation(db_path: Path, operation: str, 
                                     preferred_provider: Optional[str] = None,
                                     user_id: int = 1) -> Optional[Dict]:
    """
    Get an active, verified tether for the given operation type.
    
    Used by the routing logic to determine if we should use a tether
    instead of consuming mana.
    
    Args:
        operation: 'chat', 'processing', 'recog', etc.
        preferred_provider: Optional preference (e.g. 'claude' for chat)
    
    Returns:
        Tether dict with decrypted API key, or None if no tether available.
    """
    conn = sqlite3.connect(str(db_path), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        # Determine which capability we need
        if operation in ['chat', 'terminal_message', 'reflection_message']:
            capability = 'supports_chat'
        else:
            capability = 'supports_processing'
        
        # Build query
        query = f"""
            SELECT 
                t.id,
                t.provider,
                t.api_key_encrypted,
                tp.default_model
            FROM tethers t
            JOIN tether_providers tp ON t.provider = tp.provider_key
            WHERE t.user_id = ?
              AND t.active = 1
              AND t.verification_status = 'valid'
              AND tp.{capability} = 1
        """
        
        params = [user_id]
        
        if preferred_provider:
            query += " AND t.provider = ?"
            params.append(preferred_provider)
        
        query += " ORDER BY tp.display_order LIMIT 1"
        
        cursor.execute(query, params)
        row = cursor.fetchone()
        
        if row:
            return {
                'id': row['id'],
                'provider': row['provider'],
                'api_key': row['api_key_encrypted'],  # TODO: Decrypt
                'model': row['default_model'],
            }
        return None
        
    finally:
        conn.close()


def has_active_tether(db_path: Path, provider: str, user_id: int = 1) -> bool:
    """Quick check if user has an active, verified tether for provider."""
    conn = sqlite3.connect(str(db_path), check_same_thread=False)
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT 1 FROM tethers 
            WHERE user_id = ? 
              AND provider = ? 
              AND active = 1 
              AND verification_status = 'valid'
            LIMIT 1
        """, (user_id, provider))
        return cursor.fetchone() is not None
    finally:
        conn.close()


# =============================================================================
# TETHER USAGE LOGGING
# =============================================================================

def log_tether_usage(db_path: Path, tether_id: int, operation: str,
                     provider: str, model: Optional[str] = None,
                     tokens_input: int = 0, tokens_output: int = 0,
                     session_id: Optional[int] = None, user_id: int = 1):
    """
    Log an operation routed through a tether.
    
    This is for analytics only - tethers don't consume mana.
    """
    conn = sqlite3.connect(str(db_path), check_same_thread=False)
    cursor = conn.cursor()
    
    try:
        now = datetime.utcnow().isoformat() + "Z"
        
        cursor.execute("""
            INSERT INTO tether_usage_log (
                user_id, tether_id, operation, provider, model,
                tokens_input, tokens_output, session_id, timestamp
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (user_id, tether_id, operation, provider, model,
              tokens_input, tokens_output, session_id, now))
        
        conn.commit()
    except sqlite3.Error as e:
        print(f"[TETHER] Usage log failed: {e}")
    finally:
        conn.close()


def get_tether_usage_stats(db_path: Path, user_id: int = 1, days: int = 30) -> Dict:
    """Get tether usage statistics."""
    conn = sqlite3.connect(str(db_path), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT * FROM v_tether_usage_stats WHERE user_id = ?
        """, (user_id,))
        
        stats = {}
        for row in cursor.fetchall():
            stats[row['provider']] = {
                'operation_count': row['operation_count'],
                'tokens_input': row['total_tokens_input'] or 0,
                'tokens_output': row['total_tokens_output'] or 0,
                'last_used': row['last_used_at'],
            }
        
        return stats
    finally:
        conn.close()


# =============================================================================
# PROVIDER METADATA
# =============================================================================

def get_supported_providers(db_path: Path) -> List[Dict]:
    """Get list of supported tether providers."""
    conn = sqlite3.connect(str(db_path), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT * FROM tether_providers 
            WHERE active = 1 
            ORDER BY display_order
        """)
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()


# =============================================================================
# MODULE EXPORTS
# =============================================================================

__all__ = [
    # CRUD
    'get_tethers',
    'get_tether',
    'create_tether',
    'delete_tether',
    'toggle_tether',
    # Verification
    'verify_tether',
    # Routing
    'get_active_tether_for_operation',
    'has_active_tether',
    # Usage
    'log_tether_usage',
    'get_tether_usage_stats',
    # Metadata
    'get_supported_providers',
]
