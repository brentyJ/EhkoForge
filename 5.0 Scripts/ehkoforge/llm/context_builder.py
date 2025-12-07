"""
Context builder for Ehko responses.

Queries the reflection corpus and builds relevant context
for LLM prompts based on user queries.
"""

import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class ReflectionMatch:
    """A matched reflection from the corpus."""
    
    id: str
    title: str
    vault: str
    type: str
    content_preview: str
    relevance_score: float
    is_core_memory: bool = False
    identity_pillar: Optional[str] = None


class EhkoContextBuilder:
    """
    Builds context from the reflection corpus for LLM prompts.
    
    Phase 1: Keyword-based search using SQLite FTS or LIKE queries.
    Phase 2: TF-IDF or embedding-based semantic search.
    """
    
    def __init__(self, database_path: Path, mirrorwell_root: Path):
        """
        Initialise context builder.
        
        Args:
            database_path: Path to ehko_index.db.
            mirrorwell_root: Path to Mirrorwell vault root.
        """
        self.database_path = database_path
        self.mirrorwell_root = mirrorwell_root
        self._has_mirrorwell_extensions = None
    
    def _get_db(self) -> sqlite3.Connection:
        """Get database connection with row factory (thread-safe)."""
        conn = sqlite3.connect(str(self.database_path), check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn
    
    def _check_schema(self, conn: sqlite3.Connection) -> bool:
        """Check if mirrorwell_extensions table exists with expected columns."""
        if self._has_mirrorwell_extensions is not None:
            return self._has_mirrorwell_extensions
        
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='mirrorwell_extensions'
            """)
            if not cursor.fetchone():
                self._has_mirrorwell_extensions = False
                return False
            
            # Check columns
            cursor.execute("PRAGMA table_info(mirrorwell_extensions)")
            columns = [row[1] for row in cursor.fetchall()]
            self._has_mirrorwell_extensions = 'object_id' in columns
            return self._has_mirrorwell_extensions
        except Exception:
            self._has_mirrorwell_extensions = False
            return False
    
    def search_reflections(
        self,
        query: str,
        limit: int = 5,
        include_core_memories: bool = True,
        pillar_filter: Optional[str] = None,
    ) -> list[ReflectionMatch]:
        """
        Search reflections by keyword matching.
        
        Args:
            query: User query to match against.
            limit: Maximum results to return.
            include_core_memories: Boost core memories in results.
            pillar_filter: Filter to specific identity pillar.
        
        Returns:
            List of ReflectionMatch objects sorted by relevance.
        """
        conn = self._get_db()
        cursor = conn.cursor()
        
        # Extract keywords from query (simple tokenisation)
        keywords = [w.lower().strip() for w in query.split() if len(w) > 2]
        
        if not keywords:
            conn.close()
            return []
        
        # Check if we have mirrorwell_extensions
        has_extensions = self._check_schema(conn)
        
        matches = []
        
        for keyword in keywords:
            # Search titles (simpler query without JOIN)
            cursor.execute("""
                SELECT id, title, vault, type, file_path
                FROM reflection_objects
                WHERE LOWER(title) LIKE ?
                LIMIT ?
            """, (f"%{keyword}%", limit * 2))
            
            for row in cursor.fetchall():
                matches.append(self._row_to_match_simple(row, keyword, 0.8))
            
            # Search tags
            try:
                cursor.execute("""
                    SELECT DISTINCT ro.id, ro.title, ro.vault, ro.type, ro.file_path
                    FROM reflection_objects ro
                    JOIN tags t ON ro.id = t.object_id
                    WHERE LOWER(t.tag) LIKE ?
                    LIMIT ?
                """, (f"%{keyword}%", limit * 2))
                
                for row in cursor.fetchall():
                    matches.append(self._row_to_match_simple(row, keyword, 0.6))
            except sqlite3.OperationalError:
                # tags table might not exist
                pass
            
            # Search emotional tags
            try:
                cursor.execute("""
                    SELECT DISTINCT ro.id, ro.title, ro.vault, ro.type, ro.file_path
                    FROM reflection_objects ro
                    JOIN emotional_tags et ON ro.id = et.object_id
                    WHERE LOWER(et.emotion) LIKE ?
                    LIMIT ?
                """, (f"%{keyword}%", limit * 2))
                
                for row in cursor.fetchall():
                    matches.append(self._row_to_match_simple(row, keyword, 0.7))
            except sqlite3.OperationalError:
                # emotional_tags table might not exist
                pass
        
        conn.close()
        
        # Deduplicate and aggregate scores
        seen = {}
        for match in matches:
            if match.id in seen:
                seen[match.id].relevance_score += match.relevance_score
            else:
                seen[match.id] = match
        
        # Sort by relevance and return top N
        sorted_matches = sorted(
            seen.values(), 
            key=lambda m: m.relevance_score, 
            reverse=True
        )
        
        return sorted_matches[:limit]
    
    def _row_to_match_simple(
        self, 
        row: sqlite3.Row, 
        matched_keyword: str,
        base_score: float
    ) -> ReflectionMatch:
        """Convert database row to ReflectionMatch (simple version)."""
        # Try to get content preview from file
        content_preview = self._get_content_preview(row["file_path"])
        
        return ReflectionMatch(
            id=row["id"],
            title=row["title"],
            vault=row["vault"],
            type=row["type"],
            content_preview=content_preview,
            relevance_score=base_score,
            is_core_memory=False,
            identity_pillar=None,
        )
    
    def _get_content_preview(self, file_path: Optional[str], max_chars: int = 500) -> str:
        """
        Extract content preview from reflection file.
        
        Looks for Raw Input section first, then general content.
        """
        if not file_path:
            return ""
        
        try:
            path = Path(file_path)
            if not path.exists():
                # Try relative to Mirrorwell
                path = self.mirrorwell_root / file_path
            
            if not path.exists():
                return ""
            
            content = path.read_text(encoding="utf-8")
            
            # Try to extract Raw Input section
            if "## 0. Raw Input" in content:
                start = content.find("## 0. Raw Input")
                end = content.find("##", start + 20)
                if end == -1:
                    end = len(content)
                raw_input = content[start:end].strip()
                # Remove header
                raw_input = raw_input.replace("## 0. Raw Input (Preserved)", "").strip()
                raw_input = raw_input.replace("## 0. Raw Input", "").strip()
                return raw_input[:max_chars]
            
            # Fallback: extract after frontmatter
            if "---" in content:
                parts = content.split("---", 2)
                if len(parts) >= 3:
                    body = parts[2].strip()
                    return body[:max_chars]
            
            return content[:max_chars]
            
        except Exception:
            return ""
    
    def build_context(
        self,
        query: str,
        max_reflections: int = 3,
        max_tokens_estimate: int = 2000,
    ) -> str:
        """
        Build context string for LLM prompt injection.
        
        Args:
            query: User query to find relevant context for.
            max_reflections: Maximum reflections to include.
            max_tokens_estimate: Rough token budget (chars / 4).
        
        Returns:
            Formatted context string for system prompt.
        """
        matches = self.search_reflections(query, limit=max_reflections)
        
        if not matches:
            return ""
        
        # Build context blocks
        blocks = []
        char_budget = max_tokens_estimate * 4  # Rough chars-to-tokens
        chars_used = 0
        
        for match in matches:
            block = f"""### {match.title}
Type: {match.type} | Vault: {match.vault}

{match.content_preview}
"""
            if chars_used + len(block) > char_budget:
                break
            
            blocks.append(block)
            chars_used += len(block)
        
        return "\n---\n".join(blocks)
    
    def get_core_memories(self, limit: int = 10) -> list[ReflectionMatch]:
        """
        Retrieve core memories for identity grounding.
        
        Always available for Ehko to reference regardless of query.
        """
        conn = self._get_db()
        cursor = conn.cursor()
        
        # Check if mirrorwell_extensions exists
        if not self._check_schema(conn):
            conn.close()
            return []
        
        try:
            cursor.execute("""
                SELECT ro.id, ro.title, ro.vault, ro.type, ro.file_path,
                       me.core_memory, me.identity_pillar
                FROM reflection_objects ro
                JOIN mirrorwell_extensions me ON ro.id = me.object_id
                WHERE me.core_memory = 1
                ORDER BY ro.updated DESC
                LIMIT ?
            """, (limit,))
            
            matches = []
            for row in cursor.fetchall():
                content_preview = self._get_content_preview(row["file_path"])
                matches.append(ReflectionMatch(
                    id=row["id"],
                    title=row["title"],
                    vault=row["vault"],
                    type=row["type"],
                    content_preview=content_preview,
                    relevance_score=1.0,
                    is_core_memory=True,
                    identity_pillar=row["identity_pillar"],
                ))
            
            conn.close()
            return matches
        except sqlite3.OperationalError:
            conn.close()
            return []
    
    def get_pillar_summary(self, pillar_name: str) -> Optional[str]:
        """
        Get summary content for an identity pillar.
        
        Args:
            pillar_name: Pillar name (e.g., "The Web", "The Thread").
        
        Returns:
            Pillar summary content or None.
        """
        # Look for pillar file in Mirrorwell
        pillar_dir = self.mirrorwell_root / "1_Core Identity" / "1.1 Pillars"
        
        if not pillar_dir.exists():
            return None
        
        # Find matching pillar file
        for file in pillar_dir.glob("*.md"):
            if pillar_name.lower().replace("the ", "") in file.stem.lower():
                try:
                    content = file.read_text(encoding="utf-8")
                    # Extract after frontmatter
                    if "---" in content:
                        parts = content.split("---", 2)
                        if len(parts) >= 3:
                            return parts[2].strip()[:1500]
                except Exception:
                    pass
        
        return None
