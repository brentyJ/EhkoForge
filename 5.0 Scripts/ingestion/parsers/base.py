"""
Base parser interface and factory.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

# Import for type hints - using string annotation to avoid circular imports
# ParsedContent is defined in ..types


class BaseParser(ABC):
    """Abstract base for document parsers."""
    
    @abstractmethod
    def can_parse(self, path: Path) -> bool:
        """Check if this parser can handle the file."""
        pass
    
    @abstractmethod
    def parse(self, path: Path):
        """Parse the file and return content."""
        pass
    
    @abstractmethod
    def get_file_type(self) -> str:
        """Return the file type identifier."""
        pass


def get_parser(path: Path) -> Optional[BaseParser]:
    """
    Get appropriate parser for a file.
    
    Args:
        path: Path to file
    
    Returns:
        Parser instance or None if unsupported
    """
    from .pdf import PDFParser
    from .markdown import MarkdownParser
    from .plaintext import PlaintextParser
    from .messages import MessageParser
    
    parsers = [
        PDFParser(),
        MarkdownParser(),
        MessageParser(),  # Check before plaintext (txt files might be messages)
        PlaintextParser(),
    ]
    
    for parser in parsers:
        if parser.can_parse(path):
            return parser
    
    return None


def detect_file_type(path: Path) -> str:
    """
    Detect file type from extension and content.
    """
    suffix = path.suffix.lower()
    
    type_map = {
        ".pdf": "pdf",
        ".md": "markdown",
        ".markdown": "markdown",
        ".txt": "text",
        ".text": "text",
        ".json": "json",
        ".csv": "csv",
    }
    
    return type_map.get(suffix, "unknown")
