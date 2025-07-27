from typing import List, Dict, Optional, Any, Tuple, Set
from datetime import datetime
import re
from urllib.parse import urlparse, parse_qs, urljoin
import difflib
from collections import defaultdict
import json
from readwise_client import ReadwiseClient
from document_manager import safe_print

class DocumentDeduplicator:
    """Smart document deduplicator - removes duplicates based on content similarity and metadata quality"""
    
    def __init__(self, client: Optional[ReadwiseClient] = None):
        self.client = client or ReadwiseClient()
        self.similarity_threshold = 0.8  # Title similarity threshold
        self.url_similarity_threshold = 0.9  # URL similarity threshold
        
    def normalize_url(self, url: str) -> str:
        """Normalize URL by removing tracking parameters and fragments"""
        if not url:
            return ""
            
        try:
            parsed = urlparse(url.lower().strip())
            
            # Remove common tracking parameters
            tracking_params = {
                'utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content',
                'fbclid', 'gclid', 'msclkid', 'ref', 'source', 'campaign',
                'medium', 'term', 'content', 'mc_cid', 'mc_eid', '_ga', '_gl'
            }
            
            if parsed.query:
                query_params = parse_qs(parsed.query)
                cleaned_params = {k: v for k, v in query_params.items() 
                                if k.lower() not in tracking_params}
                
                # Rebuild query string
                if cleaned_params:
                    query_parts = []
                    for k, v_list in cleaned_params.items():
                        for v in v_list:
                            query_parts.append(f"{k}={v}")
                    new_query = "&".join(sorted(query_parts))
                else:
                    new_query = ""
            else:
                new_query = ""
            
            # Rebuild URL (remove fragments)
            normalized = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
            if new_query:
                normalized += f"?{new_query}"
                
            return normalized
            
        except Exception:
            return url.lower().strip()
    
    def calculate_title_similarity(self, title1: str, title2: str) -> float:
        """Calculate title similarity between two titles"""
        if not title1 or not title2:
            return 0.0
        
        # Normalize titles (remove extra whitespace, special characters, etc.)
        def normalize_title(title: str) -> str:
            # Remove extra whitespace and punctuation
            normalized = re.sub(r'[^\w\s\u4e00-\u9fff]', '', title.lower())
            normalized = re.sub(r'\s+', ' ', normalized).strip()
            return normalized
        
        norm_title1 = normalize_title(title1)
        norm_title2 = normalize_title(title2)
        
        if not norm_title1 or not norm_title2:
            return 0.0
        
        # Use sequence similarity comparison
        similarity = difflib.SequenceMatcher(None, norm_title1, norm_title2).ratio()
        return similarity
    
    def calculate_metadata_quality_score(self, document: Dict[str, Any]) -> float:
        """Calculate document metadata quality score (0-100)"""
        score = 0.0
        max_score = 100.0
        
        # Title quality (25 points)
        title = document.get('title') or ''
        title = title.strip() if title else ''
        if title:
            if len(title) > 10:
                score += 25
            elif len(title) > 5:
                score += 15
            else:
                score += 5
        
        # Author information (15 points)
        author = document.get('author') or ''
        author = author.strip() if author else ''
        if author and author != 'Unknown':
            score += 15
        
        # Summary/description (20 points)
        summary = document.get('summary') or ''
        summary = summary.strip() if summary else ''
        if summary:
            if len(summary) > 100:
                score += 20
            elif len(summary) > 50:
                score += 15
            else:
                score += 10
        
        # Published date (10 points)
        published_date = document.get('published_date') or document.get('created_at')
        if published_date:
            score += 10
        
        # Number of tags (10 points)
        tags = document.get('tags', [])
        if tags:
            tag_count = len(tags)
            if tag_count >= 3:
                score += 10
            elif tag_count >= 1:
                score += 5
        
        # URL quality (10 points)
        url = document.get('source_url') or document.get('url', '')
        if url:
            # Check if it's a short URL or original URL
            if any(domain in url for domain in ['bit.ly', 't.co', 'tinyurl', 'short']):
                score += 5  # Short URLs get lower score
            else:
                score += 10
        
        # Newer update time (10 points)
        updated_at = document.get('updated_at')
        if updated_at:
            try:
                # Assume newer updates are better
                update_time = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
                days_old = (datetime.now().replace(tzinfo=update_time.tzinfo) - update_time).days
                if days_old < 30:
                    score += 10
                elif days_old < 90:
                    score += 5
            except:
                pass
        
        return min(score, max_score)
    
    def find_duplicate_groups(self, documents: List[Dict[str, Any]]) -> List[List[Dict[str, Any]]]:
        """Find duplicate document groups"""
        safe_print("Analyzing document duplicates...")
        
        # Group by normalized URL
        url_groups = defaultdict(list)
        title_groups = defaultdict(list)
        
        for doc in documents:
            doc_id = doc.get('id')
            if not doc_id:
                continue
                
            # URL grouping
            url = doc.get('source_url') or doc.get('url', '')
            if url:
                normalized_url = self.normalize_url(url)
                if normalized_url:
                    url_groups[normalized_url].append(doc)
            
            # Title grouping (for cases where URLs differ but content is same)
            title = doc.get('title') or ''
            title = title.strip() if title else ''
            if title and len(title) > 10:  # Ignore titles that are too short
                title_groups[title.lower()].append(doc)
        
        # Collect duplicate groups
        duplicate_groups = []
        processed_ids = set()
        
        # Handle URL duplicates
        for url, docs in url_groups.items():
            if len(docs) > 1:
                doc_ids = {doc.get('id') for doc in docs}
                if not doc_ids.intersection(processed_ids):
                    duplicate_groups.append(docs)
                    processed_ids.update(doc_ids)
        
        # Handle title similarity duplicates (for documents not grouped by URL)
        remaining_docs = [doc for doc in documents 
                         if doc.get('id') not in processed_ids]
        
        for i, doc1 in enumerate(remaining_docs):
            if doc1.get('id') in processed_ids:
                continue
                
            similar_docs = [doc1]
            title1 = doc1.get('title', '')
            
            for doc2 in remaining_docs[i+1:]:
                if doc2.get('id') in processed_ids:
                    continue
                    
                title2 = doc2.get('title', '')
                if self.calculate_title_similarity(title1, title2) >= self.similarity_threshold:
                    similar_docs.append(doc2)
            
            if len(similar_docs) > 1:
                duplicate_groups.append(similar_docs)
                processed_ids.update(doc.get('id') for doc in similar_docs)
        
        safe_print(f"Found {len(duplicate_groups)} duplicate groups")
        return duplicate_groups
    
    def select_best_document(self, duplicate_docs: List[Dict[str, Any]]) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
        """Select the best version from duplicate documents"""
        if len(duplicate_docs) <= 1:
            return duplicate_docs[0] if duplicate_docs else None, []
        
        # Calculate quality score for each document
        scored_docs = []
        for doc in duplicate_docs:
            quality_score = self.calculate_metadata_quality_score(doc)
            scored_docs.append((doc, quality_score))
        
        # Sort by quality score
        scored_docs.sort(key=lambda x: x[1], reverse=True)
        
        best_doc = scored_docs[0][0]
        duplicates_to_remove = [doc for doc, _ in scored_docs[1:]]
        
        return best_doc, duplicates_to_remove
    
    def analyze_duplicates(self, documents: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """Analyze duplicate documents without performing deletion"""
        if documents is None:
            safe_print("Fetching all documents...")
            from document_manager import DocumentManager
            doc_manager = DocumentManager(self.client)
            documents = doc_manager.get_documents()
        
        if not documents:
            return {"error": "No documents found"}
        
        safe_print(f"Starting analysis of {len(documents)} documents...")
        
        duplicate_groups = self.find_duplicate_groups(documents)
        
        analysis_result = {
            "total_documents": len(documents),
            "duplicate_groups": len(duplicate_groups),
            "total_duplicates": sum(len(group) - 1 for group in duplicate_groups),
            "groups": []
        }
        
        for i, group in enumerate(duplicate_groups):
            best_doc, duplicates = self.select_best_document(group)
            
            group_info = {
                "group_id": i + 1,
                "documents_count": len(group),
                "best_document": {
                    "id": best_doc.get('id'),
                    "title": best_doc.get('title', ''),
                    "url": best_doc.get('source_url') or best_doc.get('url', ''),
                    "quality_score": self.calculate_metadata_quality_score(best_doc),
                    "author": best_doc.get('author', ''),
                    "created_at": best_doc.get('created_at', ''),
                    "location": best_doc.get('location', '')
                },
                "duplicates_to_remove": []
            }
            
            for dup_doc in duplicates:
                group_info["duplicates_to_remove"].append({
                    "id": dup_doc.get('id'),
                    "title": dup_doc.get('title', ''),
                    "url": dup_doc.get('source_url') or dup_doc.get('url', ''),
                    "quality_score": self.calculate_metadata_quality_score(dup_doc),
                    "author": dup_doc.get('author', ''),
                    "created_at": dup_doc.get('created_at', ''),
                    "location": dup_doc.get('location', '')
                })
            
            analysis_result["groups"].append(group_info)
        
        return analysis_result
    
    def remove_duplicates(self, 
                         documents: Optional[List[Dict[str, Any]]] = None,
                         dry_run: bool = True,
                         auto_confirm: bool = False) -> Dict[str, Any]:
        """Execute deduplication operation"""
        analysis = self.analyze_duplicates(documents)
        
        if analysis.get("error"):
            return analysis
        
        if analysis["duplicate_groups"] == 0:
            safe_print("No duplicate documents found")
            return {"message": "No duplicate documents found", "removed_count": 0}
        
        safe_print(f"\n=== Deduplication Analysis Results ===")
        safe_print(f"Total documents: {analysis['total_documents']}")
        safe_print(f"Duplicate groups: {analysis['duplicate_groups']}")
        safe_print(f"Duplicates to remove: {analysis['total_duplicates']}")
        
        # Show detailed analysis
        for group in analysis["groups"]:
            safe_print(f"\n--- Group {group['group_id']} ---")
            safe_print(f"Keep document: {group['best_document']['title'][:50]}...")
            safe_print(f"  ID: {group['best_document']['id']}")
            safe_print(f"  Quality score: {group['best_document']['quality_score']:.1f}")
            safe_print(f"  Author: {group['best_document']['author'] or 'N/A'}")
            safe_print(f"  Location: {group['best_document']['location']}")
            
            safe_print(f"Will remove {len(group['duplicates_to_remove'])} duplicate documents:")
            for dup in group["duplicates_to_remove"]:
                safe_print(f"  - {dup['title'][:50]}... (score: {dup['quality_score']:.1f})")
        
        if dry_run:
            safe_print(f"\n*** This is preview mode, no documents were actually deleted ***")
            return {"analysis": analysis, "removed_count": 0, "dry_run": True}
        
        # Confirm deletion
        if not auto_confirm:
            safe_print(f"\nDo you want to delete these {analysis['total_duplicates']} duplicate documents?")
            safe_print("Type 'yes' to confirm, any other input will cancel:")
            confirmation = input().strip().lower()
            if confirmation != 'yes':
                safe_print("Operation cancelled")
                return {"message": "Operation cancelled", "removed_count": 0}
        
        # Execute deletion
        removed_count = 0
        failed_deletions = []
        
        for group in analysis["groups"]:
            for dup in group["duplicates_to_remove"]:
                try:
                    success = self.client.delete_document(dup["id"])
                    if success:
                        removed_count += 1
                        safe_print(f"Deleted: {dup['title'][:50]}...")
                    else:
                        failed_deletions.append(dup["id"])
                        safe_print(f"Failed to delete: {dup['title'][:50]}...")
                except Exception as e:
                    failed_deletions.append(dup["id"])
                    safe_print(f"Delete error: {dup['title'][:50]}... - {e}")
        
        result = {
            "analysis": analysis,
            "removed_count": removed_count,
            "failed_deletions": failed_deletions,
            "dry_run": False
        }
        
        safe_print(f"\n=== Deduplication Complete ===")
        safe_print(f"Successfully deleted: {removed_count} duplicate documents")
        if failed_deletions:
            safe_print(f"Failed to delete: {len(failed_deletions)} documents")
        
        return result
    
    def export_analysis_report(self, analysis: Dict[str, Any], filename: Optional[str] = None) -> str:
        """Export analysis report to file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"duplicate_analysis_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, ensure_ascii=False, indent=2)
        
        safe_print(f"Analysis report exported to: {filename}")
        return filename 