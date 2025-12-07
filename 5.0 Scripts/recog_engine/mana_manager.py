"""
EhkoForge - Mana Purchase & Balance Management v0.1

Handles:
- Mana-core purchases (Stripe integration)
- User mana balance tracking (purchased + regenerative)
- BYOK/Mana/Hybrid mode switching
- Usage logging and analytics
- API key management (encrypted storage)

This module extends authority_mana.py with purchase/payment functionality.
"""

import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import json

# Encryption for API keys (optional - implement if needed)
try:
    from cryptography.fernet import Fernet
    ENCRYPTION_AVAILABLE = True
except ImportError:
    ENCRYPTION_AVAILABLE = False


# =============================================================================
# USER CONFIGURATION
# =============================================================================

def get_user_config(db_path: Path, user_id: int = 1) -> Dict:
    """Get user's mana configuration and preferences."""
    conn = sqlite3.connect(str(db_path), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT * FROM user_config WHERE user_id = ?
        """, (user_id,))
        row = cursor.fetchone()
        
        if row:
            return dict(row)
        else:
            # Return defaults
            return {
                'user_id': user_id,
                'mana_mode': 'mana',
                'byok_max_mana': 100.0,
                'byok_regen_rate': 1.0,
                'hybrid_chat_source': 'mana',
                'hybrid_processing_source': 'mana',
                'daily_mana_cap': 1000.0,
                'weekly_mana_cap': 5000.0,
                'alert_threshold': 0.8,
                'preferred_chat_provider': 'claude',
                'preferred_processing_provider': 'openai',
            }
    finally:
        conn.close()


def set_user_config(db_path: Path, user_id: int = 1, **config) -> bool:
    """Update user configuration."""
    conn = sqlite3.connect(str(db_path), check_same_thread=False)
    cursor = conn.cursor()
    
    try:
        # Build update query dynamically
        valid_fields = [
            'mana_mode', 'byok_max_mana', 'byok_regen_rate',
            'hybrid_chat_source', 'hybrid_processing_source',
            'daily_mana_cap', 'weekly_mana_cap', 'alert_threshold',
            'preferred_chat_provider', 'preferred_processing_provider'
        ]
        
        updates = []
        values = []
        for key, value in config.items():
            if key in valid_fields:
                updates.append(f"{key} = ?")
                values.append(value)
        
        if not updates:
            return False
        
        now = datetime.utcnow().isoformat() + "Z"
        updates.append("updated_at = ?")
        values.extend([now, user_id])
        
        cursor.execute(f"""
            UPDATE user_config 
            SET {', '.join(updates)}
            WHERE user_id = ?
        """, values)
        
        conn.commit()
        return True
        
    except sqlite3.Error as e:
        print(f"[MANA CONFIG] Update failed: {e}")
        return False
    finally:
        conn.close()


# =============================================================================
# MANA BALANCE MANAGEMENT
# =============================================================================

def get_mana_balance(db_path: Path, user_id: int = 1) -> Dict:
    """
    Get user's complete mana balance.
    
    Returns both regenerative (BYOK) and purchased mana.
    """
    conn = sqlite3.connect(str(db_path), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT * FROM v_user_total_mana WHERE user_id = ?
        """, (user_id,))
        row = cursor.fetchone()
        
        if row:
            return dict(row)
        else:
            return {
                'user_id': user_id,
                'mana_mode': 'mana',
                'regenerative_mana': 0.0,
                'purchased_mana': 0.0,
                'total_available': 0.0,
                'lifetime_purchased': 0.0,
                'lifetime_spent': 0.0,
            }
    finally:
        conn.close()


def add_purchased_mana(db_path: Path, amount: float, user_id: int = 1) -> bool:
    """
    Add purchased mana to user's balance.
    
    Called after successful payment processing.
    """
    conn = sqlite3.connect(str(db_path), check_same_thread=False)
    cursor = conn.cursor()
    
    try:
        now = datetime.utcnow().isoformat() + "Z"
        
        cursor.execute("""
            UPDATE user_mana_balance
            SET purchased_mana = purchased_mana + ?,
                lifetime_purchased = lifetime_purchased + ?,
                last_updated = ?
            WHERE user_id = ?
        """, (amount, amount, now, user_id))
        
        conn.commit()
        return True
        
    except sqlite3.Error as e:
        print(f"[MANA] Failed to add purchased mana: {e}")
        return False
    finally:
        conn.close()


def spend_mana_smart(db_path: Path, operation: str, amount: float, 
                     user_id: int = 1, session_id: Optional[int] = None,
                     provider: Optional[str] = None, model: Optional[str] = None,
                     tokens_used: Optional[int] = None) -> Tuple[bool, str, Dict]:
    """
    Smart mana spending that respects user's mode (BYOK/Mana/Hybrid).
    
    Returns:
        (success, message, details) tuple
        details includes: {'source': 'byok'|'purchased', 'remaining': float}
    """
    config = get_user_config(db_path, user_id)
    balance = get_mana_balance(db_path, user_id)
    
    # Determine source based on mode
    mode = config['mana_mode']
    source = None
    
    if mode == 'byok':
        # Use regenerative mana only
        if balance['regenerative_mana'] >= amount:
            source = 'byok'
        else:
            return (False, f"Insufficient BYOK mana. Have {balance['regenerative_mana']:.1f}, need {amount:.1f}", {})
    
    elif mode == 'mana':
        # Use purchased mana only
        if balance['purchased_mana'] >= amount:
            source = 'purchased'
        else:
            return (False, f"Insufficient purchased mana. Have {balance['purchased_mana']:.1f}, need {amount:.1f}. [Top Up]", {})
    
    elif mode == 'hybrid':
        # Route based on operation type
        if operation in ['chat', 'terminal_message', 'reflection_message']:
            preferred = config['hybrid_chat_source']
        else:
            preferred = config['hybrid_processing_source']
        
        # Try preferred source first
        if preferred == 'byok' and balance['regenerative_mana'] >= amount:
            source = 'byok'
        elif preferred == 'purchased' and balance['purchased_mana'] >= amount:
            source = 'purchased'
        # Fall back to other source
        elif balance['purchased_mana'] >= amount:
            source = 'purchased'
        elif balance['regenerative_mana'] >= amount:
            source = 'byok'
        else:
            return (False, f"Insufficient mana in both pools. Need {amount:.1f}", {})
    
    # Deduct from appropriate pool
    conn = sqlite3.connect(str(db_path), check_same_thread=False)
    cursor = conn.cursor()
    
    try:
        now = datetime.utcnow().isoformat() + "Z"
        
        if source == 'byok':
            # Deduct from regenerative pool (mana_state table)
            cursor.execute("""
                UPDATE mana_state
                SET current_mana = current_mana - ?,
                    last_updated = ?
                WHERE id = 1
            """, (amount, now))
            
        elif source == 'purchased':
            # Deduct from purchased pool
            cursor.execute("""
                UPDATE user_mana_balance
                SET purchased_mana = purchased_mana - ?,
                    lifetime_spent = lifetime_spent + ?,
                    last_updated = ?
                WHERE user_id = ?
            """, (amount, amount, now, user_id))
        
        # Log usage
        cursor.execute("""
            INSERT INTO mana_usage_log (
                user_id, operation, mana_spent, source, 
                provider, model, tokens_used, session_id, timestamp
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (user_id, operation, amount, source, provider, model, tokens_used, session_id, now))
        
        conn.commit()
        
        # Get updated balance
        updated_balance = get_mana_balance(db_path, user_id)
        
        return (True, f"Spent {amount:.1f} mana from {source} pool", {
            'source': source,
            'remaining_total': updated_balance['total_available'],
            'remaining_byok': updated_balance['regenerative_mana'],
            'remaining_purchased': updated_balance['purchased_mana'],
        })
        
    except sqlite3.Error as e:
        return (False, f"Database error: {e}", {})
    finally:
        conn.close()


# =============================================================================
# MANA PURCHASES (STRIPE)
# =============================================================================

def get_pricing_tiers(db_path: Path) -> List[Dict]:
    """Get available mana-core pricing tiers."""
    conn = sqlite3.connect(str(db_path), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT * FROM mana_pricing 
            WHERE active = 1 
            ORDER BY display_order
        """)
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()


def record_purchase(db_path: Path, user_id: int, tier_id: int, 
                   stripe_payment_intent_id: str,
                   stripe_charge_id: Optional[str] = None) -> Optional[int]:
    """
    Record a mana-core purchase after successful Stripe payment.
    
    Returns purchase_id if successful, None otherwise.
    """
    conn = sqlite3.connect(str(db_path), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        # Get tier details
        cursor.execute("""
            SELECT mana_amount, price_usd, bonus_percentage 
            FROM mana_pricing WHERE id = ?
        """, (tier_id,))
        tier = cursor.fetchone()
        
        if not tier:
            print(f"[PURCHASE] Invalid tier_id: {tier_id}")
            return None
        
        # Calculate total mana (with bonus)
        base_mana = tier['mana_amount']
        bonus = base_mana * (tier['bonus_percentage'] / 100.0)
        total_mana = base_mana + bonus
        
        now = datetime.utcnow().isoformat() + "Z"
        
        # Record purchase
        cursor.execute("""
            INSERT INTO mana_purchases (
                user_id, amount_mana, cost_usd, 
                stripe_payment_intent_id, stripe_charge_id,
                purchase_date, status
            ) VALUES (?, ?, ?, ?, ?, ?, 'completed')
        """, (user_id, total_mana, tier['price_usd'], 
              stripe_payment_intent_id, stripe_charge_id, now))
        
        purchase_id = cursor.lastrowid
        
        # Add mana to balance
        cursor.execute("""
            UPDATE user_mana_balance
            SET purchased_mana = purchased_mana + ?,
                lifetime_purchased = lifetime_purchased + ?,
                last_updated = ?
            WHERE user_id = ?
        """, (total_mana, total_mana, now, user_id))
        
        conn.commit()
        
        print(f"[PURCHASE] Recorded: {total_mana} mana for ${tier['price_usd']}")
        return purchase_id
        
    except sqlite3.Error as e:
        print(f"[PURCHASE] Failed to record: {e}")
        conn.rollback()
        return None
    finally:
        conn.close()


def get_purchase_history(db_path: Path, user_id: int = 1, limit: int = 10) -> List[Dict]:
    """Get user's purchase history."""
    conn = sqlite3.connect(str(db_path), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT * FROM mana_purchases 
            WHERE user_id = ?
            ORDER BY purchase_date DESC
            LIMIT ?
        """, (user_id, limit))
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()


# =============================================================================
# USAGE ANALYTICS
# =============================================================================

def get_usage_stats(db_path: Path, user_id: int = 1, days: int = 30) -> Dict:
    """Get usage statistics for the past N days."""
    conn = sqlite3.connect(str(db_path), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        cutoff = (datetime.utcnow() - timedelta(days=days)).isoformat() + "Z"
        
        # Total usage
        cursor.execute("""
            SELECT 
                SUM(mana_spent) as total_spent,
                COUNT(*) as operation_count,
                AVG(mana_spent) as avg_per_operation
            FROM mana_usage_log
            WHERE user_id = ? AND timestamp >= ?
        """, (user_id, cutoff))
        totals = dict(cursor.fetchone())
        
        # By operation type
        cursor.execute("""
            SELECT operation, SUM(mana_spent) as spent, COUNT(*) as count
            FROM mana_usage_log
            WHERE user_id = ? AND timestamp >= ?
            GROUP BY operation
            ORDER BY spent DESC
        """, (user_id, cutoff))
        by_operation = [dict(row) for row in cursor.fetchall()]
        
        # By source (BYOK vs purchased)
        cursor.execute("""
            SELECT source, SUM(mana_spent) as spent, COUNT(*) as count
            FROM mana_usage_log
            WHERE user_id = ? AND timestamp >= ?
            GROUP BY source
        """, (user_id, cutoff))
        by_source = [dict(row) for row in cursor.fetchall()]
        
        # Daily breakdown
        cursor.execute("""
            SELECT DATE(timestamp) as date, SUM(mana_spent) as spent
            FROM mana_usage_log
            WHERE user_id = ? AND timestamp >= ?
            GROUP BY DATE(timestamp)
            ORDER BY date DESC
        """, (user_id, cutoff))
        daily = [dict(row) for row in cursor.fetchall()]
        
        return {
            'period_days': days,
            'totals': totals,
            'by_operation': by_operation,
            'by_source': by_source,
            'daily': daily,
        }
        
    finally:
        conn.close()


def check_spending_limits(db_path: Path, user_id: int = 1) -> Dict:
    """Check if user is approaching spending limits."""
    config = get_user_config(db_path, user_id)
    
    # Get today's usage
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0).isoformat() + "Z"
    
    conn = sqlite3.connect(str(db_path), check_same_thread=False)
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT SUM(mana_spent) FROM mana_usage_log
            WHERE user_id = ? AND timestamp >= ?
        """, (user_id, today_start))
        daily_spent = cursor.fetchone()[0] or 0.0
        
        # Get this week's usage
        week_start = (datetime.utcnow() - timedelta(days=7)).isoformat() + "Z"
        cursor.execute("""
            SELECT SUM(mana_spent) FROM mana_usage_log
            WHERE user_id = ? AND timestamp >= ?
        """, (user_id, week_start))
        weekly_spent = cursor.fetchone()[0] or 0.0
        
        daily_cap = config['daily_mana_cap']
        weekly_cap = config['weekly_mana_cap']
        alert_threshold = config['alert_threshold']
        
        return {
            'daily_spent': daily_spent,
            'daily_cap': daily_cap,
            'daily_remaining': daily_cap - daily_spent,
            'daily_percent': (daily_spent / daily_cap) if daily_cap > 0 else 0,
            'daily_alert': (daily_spent / daily_cap) >= alert_threshold if daily_cap > 0 else False,
            'weekly_spent': weekly_spent,
            'weekly_cap': weekly_cap,
            'weekly_remaining': weekly_cap - weekly_spent,
            'weekly_percent': (weekly_spent / weekly_cap) if weekly_cap > 0 else 0,
            'weekly_alert': (weekly_spent / weekly_cap) >= alert_threshold if weekly_cap > 0 else False,
        }
        
    finally:
        conn.close()


# =============================================================================
# API KEY MANAGEMENT (BYOK)
# =============================================================================

def set_api_keys(db_path: Path, user_id: int = 1, 
                 claude_key: Optional[str] = None, 
                 openai_key: Optional[str] = None) -> bool:
    """
    Store user's API keys (BYOK mode).
    
    NOTE: Keys should be encrypted before storage.
    Currently stores plaintext - implement encryption if needed.
    """
    conn = sqlite3.connect(str(db_path), check_same_thread=False)
    cursor = conn.cursor()
    
    try:
        now = datetime.utcnow().isoformat() + "Z"
        
        updates = []
        values = []
        
        if claude_key is not None:
            updates.append("claude_api_key_encrypted = ?")
            values.append(claude_key)  # TODO: Encrypt
        
        if openai_key is not None:
            updates.append("openai_api_key_encrypted = ?")
            values.append(openai_key)  # TODO: Encrypt
        
        if not updates:
            return False
        
        updates.append("key_updated_at = ?")
        values.extend([now, user_id])
        
        cursor.execute(f"""
            UPDATE user_api_keys 
            SET {', '.join(updates)}
            WHERE user_id = ?
        """, values)
        
        conn.commit()
        return True
        
    except sqlite3.Error as e:
        print(f"[API KEYS] Update failed: {e}")
        return False
    finally:
        conn.close()


def get_api_keys(db_path: Path, user_id: int = 1) -> Dict[str, Optional[str]]:
    """
    Retrieve user's API keys (BYOK mode).
    
    Returns decrypted keys (currently plaintext).
    """
    conn = sqlite3.connect(str(db_path), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT claude_api_key_encrypted, openai_api_key_encrypted
            FROM user_api_keys WHERE user_id = ?
        """, (user_id,))
        row = cursor.fetchone()
        
        if row:
            return {
                'claude': row['claude_api_key_encrypted'],  # TODO: Decrypt
                'openai': row['openai_api_key_encrypted'],  # TODO: Decrypt
            }
        else:
            return {'claude': None, 'openai': None}
    finally:
        conn.close()


# =============================================================================
# MODULE EXPORTS
# =============================================================================

__all__ = [
    # Config
    'get_user_config',
    'set_user_config',
    # Balance
    'get_mana_balance',
    'add_purchased_mana',
    'spend_mana_smart',
    # Purchases
    'get_pricing_tiers',
    'record_purchase',
    'get_purchase_history',
    # Analytics
    'get_usage_stats',
    'check_spending_limits',
    # BYOK
    'set_api_keys',
    'get_api_keys',
]
