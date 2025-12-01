#!/usr/bin/env python3
"""
Seed Test Ingots
Creates sample ingots for UI testing without running full smelt pipeline.
"""

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from uuid import uuid4

DB_PATH = Path("G:/Other computers/Ehko/Obsidian/EhkoForge/_data/ehko_index.db")

TEST_INGOTS = [
    {
        "summary": "A deep-seated need for control stems from childhood unpredictability. When external circumstances feel chaotic, the instinct is to micromanage what can be controlled, often at the cost of flexibility and connection.",
        "themes": ["control", "anxiety", "childhood", "coping-mechanisms"],
        "emotional_tags": ["fear", "anxiety"],
        "patterns": ["hypervigilance", "micromanagement", "avoidance"],
        "significance": 0.85,
        "confidence": 0.8,
        "layer_type": "pattern",
    },
    {
        "summary": "Family relationships are complicated by a history of emotional unavailability. There's a tension between wanting connection and protecting against disappointment.",
        "themes": ["family", "relationships", "boundaries", "vulnerability"],
        "emotional_tags": ["loneliness", "ambivalence", "hope"],
        "patterns": ["emotional-guarding", "approach-avoidance"],
        "significance": 0.72,
        "confidence": 0.75,
        "layer_type": "trait",
    },
    {
        "summary": "Building things that outlast you matters deeply. The EhkoForge project represents a desire to leave something meaningful behind, to be understood after death.",
        "themes": ["legacy", "mortality", "creation", "meaning"],
        "emotional_tags": ["hope", "pride", "fear"],
        "patterns": ["meaning-making", "future-orientation"],
        "significance": 0.91,
        "confidence": 0.9,
        "layer_type": "value",
    },
    {
        "summary": "ADHD isn't a limitation to overcome but a different operating system. Lateral thinking and hyperfocus are strengths when channelled into aligned work.",
        "themes": ["adhd", "neurodivergence", "identity", "strengths"],
        "emotional_tags": ["pride", "gratitude"],
        "patterns": ["reframing", "self-acceptance"],
        "significance": 0.65,
        "confidence": 0.85,
        "layer_type": "trait",
    },
    {
        "summary": "The police resignation was a moment of integrity under pressure. Choosing ethics over career security, even when the system was rigged against you.",
        "themes": ["integrity", "career", "injustice", "resilience"],
        "emotional_tags": ["anger", "pride", "sadness"],
        "patterns": ["principled-stance", "resilience"],
        "significance": 0.78,
        "confidence": 0.7,
        "layer_type": "memory",
    },
]


def seed_ingots():
    """Insert test ingots into database."""
    print(f"Seeding test ingots into: {DB_PATH}")
    print("-" * 50)
    
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    now = datetime.utcnow().isoformat() + "Z"
    
    for i, ingot_data in enumerate(TEST_INGOTS):
        ingot_id = str(uuid4())
        
        cursor.execute("""
            INSERT INTO ingots (
                id, created_at, updated_at, status, significance, confidence,
                summary, themes_json, emotional_tags_json, patterns_json,
                source_count, earliest_source_date, latest_source_date,
                last_analysis_at, analysis_model, analysis_pass
            ) VALUES (?, ?, ?, 'surfaced', ?, ?, ?, ?, ?, ?, 1, ?, ?, ?, 'test-seed', 1)
        """, (
            ingot_id,
            now,
            now,
            ingot_data["significance"],
            ingot_data["confidence"],
            ingot_data["summary"],
            json.dumps(ingot_data["themes"]),
            json.dumps(ingot_data["emotional_tags"]),
            json.dumps(ingot_data["patterns"]),
            now,
            now,
            now,
        ))
        
        # Add a fake source
        cursor.execute("""
            INSERT INTO ingot_sources (ingot_id, source_type, source_id, excerpt, added_at)
            VALUES (?, 'test', 'seed-data', ?, ?)
        """, (ingot_id, f"Test excerpt for ingot {i+1}", now))
        
        # Log creation
        cursor.execute("""
            INSERT INTO ingot_history (ingot_id, event_type, event_at, trigger)
            VALUES (?, 'created', ?, 'test-seed')
        """, (ingot_id, now))
        
        tier = get_tier(ingot_data["significance"])
        print(f"  [{tier.upper():6}] {ingot_data['summary'][:60]}...")
    
    conn.commit()
    conn.close()
    
    print("-" * 50)
    print(f"✓ Seeded {len(TEST_INGOTS)} test ingots")
    print("  Refresh the Forge UI to see them")


def get_tier(significance):
    if significance >= 0.9:
        return "mythic"
    elif significance >= 0.75:
        return "gold"
    elif significance >= 0.5:
        return "silver"
    elif significance >= 0.25:
        return "iron"
    else:
        return "copper"


if __name__ == "__main__":
    seed_ingots()
