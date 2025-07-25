import requests
import json
import time
from typing import List, Dict, Optional, Any
from datetime import datetime
from config import Config

class ReadwiseClient:
    """Readwise Reader API client"""
    
    def __init__(self, config: Config = None):
        self.config = config or Config()
        
    def verify_token(self) -> bool:
        """Verify if API token is valid"""
        try:
            response = requests.get(
                self.config.auth_url,
                headers=self.config.get_headers()
            )
            return response.status_code == 204
        except Exception as e:
            print(f"Error verifying token: {e}")
            return False
    
    def save_document(self, 
                     url: str,
                     html: Optional[str] = None,
                     should_clean_html: bool = False,
                     title: Optional[str] = None,
                     author: Optional[str] = None,
                     summary: Optional[str] = None,
                     published_date: Optional[str] = None,
                     image_url: Optional[str] = None,
                     location: str = "new",
                     category: Optional[str] = None,
                     saved_using: Optional[str] = None,
                     tags: Optional[List[str]] = None,
                     notes: Optional[str] = None) -> Dict[str, Any]:
        """Save new document to Reader"""
        
        data = {"url": url}
        
        if html is not None:
            data["html"] = html
        if should_clean_html:
            data["should_clean_html"] = should_clean_html
        if title is not None:
            data["title"] = title
        if author is not None:
            data["author"] = author
        if summary is not None:
            data["summary"] = summary
        if published_date is not None:
            data["published_date"] = published_date
        if image_url is not None:
            data["image_url"] = image_url
        if location != "new":
            data["location"] = location
        if category is not None:
            data["category"] = category
        if saved_using is not None:
            data["saved_using"] = saved_using
        if tags is not None:
            data["tags"] = tags
        if notes is not None:
            data["notes"] = notes
            
        try:
            response = requests.post(
                f"{self.config.base_url}/save/",
                headers=self.config.get_headers(),
                json=data
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error saving document: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response content: {e.response.text}")
            raise
    
    def list_documents(self,
                      document_id: Optional[str] = None,
                      updated_after: Optional[str] = None,
                      location: Optional[str] = None,
                      category: Optional[str] = None,
                      tags: Optional[List[str]] = None,
                      with_html_content: bool = False,
                      page_cursor: Optional[str] = None) -> Dict[str, Any]:
        """List documents"""
        
        params = {}
        
        if document_id is not None:
            params["id"] = document_id
        if updated_after is not None:
            params["updatedAfter"] = updated_after
        if location is not None:
            params["location"] = location
        if category is not None:
            params["category"] = category
        if tags is not None:
            for tag in tags:
                params["tag"] = tag  # API supports multiple tag parameters
        if with_html_content:
            params["withHtmlContent"] = "true"
        if page_cursor is not None:
            params["pageCursor"] = page_cursor
            
        try:
            response = requests.get(
                f"{self.config.base_url}/list/",
                headers=self.config.get_headers(),
                params=params
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error listing documents: {e}")
            raise
    
    def get_all_documents(self,
                         location: Optional[str] = None,
                         category: Optional[str] = None,
                         updated_after: Optional[str] = None,
                         delay_seconds: float = 3.0,
                         max_documents: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get all documents (handle pagination with rate limiting)
        
        Args:
            location: Document location filter
            category: Document category filter  
            updated_after: Only get documents updated after this date
            delay_seconds: Delay between API calls to respect rate limits (default 3s)
            max_documents: Stop after fetching this many documents (None for all)
        """
        
        all_documents = []
        next_page_cursor = None
        request_count = 0
        
        print("Fetching all documents with rate limiting...")
        
        while True:
            try:
                # Add delay between requests to respect rate limits (20 requests/minute = 3s between requests)
                if request_count > 0:
                    print(f"Waiting {delay_seconds}s before next request (rate limiting)...")
                    time.sleep(delay_seconds)
                
                response = self.list_documents(
                    location=location,
                    category=category,
                    updated_after=updated_after,
                    page_cursor=next_page_cursor
                )
                
                request_count += 1
                results = response.get('results', [])
                all_documents.extend(results)
                next_page_cursor = response.get('nextPageCursor')
                
                print(f"Fetched batch {request_count}: {len(results)} documents (total: {len(all_documents)})")
                
                # Check if we've reached the maximum number of documents
                if max_documents and len(all_documents) >= max_documents:
                    all_documents = all_documents[:max_documents]
                    print(f"Reached maximum document limit ({max_documents}), stopping...")
                    break
                
                if not next_page_cursor:
                    break
                    
            except requests.exceptions.RequestException as e:
                if hasattr(e, 'response') and e.response is not None:
                    if e.response.status_code == 429:  # Rate limit exceeded
                        print(f"Rate limit hit, waiting 60 seconds before retry...")
                        time.sleep(60)
                        continue
                print(f"Error fetching documents: {e}")
                raise
                
        print(f"Completed fetching {len(all_documents)} documents in {request_count} requests")
        return all_documents
    
    def update_document(self,
                       document_id: str,
                       title: Optional[str] = None,
                       author: Optional[str] = None,
                       summary: Optional[str] = None,
                       published_date: Optional[str] = None,
                       image_url: Optional[str] = None,
                       location: Optional[str] = None,
                       category: Optional[str] = None) -> Dict[str, Any]:
        """Update document"""
        
        data = {}
        
        if title is not None:
            data["title"] = title
        if author is not None:
            data["author"] = author
        if summary is not None:
            data["summary"] = summary
        if published_date is not None:
            data["published_date"] = published_date
        if image_url is not None:
            data["image_url"] = image_url
        if location is not None:
            data["location"] = location
        if category is not None:
            data["category"] = category
            
        try:
            response = requests.patch(
                f"{self.config.base_url}/update/{document_id}/",
                headers=self.config.get_headers(),
                json=data
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error updating document: {e}")
            raise
    
    def delete_document(self, document_id: str) -> bool:
        """Delete document"""
        
        try:
            response = requests.delete(
                f"{self.config.base_url}/delete/{document_id}/",
                headers=self.config.get_headers()
            )
            response.raise_for_status()
            return response.status_code == 204
        except requests.exceptions.RequestException as e:
            print(f"Error deleting document: {e}")
            raise
    
    def list_tags(self, page_cursor: Optional[str] = None) -> Dict[str, Any]:
        """List all tags"""
        
        params = {}
        if page_cursor is not None:
            params["pageCursor"] = page_cursor
            
        try:
            response = requests.get(
                f"{self.config.base_url}/tags/",
                headers=self.config.get_headers(),
                params=params
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error listing tags: {e}")
            raise
    
    def get_all_tags(self, delay_seconds: float = 3.0) -> List[Dict[str, str]]:
        """Get all tags (handle pagination with rate limiting)
        
        Args:
            delay_seconds: Delay between API calls to respect rate limits (default 3s)
        """
        
        all_tags = []
        next_page_cursor = None
        request_count = 0
        
        while True:
            try:
                # Add delay between requests to respect rate limits
                if request_count > 0:
                    time.sleep(delay_seconds)
                
                response = self.list_tags(page_cursor=next_page_cursor)
                request_count += 1
                
                results = response.get('results', [])
                all_tags.extend(results)
                next_page_cursor = response.get('nextPageCursor')
                
                if not next_page_cursor:
                    break
                    
            except requests.exceptions.RequestException as e:
                if hasattr(e, 'response') and e.response is not None:
                    if e.response.status_code == 429:  # Rate limit exceeded
                        time.sleep(60)
                        continue
                raise
                
        return all_tags 