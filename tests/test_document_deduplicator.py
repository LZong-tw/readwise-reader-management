import unittest
from unittest.mock import Mock, patch, MagicMock
import json
from document_deduplicator import DocumentDeduplicator

class TestDocumentDeduplicator(unittest.TestCase):
    """DocumentDeduplicator tests"""
    
    def setUp(self):
        """Set up test environment"""
        self.mock_client = Mock()
        self.deduplicator = DocumentDeduplicator(self.mock_client)
        
        # Create test document data
        self.test_documents = [
            {
                "id": "doc1",
                "title": "Python Programming Guide for Beginners",
                "author": "John Doe",
                "source_url": "https://example.com/python-guide",
                "summary": "This is a detailed Python programming guide for beginners, covering basic syntax and advanced concepts.",
                "location": "new",
                "created_at": "2024-01-15T10:00:00Z",
                "updated_at": "2024-01-15T10:00:00Z",
                "tags": [{"name": "python"}, {"name": "programming"}]
            },
            {
                "id": "doc2", 
                "title": "Python Programming Guide",
                "author": "",
                "source_url": "https://example.com/python-guide?utm_source=facebook",
                "summary": "",
                "location": "new",
                "created_at": "2024-01-14T09:00:00Z",
                "updated_at": "2024-01-14T09:00:00Z",
                "tags": []
            },
            {
                "id": "doc3",
                "title": "JavaScript Basics Tutorial",
                "author": "Jane Smith",
                "source_url": "https://example.com/js-tutorial",
                "summary": "Learn the basics of JavaScript programming.",
                "location": "new",
                "created_at": "2024-01-16T11:00:00Z",
                "updated_at": "2024-01-16T11:00:00Z",
                "tags": [{"name": "javascript"}]
            },
            {
                "id": "doc4",
                "title": "Machine Learning in Practice",
                "author": "Bob Wilson",
                "source_url": "https://example.com/ml-practical",
                "summary": "Practical applications and case studies in machine learning.",
                "location": "later",
                "created_at": "2024-01-17T12:00:00Z",
                "updated_at": "2024-01-17T12:00:00Z",
                "tags": [{"name": "ml"}, {"name": "ai"}, {"name": "data"}]
            }
        ]
    
    def test_normalize_url(self):
        """Test URL normalization functionality"""
        # Test removing tracking parameters
        url_with_tracking = "https://example.com/article?utm_source=google&utm_medium=email&ref=newsletter"
        normalized = self.deduplicator.normalize_url(url_with_tracking)
        self.assertEqual(normalized, "https://example.com/article")
        
        # Test preserving valid parameters
        url_with_valid_params = "https://example.com/search?q=python&lang=en"
        normalized = self.deduplicator.normalize_url(url_with_valid_params)
        self.assertEqual(normalized, "https://example.com/search?lang=en&q=python")
        
        # Test empty URL
        self.assertEqual(self.deduplicator.normalize_url(""), "")
        self.assertEqual(self.deduplicator.normalize_url(None), "")
    
    def test_calculate_title_similarity(self):
        """Test title similarity calculation"""
        # Test identical titles
        similarity = self.deduplicator.calculate_title_similarity(
            "Python Programming", "Python Programming"
        )
        self.assertEqual(similarity, 1.0)
        
        # Test similar titles
        similarity = self.deduplicator.calculate_title_similarity(
            "Python Programming Guide", "Python Programming Tutorial"
        )
        self.assertGreater(similarity, 0.3)  # Should have some similarity
        
        # Test different titles
        similarity = self.deduplicator.calculate_title_similarity(
            "Python Programming", "JavaScript Basics"
        )
        self.assertLess(similarity, 0.5)  # Similarity should be low
        
        # Test empty titles
        similarity = self.deduplicator.calculate_title_similarity("", "Python")
        self.assertEqual(similarity, 0.0)
    
    def test_calculate_metadata_quality_score(self):
        """Test metadata quality scoring"""
        # Test high-quality document
        high_quality_doc = self.test_documents[0]
        score = self.deduplicator.calculate_metadata_quality_score(high_quality_doc)
        self.assertGreater(score, 70)  # High-quality document should have high score
        
        # Test low-quality document
        low_quality_doc = self.test_documents[1]
        score = self.deduplicator.calculate_metadata_quality_score(low_quality_doc)
        self.assertLess(score, 50)  # Low-quality document should have lower score
        
        # Test empty document
        empty_doc = {"id": "empty"}
        score = self.deduplicator.calculate_metadata_quality_score(empty_doc)
        self.assertEqual(score, 0.0)
    
    def test_find_duplicate_groups(self):
        """Test duplicate document group identification"""
        # Create test data with duplicates
        documents_with_duplicates = [
            {
                "id": "doc1",
                "title": "Python Programming Guide",
                "source_url": "https://example.com/python-guide",
                "author": "John Doe",
                "summary": "Detailed guide"
            },
            {
                "id": "doc2",
                "title": "Python Programming Tutorial", 
                "source_url": "https://example.com/python-guide?utm_source=fb",
                "author": "",
                "summary": ""
            },
            {
                "id": "doc3",
                "title": "JavaScript Tutorial",
                "source_url": "https://example.com/js-tutorial", 
                "author": "Jane Smith",
                "summary": "JS basics"
            }
        ]
        
        duplicate_groups = self.deduplicator.find_duplicate_groups(documents_with_duplicates)
        
        # Should find one duplicate group (doc1 and doc2)
        self.assertEqual(len(duplicate_groups), 1)
        self.assertEqual(len(duplicate_groups[0]), 2)
        
        # Check that the group contains the correct documents
        group_ids = {doc["id"] for doc in duplicate_groups[0]}
        self.assertIn("doc1", group_ids)
        self.assertIn("doc2", group_ids)
    
    def test_select_best_document(self):
        """Test best document selection"""
        # Use the first two test documents (duplicates)
        duplicate_docs = self.test_documents[:2]
        
        best_doc, duplicates_to_remove = self.deduplicator.select_best_document(duplicate_docs)
        
        # The first document should be selected as best (has more complete metadata)
        self.assertEqual(best_doc["id"], "doc1")
        self.assertEqual(len(duplicates_to_remove), 1)
        self.assertEqual(duplicates_to_remove[0]["id"], "doc2")
    
    @patch('document_deduplicator.DocumentManager')
    def test_analyze_duplicates(self, mock_doc_manager_class):
        """Test duplicate analysis functionality"""
        # Set up mock
        mock_doc_manager = Mock()
        mock_doc_manager.get_documents.return_value = self.test_documents
        mock_doc_manager_class.return_value = mock_doc_manager
        
        # Execute analysis
        analysis = self.deduplicator.analyze_duplicates()
        
        # Check analysis result structure
        self.assertIn("total_documents", analysis)
        self.assertIn("duplicate_groups", analysis)
        self.assertIn("total_duplicates", analysis)
        self.assertIn("groups", analysis)
        
        # Check total document count
        self.assertEqual(analysis["total_documents"], 4)
    
    def test_analyze_duplicates_with_no_documents(self):
        """Test analysis with no documents"""
        analysis = self.deduplicator.analyze_duplicates([])
        self.assertIn("error", analysis)
    
    @patch('document_deduplicator.DocumentManager')
    def test_remove_duplicates_dry_run(self, mock_doc_manager_class):
        """Test deduplication preview mode"""
        # Set up mock
        mock_doc_manager = Mock()
        mock_doc_manager.get_documents.return_value = self.test_documents
        mock_doc_manager_class.return_value = mock_doc_manager
        
        # Execute preview
        result = self.deduplicator.remove_duplicates(dry_run=True)
        
        # Check results
        self.assertTrue(result.get("dry_run"))
        self.assertEqual(result.get("removed_count"), 0)
        
        # Confirm delete API was not called
        self.mock_client.delete_document.assert_not_called()
    
    def test_export_analysis_report(self):
        """Test analysis report export"""
        analysis_data = {
            "total_documents": 10,
            "duplicate_groups": 2,
            "total_duplicates": 3,
            "groups": []
        }
        
        with patch('builtins.open', create=True) as mock_open:
            with patch('json.dump') as mock_json_dump:
                filename = self.deduplicator.export_analysis_report(analysis_data, "test_report.json")
                
                # Check filename
                self.assertEqual(filename, "test_report.json")
                
                # Check that file write was called
                mock_open.assert_called_once_with("test_report.json", 'w', encoding='utf-8')
                mock_json_dump.assert_called_once()

if __name__ == '__main__':
    unittest.main() 