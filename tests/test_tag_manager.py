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
        mock_client.list_documents_all.return_value = mock_documents
        
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
        mock_client.list_documents_all.return_value = mock_documents
        
        stats = manager.get_tag_statistics()
        
        assert stats['total_documents'] == 5
        assert stats['documents_with_tags'] == 4
        assert stats['documents_without_tags'] == 1
        assert stats['total_unique_tags'] == 5
        assert stats['tag_usage']['python'] == 3
        assert stats['tag_usage']['testing'] == 2
        assert stats['tag_usage']['api'] == 2
        assert stats['tag_usage']['javascript'] == 1
        assert stats['tag_usage']['web-dev'] == 1
        
        captured = capsys.readouterr()
        assert 'Getting tag statistics...' in captured.out
        assert 'Total documents: 5' in captured.out
    
    def test_print_tags(self, manager, mock_client, sample_tags, capsys):
        """Test printing tags"""
        mock_client.get_all_tags.return_value = sample_tags[:2]  # Use only first 2 tags
        
        manager.print_tags()
        
        captured = capsys.readouterr()
        assert 'Total tags: 2' in captured.out
        assert 'Python (python)' in captured.out
        assert 'JavaScript (javascript)' in captured.out
    
    def test_print_tags_empty(self, manager, mock_client, capsys):
        """Test printing when no tags exist"""
        mock_client.get_all_tags.return_value = []
        
        manager.print_tags()
        
        captured = capsys.readouterr()
        assert 'Total tags: 0' in captured.out
        assert 'No tags found' in captured.out
    
    def test_print_tag_statistics(self, manager, mock_client, capsys):
        """Test printing tag statistics"""
        mock_documents = [
            {'id': '1', 'tags': ['python', 'testing']},
            {'id': '2', 'tags': ['python']},
            {'id': '3', 'tags': []}
        ]
        mock_client.list_documents_all.return_value = mock_documents
        
        manager.print_tag_statistics()
        
        captured = capsys.readouterr()
        assert 'Tag Statistics' in captured.out
        assert 'Total documents: 3' in captured.out
        assert 'Documents with tags: 2' in captured.out
        assert 'Documents without tags: 1' in captured.out
        assert 'Unique tags: 2' in captured.out
        assert 'Top 10 most used tags:' in captured.out
        assert 'python: 2 documents' in captured.out
        assert 'testing: 1 documents' in captured.out
    
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
        mock_client.list_documents_all.return_value = mock_documents
        
        manager.print_documents_for_tag('python')
        
        captured = capsys.readouterr()
        assert "Documents with tag 'python':" in captured.out
        assert 'Found 2 documents' in captured.out
        assert 'Python Basics' in captured.out
        assert 'John Doe' in captured.out
        assert 'Advanced Python' in captured.out
        assert 'No author' in captured.out
    
    def test_print_documents_for_tag_no_results(self, manager, mock_client, capsys):
        """Test printing documents for tag with no results"""
        mock_client.list_documents_all.return_value = []
        
        manager.print_documents_for_tag('nonexistent')
        
        captured = capsys.readouterr()
        assert "Documents with tag 'nonexistent':" in captured.out
        assert 'No documents found with this tag' in captured.out