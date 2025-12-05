---
title: "ReCog Core Engine Specification"
vault: "EhkoForge"
type: "specification"
category: "Core Architecture"
status: active
version: "1.0"
created: 2025-12-05
updated: 2025-12-05
tags: [recog, engine, architecture, standalone]
supersedes:
  - "ReCog_Engine_Spec_v0_2.md"
---

# RECOG CORE ENGINE SPECIFICATION v1.0

## 1. Overview

### 1.1 What ReCog Is

**ReCog** (Recursive Cognition Engine) is a standalone text analysis engine that extracts, correlates, and synthesises insights from unstructured text corpora.

It is:
- **Domain-agnostic** — Works on any text: transcripts, documents, chat logs, research notes
- **Recursive** — Each processing pass refines and connects insights from previous passes
- **Portable** — No dependencies on any specific application or database schema
- **LLM-orchestrated** — Uses language models for semantic analysis, not keyword matching

### 1.2 What ReCog Is Not

- Not an application — It's an engine that applications integrate
- Not a database — It processes data; storage is the adapter's responsibility
- Not a chatbot — It analyses content, doesn't generate conversational responses
- Not magic — Defined stages, clear inputs/outputs, explicit termination conditions

### 1.3 Core Value Proposition

**Problem:** Organisations accumulate vast amounts of unstructured text (meetings, interviews, research, communications) but lack tools to systematically extract patterns and connections.

**Solution:** ReCog processes text corpora through iterative analysis passes, surfacing insights that humans would miss and connections that span documents.

---

## 2. Architecture

### 2.1 High-Level Structure

```
┌─────────────────────────────────────────────────────────────────┐
│                         RECOG ENGINE                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐                                               │
│  │   ADAPTER    │  (Application-specific integration)           │
│  │              │                                               │
│  │  - Input     │◄─── Raw text, context, configuration          │
│  │  - Output    │───► Structured insights, patterns             │
│  │  - Context   │◄─── Domain knowledge (optional)               │
│  └──────┬───────┘                                               │
│         │                                                       │
│         ▼                                                       │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                      CORE PIPELINE                        │   │
│  │                                                           │   │
│  │   ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌───────┐ │   │
│  │   │ EXTRACT │───►│ CORRELATE│───►│SYNTHESISE│───►│ OUTPUT│ │   │
│  │   │ (Tier 1)│    │ (Tier 2) │    │ (Tier 3) │    │       │ │   │
│  │   └─────────┘    └─────────┘    └─────────┘    └───────┘ │   │
│  │        ▲                                                  │   │
│  │        │                                                  │   │
│  │   ┌─────────┐                                             │   │
│  │   │ SIGNAL  │  (Tier 0 - No LLM)                          │   │
│  │   └─────────┘                                             │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Processing Tiers

| Tier | Name | LLM Cost | Purpose |
|------|------|----------|---------|
| 0 | Signal | None | Structural analysis, keyword detection, metadata extraction |
| 1 | Extract | Low-Medium | Insight extraction from individual documents |
| 2 | Correlate | Medium | Pattern detection across insights |
| 3 | Synthesise | High | Deep analysis, contradiction resolution, report generation |

### 2.3 Module Structure

```
recog_engine/
├── core/
│   ├── __init__.py
│   ├── types.py          # Data classes: Insight, Pattern, Corpus, Document
│   ├── signal.py         # Tier 0: Zero-cost preprocessing
│   ├── extractor.py      # Tier 1: Document → Insights
│   ├── correlator.py     # Tier 2: Insights → Patterns
│   └── synthesizer.py    # Tier 3: Patterns → Synthesis
├── adapters/
│   ├── __init__.py
│   ├── base.py           # Abstract adapter interface
│   └── memory.py         # In-memory adapter (for testing/standalone)
├── llm/
│   ├── __init__.py
│   ├── base.py           # Abstract LLM provider
│   └── config.py         # Model routing, API configuration
├── config.py             # Engine configuration
└── engine.py             # Main orchestrator
```

---

## 3. Data Types

### 3.1 Core Types

All types are plain Python dataclasses, JSON-serialisable, with no external dependencies.

```python
@dataclass
class Document:
    """A single unit of text to be processed."""
    id: str                          # Unique identifier
    content: str                     # Raw text
    source_type: str                 # e.g., "transcript", "document", "chat"
    source_ref: str                  # Original location/identifier
    metadata: Dict[str, Any]         # Arbitrary metadata
    created_at: datetime
    signals: Optional[Dict] = None   # Tier 0 output


@dataclass
class Insight:
    """A discrete insight extracted from one or more documents."""
    id: str
    summary: str                     # 1-3 sentence distillation
    themes: List[str]                # Categorical tags
    significance: float              # 0.0-1.0 importance score
    confidence: float                # 0.0-1.0 extraction confidence
    source_ids: List[str]            # Document IDs this came from
    excerpts: List[str]              # Supporting quotes
    metadata: Dict[str, Any]         # Type-specific data
    created_at: datetime
    pass_count: int = 1              # How many extraction passes


@dataclass
class Pattern:
    """A connection or theme across multiple insights."""
    id: str
    summary: str                     # Pattern description
    pattern_type: str                # "recurring", "contradiction", "evolution", "cluster"
    insight_ids: List[str]           # Insights that form this pattern
    strength: float                  # 0.0-1.0 pattern strength
    metadata: Dict[str, Any]
    created_at: datetime


@dataclass
class Synthesis:
    """High-level conclusion from pattern analysis."""
    id: str
    title: str
    content: str                     # Full synthesis text
    pattern_ids: List[str]           # Patterns contributing to this
    insight_ids: List[str]           # Direct insight references
    synthesis_type: str              # "report", "recommendation", "summary"
    metadata: Dict[str, Any]
    created_at: datetime


@dataclass
class Corpus:
    """A collection of documents being processed together."""
    id: str
    name: str
    documents: List[Document]
    insights: List[Insight]
    patterns: List[Pattern]
    syntheses: List[Synthesis]
    config: Dict[str, Any]           # Processing configuration
    created_at: datetime
    updated_at: datetime
```

### 3.2 Processing State

```python
@dataclass
class ProcessingState:
    """Tracks processing progress for a corpus."""
    corpus_id: str
    current_tier: int                # 0-3
    documents_processed: int
    documents_total: int
    insights_extracted: int
    patterns_found: int
    passes_completed: int
    status: str                      # "pending", "processing", "complete", "failed"
    error: Optional[str]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
```

---

## 4. Adapter Interface

### 4.1 Abstract Base

Adapters connect ReCog to specific applications. They handle:
- **Input**: Loading documents into the engine
- **Output**: Storing/displaying results
- **Context**: Providing domain-specific knowledge
- **Persistence**: Saving state between runs

```python
from abc import ABC, abstractmethod
from typing import List, Optional, Iterator
from recog_engine.core.types import Document, Insight, Pattern, Synthesis, Corpus


class RecogAdapter(ABC):
    """Base class for ReCog adapters."""
    
    # ─────────────────────────────────────────────────────────────
    # INPUT: Loading documents
    # ─────────────────────────────────────────────────────────────
    
    @abstractmethod
    def load_documents(self, **filters) -> Iterator[Document]:
        """
        Yield documents to process.
        
        Filters are adapter-specific (date range, source type, etc.)
        """
        pass
    
    @abstractmethod
    def get_document(self, doc_id: str) -> Optional[Document]:
        """Retrieve a specific document by ID."""
        pass
    
    # ─────────────────────────────────────────────────────────────
    # OUTPUT: Storing results
    # ─────────────────────────────────────────────────────────────
    
    @abstractmethod
    def save_insight(self, insight: Insight) -> None:
        """Persist an extracted insight."""
        pass
    
    @abstractmethod
    def save_pattern(self, pattern: Pattern) -> None:
        """Persist a detected pattern."""
        pass
    
    @abstractmethod
    def save_synthesis(self, synthesis: Synthesis) -> None:
        """Persist a synthesis."""
        pass
    
    @abstractmethod
    def get_insights(self, **filters) -> List[Insight]:
        """Retrieve insights, optionally filtered."""
        pass
    
    @abstractmethod
    def get_patterns(self, **filters) -> List[Pattern]:
        """Retrieve patterns, optionally filtered."""
        pass
    
    # ─────────────────────────────────────────────────────────────
    # CONTEXT: Domain knowledge (optional)
    # ─────────────────────────────────────────────────────────────
    
    def get_context(self) -> Optional[str]:
        """
        Return domain context to include in LLM prompts.
        
        Examples:
        - EhkoForge: Identity pillars, core memories
        - Enterprise: Company glossary, project background
        - Research: Prior findings, hypotheses
        
        Returns None if no context available.
        """
        return None
    
    def get_existing_themes(self) -> List[str]:
        """
        Return known themes for consistency.
        
        Helps extraction use consistent terminology.
        """
        return []
    
    # ─────────────────────────────────────────────────────────────
    # STATE: Processing persistence
    # ─────────────────────────────────────────────────────────────
    
    def save_state(self, state: ProcessingState) -> None:
        """Persist processing state (optional)."""
        pass
    
    def load_state(self, corpus_id: str) -> Optional[ProcessingState]:
        """Load processing state (optional)."""
        return None
```

### 4.2 Example: Memory Adapter

For testing and CLI usage — stores everything in memory.

```python
class MemoryAdapter(RecogAdapter):
    """In-memory adapter for testing and standalone use."""
    
    def __init__(self):
        self.documents: Dict[str, Document] = {}
        self.insights: Dict[str, Insight] = {}
        self.patterns: Dict[str, Pattern] = {}
        self.syntheses: Dict[str, Synthesis] = {}
    
    def load_documents(self, **filters) -> Iterator[Document]:
        for doc in self.documents.values():
            yield doc
    
    def get_document(self, doc_id: str) -> Optional[Document]:
        return self.documents.get(doc_id)
    
    def save_insight(self, insight: Insight) -> None:
        self.insights[insight.id] = insight
    
    # ... etc
```

### 4.3 Example: EhkoForge Adapter

Maps ReCog types to EhkoForge's data model.

```python
class EhkoForgeAdapter(RecogAdapter):
    """
    Adapter for EhkoForge digital identity system.
    
    Mappings:
    - Document → forge_messages, transcript_segments, reflection_objects
    - Insight → ingots table
    - Pattern → ingots with type='pattern'
    - Synthesis → ehko_personality_layers
    - Context → identity_pillars, core_memory_index
    """
    
    def __init__(self, db_path: Path, mirrorwell_path: Path):
        self.db_path = db_path
        self.mirrorwell_path = mirrorwell_path
    
    def load_documents(self, source_type: str = None, 
                       since: datetime = None) -> Iterator[Document]:
        """Load chat sessions, transcripts, or reflections."""
        # Implementation queries ehko_index.db
        pass
    
    def save_insight(self, insight: Insight) -> None:
        """Save to ingots table with EhkoForge-specific fields."""
        # Maps: summary → summary, themes → themes_json, etc.
        # Adds: layer_type, emotional_tags (from insight.metadata)
        pass
    
    def get_context(self) -> str:
        """Load identity pillars and core memories as context."""
        # Queries identity_pillars, core_memory_index
        # Returns formatted context string
        pass
```

---

## 5. Processing Pipeline

### 5.1 Tier 0: Signal Extraction

**Purpose:** Zero-LLM-cost preprocessing to guide later analysis.

**Input:** Raw document text

**Output:** Signal dictionary containing:
- Word/character counts
- Emotion keyword matches
- Intensity markers (exclamations, all-caps, absolutes)
- Question patterns (self-inquiry, rhetorical)
- Temporal references (past, present, future, habitual)
- Basic entity detection (people, titles)
- Structural analysis (paragraphs, sentences, speaker changes)
- Composite flags (high_emotion, self_reflective, narrative, analytical)

**Implementation:** Pure Python, no external dependencies. Already implemented in `tier0.py`.

### 5.2 Tier 1: Extraction

**Purpose:** Extract discrete insights from individual documents.

**Input:**
- Document content
- Tier 0 signals
- Adapter context (optional)
- Existing themes (for consistency)

**Process:**
```
FOR each document in batch:
    1. Load document + signals
    2. Build extraction prompt:
       - Include signals summary as hints
       - Include context if available
       - Include existing themes for vocabulary consistency
    3. LLM call (low-cost model)
    4. Parse response into Insight objects
    5. Deduplicate against existing insights (similarity check)
    6. Yield new/updated insights
```

**Output:** List of Insight objects

**Termination:**
- All documents in batch processed
- OR max_documents limit reached

**LLM Prompt Structure:**
```
You are analysing text to extract meaningful insights.

## Context (if provided)
{adapter_context}

## Document Signals
{tier0_summary}

## Known Themes (use when applicable)
{existing_themes}

## Content
{document_content}

## Task
Extract 0-5 insights. An insight is a discrete observation worth preserving.

For each insight provide:
- summary: 1-3 sentence distillation (not a quote)
- themes: 2-5 categorical tags (lowercase, hyphenated)
- significance: 0.0-1.0 importance score
- confidence: 0.0-1.0 extraction confidence
- excerpt: Most relevant supporting quote

Return JSON only.
```

### 5.3 Tier 2: Correlation

**Purpose:** Find patterns across multiple insights.

**Input:**
- All insights from corpus (or filtered subset)
- Adapter context (optional)

**Process:**
```
1. Group insights by theme overlap

2. FOR each theme cluster (size >= 3):
    LLM call:
    - "What pattern connects these insights?"
    - "Is this recurring, contradictory, or evolutionary?"
    
    IF pattern found:
        Create Pattern object
        Link source insights
        Update insight significance scores

3. FOR unclustered insights:
    LLM call:
    - "Does this connect to any existing pattern?"
    - "Does this relate to the provided context?"
    
    IF connection found:
        Update Pattern or create new

4. Merge similar patterns

LOOP TERMINATION:
- All clusters processed
- OR max_passes reached
- OR yield drops below threshold (< 5% new connections)
```

**Output:** List of Pattern objects

**Pattern Types:**
- `recurring` — Same theme appears across multiple sources/times
- `contradiction` — Conflicting insights (may indicate evolution or error)
- `evolution` — Theme changes over time
- `cluster` — Related insights without clear temporal relationship

### 5.4 Tier 3: Synthesis

**Purpose:** Deep analysis producing human-readable conclusions.

**Input:**
- Patterns from Tier 2
- High-significance insights
- Adapter context

**Process:**
```
1. Select patterns above significance threshold

2. LLM call (high-capability model):
   - Comprehensive prompt with all relevant patterns
   - Request structured synthesis
   - May request specific format (report, recommendations, summary)

3. Parse into Synthesis object

4. Link back to source patterns and insights
```

**Output:** Synthesis object(s)

**Synthesis Types:**
- `report` — Comprehensive analysis document
- `recommendation` — Actionable insights
- `summary` — Executive overview
- `narrative` — Chronological story (for personal/biographical use)

---

## 6. Engine Orchestration

### 6.1 Main Engine Class

```python
class RecogEngine:
    """Main orchestrator for ReCog processing."""
    
    def __init__(self, adapter: RecogAdapter, config: RecogConfig):
        self.adapter = adapter
        self.config = config
        self.llm = self._init_llm()
    
    def process_corpus(self, 
                       corpus_id: str,
                       tiers: List[int] = [0, 1, 2],
                       **filters) -> ProcessingState:
        """
        Run processing pipeline on a corpus.
        
        Args:
            corpus_id: Identifier for this processing run
            tiers: Which tiers to run (default: 0, 1, 2)
            **filters: Passed to adapter.load_documents()
            
        Returns:
            Final processing state
        """
        pass
    
    def run_tier(self, tier: int, corpus_id: str) -> None:
        """Run a specific tier on a corpus."""
        pass
    
    def get_state(self, corpus_id: str) -> ProcessingState:
        """Get current processing state."""
        pass
```

### 6.2 Configuration

```python
@dataclass
class RecogConfig:
    """Engine configuration."""
    
    # Tier 0
    signal_enabled: bool = True
    
    # Tier 1: Extraction
    extraction_model: str = "gpt-4o-mini"      # Low-cost, high-volume
    extraction_batch_size: int = 10
    extraction_max_passes: int = 3
    similarity_threshold: float = 0.7          # For deduplication
    
    # Tier 2: Correlation
    correlation_model: str = "claude-sonnet"   # Better reasoning
    correlation_min_cluster: int = 3
    correlation_max_passes: int = 2
    correlation_yield_threshold: float = 0.05
    
    # Tier 3: Synthesis
    synthesis_model: str = "claude-opus"       # Highest capability
    synthesis_min_patterns: int = 3
    synthesis_significance_threshold: float = 0.5
    
    # General
    max_content_tokens: int = 8000             # Truncation limit
    temperature: float = 0.3                   # Lower = more consistent
```

---

## 7. Usage Examples

### 7.1 Standalone CLI

```python
from recog_engine import RecogEngine, RecogConfig
from recog_engine.adapters import MemoryAdapter

# Create adapter and load documents
adapter = MemoryAdapter()
adapter.add_document(Document(
    id="doc1",
    content="Meeting transcript text...",
    source_type="transcript",
    source_ref="2025-01-15-standup.txt",
    metadata={},
    created_at=datetime.now()
))

# Configure and run
config = RecogConfig(extraction_model="gpt-4o-mini")
engine = RecogEngine(adapter, config)
state = engine.process_corpus("meeting-analysis", tiers=[0, 1, 2])

# Get results
insights = adapter.get_insights()
patterns = adapter.get_patterns()
```

### 7.2 EhkoForge Integration

```python
from recog_engine import RecogEngine, RecogConfig
from recog_engine.adapters.ehkoforge import EhkoForgeAdapter

# EhkoForge-specific adapter
adapter = EhkoForgeAdapter(
    db_path=Path("ehko_index.db"),
    mirrorwell_path=Path("Mirrorwell/")
)

config = RecogConfig()
engine = RecogEngine(adapter, config)

# Process recent chat sessions
state = engine.process_corpus(
    corpus_id="daily-reflection",
    source_type="chat_session",
    since=datetime.now() - timedelta(days=1)
)

# Results automatically saved to ingots table via adapter
```

### 7.3 Enterprise: Research Analysis

```python
from recog_engine import RecogEngine, RecogConfig
from recog_engine.adapters import FileSystemAdapter

# Load research documents
adapter = FileSystemAdapter(
    input_dir=Path("research/interviews/"),
    output_dir=Path("research/analysis/")
)

# Custom context
adapter.set_context("""
Research project: Customer journey pain points
Hypotheses:
1. Onboarding friction causes early churn
2. Support response time correlates with NPS
""")

config = RecogConfig(
    synthesis_model="claude-opus",  # Best for research synthesis
)

engine = RecogEngine(adapter, config)
state = engine.process_corpus("q4-research", tiers=[0, 1, 2, 3])

# Tier 3 produces research report
synthesis = adapter.get_syntheses()[0]
print(synthesis.content)
```

---

## 8. Implementation Order

### Phase 1: Core Types & Signal (Current Sprint)
- [ ] `core/types.py` — Data classes
- [ ] `core/signal.py` — Refactor tier0.py to use new types
- [ ] `adapters/base.py` — Abstract interface
- [ ] `adapters/memory.py` — In-memory for testing

### Phase 2: Extraction
- [ ] `core/extractor.py` — Tier 1 implementation
- [ ] `llm/base.py` — Abstract LLM provider
- [ ] `llm/config.py` — Model routing
- [ ] `engine.py` — Basic orchestration (Tier 0-1 only)

### Phase 3: Correlation
- [ ] `core/correlator.py` — Tier 2 implementation
- [ ] Pattern detection prompts
- [ ] Similarity/deduplication logic

### Phase 4: Synthesis & Adapters
- [ ] `core/synthesizer.py` — Tier 3 implementation
- [ ] `adapters/ehkoforge.py` — EhkoForge integration
- [ ] Full pipeline testing

### Phase 5: Polish
- [ ] CLI interface
- [ ] Configuration file support
- [ ] Logging and monitoring
- [ ] Documentation

---

## 9. Migration Path

### From Current Implementation

The existing `smelt.py` and `tier0.py` contain working logic that will be refactored:

| Current | New Location | Changes |
|---------|--------------|---------|
| `tier0.py` | `core/signal.py` | Minimal — wrap in Document-aware interface |
| `smelt.py` extraction | `core/extractor.py` | Decouple from DB, use Insight type |
| `smelt.py` queue logic | `adapters/ehkoforge.py` | Move to adapter |
| `smelt.py` surfacing | `adapters/ehkoforge.py` | EhkoForge-specific concept |
| Ingot tables | `adapters/ehkoforge.py` | Adapter maps Insight → ingot |

### Deprecation

Once ReCog Core is operational:
- `smelt.py` → Deprecated, replaced by `engine.py` + `ehkoforge.py` adapter
- `Ingot_System_Schema_v0_1.md` → Becomes "EhkoForge Adapter Schema"
- `Smelt_Processor_Spec_v0_1.md` → Superseded by this spec

---

## 10. Terminology Mapping

For client-facing documentation, avoid EhkoForge-specific terms:

| EhkoForge Term | ReCog Term | Definition |
|----------------|------------|------------|
| Ingot | Insight | Discrete extracted observation |
| Smelt | Extract | Tier 1 processing |
| Forge | Synthesise | Tier 3 processing |
| Surfacing | Promotion | Moving insight to review queue |
| Personality Layer | (Adapter output) | EhkoForge-specific synthesis target |
| Authority | (Not applicable) | EhkoForge gamification |
| Mana | (Not applicable) | EhkoForge resource economy |

---

## 11. Licensing

ReCog Engine is licensed under **AGPLv3**.

Commercial licensing available for:
- Closed-source integration
- Enterprise support agreements
- Custom adapter development

Contact: brent@ehkolabs.io

---

**Changelog**
- v1.0 — 2025-12-05 — Initial specification. Standalone engine architecture, adapter pattern, processing tiers, data types. Supersedes ReCog_Engine_Spec_v0_2.md.
