"""
Ingestion type definitions.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict, Any


@dataclass
class ParsedContent:
    """Result from a parser."""
    text: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    pages: Optional[List[str]] = None  # For PDFs, text per page
    
    # Extracted metadata
    title: Optional[str] = None
    author: Optional[str] = None
    date: Optional[str] = None
    subject: Optional[str] = None
    recipients: Optional[List[str]] = None


@dataclass
class DocumentChunk:
    """A chunk of document content."""
    content: str
    chunk_index: int
    token_count: int
    
    # Position in source
    start_char: int
    end_char: int
    page_number: Optional[int] = None
    
    # Context
    preceding_context: str = ""
    following_context: str = ""


@dataclass
class IngestedDocument:
    """Represents an ingested document."""
    id: Optional[int] = None
    filename: str = ""
    file_hash: str = ""
    file_type: str = ""
    file_path: str = ""
    file_size: int = 0
    ingested_at: Optional[datetime] = None
    
    # Metadata
    doc_date: Optional[str] = None
    doc_author: Optional[str] = None
    doc_subject: Optional[str] = None
    doc_recipients: Optional[List[str]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Processing state
    status: str = "pending"
    chunk_count: int = 0
    insights_extracted: int = 0
    error_message: Optional[str] = None
    
    # Content
    chunks: List[DocumentChunk] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "filename": self.filename,
            "file_hash": self.file_hash,
            "file_type": self.file_type,
            "file_path": self.file_path,
            "file_size": self.file_size,
            "doc_date": self.doc_date,
            "doc_author": self.doc_author,
            "doc_subject": self.doc_subject,
            "status": self.status,
            "chunk_count": self.chunk_count,
            "insights_extracted": self.insights_extracted,
        }
