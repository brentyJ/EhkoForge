-- Document Ingestion Schema v0.1
-- EhkoForge - Bulk document processing for ReCog
-- Created: 2025-12-06

-- =============================================================================
-- INGESTED DOCUMENTS
-- Track all documents dropped into the system
-- =============================================================================

CREATE TABLE IF NOT EXISTS ingested_documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT NOT NULL,
    file_hash TEXT UNIQUE,              -- SHA256, prevents duplicates
    file_type TEXT NOT NULL,            -- pdf, md, txt, whatsapp, sms, email
    file_path TEXT,                     -- Original path (for reference)
    file_size INTEGER,                  -- Bytes
    ingested_at TEXT DEFAULT (datetime('now')),
    
    -- Extracted metadata
    doc_date TEXT,                      -- When was this written/sent?
    doc_author TEXT,                    -- Who wrote it?
    doc_subject TEXT,                   -- Subject line, title, filename stem
    doc_recipients TEXT,                -- JSON array if applicable
    
    -- Additional metadata (JSON for flexibility)
    metadata TEXT,                      -- {"thread_id": "...", "reply_to": "...", etc}
    
    -- Processing state
    status TEXT DEFAULT 'pending',      -- pending, chunking, processing, complete, failed
    chunk_count INTEGER DEFAULT 0,
    insights_extracted INTEGER DEFAULT 0,
    error_message TEXT,
    completed_at TEXT
);

CREATE INDEX IF NOT EXISTS idx_ingested_docs_status ON ingested_documents(status);
CREATE INDEX IF NOT EXISTS idx_ingested_docs_type ON ingested_documents(file_type);
CREATE INDEX IF NOT EXISTS idx_ingested_docs_date ON ingested_documents(doc_date);
CREATE INDEX IF NOT EXISTS idx_ingested_docs_hash ON ingested_documents(file_hash);

-- =============================================================================
-- DOCUMENT CHUNKS
-- Content split into processable pieces with source tracing
-- =============================================================================

CREATE TABLE IF NOT EXISTS document_chunks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id INTEGER NOT NULL REFERENCES ingested_documents(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL,       -- Order within document
    content TEXT NOT NULL,
    token_count INTEGER,
    
    -- Position in source (for reconstruction)
    start_char INTEGER,
    end_char INTEGER,
    page_number INTEGER,                -- For PDFs
    
    -- Context preservation
    preceding_context TEXT,             -- ~200 chars before chunk
    following_context TEXT,             -- ~200 chars after chunk
    
    -- Processing state
    tier0_processed INTEGER DEFAULT 0,
    tier0_signals TEXT,                 -- JSON: extracted signals
    recog_processed INTEGER DEFAULT 0,
    recog_insight_id TEXT,              -- Links to ingots table
    
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_chunks_document ON document_chunks(document_id);
CREATE INDEX IF NOT EXISTS idx_chunks_unprocessed ON document_chunks(recog_processed) WHERE recog_processed = 0;

-- =============================================================================
-- DOCUMENT ENTITIES
-- Extracted entities for cross-document correlation
-- =============================================================================

CREATE TABLE IF NOT EXISTS document_entities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id INTEGER NOT NULL REFERENCES ingested_documents(id) ON DELETE CASCADE,
    chunk_id INTEGER REFERENCES document_chunks(id) ON DELETE SET NULL,
    
    entity_type TEXT NOT NULL,          -- person, date, place, event, reference, email, phone, project
    entity_value TEXT NOT NULL,         -- The actual entity
    entity_normalised TEXT,             -- Normalised form (lowercase, trimmed, etc)
    
    confidence REAL DEFAULT 1.0,        -- 0.0-1.0
    extraction_method TEXT,             -- regex, llm, metadata
    context TEXT,                       -- Surrounding text for disambiguation
    
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_entities_document ON document_entities(document_id);
CREATE INDEX IF NOT EXISTS idx_entities_type ON document_entities(entity_type);
CREATE INDEX IF NOT EXISTS idx_entities_value ON document_entities(entity_normalised);

-- =============================================================================
-- DOCUMENT RELATIONSHIPS
-- Cross-document links discovered through correlation
-- =============================================================================

CREATE TABLE IF NOT EXISTS document_relationships (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    doc_a_id INTEGER NOT NULL REFERENCES ingested_documents(id) ON DELETE CASCADE,
    doc_b_id INTEGER NOT NULL REFERENCES ingested_documents(id) ON DELETE CASCADE,
    
    relationship_type TEXT NOT NULL,    -- reply_to, references, same_thread, same_topic, 
                                        -- temporal_sequence, same_author, mentions_same_entity
    
    confidence REAL DEFAULT 0.5,        -- 0.0-1.0
    evidence TEXT,                      -- JSON: why we think they're linked
    
    -- For thread reconstruction
    thread_id TEXT,                     -- Groups related docs into threads
    sequence_order INTEGER,             -- Position in thread/sequence
    
    created_by TEXT,                    -- rule, llm, user
    created_at TEXT DEFAULT (datetime('now')),
    
    UNIQUE(doc_a_id, doc_b_id, relationship_type)
);

CREATE INDEX IF NOT EXISTS idx_relationships_doc_a ON document_relationships(doc_a_id);
CREATE INDEX IF NOT EXISTS idx_relationships_doc_b ON document_relationships(doc_b_id);
CREATE INDEX IF NOT EXISTS idx_relationships_thread ON document_relationships(thread_id);
CREATE INDEX IF NOT EXISTS idx_relationships_type ON document_relationships(relationship_type);

-- =============================================================================
-- ENTITY LINKS
-- Connect same entities across documents
-- =============================================================================

CREATE TABLE IF NOT EXISTS entity_links (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_a_id INTEGER NOT NULL REFERENCES document_entities(id) ON DELETE CASCADE,
    entity_b_id INTEGER NOT NULL REFERENCES document_entities(id) ON DELETE CASCADE,
    
    link_type TEXT DEFAULT 'same',      -- same, related, alias
    confidence REAL DEFAULT 0.5,
    
    created_at TEXT DEFAULT (datetime('now')),
    
    UNIQUE(entity_a_id, entity_b_id)
);

CREATE INDEX IF NOT EXISTS idx_entity_links_a ON entity_links(entity_a_id);
CREATE INDEX IF NOT EXISTS idx_entity_links_b ON entity_links(entity_b_id);

-- =============================================================================
-- INGESTION LOG
-- Track processing history
-- =============================================================================

CREATE TABLE IF NOT EXISTS ingestion_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id INTEGER REFERENCES ingested_documents(id) ON DELETE CASCADE,
    action TEXT NOT NULL,               -- queued, parsing, chunking, tier0, tier1, complete, failed
    details TEXT,                       -- JSON with action-specific info
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_ingestion_log_doc ON ingestion_log(document_id);
