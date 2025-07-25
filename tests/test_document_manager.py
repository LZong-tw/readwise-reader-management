import pytest
import json
from unittest.mock import Mock, patch, call
from datetime import datetime
from document_manager import DocumentManager, safe_print
from readwise_client import ReadwiseClient


class TestDocumentManager:
    """Test cases for DocumentManager class"""
    
    @pytest.fixture
    def mock_client(self):
        """Create a mock ReadwiseClient"""
        return Mock(spec=ReadwiseClient)
    
    @pytest.fixture
    def manager(self, mock_client):
        """Create a DocumentManager instance with mock client"""
        return DocumentManager(client=mock_client)
    
    def test_safe_print_normal(self, capsys):
        """Test safe_print with normal text"""
        safe_print("Hello World")
        captured = capsys.readouterr()
        assert captured.out == "Hello World\n"
    
    def test_safe_print_unicode(self, capsys):
        """Test safe_print with unicode characters"""
        safe_print("Hello 世界 🌍")
        captured = capsys.readouterr()
        assert "Hello" in captured.out
    
    def test_add_article(self, manager, mock_client, capsys):
        """Test adding an article"""
        mock_client.save_document.return_value = {
            'id': '12345',
            'url': 'https://example.com',
            'title': 'Test Article'
        }
        
        result = manager.add_article(
            url='https://example.com',
            title='Test Article',
            tags=['test'],
            location='new'
        )
        
        assert result['id'] == '12345'
        mock_client.save_document.assert_called_once_with(
            url='https://example.com',
            title='Test Article',
            tags=['test'],
            location='new',
            category='article'
        )
        
        captured = capsys.readouterr()
        assert 'Adding article: https://example.com' in captured.out
        assert 'Article added, ID: 12345' in captured.out
    
    def test_add_from_html(self, manager, mock_client, capsys):
        """Test adding document from HTML"""
        mock_client.save_document.return_value = {
            'id': '12345',
            'title': 'HTML Document'
        }
        
        result = manager.add_from_html(
            url='https://example.com',
            html='<html><body>Content</body></html>',
            title='HTML Document',
            author='Test Author',
            tags=['html'],
            clean_html=True
        )
        
        assert result['id'] == '12345'
        mock_client.save_document.assert_called_once_with(
            url='https://example.com',
            html='<html><body>Content</body></html>',
            title='HTML Document',
            author='Test Author',
            tags=['html'],
            should_clean_html=True,
            category='article'
        )
    
    def test_list_documents_no_results(self, manager, mock_client, capsys):
        """Test listing documents with no results"""
        mock_client.get_all_documents.return_value = []
        
        result = manager.get_documents()
        
        assert result == []
        mock_client.get_all_documents.assert_called_once()
    
    def test_list_documents_with_results(self, manager, mock_client, capsys):
        """Test listing documents with results"""
        mock_client.list_documents.return_value = {
            'count': 2,
            'results': [
                {
                    'id': '1',
                    'title': 'Document 1',
                    'author': 'Author 1',
                    'created_at': '2024-01-01T00:00:00Z',
                    'location': 'new',
                    'category': 'article',
                    'tags': ['tag1', 'tag2']
                },
                {
                    'id': '2',
                    'title': 'Document 2',
                    'author': None,
                    'created_at': '2024-01-02T00:00:00Z',
                    'location': 'archive',
                    'category': 'email',
                    'tags': []
                }
            ]
        }
        
        mock_client.get_all_documents.return_value = mock_client.list_documents.return_value['results']
        
        result = manager.get_documents(location='all', limit=10)
        
        assert len(result) == 2
        assert result[0]['title'] == 'Document 1'
        assert result[1]['title'] == 'Document 2'
    
    def test_search_documents(self, manager, mock_client, capsys):
        """Test searching documents"""
        mock_client.get_all_documents.return_value = [
            {'id': '1', 'title': 'Python Tutorial', 'category': 'article'},
            {'id': '2', 'title': 'JavaScript Guide', 'category': 'article'},
            {'id': '3', 'title': 'Python Advanced', 'category': 'book'}
        ]
        
        results = manager.search_documents('python')
        
        assert len(results) == 2
        assert all('python' in doc['title'].lower() for doc in results)
    
    def test_search_documents_no_results(self, manager, mock_client, capsys):
        """Test searching documents with no results"""
        mock_client.get_all_documents.return_value = [
            {'id': '1', 'title': 'Document 1'},
            {'id': '2', 'title': 'Document 2'}
        ]
        
        results = manager.search_documents('nonexistent')
        
        assert len(results) == 0
    
    def test_get_document_details(self, manager, mock_client, capsys):
        """Test getting document details"""
        mock_document = {
            'id': '12345',
            'title': 'Test Document',
            'author': 'Test Author',
            'summary': 'Test summary',
            'url': 'https://example.com',
            'tags': ['tag1', 'tag2'],
            'location': 'new',
            'category': 'article',
            'created_at': '2024-01-01T00:00:00Z',
            'updated_at': '2024-01-02T00:00:00Z',
            'notes': 'Test notes'
        }
        # Mock the client method that's actually called
        mock_client.list_documents.return_value = {'results': [mock_document]}
        
        result = manager.get_document_by_id('12345')
        
        assert result == mock_document
        mock_client.list_documents.assert_called_once_with(document_id='12345')
    
    def test_update_document(self, manager, mock_client, capsys):
        """Test updating a document"""
        mock_client.update_document.return_value = {
            'id': '12345',
            'status': 'updated'
        }
        
        result = manager.update_document_metadata(
            document_id='12345',
            title='Updated Title'
        )
        
        assert result['status'] == 'updated'
        mock_client.update_document.assert_called_once_with(
            document_id='12345',
            title='Updated Title',
            author=None,
            summary=None
        )
    
    def test_delete_document_success(self, manager, mock_client, capsys):
        """Test successful document deletion"""
        mock_client.delete_document.return_value = True
        
        result = manager.delete_document('12345')
        
        assert result is True
        mock_client.delete_document.assert_called_once_with('12345')
        
        captured = capsys.readouterr()
        assert 'Document deleted' in captured.out
    
    def test_delete_document_failure(self, manager, mock_client, capsys):
        """Test failed document deletion"""
        mock_client.delete_document.return_value = False
        
        result = manager.delete_document('12345')
        
        assert result is False
        
        captured = capsys.readouterr()
        assert 'Delete failed' in captured.out
    
    def test_export_documents(self, manager, mock_client, tmp_path):
        """Test exporting documents to JSON"""
        mock_documents = [
            {'id': '1', 'title': 'Doc 1'},
            {'id': '2', 'title': 'Doc 2'}
        ]
        mock_client.get_all_documents.return_value = mock_documents
        
        # Create a temporary file path
        export_file = tmp_path / "export.json"
        
        with patch('builtins.open', create=True) as mock_open:
            result_filename = manager.export_documents(filename=str(export_file))
            
            # Verify file was created (filename will have timestamp)
            assert result_filename is not None
            assert 'export.json' in result_filename
            
            # Get the file handle
            file_handle = mock_open.return_value.__enter__.return_value
            
            # Verify json.dump was called with correct data
            written_data = []
            for call in file_handle.write.call_args_list:
                written_data.append(call[0][0])
            
            # Join all written data and verify it contains our documents
            full_content = ''.join(written_data)
            assert 'Doc 1' in full_content
            assert 'Doc 2' in full_content
    
    def test_get_statistics(self, manager, mock_client, capsys):
        """Test getting document statistics"""
        mock_documents = [
            {'id': '1', 'location': 'new', 'category': 'article', 
             'created_at': '2024-01-01T00:00:00Z'},
            {'id': '2', 'location': 'archive', 'category': 'article',
             'created_at': '2024-01-01T00:00:00Z'},
            {'id': '3', 'location': 'new', 'category': 'email',
             'created_at': '2024-01-02T00:00:00Z'},
        ]
        # Mock the get_documents method at the manager level
        from unittest.mock import patch
        with patch.object(manager, 'get_documents') as mock_get_docs:
            mock_get_docs.return_value = []  # Empty for limit=1 calls
            
            # Mock list_documents calls for count extraction
            mock_client.list_documents.side_effect = [
                {'count': 2, 'results': []},  # new
                {'count': 0, 'results': []},  # later  
                {'count': 1, 'results': []},  # archive
                {'count': 0, 'results': []}   # feed
            ]
            
            stats = manager.get_stats()
            
            assert stats['total'] == 3
            assert stats['new'] == 2
            assert stats['archive'] == 1
            assert stats['later'] == 0
            assert stats['feed'] == 0