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
    
    def normalize_url_simple(self, url: str) -> str:
        """Simple URL normalization - remove http/https protocol and trailing slash"""
        if not url:
            return ""
        
        url = url.strip().lower()
        
        # Remove http:// and https://
        if url.startswith('https://'):
            url = url[8:]  # Remove 'https://'
        elif url.startswith('http://'):
            url = url[7:]   # Remove 'http://'
        
        # Remove trailing slash
        if url.endswith('/'):
            url = url[:-1]
        
        return url
    
    def normalize_url_advanced(self, url: str) -> str:
        """Advanced URL normalization - remove protocol, query string, fragment, and trailing slash
        
        WARNING: This is more aggressive and may group different pages as duplicates.
        Use with caution and always review results before deletion.
        """
        if not url:
            return ""
        
        try:
            from urllib.parse import urlparse
            
            # Parse the URL
            parsed = urlparse(url.strip().lower())
            
            # Rebuild URL without query string and fragment
            # Keep only scheme + netloc + path
            normalized = f"{parsed.netloc}{parsed.path}"
            
            # Remove trailing slash
            if normalized.endswith('/'):
                normalized = normalized[:-1]
            
            return normalized
        except Exception:
            # Fallback to simple normalization if parsing fails
            return self.normalize_url_simple(url)
    
    def find_csv_duplicates(self, csv_file_path: str) -> Dict[str, Any]:
        """Find duplicates in CSV file based on source_url without http/https"""
        import csv
        
        safe_print(f"Analyzing duplicates in CSV file: {csv_file_path}")
        
        documents = []
        url_groups = defaultdict(list)
        
        # Read CSV file
        try:
            with open(csv_file_path, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row_num, row in enumerate(reader, start=1):
                    documents.append(row)
                    
                    # Group by normalized source_url
                    source_url = row.get('source_url', '').strip()
                    if source_url:
                        normalized_url = self.normalize_url_simple(source_url)
                        if normalized_url:
                            url_groups[normalized_url].append({
                                'row_number': row_num,
                                'data': row
                            })
        except Exception as e:
            return {"error": f"Failed to read CSV file: {e}"}
        
        # Find duplicate groups
        duplicate_groups = []
        total_duplicates = 0
        
        for normalized_url, docs in url_groups.items():
            if len(docs) > 1:
                duplicate_groups.append({
                    'normalized_url': normalized_url,
                    'documents': docs,
                    'count': len(docs)
                })
                total_duplicates += len(docs) - 1  # Subtract 1 because we keep one
        
        analysis_result = {
            "csv_file": csv_file_path,
            "total_documents": len(documents),
            "duplicate_groups": len(duplicate_groups),
            "total_duplicates": total_duplicates,
            "groups": duplicate_groups
        }
        
        safe_print(f"Found {len(duplicate_groups)} duplicate groups with {total_duplicates} total duplicates")
        
        return analysis_result
    
    def find_csv_duplicates_advanced(self, csv_file_path: str) -> Dict[str, Any]:
        """Advanced duplicate analysis - combines URL normalization with title similarity
        
        Rules for advanced duplicate detection:
        1. Title similarity > 50% (regardless of URL)
        2. OR: Same URL after removing query strings AND title similarity > 50%
        
        This provides smarter duplicate detection while maintaining safety.
        """
        import csv
        
        safe_print(f"🔍 ADVANCED MODE: Analyzing duplicates with smart URL + title matching")
        safe_print(f"File: {csv_file_path}")
        safe_print(f"Rules: Title similarity >50% OR (same URL without query + title similarity >50%)")
        
        documents = []
        
        # Read CSV file
        try:
            with open(csv_file_path, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row_num, row in enumerate(reader, start=1):
                    documents.append({
                        'row_number': row_num,
                        'data': row
                    })
        except Exception as e:
            return {"error": f"Failed to read CSV file: {e}"}
        
        # Find duplicate groups using advanced logic
        duplicate_groups = []
        processed_indices = set()
        total_duplicates = 0
        
        for i, doc1 in enumerate(documents):
            if i in processed_indices:
                continue
                
            group = [doc1]
            group_indices = {i}
            
            title1 = doc1['data'].get('title', '').strip()
            url1 = doc1['data'].get('source_url', '').strip()
            normalized_url1 = self.normalize_url_advanced(url1) if url1 else ""
            
            # Find similar documents
            for j, doc2 in enumerate(documents[i+1:], start=i+1):
                if j in processed_indices:
                    continue
                    
                title2 = doc2['data'].get('title', '').strip()
                url2 = doc2['data'].get('source_url', '').strip()
                normalized_url2 = self.normalize_url_advanced(url2) if url2 else ""
                
                is_duplicate = False
                match_reason = ""
                
                # Calculate title similarity
                title_similarity = self.calculate_title_similarity(title1, title2) if (title1 and title2) else 0.0
                
                # Rule 1: High title similarity (>50%)
                if title_similarity > 0.5:
                    is_duplicate = True
                    match_reason = f"Title similarity: {title_similarity:.1%}"
                
                # Rule 2: Same normalized URL AND title similarity >50%
                elif (normalized_url1 and normalized_url2 and 
                      normalized_url1 == normalized_url2 and 
                      title_similarity > 0.5):
                    is_duplicate = True
                    match_reason = f"Same URL (no query) + title similarity: {title_similarity:.1%}"
                
                if is_duplicate:
                    group.append(doc2)
                    group_indices.add(j)
            
            # Add to duplicate groups if we found duplicates
            if len(group) > 1:
                # Create example info for the group
                example_urls = [doc['data'].get('source_url', '') for doc in group[:3]]
                example_titles = [doc['data'].get('title', '')[:50] + "..." if len(doc['data'].get('title', '')) > 50 
                                else doc['data'].get('title', '') for doc in group[:3]]
                
                duplicate_groups.append({
                    'normalized_url': normalized_url1,  # Representative URL
                    'documents': group,
                    'count': len(group),
                    'example_urls': example_urls,
                    'example_titles': example_titles,
                    'match_reason': match_reason  # Why these were grouped
                })
                total_duplicates += len(group) - 1
                processed_indices.update(group_indices)
        
        analysis_result = {
            "csv_file": csv_file_path,
            "mode": "advanced",
            "total_documents": len(documents),
            "duplicate_groups": len(duplicate_groups),
            "total_duplicates": total_duplicates,
            "groups": duplicate_groups,
            "warning": "Advanced mode: Smart URL + title similarity matching. Review carefully before deletion."
        }
        
        safe_print(f"Advanced analysis found {len(duplicate_groups)} duplicate groups with {total_duplicates} total duplicates")
        safe_print(f"📊 Used smart matching: title similarity >50% OR same URL (no query) + title similarity >50%")
        
        return analysis_result
    
    def export_csv_duplicates(self, analysis: Dict[str, Any], output_file: Optional[str] = None) -> str:
        """Export duplicate analysis to CSV file"""
        import csv
        
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            mode_suffix = "_advanced" if analysis.get("mode") == "advanced" else ""
            output_file = f"readwise_duplicates{mode_suffix}_{timestamp}.csv"
        
        try:
            with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
                # Add extra fields for advanced mode
                fieldnames = ['group_id', 'normalized_url', 'row_number', 'id', 'title', 'source_url', 'author', 'source', 'notes', 'tags', 'created_at', 'location']
                if analysis.get("mode") == "advanced":
                    fieldnames.insert(2, 'match_reason')     # Why these were grouped
                    fieldnames.insert(3, 'example_urls')     # Sample URLs in group
                    fieldnames.insert(4, 'example_titles')   # Sample titles in group
                
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for group_id, group in enumerate(analysis['groups'], start=1):
                    # For advanced mode, prepare additional info
                    match_reason_str = ""
                    example_urls_str = ""
                    example_titles_str = ""
                    
                    if analysis.get("mode") == "advanced":
                        match_reason_str = group.get('match_reason', '')
                        if 'example_urls' in group:
                            example_urls_str = " | ".join(group['example_urls'][:3])
                        if 'example_titles' in group:
                            example_titles_str = " | ".join(group['example_titles'][:3])
                    
                    for idx, doc_info in enumerate(group['documents']):
                        row_data = doc_info['data']
                        output_row = {
                            'group_id': group_id,
                            'normalized_url': group['normalized_url'],
                            'row_number': doc_info['row_number'],
                            'id': row_data.get('id', ''),
                            'title': row_data.get('title', ''),
                            'source_url': row_data.get('source_url', ''),
                            'author': row_data.get('author', ''),
                            'source': row_data.get('source', ''),
                            'notes': row_data.get('notes', ''),
                            'tags': row_data.get('tags', ''),
                            'created_at': row_data.get('created_at', ''),
                            'location': row_data.get('location', '')
                        }
                        
                        # Add advanced mode fields only for the first row of each group
                        if analysis.get("mode") == "advanced":
                            output_row['match_reason'] = match_reason_str if idx == 0 else ""
                            output_row['example_urls'] = example_urls_str if idx == 0 else ""
                            output_row['example_titles'] = example_titles_str if idx == 0 else ""
                        
                        writer.writerow(output_row)
            
            safe_print(f"Duplicate analysis exported to: {output_file}")
            return output_file
            
        except Exception as e:
            safe_print(f"Failed to export duplicates to CSV: {e}")
            return ""

    def export_analysis_report(self, analysis: Dict[str, Any], filename: Optional[str] = None) -> str:
        """Export analysis report to file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"duplicate_analysis_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, ensure_ascii=False, indent=2)
        
        safe_print(f"Analysis report exported to: {filename}")
        return filename 

    def analyze_deletion_plan(self, csv_file_path: str, prefer_newer: bool = False) -> Dict[str, Any]:
        """Analyze duplicates CSV file and create deletion plan based on NOTE, TAG and created_at priority"""
        import csv
        from datetime import datetime
        
        safe_print(f"Analyzing deletion plan from CSV file: {csv_file_path}")
        
        groups = {}
        all_documents = []
        
        # Read CSV file
        try:
            with open(csv_file_path, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    all_documents.append(row)
                    group_id = row.get('group_id', '')
                    if group_id:
                        if group_id not in groups:
                            groups[group_id] = []
                        groups[group_id].append(row)
        except Exception as e:
            return {"error": f"Failed to read CSV file: {e}"}
        
        # Analyze each group and determine what to keep/delete
        deletion_plan = []
        total_to_delete = 0
        
        for group_id, documents in groups.items():
            if len(documents) <= 1:
                continue  # Skip groups with only one document
            
            # Find the best document to keep based on priority
            best_document = self._select_best_document_to_keep(documents, prefer_newer=prefer_newer)
            
            # Documents to delete
            documents_to_delete = [doc for doc in documents if doc['id'] != best_document['id']]
            
            group_plan = {
                'group_id': group_id,
                'normalized_url': documents[0].get('normalized_url', ''),
                'total_documents': len(documents),
                'keep_document': best_document,
                'delete_documents': documents_to_delete,
                'deletion_count': len(documents_to_delete)
            }
            
            deletion_plan.append(group_plan)
            total_to_delete += len(documents_to_delete)
        
        analysis_result = {
            "csv_file": csv_file_path,
            "total_documents": len(all_documents),
            "duplicate_groups": len(deletion_plan),
            "total_to_delete": total_to_delete,
            "groups": deletion_plan
        }
        
        safe_print(f"Created deletion plan for {len(deletion_plan)} groups, planning to delete {total_to_delete} documents")
        
        return analysis_result
    
    def _select_best_document_to_keep(self, documents: List[Dict[str, Any]], prefer_newer: bool = False) -> Dict[str, Any]:
        """Select the best document to keep based on NOTE, TAG, and created_at priority"""
        from datetime import datetime
        
        # Priority 1: Documents with notes (non-empty notes field)
        docs_with_notes = [doc for doc in documents if doc.get('notes', '').strip()]
        docs_without_notes = [doc for doc in documents if not doc.get('notes', '').strip()]
        
        # If only some documents have notes, prefer those with notes
        if docs_with_notes and docs_without_notes:
            if len(docs_with_notes) == 1:
                return docs_with_notes[0]
            # If multiple have notes, continue to next criteria with this subset
            documents = docs_with_notes
        # If all have notes or all don't have notes, continue with all documents
        
        # Priority 2: Documents with tags (non-empty tags field)
        docs_with_tags = [doc for doc in documents if doc.get('tags', '').strip()]
        docs_without_tags = [doc for doc in documents if not doc.get('tags', '').strip()]
        
        # If only some documents have tags, prefer those with tags
        if docs_with_tags and docs_without_tags:
            if len(docs_with_tags) == 1:
                return docs_with_tags[0]
            # If multiple have tags, continue to next criteria with this subset
            documents = docs_with_tags
        # If all have tags or all don't have tags, continue with all documents
        
        # Priority 3: Date preference (older/newer based on prefer_newer flag)
        documents_with_dates = []
        for doc in documents:
            created_at = doc.get('created_at', '').strip()
            if created_at:
                try:
                    # Try to parse the date
                    # Common formats: ISO format, or readwise format
                    if 'T' in created_at:
                        # ISO format like "2023-07-27T10:30:00Z"
                        date_obj = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    else:
                        # Try other common formats
                        date_obj = datetime.strptime(created_at, "%Y-%m-%d %H:%M:%S")
                    
                    documents_with_dates.append((doc, date_obj))
                except (ValueError, TypeError):
                    # If date parsing fails, treat as no date
                    pass
        
        if documents_with_dates:
            # Sort by date based on preference
            if prefer_newer:
                # Sort by date descending (newest first)
                documents_with_dates.sort(key=lambda x: x[1], reverse=True)
            else:
                # Sort by date ascending (oldest first) - default behavior
                documents_with_dates.sort(key=lambda x: x[1], reverse=False)
            return documents_with_dates[0][0]
        
        # Fallback: return the first document if no other criteria can be applied
        return documents[0]
    
    def export_deletion_plan(self, analysis: Dict[str, Any], output_file: Optional[str] = None) -> str:
        """Export deletion plan to CSV file"""
        import csv
        
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"readwise_deletion_plan_{timestamp}.csv"
        
        try:
            with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = [
                    'group_id', 'action', 'document_id', 'title', 'source_url', 
                    'author', 'notes', 'tags', 'created_at', 'reason'
                ]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for group in analysis['groups']:
                    # Write the document to keep
                    keep_doc = group['keep_document']
                    writer.writerow({
                        'group_id': group['group_id'],
                        'action': 'KEEP',
                        'document_id': keep_doc.get('id', ''),
                        'title': keep_doc.get('title', ''),
                        'source_url': keep_doc.get('source_url', ''),
                        'author': keep_doc.get('author', ''),
                        'notes': keep_doc.get('notes', ''),
                        'tags': keep_doc.get('tags', ''),
                        'created_at': keep_doc.get('created_at', ''),
                        'reason': self._get_keep_reason(keep_doc, group['delete_documents'])
                    })
                    
                    # Write the documents to delete
                    for delete_doc in group['delete_documents']:
                        writer.writerow({
                            'group_id': group['group_id'],
                            'action': 'DELETE',
                            'document_id': delete_doc.get('id', ''),
                            'title': delete_doc.get('title', ''),
                            'source_url': delete_doc.get('source_url', ''),
                            'author': delete_doc.get('author', ''),
                            'notes': delete_doc.get('notes', ''),
                            'tags': delete_doc.get('tags', ''),
                            'created_at': delete_doc.get('created_at', ''),
                            'reason': 'Duplicate document'
                        })
            
            safe_print(f"Deletion plan exported to: {output_file}")
            return output_file
            
        except Exception as e:
            safe_print(f"Failed to export deletion plan to CSV: {e}")
            return ""
    
    def _get_keep_reason(self, keep_doc: Dict[str, Any], delete_docs: List[Dict[str, Any]]) -> str:
        """Generate reason why this document was selected to keep"""
        has_notes = bool(keep_doc.get('notes', '').strip())
        has_tags = bool(keep_doc.get('tags', '').strip())
        
        # Check if any documents being deleted have notes/tags
        deleted_have_notes = any(bool(doc.get('notes', '').strip()) for doc in delete_docs)
        deleted_have_tags = any(bool(doc.get('tags', '').strip()) for doc in delete_docs)
        
        if has_notes and not deleted_have_notes:
            return "Has notes"
        elif has_tags and not deleted_have_tags:
            return "Has tags"
        elif has_notes and deleted_have_notes:
            return "Has notes (preferred among notes)"
        elif has_tags and deleted_have_tags:
            return "Has tags (preferred among tags)"
        else:
            return "Oldest creation date" 

    def execute_deletion_plan(self, csv_file_path: str, dry_run: bool = True, batch_size: int = 5) -> Dict[str, Any]:
        """Execute deletion plan from CSV file"""
        import csv
        import time
        import signal
        from datetime import datetime
        
        safe_print(f"{'[DRY RUN] ' if dry_run else ''}Executing deletion plan from: {csv_file_path}")
        
        deletion_candidates = []
        
        # Read deletion plan CSV
        try:
            with open(csv_file_path, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    if row.get('action', '').upper() == 'DELETE':
                        deletion_candidates.append({
                            'document_id': row.get('document_id', ''),
                            'title': row.get('title', ''),
                            'source_url': row.get('source_url', ''),
                            'reason': row.get('reason', ''),
                            'group_id': row.get('group_id', '')
                        })
        except Exception as e:
            return {"error": f"Failed to read CSV file: {e}"}
        
        if not deletion_candidates:
            safe_print("No documents marked for deletion found in the plan.")
            return {
                "total_candidates": 0,
                "processed": 0,
                "successful_deletions": 0,
                "failed_deletions": 0,
                "errors": []
            }
        
        safe_print(f"Found {len(deletion_candidates)} documents marked for deletion")
        
        if dry_run:
            safe_print("\n=== DRY RUN MODE - NO ACTUAL DELETIONS WILL BE PERFORMED ===")
            safe_print("Documents that would be deleted:")
            for i, doc in enumerate(deletion_candidates[:10], 1):  # Show first 10
                safe_print(f"  {i}. [{doc['group_id']}] {doc['title'][:60]}...")
                safe_print(f"     ID: {doc['document_id']}")
                safe_print(f"     Reason: {doc['reason']}")
                safe_print(f"     URL: {doc['source_url'][:80]}...")
                safe_print("")
            
            if len(deletion_candidates) > 10:
                safe_print(f"... and {len(deletion_candidates) - 10} more documents")
            
            return {
                "dry_run": True,
                "total_candidates": len(deletion_candidates),
                "preview_shown": min(10, len(deletion_candidates))
            }
        
        # Execute actual deletions
        safe_print(f"\n⚠️  WARNING: About to delete {len(deletion_candidates)} documents!")
        safe_print("This action cannot be undone.")
        
        successful_deletions = 0
        failed_deletions = 0
        errors = []
        successfully_deleted_ids = set()  # Track successfully deleted document IDs
        interrupted = False  # Track if Ctrl+C was pressed
        
        # Setup signal handlers for graceful shutdown across platforms
        def signal_handler(signum, frame):
            nonlocal interrupted
            interrupted = True
            
            # Identify the signal received
            signal_name = "Unknown signal"
            if signum == signal.SIGINT:
                signal_name = "Ctrl+C (SIGINT)"
            elif signum == signal.SIGTERM:
                signal_name = "Termination request (SIGTERM)"
            elif hasattr(signal, 'SIGBREAK') and signum == signal.SIGBREAK:
                signal_name = "Ctrl+Break or window close (SIGBREAK)"
            elif hasattr(signal, 'SIGHUP') and signum == signal.SIGHUP:
                signal_name = "Terminal hangup (SIGHUP)"
            
            safe_print(f"\n\n🛑 {signal_name} detected - gracefully stopping after current document...")
            safe_print("⚠️  Please wait for safe completion...")
        
        # Register signal handlers for graceful shutdown across platforms
        original_handlers = {}
        signals_to_handle = [signal.SIGINT, signal.SIGTERM]
        
        # Add platform-specific signals
        if hasattr(signal, 'SIGBREAK'):  # Windows - Ctrl+Break and some window close events
            signals_to_handle.append(signal.SIGBREAK)
        if hasattr(signal, 'SIGHUP'):    # Unix/Linux/WSL - terminal hangup/close
            signals_to_handle.append(signal.SIGHUP)
        
        # Register all available signal handlers
        for sig in signals_to_handle:
            try:
                original_handlers[sig] = signal.signal(sig, signal_handler)
            except (OSError, ValueError) as e:
                # Some signals might not be available on all platforms
                safe_print(f"Warning: Could not register handler for signal {sig}: {e}")
        
        try:
            # Process in batches to respect rate limits
            for i in range(0, len(deletion_candidates), batch_size):
                if interrupted:
                    safe_print("🛑 Stopping due to user interrupt...")
                    break
                    
                batch = deletion_candidates[i:i+batch_size]
                safe_print(f"\nProcessing batch {i//batch_size + 1}/{(len(deletion_candidates) + batch_size - 1)//batch_size}")
                
                for doc in batch:
                    if interrupted:
                        safe_print("🛑 Stopping due to user interrupt...")
                        break
                        
                    safe_print(f"Deleting: [{doc['group_id']}] {doc['title'][:50]}...")
                    
                    # Implement retry logic for 429 errors (unlimited retries)
                    retry_count = 0
                    deletion_successful = False
                    
                    while not deletion_successful and not interrupted:
                        try:
                            result = self.client.delete_document(doc['document_id'])
                            
                            if result:
                                successful_deletions += 1
                                successfully_deleted_ids.add(doc['document_id'])
                                safe_print(f"  ✅ Deleted successfully")
                                deletion_successful = True
                            else:
                                failed_deletions += 1
                                error_msg = "API returned failure status"
                                errors.append(f"Document {doc['document_id']}: {error_msg}")
                                safe_print(f"  ❌ Failed: {error_msg}")
                                deletion_successful = True  # Don't retry for non-429 failures
                        
                        except Exception as e:
                            error_msg = str(e)
                            
                            # Check if this is a 429 (rate limit) error
                            if "429" in error_msg:
                                retry_count += 1
                                
                                # Try to extract Retry-After value from error message
                                retry_after = self._extract_retry_after(e)
                                if retry_after:
                                    safe_print(f"  ⚠️  Rate limited (429). Retry #{retry_count} after {retry_after}s...")
                                    time.sleep(retry_after)
                                else:
                                    # Default retry delay if no Retry-After header
                                    default_delay = 60  # 60 seconds default
                                    safe_print(f"  ⚠️  Rate limited (429). Retry #{retry_count} after {default_delay}s (default)...")
                                    time.sleep(default_delay)
                                # Continue the loop to retry
                            else:
                                # Non-429 error - fail immediately
                                failed_deletions += 1
                                errors.append(f"Document {doc['document_id']}: {error_msg}")
                                safe_print(f"  ❌ Exception: {error_msg}")
                                deletion_successful = True  # Exit retry loop
                    
                    if interrupted:
                        break
                    
                    # Respect Readwise Reader API rate limit: 20 requests per minute
                    # Wait 3.5 seconds between requests to stay well under the limit
                    if doc != batch[-1] or i + batch_size < len(deletion_candidates):
                        safe_print(f"  ⏳ Waiting 3.5s to respect API rate limit (20 req/min)...")
                        time.sleep(3.5)
                
                if interrupted:
                    break
        
        finally:
            # Restore all original signal handlers
            for sig, original_handler in original_handlers.items():
                try:
                    signal.signal(sig, original_handler)
                except (OSError, ValueError):
                    # Ignore errors when restoring handlers
                    pass
        
        # Generate execution report
        completion_status = "INTERRUPTED" if interrupted else "COMPLETED"
        safe_print(f"\n=== DELETION EXECUTION {completion_status} ===")
        safe_print(f"Total candidates: {len(deletion_candidates)}")
        safe_print(f"Successful deletions: {successful_deletions}")
        safe_print(f"Failed deletions: {failed_deletions}")
        
        if interrupted:
            safe_print(f"\n⚠️  Execution was interrupted by user (Ctrl+C)")
            safe_print(f"Processed: {successful_deletions + failed_deletions}/{len(deletion_candidates)} documents")
        
        if errors:
            safe_print(f"\nErrors encountered:")
            for error in errors[:5]:  # Show first 5 errors
                safe_print(f"  - {error}")
            if len(errors) > 5:
                safe_print(f"  ... and {len(errors) - 5} more errors")
        
        # Create updated plan file ONLY on normal completion or Ctrl+C interrupt
        # NOT on unexpected crashes or exceptions
        new_plan_file = None
        if not dry_run and (successfully_deleted_ids or len(errors) > 0):
            # Save updated plan since we processed some documents
            safe_print(f"\n💾 Saving updated deletion plan...")
            new_plan_file = self._update_deletion_plan(
                csv_file_path, 
                successfully_deleted_ids, 
                errors
            )
        
        # Export execution report
        report_data = {
            "execution_timestamp": datetime.now().isoformat(),
            "completion_status": completion_status,
            "interrupted": interrupted,
            "total_candidates": len(deletion_candidates),
            "successful_deletions": successful_deletions,
            "failed_deletions": failed_deletions,
            "success_rate": f"{(successful_deletions / len(deletion_candidates) * 100):.1f}%" if deletion_candidates else "0%",
            "errors": errors,
            "updated_plan_file": new_plan_file
        }
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_filename = f"readwise_deletion_execution_{timestamp}.json"
        
        try:
            import json
            with open(report_filename, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False)
            safe_print(f"Execution report saved to: {report_filename}")
        except Exception as e:
            safe_print(f"Warning: Could not save execution report: {e}")
        
        return {
            "total_candidates": len(deletion_candidates),
            "processed": successful_deletions + failed_deletions,
            "successful_deletions": successful_deletions,
            "failed_deletions": failed_deletions,
            "success_rate": successful_deletions / len(deletion_candidates) if deletion_candidates else 0,
            "errors": errors,
            "report_file": report_filename,
            "updated_plan_file": new_plan_file,
            "interrupted": interrupted,
            "completion_status": completion_status
        }
    
    def _extract_retry_after(self, exception: Exception) -> Optional[int]:
        """Extract Retry-After value from HTTP exception"""
        try:
            # Check if this is a requests HTTPError with response object
            response = getattr(exception, 'response', None)
            if response is not None:
                # Get Retry-After header (can be in seconds or HTTP date format)
                retry_after = response.headers.get('Retry-After')
                if retry_after:
                    try:
                        # Try to parse as integer (seconds)
                        return int(retry_after)
                    except ValueError:
                        # If not integer, might be HTTP date format
                        # For simplicity, return None and use default delay
                        safe_print(f"    Warning: Could not parse Retry-After header: {retry_after}")
                        return None
            
            return None
        except Exception:
            # If any error occurs during extraction, return None
            return None
    
    def _update_deletion_plan(self, original_csv_path: str, successfully_deleted_ids: set, errors: List[str]) -> Optional[str]:
        """Update deletion plan by removing successfully deleted and 404 documents"""
        import csv
        import os
        from datetime import datetime
        
        # Extract document IDs that had 404 errors
        error_404_ids = set()
        for error in errors:
            if "404" in error:
                # Extract document ID from error message like "Document 01abc123: 404 Client Error..."
                if "Document " in error and ":" in error:
                    doc_id = error.split("Document ")[1].split(":")[0].strip()
                    error_404_ids.add(doc_id)
        
        # Combine successfully deleted IDs and 404 error IDs
        processed_document_ids = successfully_deleted_ids.union(error_404_ids)
        
        if len(processed_document_ids) == 0:
            # No documents were processed, no need to update plan
            return None
        
        safe_print(f"\n📝 Updating deletion plan...")
        safe_print(f"   - Successfully deleted: {len(successfully_deleted_ids)} documents")
        safe_print(f"   - 404 errors (already deleted): {len(error_404_ids)} documents")
        
        # Read original plan file and filter out processed documents
        remaining_rows = []
        total_original_rows = 0
        
        try:
            with open(original_csv_path, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    total_original_rows += 1
                    document_id = row.get('document_id', '').strip()
                    action = row.get('action', '').upper()
                    
                    # Keep KEEP actions and DELETE actions that weren't processed
                    if action == 'KEEP' or (action == 'DELETE' and document_id not in processed_document_ids):
                        remaining_rows.append(row)
        
        except Exception as e:
            safe_print(f"Warning: Could not read original plan file: {e}")
            return None
        
        # Calculate how many DELETE rows remain
        remaining_delete_count = sum(1 for row in remaining_rows if row.get('action', '').upper() == 'DELETE')
        
        if remaining_delete_count == 0:
            safe_print(f"✅ All deletion tasks completed! No remaining documents to delete.")
            return None
        
        # Generate new plan filename
        original_basename = os.path.splitext(os.path.basename(original_csv_path))[0]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        new_plan_filename = f"{original_basename}_updated_{timestamp}.csv"
        
        # Write updated plan file
        try:
            with open(new_plan_filename, 'w', newline='', encoding='utf-8') as csvfile:
                if remaining_rows:
                    fieldnames = remaining_rows[0].keys()
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(remaining_rows)
            
            processed_count = len(processed_document_ids)
            safe_print(f"📄 Updated plan saved: {new_plan_filename}")
            safe_print(f"   - Original plan: {total_original_rows} rows")
            safe_print(f"   - Processed: {processed_count} documents (deleted + 404)")
            safe_print(f"   - Remaining: {remaining_delete_count} documents to delete")
            
            return new_plan_filename
            
        except Exception as e:
            safe_print(f"Warning: Could not save updated plan file: {e}")
            return None 