#!/usr/bin/env python3
import argparse
import sys
from typing import List, Optional
import json

from config import Config
from readwise_client import ReadwiseClient
from document_manager import DocumentManager, safe_print
from tag_manager import TagManager
from document_deduplicator import DocumentDeduplicator

class ReadwiseCLI:
    """Readwise command line interface"""
    
    def __init__(self):
        try:
            self.config = Config()
            self.client = ReadwiseClient(self.config)
            self.doc_manager = DocumentManager(self.client)
            self.tag_manager = TagManager(self.client)
            self.deduplicator = DocumentDeduplicator(self.client)
        except ValueError as e:
            print(f"Error: {e}")
            sys.exit(1)
    
    def verify_connection(self) -> bool:
        """Verify API connection"""
        if not self.client.verify_token():
            print("Error: API token invalid or network connection failed")
            return False
        return True
    
    def add_article(self, args) -> None:
        """Add article"""
        tags = args.tags.split(',') if args.tags else None
        
        try:
            result = self.doc_manager.add_article(
                url=args.url,
                title=args.title,
                tags=tags,
                location=args.location
            )
            print(f"Successfully added article: {result.get('url')}")
        except Exception as e:
            print(f"Failed to add article: {e}")
    
    def list_documents(self, args) -> None:
        """List documents"""
        try:
            docs = self.doc_manager.get_documents(
                location=args.location,
                category=args.category,
                limit=args.limit
            )
            
            if not docs:
                print("No documents found matching criteria")
                return
            
            if args.format == 'json':
                print(json.dumps(docs, ensure_ascii=False, indent=2))
            else:
                for i, doc in enumerate(docs, 1):
                    safe_print(f"\n{i}. {doc.get('title', 'N/A')}")
                    print(f"   ID: {doc.get('id')}")
                    print(f"   URL: {doc.get('source_url', doc.get('url', 'N/A'))}")
                    print(f"   Location: {doc.get('location', 'N/A')}")
                    print(f"   Updated: {doc.get('updated_at', 'N/A')}")
                    
                    if args.verbose:
                        self.doc_manager.display_document_summary(doc)
                        
        except Exception as e:
            print(f"Failed to list documents: {e}")
    
    def search_documents(self, args) -> None:
        """Search documents"""
        try:
            docs = self.doc_manager.search_documents(
                keyword=args.keyword,
                location=args.location
            )
            
            if not docs:
                print(f"No documents found containing '{args.keyword}'")
                return
            
            for i, doc in enumerate(docs, 1):
                safe_print(f"\n{i}. {doc.get('title', 'N/A')}")
                print(f"   ID: {doc.get('id')}")
                print(f"   URL: {doc.get('source_url', doc.get('url', 'N/A'))}")
                
        except Exception as e:
            print(f"Failed to search documents: {e}")
    
    def update_document(self, args) -> None:
        """Update document"""
        try:
            if args.location:
                result = self.doc_manager.move_document(args.id, args.location)
                print(f"Document moved to {args.location}")
            else:
                result = self.doc_manager.update_document_metadata(
                    document_id=args.id,
                    title=args.title,
                    author=args.author,
                    summary=args.summary
                )
                print("Document metadata updated")
                
        except Exception as e:
            print(f"Failed to update document: {e}")
    
    def delete_document(self, args) -> None:
        """Delete document"""
        if not args.force:
            confirm = input(f"Are you sure you want to delete document {args.id}? (y/N): ")
            if confirm.lower() != 'y':
                print("Delete cancelled")
                return
        
        try:
            success = self.doc_manager.delete_document(args.id)
            if success:
                print("Document deleted")
            else:
                print("Delete failed")
        except Exception as e:
            print(f"Failed to delete document: {e}")
    
    def show_stats(self, args) -> None:
        """Show statistics"""
        try:
            stats = self.doc_manager.get_stats()
            
            print("\n=== Document Statistics ===")
            print(f"Total: {stats['total']}")
            print(f"New: {stats['new']}")
            print(f"Later: {stats['later']}")
            print(f"Archive: {stats['archive']}")
            print(f"Feed: {stats['feed']}")
            
            if args.include_tags:
                self.tag_manager.display_tag_stats()
                
        except Exception as e:
            print(f"Failed to get statistics: {e}")
    
    def export_documents(self, args) -> None:
        """Export documents"""
        try:
            filename = self.doc_manager.export_documents(
                location=args.location,
                filename=args.output
            )
            print(f"Documents exported to: {filename}")
        except Exception as e:
            print(f"Export failed: {e}")
    
    def list_tags(self, args) -> None:
        """List tags"""
        try:
            if args.search:
                tags = self.tag_manager.search_tags(args.search)
            else:
                tags = self.tag_manager.list_tags(sort_by=args.sort)
            
            if not tags:
                print("No tags found")
                return
            
            if args.format == 'json':
                print(json.dumps(tags, ensure_ascii=False, indent=2))
            else:
                for i, tag in enumerate(tags, 1):
                    print(f"{i}. {tag.get('name')} (key: {tag.get('key')})")
                    
                    if args.verbose:
                        self.tag_manager.display_tag_summary(tag)
                        
        except Exception as e:
            print(f"Failed to list tags: {e}")
    
    def tag_stats(self, args) -> None:
        """Tag statistics"""
        try:
            self.tag_manager.display_tag_stats()
        except Exception as e:
            print(f"Failed to get tag statistics: {e}")
    
    def analyze_duplicates(self, args) -> None:
        """Analyze duplicate documents without deletion"""
        try:
            safe_print("Starting duplicate analysis...")
            
            # Get documents based on parameters
            documents = None
            if args.location:
                documents = self.doc_manager.get_documents(location=args.location)
            
            analysis = self.deduplicator.analyze_duplicates(documents)
            
            if analysis.get("error"):
                print(f"Analysis failed: {analysis['error']}")
                return
            
            if analysis["duplicate_groups"] == 0:
                safe_print("No duplicate documents found")
                return
            
            # Display analysis results
            safe_print(f"\n=== Duplicate Document Analysis Results ===")
            safe_print(f"Total documents: {analysis['total_documents']}")
            safe_print(f"Duplicate groups: {analysis['duplicate_groups']}")
            safe_print(f"Duplicates to remove: {analysis['total_duplicates']}")
            
            if args.format == 'json':
                print(json.dumps(analysis, ensure_ascii=False, indent=2))
            else:
                for group in analysis["groups"]:
                    safe_print(f"\n--- Group {group['group_id']} ---")
                    safe_print(f"Keep document: {group['best_document']['title'][:60]}...")
                    safe_print(f"  ID: {group['best_document']['id']}")
                    safe_print(f"  Quality score: {group['best_document']['quality_score']:.1f}")
                    safe_print(f"  Author: {group['best_document']['author'] or 'N/A'}")
                    safe_print(f"  Location: {group['best_document']['location']}")
                    
                    safe_print(f"Will remove {len(group['duplicates_to_remove'])} duplicate documents:")
                    for dup in group["duplicates_to_remove"]:
                        safe_print(f"  - {dup['title'][:60]}... (score: {dup['quality_score']:.1f})")
            
            # Export report
            if args.export:
                filename = self.deduplicator.export_analysis_report(analysis, args.export)
                
        except Exception as e:
            print(f"Analysis failed: {e}")
    
    def remove_duplicates(self, args) -> None:
        """Execute deduplication operation"""
        try:
            safe_print("Starting deduplication process...")
            
            # Get documents based on parameters
            documents = None
            if args.location:
                documents = self.doc_manager.get_documents(location=args.location)
            
            result = self.deduplicator.remove_duplicates(
                documents=documents,
                dry_run=args.dry_run,
                auto_confirm=args.force
            )
            
            if result.get("error"):
                print(f"Deduplication failed: {result['error']}")
                return
            
            if result.get("message"):
                safe_print(result["message"])
                return
            
            # Display results
            if result.get("dry_run"):
                safe_print("\n*** This is preview mode, no documents were actually deleted ***")
                safe_print("Use --execute parameter to perform actual deletion")
            else:
                safe_print(f"\n=== Deduplication Complete ===")
                safe_print(f"Successfully deleted: {result.get('removed_count', 0)} duplicate documents")
                if result.get("failed_deletions"):
                    safe_print(f"Failed to delete: {len(result['failed_deletions'])} documents")
            
            # Export report
            if args.export and result.get("analysis"):
                filename = self.deduplicator.export_analysis_report(result["analysis"], args.export)
                
        except Exception as e:
            print(f"Deduplication failed: {e}")
    
    def setup_token(self, args) -> None:
        """Setup API token"""
        if args.token:
            try:
                self.config.save_token(args.token)
                print("API token saved")
                
                # Verify new token
                if self.client.verify_token():
                    print("Token verification successful")
                else:
                    print("Warning: Token verification failed")
            except Exception as e:
                print(f"Failed to save token: {e}")
        else:
            print("Please provide API token")
            print("Usage: python cli.py setup-token --token YOUR_TOKEN")
            print("Get token: https://readwise.io/access_token")

def main():
    parser = argparse.ArgumentParser(description="Readwise Reader Management Tool")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Add article
    add_parser = subparsers.add_parser('add', help='Add article')
    add_parser.add_argument('url', help='Article URL')
    add_parser.add_argument('--title', help='Article title')
    add_parser.add_argument('--tags', help='Tags, comma separated')
    add_parser.add_argument('--location', default='new', 
                           choices=['new', 'later', 'archive', 'feed'],
                           help='Document location')
    
    # List documents
    list_parser = subparsers.add_parser('list', help='List documents')
    list_parser.add_argument('--location', choices=['new', 'later', 'archive', 'feed'],
                            help='Filter by location')
    list_parser.add_argument('--category', help='Filter by category')
    list_parser.add_argument('--limit', type=int, help='Limit count')
    list_parser.add_argument('--format', choices=['text', 'json'], default='text',
                            help='Output format')
    list_parser.add_argument('--verbose', '-v', action='store_true', 
                            help='Show detailed information')
    
    # Search documents
    search_parser = subparsers.add_parser('search', help='Search documents')
    search_parser.add_argument('keyword', help='Search keyword')
    search_parser.add_argument('--location', choices=['new', 'later', 'archive', 'feed'],
                              help='Search scope')
    
    # Update document
    update_parser = subparsers.add_parser('update', help='Update document')
    update_parser.add_argument('id', help='Document ID')
    update_parser.add_argument('--title', help='New title')
    update_parser.add_argument('--author', help='New author')
    update_parser.add_argument('--summary', help='New summary')
    update_parser.add_argument('--location', choices=['new', 'later', 'archive', 'feed'],
                              help='Move to location')
    
    # Delete document
    delete_parser = subparsers.add_parser('delete', help='Delete document')
    delete_parser.add_argument('id', help='Document ID')
    delete_parser.add_argument('--force', '-f', action='store_true',
                              help='Force delete without confirmation')
    
    # Statistics
    stats_parser = subparsers.add_parser('stats', help='Show statistics')
    stats_parser.add_argument('--include-tags', action='store_true',
                             help='Include tag statistics')
    
    # Export documents
    export_parser = subparsers.add_parser('export', help='Export documents')
    export_parser.add_argument('--location', choices=['new', 'later', 'archive', 'feed'],
                              help='Export location')
    export_parser.add_argument('--output', '-o', help='Output filename')
    
    # Tag management
    tags_parser = subparsers.add_parser('tags', help='List tags')
    tags_parser.add_argument('--search', help='Search tags')
    tags_parser.add_argument('--sort', choices=['name', 'key'], default='name',
                            help='Sort method')
    tags_parser.add_argument('--format', choices=['text', 'json'], default='text',
                            help='Output format')
    tags_parser.add_argument('--verbose', '-v', action='store_true',
                            help='Show detailed information')
    
    # Tag statistics
    tag_stats_parser = subparsers.add_parser('tag-stats', help='Tag statistics')
    
    # Deduplication analysis
    dedup_analyze_parser = subparsers.add_parser('analyze-duplicates', 
                                                help='Analyze duplicate documents (no deletion)')
    dedup_analyze_parser.add_argument('--location', 
                                     choices=['new', 'later', 'archive', 'feed'],
                                     help='Limit analysis to specific location')
    dedup_analyze_parser.add_argument('--format', choices=['text', 'json'], 
                                     default='text', help='Output format')
    dedup_analyze_parser.add_argument('--export', help='Export analysis report to specified file')
    
    # Deduplication execution
    dedup_remove_parser = subparsers.add_parser('remove-duplicates', 
                                               help='Execute deduplication operation')
    dedup_remove_parser.add_argument('--location', 
                                    choices=['new', 'later', 'archive', 'feed'],
                                    help='Limit processing to specific location')
    dedup_remove_parser.add_argument('--dry-run', action='store_true', 
                                    default=True, help='Preview mode (default)')
    dedup_remove_parser.add_argument('--execute', dest='dry_run', 
                                    action='store_false', 
                                    help='Actually execute deletion (disable preview mode)')
    dedup_remove_parser.add_argument('--force', action='store_true',
                                    help='Auto-confirm without asking user')
    dedup_remove_parser.add_argument('--export', help='Export processing report to specified file')
    
    # Setup token
    setup_parser = subparsers.add_parser('setup-token', help='Setup API token')
    setup_parser.add_argument('--token', help='Readwise API token')
    
    # Verify connection
    verify_parser = subparsers.add_parser('verify', help='Verify API connection')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    cli = ReadwiseCLI()
    
    # Special commands don't need connection verification
    if args.command == 'setup-token':
        cli.setup_token(args)
        return
    
    if args.command == 'verify':
        if cli.verify_connection():
            print("API connection OK")
        else:
            print("API connection failed")
        return
    
    # Other commands need connection verification
    if not cli.verify_connection():
        print("Please set up a valid API token first")
        print("Use command: python cli.py setup-token --token YOUR_TOKEN")
        sys.exit(1)
    
    # Execute corresponding command
    command_map = {
        'add': cli.add_article,
        'list': cli.list_documents,
        'search': cli.search_documents,
        'update': cli.update_document,
        'delete': cli.delete_document,
        'stats': cli.show_stats,
        'export': cli.export_documents,
        'tags': cli.list_tags,
        'tag-stats': cli.tag_stats,
        'analyze-duplicates': cli.analyze_duplicates,
        'remove-duplicates': cli.remove_duplicates,
    }
    
    if args.command in command_map:
        command_map[args.command](args)
    else:
        print(f"Unknown command: {args.command}")
        parser.print_help()

if __name__ == '__main__':
    main() 