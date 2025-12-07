"""
EhkoForge Document Ingestion Module v1.0

Bulk document processing pipeline for ReCog engine.
Supports PDF, markdown, text, and message exports.

Usage:
    from ingestion import IngestService
    
    service = IngestService(db_path)
    service.process_inbox()  # Process all files in _inbox/
    service.ingest_file(path)  # Process single file
"""

from .service import IngestService
from .chunker import Chunker
from .types import IngestedDocument, DocumentChunk, ParsedContent

__version__ = "1.0"
__all__ = ["IngestService", "Chunker", "IngestedDocument", "DocumentChunk", "ParsedContent"]
