#!/usr/bin/env python3
"""
EhkoForge Document Ingestion CLI v1.0

Process documents from inbox or specific files.

Usage:
    python ingest.py                    # Process all files in _inbox/
    python ingest.py file.pdf           # Process specific file
    python ingest.py --status           # Show ingestion stats
    python ingest.py --pending          # Show pending documents
    python ingest.py --chunks           # Show unprocessed chunks
"""

import argparse
import sys
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from ingestion import IngestService

DB_PATH = Path(__file__).parent.parent / "_data" / "ehko_index.db"


def main():
    parser = argparse.ArgumentParser(
        description="EhkoForge Document Ingestion",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python ingest.py                    Process inbox
    python ingest.py document.pdf       Process specific file
    python ingest.py --status           Show statistics
    python ingest.py --pending          List pending documents
    python ingest.py --chunks 50        Show 50 unprocessed chunks
        """
    )
    
    parser.add_argument(
        "file",
        nargs="?",
        help="Specific file to ingest (optional)"
    )
    parser.add_argument(
        "--status", "-s",
        action="store_true",
        help="Show ingestion statistics"
    )
    parser.add_argument(
        "--pending", "-p",
        action="store_true",
        help="List pending documents"
    )
    parser.add_argument(
        "--chunks", "-c",
        type=int,
        nargs="?",
        const=20,
        help="Show unprocessed chunks (default: 20)"
    )
    parser.add_argument(
        "--no-move",
        action="store_true",
        help="Don't move files to _processed after ingestion"
    )
    parser.add_argument(
        "--db",
        type=str,
        default=str(DB_PATH),
        help="Database path"
    )
    
    args = parser.parse_args()
    
    # Initialize service
    service = IngestService(db_path=args.db)
    
    # Handle commands
    if args.status:
        show_status(service)
    elif args.pending:
        show_pending(service)
    elif args.chunks is not None:
        show_chunks(service, args.chunks)
    elif args.file:
        ingest_file(service, args.file, not args.no_move)
    else:
        process_inbox(service, not args.no_move)


def show_status(service: IngestService):
    """Display ingestion statistics."""
    stats = service.get_ingestion_stats()
    
    print("\n" + "=" * 50)
    print("DOCUMENT INGESTION STATUS")
    print("=" * 50)
    
    print(f"\nDocuments: {stats['documents']['total']}")
    
    if stats['documents']['by_status']:
        print("\n  By Status:")
        for status, count in stats['documents']['by_status'].items():
            print(f"    {status}: {count}")
    
    if stats['documents']['by_type']:
        print("\n  By Type:")
        for file_type, count in stats['documents']['by_type'].items():
            print(f"    {file_type}: {count}")
    
    if stats['chunks']:
        print(f"\nChunks:")
        print(f"    Total: {stats['chunks']['total_chunks'] or 0}")
        print(f"    Unprocessed: {stats['chunks']['unprocessed'] or 0}")
        print(f"    Total tokens: {stats['chunks']['total_tokens'] or 0:,}")
    
    print()


def show_pending(service: IngestService):
    """List documents pending processing."""
    pending = service.get_pending_documents()
    
    print("\n" + "=" * 50)
    print(f"PENDING DOCUMENTS ({len(pending)})")
    print("=" * 50)
    
    if not pending:
        print("\nNo pending documents.")
    else:
        for doc in pending:
            print(f"\n  [{doc['id']}] {doc['filename']}")
            print(f"       Type: {doc['file_type']}, Chunks: {doc['chunk_count']}")
            if doc['doc_subject']:
                print(f"       Subject: {doc['doc_subject'][:50]}")
    
    print()


def show_chunks(service: IngestService, limit: int):
    """Show unprocessed chunks."""
    chunks = service.get_unprocessed_chunks(limit=limit)
    
    print("\n" + "=" * 50)
    print(f"UNPROCESSED CHUNKS (showing {len(chunks)})")
    print("=" * 50)
    
    if not chunks:
        print("\nNo unprocessed chunks.")
    else:
        for chunk in chunks:
            print(f"\n  Chunk {chunk['id']} (doc {chunk['document_id']}, #{chunk['chunk_index']})")
            print(f"  File: {chunk['filename']}")
            print(f"  Tokens: {chunk['token_count']}")
            preview = chunk['content'][:150].replace('\n', ' ')
            print(f"  Preview: {preview}...")
    
    print()


def ingest_file(service: IngestService, file_path: str, move_after: bool):
    """Ingest a specific file."""
    path = Path(file_path)
    
    if not path.exists():
        print(f"ERROR: File not found: {file_path}")
        sys.exit(1)
    
    print(f"\nIngesting: {path.name}")
    print("-" * 40)
    
    result = service.ingest_file(path, move_after=move_after)
    
    if result.get("error"):
        print(f"ERROR: {result['error']}")
        sys.exit(1)
    elif result.get("skipped"):
        print(f"SKIPPED: {result.get('reason', 'unknown')}")
    else:
        print(f"✓ Document ID: {result['document_id']}")
        print(f"  Type: {result['file_type']}")
        print(f"  Chunks: {result['chunks']}")
        if result.get('title'):
            print(f"  Title: {result['title']}")
    
    print()


def process_inbox(service: IngestService, move_after: bool):
    """Process all files in inbox."""
    print(f"\nProcessing inbox: {service.inbox_path}")
    print("-" * 40)
    
    results = service.process_inbox(move_after=move_after)
    
    print(f"\nResults:")
    print(f"  Processed: {results['processed']}")
    print(f"  Skipped: {results['skipped']}")
    print(f"  Failed: {results['failed']}")
    
    if results['files']:
        print(f"\nDetails:")
        for f in results['files']:
            if f.get('error'):
                print(f"  [ERR] {f['filename']}: {f['error']}")
            elif f.get('skipped'):
                print(f"  - {f['filename']}: skipped ({f.get('reason', '?')})")
            else:
                print(f"  [OK] {f['filename']}: {f.get('chunks', 0)} chunks")
    
    print()


if __name__ == "__main__":
    main()
