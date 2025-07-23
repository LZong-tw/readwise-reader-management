from typing import List, Dict, Optional, Any
from datetime import datetime
import json
from readwise_client import ReadwiseClient
from config import Config

class DocumentManager:
    """Readwise document manager"""
    
    def __init__(self, client: Optional[ReadwiseClient] = None):
        self.client = client or ReadwiseClient()
        
    def add_article(self, url: str, title: Optional[str] = None, 
                   tags: Optional[List[str]] = None, location: str = "new") -> Dict[str, Any]:
        """Add article"""
        print(f"Adding article: {url}")
        result = self.client.save_document(
            url=url,
            title=title,
            tags=tags,
            location=location,
            category="article"
        )
        print(f"Article added, ID: {result.get('id')}")
        return result
    
    def add_from_html(self, url: str, html: str, title: Optional[str] = None,
                     author: Optional[str] = None, tags: Optional[List[str]] = None,
                     clean_html: bool = True) -> Dict[str, Any]:
        """Add document from HTML content"""
        print(f"Adding document from HTML: {title or url}")
        result = self.client.save_document(
            url=url,
            html=html,
            should_clean_html=clean_html,
            title=title,
            author=author,
            tags=tags,
            category="article"
        )
        print(f"Document added, ID: {result.get('id')}")
        return result
    
    def get_documents(self, location: Optional[str] = None, 
                     category: Optional[str] = None,
                     tags: Optional[List[str]] = None,
                     limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get document list"""
        print("Getting document list...")
        
        if limit and limit <= 100:
            # If limit is small, use single request
            response = self.client.list_documents(
                location=location,
                category=category,
                tags=tags
            )
            documents = response.get('results', [])
            if limit:
                documents = documents[:limit]
        else:
            # Get all documents
            documents = self.client.get_all_documents(
                location=location,
                category=category
            )
            if limit:
                documents = documents[:limit]
        
        print(f"Found {len(documents)} documents")
        return documents
    
    def search_documents(self, keyword: str, 
                        location: Optional[str] = None) -> List[Dict[str, Any]]:
        """Search documents (based on title)"""
        print(f"Searching for documents containing '{keyword}'...")
        all_docs = self.get_documents(location=location)
        
        matching_docs = []
        for doc in all_docs:
            title = doc.get('title', '').lower()
            if keyword.lower() in title:
                matching_docs.append(doc)
        
        print(f"Found {len(matching_docs)} matching documents")
        return matching_docs
    
    def move_document(self, document_id: str, location: str) -> Dict[str, Any]:
        """Move document to different location"""
        valid_locations = ['new', 'later', 'archive', 'feed']
        if location not in valid_locations:
            raise ValueError(f"Invalid location: {location}. Valid locations: {valid_locations}")
        
        print(f"Moving document {document_id} to {location}")
        result = self.client.update_document(document_id, location=location)
        print(f"Document moved to {location}")
        return result
    
    def update_document_metadata(self, document_id: str,
                               title: Optional[str] = None,
                               author: Optional[str] = None,
                               summary: Optional[str] = None) -> Dict[str, Any]:
        """Update document metadata"""
        print(f"Updating metadata for document {document_id}")
        result = self.client.update_document(
            document_id=document_id,
            title=title,
            author=author,
            summary=summary
        )
        print("Document metadata updated")
        return result
    
    def delete_document(self, document_id: str) -> bool:
        """Delete document"""
        print(f"Deleting document {document_id}")
        result = self.client.delete_document(document_id)
        if result:
            print("Document deleted")
        else:
            print("Delete failed")
        return result
    
    def archive_document(self, document_id: str) -> Dict[str, Any]:
        """Archive document"""
        return self.move_document(document_id, "archive")
    
    def save_for_later(self, document_id: str) -> Dict[str, Any]:
        """Mark for later reading"""
        return self.move_document(document_id, "later")
    
    def get_document_by_id(self, document_id: str) -> Optional[Dict[str, Any]]:
        """Get single document by ID"""
        try:
            response = self.client.list_documents(document_id=document_id)
            results = response.get('results', [])
            return results[0] if results else None
        except Exception as e:
            print(f"Error getting document: {e}")
            return None
    
    def get_stats(self) -> Dict[str, int]:
        """Get document statistics"""
        print("Calculating statistics...")
        
        stats = {
            'total': 0,
            'new': 0,
            'later': 0,
            'archive': 0,
            'feed': 0
        }
        
        # Get document count for each location
        for location in ['new', 'later', 'archive', 'feed']:
            try:
                docs = self.get_documents(location=location, limit=1)
                # Need to get total count, so use full API response
                response = self.client.list_documents(location=location)
                count = response.get('count', 0)
                stats[location] = count
                stats['total'] += count
            except Exception as e:
                print(f"Error getting {location} statistics: {e}")
                stats[location] = 0
        
        return stats
    
    def export_documents(self, location: Optional[str] = None, 
                        filename: Optional[str] = None) -> str:
        """Export documents to JSON file"""
        docs = self.get_documents(location=location)
        
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            location_suffix = f"_{location}" if location else ""
            filename = f"readwise_export{location_suffix}_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(docs, f, ensure_ascii=False, indent=2)
        
        print(f"Exported {len(docs)} documents to {filename}")
        return filename
    
    def display_document_summary(self, document: Dict[str, Any]) -> None:
        """Display document summary information"""
        print(f"\n--- Document Summary ---")
        print(f"ID: {document.get('id')}")
        print(f"Title: {document.get('title', 'N/A')}")
        print(f"Author: {document.get('author', 'N/A')}")
        print(f"URL: {document.get('source_url', document.get('url', 'N/A'))}")
        print(f"Location: {document.get('location', 'N/A')}")
        print(f"Category: {document.get('category', 'N/A')}")
        print(f"Created: {document.get('created_at', 'N/A')}")
        print(f"Updated: {document.get('updated_at', 'N/A')}")
        
        tags = document.get('tags', {})
        if tags:
            tag_names = [tag.get('name', '') for tag in tags]
            print(f"Tags: {', '.join(tag_names)}")
        
        summary = document.get('summary')
        if summary:
            print(f"Summary: {summary[:100]}..." if len(summary) > 100 else f"Summary: {summary}")
        
        print("-" * 30) 