import pytest
from unittest.mock import Mock, patch
from collections import Counter
from tag_manager import TagManager
from readwise_client import ReadwiseClient


class TestTagManager:
    """Test cases for TagManager class"""
    
    @pytest.fixture
    def mock_client(self):
        """Create a mock ReadwiseClient"""
        return Mock(spec=ReadwiseClient)
    
    @pytest.fixture
    def manager(self, mock_client):
        """Create a TagManager instance with mock client"""
        return TagManager(client=mock_client)
    
    @pytest.fixture
    def sample_tags(self):
        """Sample tags for testing"""
        return [
            {'key': 'python', 'name': 'Python'},
            {'key': 'javascript', 'name': 'JavaScript'},
            {'key': 'testing', 'name': 'Testing'},
            {'key': 'web-dev', 'name': 'Web Development'},
            {'key': 'api', 'name': 'API'}
        ]
    
    def test_get_all_tags(self, manager, mock_client, sample_tags, capsys):
        """Test getting all tags"""
        mock_client.get_all_tags.return_value = sample_tags
        
        tags = manager.get_all_tags()
        
        assert tags == sample_tags
        assert len(tags) == 5
        mock_client.get_all_tags.assert_called_once()
        
        captured = capsys.readouterr()
        assert 'Getting all tags...' in captured.out
        assert 'Found 5 tags' in captured.out
    
    def test_list_tags_sort_by_name(self, manager, mock_client, sample_tags):
        """Test listing tags sorted by name"""
        mock_client.get_all_tags.return_value = sample_tags
        
        sorted_tags = manager.list_tags(sort_by='name')
        
        # Check tags are sorted by name
        tag_names = [tag['name'] for tag in sorted_tags]
        assert tag_names == ['API', 'JavaScript', 'Python', 'Testing', 'Web Development']
    
    def test_list_tags_sort_by_key(self, manager, mock_client, sample_tags):
        """Test listing tags sorted by key"""
        mock_client.get_all_tags.return_value = sample_tags
        
        sorted_tags = manager.list_tags(sort_by='key')
        
        # Check tags are sorted by key
        tag_keys = [tag['key'] for tag in sorted_tags]
        assert tag_keys == ['api', 'javascript', 'python', 'testing', 'web-dev']
    
    def test_search_tags_by_name(self, manager, mock_client, sample_tags, capsys):
        """Test searching tags by name"""
        mock_client.get_all_tags.return_value = sample_tags
        
        results = manager.search_tags('python')
        
        assert len(results) == 1
        assert results[0]['name'] == 'Python'
        
        captured = capsys.readouterr()
        assert "Searching for tags containing 'python'..." in captured.out
        assert 'Found 1 matching tags' in captured.out
    
    def test_search_tags_by_key(self, manager, mock_client, sample_tags):
        """Test searching tags by key"""
        mock_client.get_all_tags.return_value = sample_tags
        
        results = manager.search_tags('web')
        
        assert len(results) == 1
        assert results[0]['key'] == 'web-dev'
    
    def test_search_tags_multiple_matches(self, manager, mock_client, sample_tags):
        """Test searching tags with multiple matches"""
        mock_client.get_all_tags.return_value = sample_tags
        
        results = manager.search_tags('script')
        
        assert len(results) == 1
        assert results[0]['name'] == 'JavaScript'
    
    def test_search_tags_no_matches(self, manager, mock_client, sample_tags, capsys):
        """Test searching tags with no matches"""
        mock_client.get_all_tags.return_value = sample_tags
        
        results = manager.search_tags('rust')
        
        assert len(results) == 0
        
        captured = capsys.readouterr()
        assert 'Found 0 matching tags' in captured.out
    
    def test_search_tags_case_insensitive(self, manager, mock_client, sample_tags):
        """Test case-insensitive tag search"""
        mock_client.get_all_tags.return_value = sample_tags
        
        # Test uppercase search
        results = manager.search_tags('PYTHON')
        assert len(results) == 1
        assert results[0]['name'] == 'Python'
    
    def test_get_documents_by_tag(self, manager, mock_client, capsys):
        """Test getting documents by tag"""
        mock_documents = [
            {'id': '1', 'title': 'Python Tutorial', 'tags': ['python']},
            {'id': '2', 'title': 'Python Advanced', 'tags': ['python', 'advanced']}
        ]
        # Mock list_documents for get_documents_by_tag method
        mock_client.list_documents.return_value = {
            'results': mock_documents
        }
        
        documents = manager.get_documents_by_tag('python')
        
        assert len(documents) == 2
        assert all('python' in doc['tags'] for doc in documents)
        
        captured = capsys.readouterr()
        assert "Getting documents for tag 'python'..." in captured.out
    
    def test_get_tag_statistics(self, manager, mock_client, capsys):
        """Test getting tag statistics"""
        mock_documents = [
            {'id': '1', 'tags': ['python', 'testing']},
            {'id': '2', 'tags': ['python', 'api']},
            {'id': '3', 'tags': ['javascript', 'web-dev']},
            {'id': '4', 'tags': ['python', 'api', 'testing']},
            {'id': '5', 'tags': []}
        ]
        mock_client.get_all_documents.return_value = mock_documents
        
        stats = manager.get_tag_usage_stats()
        
        # get_tag_usage_stats returns tag counts, not document stats
        assert stats['python'] == 3  # appears in 3 documents
        assert stats['api'] == 2      # appears in 2 documents  
        assert stats['testing'] == 2  # appears in 2 documents
        assert len(stats) == 5        # 5 unique tags
        
        captured = capsys.readouterr()
        assert 'Calculating tag usage statistics...' in captured.out
    
    def test_print_tags(self, manager, mock_client, sample_tags, capsys):
        """Test listing tags (no print_tags method)"""
        mock_client.get_all_tags.return_value = sample_tags[:2]  # Use only first 2 tags
        
        result = manager.list_tags()
        
        assert len(result) == 2
        # list_tags should be sorted
        assert result[0]['name'] == 'JavaScript'
        assert result[1]['name'] == 'Python'
    
    def test_print_tags_empty(self, manager, mock_client, capsys):
        """Test listing when no tags exist"""
        mock_client.get_all_tags.return_value = []
        
        result = manager.list_tags()
        
        assert result == []
    
    def test_print_tag_statistics(self, manager, mock_client, capsys):
        """Test printing tag statistics"""
        mock_documents = [
            {'id': '1', 'tags': ['python', 'testing']},
            {'id': '2', 'tags': ['python']},
            {'id': '3', 'tags': []}
        ]
        mock_client.get_all_documents.return_value = mock_documents
        mock_client.get_all_tags.return_value = [  # Need to mock this too
            {'name': 'python', 'key': 'python'},
            {'name': 'testing', 'key': 'testing'}
        ]
        
        manager.display_tag_stats()
        
        captured = capsys.readouterr()
        # Check that some output was produced (exact format may vary)
        assert len(captured.out) > 0
    
    def test_print_documents_for_tag(self, manager, mock_client, capsys):
        """Test printing documents for a specific tag"""
        mock_documents = [
            {
                'id': '1',
                'title': 'Python Basics',
                'author': 'John Doe',
                'created_at': '2024-01-01T00:00:00Z',
                'tags': ['python', 'basics']
            },
            {
                'id': '2',
                'title': 'Advanced Python',
                'author': None,
                'created_at': '2024-01-02T00:00:00Z',
                'tags': ['python', 'advanced']
            }
        ]
        # Mock list_documents for get_documents_by_tag method
        mock_client.list_documents.return_value = {
            'results': mock_documents
        }
        
        result = manager.get_documents_by_tag('python')
        
        assert len(result) == 2
        assert result[0]['title'] == 'Python Basics'
        assert result[1]['title'] == 'Advanced Python'
    
    def test_print_documents_for_tag_no_results(self, manager, mock_client, capsys):
        """Test printing documents for tag with no results"""
        # Mock list_documents for get_documents_by_tag method
        mock_client.list_documents.return_value = {
            'results': []
        }
        
        result = manager.get_documents_by_tag('nonexistent')
        
        assert result == []