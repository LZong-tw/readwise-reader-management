import pytest
import responses
import json
from datetime import datetime
from unittest.mock import Mock, patch
from readwise_client import ReadwiseClient
from config import Config


class TestReadwiseClient:
    """Test cases for ReadwiseClient class"""
    
    @pytest.fixture
    def mock_config(self):
        """Create a mock config object"""
        config = Mock(spec=Config)
        config.api_token = 'test_token'
        config.base_url = 'https://readwise.io/api/v3'
        config.auth_url = 'https://readwise.io/api/v2/auth/'
        config.get_headers.return_value = {
            'Authorization': 'Token test_token',
            'Content-Type': 'application/json'
        }
        return config
    
    @pytest.fixture
    def client(self, mock_config):
        """Create a ReadwiseClient instance with mock config"""
        return ReadwiseClient(config=mock_config)
    
    @responses.activate
    def test_verify_token_success(self, client):
        """Test successful token verification"""
        responses.add(
            responses.GET,
            'https://readwise.io/api/v2/auth/',
            status=204
        )
        
        assert client.verify_token() is True
    
    @responses.activate
    def test_verify_token_failure(self, client):
        """Test failed token verification"""
        responses.add(
            responses.GET,
            'https://readwise.io/api/v2/auth/',
            status=401
        )
        
        assert client.verify_token() is False
    
    @responses.activate
    def test_verify_token_exception(self, client):
        """Test token verification with network exception"""
        responses.add(
            responses.GET,
            'https://readwise.io/api/v2/auth/',
            body=Exception('Network error')
        )
        
        assert client.verify_token() is False
    
    @responses.activate
    def test_save_document_minimal(self, client):
        """Test saving document with minimal parameters"""
        expected_response = {
            'id': '12345',
            'url': 'https://example.com',
            'title': 'Example Article'
        }
        
        responses.add(
            responses.POST,
            'https://readwise.io/api/v3/save/',
            json=expected_response,
            status=200
        )
        
        result = client.save_document(url='https://example.com')
        
        assert result == expected_response
        assert len(responses.calls) == 1
        assert json.loads(responses.calls[0].request.body) == {'url': 'https://example.com'}
    
    @responses.activate
    def test_save_document_full(self, client):
        """Test saving document with all parameters"""
        expected_response = {'id': '12345', 'status': 'created'}
        
        responses.add(
            responses.POST,
            'https://readwise.io/api/v3/save/',
            json=expected_response,
            status=200
        )
        
        result = client.save_document(
            url='https://example.com',
            html='<html>Content</html>',
            should_clean_html=True,
            title='Test Article',
            author='Test Author',
            summary='Test Summary',
            published_date='2024-01-01',
            image_url='https://example.com/image.jpg',
            location='new',
            category='article',
            saved_using='api',
            tags=['test', 'python'],
            notes='Test notes'
        )
        
        assert result == expected_response
        
        # Check request body
        request_body = json.loads(responses.calls[0].request.body)
        assert request_body['url'] == 'https://example.com'
        assert request_body['html'] == '<html>Content</html>'
        assert request_body['should_clean_html'] is True
        assert request_body['title'] == 'Test Article'
        assert request_body['tags'] == ['test', 'python']
    
    @responses.activate
    def test_list_documents_basic(self, client):
        """Test listing documents with basic parameters"""
        expected_response = {
            'count': 2,
            'results': [
                {'id': '1', 'title': 'Doc 1'},
                {'id': '2', 'title': 'Doc 2'}
            ]
        }
        
        responses.add(
            responses.GET,
            'https://readwise.io/api/v3/list/',
            json=expected_response,
            status=200
        )
        
        result = client.list_documents()
        
        assert result == expected_response
        assert len(responses.calls) == 1
    
    @responses.activate
    def test_list_documents_with_filters(self, client):
        """Test listing documents with filters"""
        expected_response = {'count': 1, 'results': [{'id': '1'}]}
        
        responses.add(
            responses.GET,
            'https://readwise.io/api/v3/list/',
            json=expected_response,
            status=200
        )
        
        result = client.list_documents(
            location='archive',
            category='article',
            tag_ids=['tag1', 'tag2']
        )
        
        assert result == expected_response
        
        # Check query parameters
        query_params = responses.calls[0].request.url.split('?')[1]
        assert 'location=archive' in query_params
        assert 'category=article' in query_params
    
    @responses.activate
    def test_get_document(self, client):
        """Test getting a single document"""
        expected_response = {
            'id': '12345',
            'title': 'Test Document',
            'content': 'Test content'
        }
        
        responses.add(
            responses.GET,
            'https://readwise.io/api/v3/documents/12345/',
            json=expected_response,
            status=200
        )
        
        result = client.get_document('12345')
        
        assert result == expected_response
    
    @responses.activate
    def test_update_document(self, client):
        """Test updating a document"""
        expected_response = {'id': '12345', 'status': 'updated'}
        
        responses.add(
            responses.PATCH,
            'https://readwise.io/api/v3/documents/12345/',
            json=expected_response,
            status=200
        )
        
        result = client.update_document(
            document_id='12345',
            title='Updated Title',
            notes='Updated notes'
        )
        
        assert result == expected_response
        
        # Check request body
        request_body = json.loads(responses.calls[0].request.body)
        assert request_body['title'] == 'Updated Title'
        assert request_body['notes'] == 'Updated notes'
    
    @responses.activate
    def test_delete_document(self, client):
        """Test deleting a document"""
        responses.add(
            responses.DELETE,
            'https://readwise.io/api/v3/documents/12345/',
            status=204
        )
        
        result = client.delete_document('12345')
        
        assert result is True
    
    @responses.activate
    def test_delete_document_failure(self, client):
        """Test failed document deletion"""
        responses.add(
            responses.DELETE,
            'https://readwise.io/api/v3/documents/12345/',
            status=404
        )
        
        result = client.delete_document('12345')
        
        assert result is False
    
    @responses.activate
    def test_list_tags(self, client):
        """Test listing tags"""
        expected_response = {
            'count': 2,
            'results': [
                {'id': 'tag1', 'name': 'Python'},
                {'id': 'tag2', 'name': 'Testing'}
            ]
        }
        
        responses.add(
            responses.GET,
            'https://readwise.io/api/v3/tags/',
            json=expected_response,
            status=200
        )
        
        result = client.list_tags()
        
        assert result == expected_response
    
    @responses.activate
    def test_request_with_pagination(self, client):
        """Test request handling with pagination"""
        # First page
        responses.add(
            responses.GET,
            'https://readwise.io/api/v3/list/',
            json={
                'count': 150,
                'next': 'https://readwise.io/api/v3/list/?page=2',
                'results': [{'id': f'{i}'} for i in range(100)]
            },
            status=200
        )
        
        # Second page
        responses.add(
            responses.GET,
            'https://readwise.io/api/v3/list/?page=2',
            json={
                'count': 150,
                'next': None,
                'results': [{'id': f'{i}'} for i in range(100, 150)]
            },
            status=200
        )
        
        # Call list_documents_all which should handle pagination
        results = client.list_documents_all()
        
        assert len(results) == 150
        assert results[0]['id'] == '0'
        assert results[149]['id'] == '149'
    
    @responses.activate
    def test_error_handling(self, client):
        """Test error handling in API calls"""
        responses.add(
            responses.GET,
            'https://readwise.io/api/v3/documents/12345/',
            json={'error': 'Not found'},
            status=404
        )
        
        with pytest.raises(Exception) as exc_info:
            client.get_document('12345')
        
        assert 'Error fetching document' in str(exc_info.value)