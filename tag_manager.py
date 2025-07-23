from typing import List, Dict, Optional, Any
from collections import Counter
from readwise_client import ReadwiseClient

class TagManager:
    """Readwise tag manager"""
    
    def __init__(self, client: Optional[ReadwiseClient] = None):
        self.client = client or ReadwiseClient()
        
    def get_all_tags(self) -> List[Dict[str, str]]:
        """Get all tags"""
        print("Getting all tags...")
        tags = self.client.get_all_tags()
        print(f"Found {len(tags)} tags")
        return tags
    
    def list_tags(self, sort_by: str = "name") -> List[Dict[str, str]]:
        """List tags with sorting"""
        tags = self.get_all_tags()
        
        if sort_by == "name":
            tags.sort(key=lambda x: x.get('name', '').lower())
        elif sort_by == "key":
            tags.sort(key=lambda x: x.get('key', '').lower())
        
        return tags
    
    def search_tags(self, keyword: str) -> List[Dict[str, str]]:
        """Search tags"""
        print(f"Searching for tags containing '{keyword}'...")
        all_tags = self.get_all_tags()
        
        matching_tags = []
        keyword_lower = keyword.lower()
        
        for tag in all_tags:
            tag_name = tag.get('name', '').lower()
            tag_key = tag.get('key', '').lower()
            
            if keyword_lower in tag_name or keyword_lower in tag_key:
                matching_tags.append(tag)
        
        print(f"Found {len(matching_tags)} matching tags")
        return matching_tags
    
    def get_documents_by_tag(self, tag_key: str) -> List[Dict[str, Any]]:
        """Get documents by tag"""
        print(f"Getting documents for tag '{tag_key}'...")
        
        # Use list_documents API tag parameter
        response = self.client.list_documents(tags=[tag_key])
        documents = response.get('results', [])
        
        print(f"Found {len(documents)} documents")
        return documents
    
    def get_tag_usage_stats(self) -> Dict[str, int]:
        """Get tag usage statistics"""
        print("Calculating tag usage statistics...")
        
        # Get all documents
        all_documents = self.client.get_all_documents()
        
        tag_counts = Counter()
        
        for doc in all_documents:
            tags = doc.get('tags', {})
            if isinstance(tags, dict):
                # If tags is in dict format
                for tag_key, tag_info in tags.items():
                    tag_counts[tag_key] += 1
            elif isinstance(tags, list):
                # If tags is in list format
                for tag in tags:
                    if isinstance(tag, dict):
                        tag_key = tag.get('key', tag.get('name', ''))
                    else:
                        tag_key = str(tag)
                    if tag_key:
                        tag_counts[tag_key] += 1
        
        print(f"Statistics complete, found {len(tag_counts)} tags in use")
        return dict(tag_counts)
    
    def get_popular_tags(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get most popular tags"""
        usage_stats = self.get_tag_usage_stats()
        all_tags = self.get_all_tags()
        
        # Create tag name mapping
        tag_info_map = {tag['key']: tag for tag in all_tags}
        
        # Sort by usage count
        popular_tags = []
        for tag_key, count in sorted(usage_stats.items(), 
                                   key=lambda x: x[1], reverse=True)[:limit]:
            tag_info = tag_info_map.get(tag_key, {'key': tag_key, 'name': tag_key})
            popular_tags.append({
                'key': tag_key,
                'name': tag_info.get('name', tag_key),
                'usage_count': count
            })
        
        return popular_tags
    
    def get_unused_tags(self) -> List[Dict[str, str]]:
        """Get unused tags"""
        print("Finding unused tags...")
        
        all_tags = self.get_all_tags()
        usage_stats = self.get_tag_usage_stats()
        
        unused_tags = []
        for tag in all_tags:
            tag_key = tag.get('key', '')
            if tag_key not in usage_stats:
                unused_tags.append(tag)
        
        print(f"Found {len(unused_tags)} unused tags")
        return unused_tags
    
    def find_documents_with_multiple_tags(self, tag_keys: List[str]) -> List[Dict[str, Any]]:
        """Find documents containing multiple specified tags"""
        print(f"Finding documents containing tags {tag_keys}...")
        
        # Get all documents
        all_documents = self.client.get_all_documents()
        
        matching_docs = []
        for doc in all_documents:
            doc_tags = set()
            tags = doc.get('tags', {})
            
            if isinstance(tags, dict):
                doc_tags = set(tags.keys())
            elif isinstance(tags, list):
                for tag in tags:
                    if isinstance(tag, dict):
                        tag_key = tag.get('key', tag.get('name', ''))
                    else:
                        tag_key = str(tag)
                    if tag_key:
                        doc_tags.add(tag_key)
            
            # Check if contains all specified tags
            if all(tag_key in doc_tags for tag_key in tag_keys):
                matching_docs.append(doc)
        
        print(f"Found {len(matching_docs)} matching documents")
        return matching_docs
    
    def display_tag_summary(self, tag: Dict[str, str], include_usage: bool = True) -> None:
        """Display tag summary information"""
        print(f"\n--- Tag Summary ---")
        print(f"Tag Name: {tag.get('name', 'N/A')}")
        print(f"Tag Key: {tag.get('key', 'N/A')}")
        
        if include_usage:
            try:
                usage_stats = self.get_tag_usage_stats()
                usage_count = usage_stats.get(tag.get('key', ''), 0)
                print(f"Usage Count: {usage_count}")
            except Exception as e:
                print(f"Unable to get usage statistics: {e}")
        
        print("-" * 20)
    
    def display_tag_stats(self) -> None:
        """Display tag statistics"""
        print("\n=== Tag Statistics ===")
        
        all_tags = self.get_all_tags()
        print(f"Total Tags: {len(all_tags)}")
        
        try:
            usage_stats = self.get_tag_usage_stats()
            used_tags = len([k for k, v in usage_stats.items() if v > 0])
            unused_tags = len(all_tags) - used_tags
            
            print(f"Used Tags: {used_tags}")
            print(f"Unused Tags: {unused_tags}")
            
            if usage_stats:
                avg_usage = sum(usage_stats.values()) / len(usage_stats)
                max_usage = max(usage_stats.values())
                print(f"Average Usage: {avg_usage:.1f}")
                print(f"Max Usage: {max_usage}")
                
            print("\n--- Most Popular Tags ---")
            popular = self.get_popular_tags(5)
            for i, tag in enumerate(popular, 1):
                print(f"{i}. {tag['name']} ({tag['usage_count']} times)")
                
        except Exception as e:
            print(f"Unable to get usage statistics: {e}")
        
        print("=" * 20) 