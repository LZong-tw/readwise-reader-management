import pytest
from unittest.mock import Mock, patch, MagicMock
from flask import url_for
import json
import web_app
from config import Config
from readwise_client import ReadwiseClient
from document_manager import DocumentManager
from tag_manager import TagManager


class TestWebApp:
    """Test cases for Flask web application"""
    
    @pytest.fixture
    def app(self):
        """Create Flask test app"""
        web_app.app.config['TESTING'] = True
        web_app.app.config['SECRET_KEY'] = 'test-secret-key'
        return web_app.app
    
    @pytest.fixture
    def client(self, app):
        """Create Flask test client"""
        return app.test_client()
    
    @pytest.fixture
    def mock_managers(self):
        """Mock all manager instances"""
        with patch('web_app.Config') as mock_config, \
             patch('web_app.ReadwiseClient') as mock_readwise_client, \
             patch('web_app.DocumentManager') as mock_doc_manager, \
             patch('web_app.TagManager') as mock_tag_manager:
            
            # Setup mock instances
            mock_config_instance = Mock(spec=Config)
            mock_client_instance = Mock(spec=ReadwiseClient)
            mock_doc_instance = Mock(spec=DocumentManager)
            mock_tag_instance = Mock(spec=TagManager)
            
            # Configure constructors
            mock_config.return_value = mock_config_instance
            mock_readwise_client.return_value = mock_client_instance
            mock_doc_manager.return_value = mock_doc_instance
            mock_tag_manager.return_value = mock_tag_instance
            
            yield {
                'config': mock_config_instance,
                'client': mock_client_instance,
                'doc_manager': mock_doc_instance,
                'tag_manager': mock_tag_instance
            }
    
    def test_init_managers_success(self, mock_managers):
        """Test successful manager initialization"""
        result = web_app.init_managers()
        
        assert result is True
        assert web_app.doc_manager is not None
        assert web_app.tag_manager is not None
        assert web_app.client is not None
    
    def test_init_managers_failure(self):
        """Test failed manager initialization"""
        with patch('web_app.Config', side_effect=Exception('Config error')):
            result = web_app.init_managers()
            
            assert result is False
    
    def test_index_route_no_managers(self, client):
        """Test index route when managers fail to initialize"""
        with patch('web_app.init_managers', return_value=False):
            response = client.get('/')
            
            assert response.status_code == 200
            assert b'setup.html' in response.data or b'Setup' in response.data
    
    def test_index_route_success(self, client, mock_managers):
        """Test index route with successful data retrieval"""
        # Setup mock data
        mock_stats = {
            'total': 100,
            'locations': {'new': 50, 'archive': 30, 'later': 20},
            'categories': {'article': 60, 'email': 40}
        }
        mock_recent_docs = [
            {'id': '1', 'title': 'Doc 1'},
            {'id': '2', 'title': 'Doc 2'}
        ]
        
        mock_managers['doc_manager'].get_stats.return_value = mock_stats
        mock_managers['doc_manager'].get_documents.return_value = mock_recent_docs
        
        with patch('web_app.init_managers', return_value=True):
            web_app.doc_manager = mock_managers['doc_manager']
            
            response = client.get('/')
            
            assert response.status_code == 200
            # Check if template receives the data
            assert mock_managers['doc_manager'].get_stats.called
            assert mock_managers['doc_manager'].get_documents.called
    
    def test_index_route_exception(self, client, mock_managers):
        """Test index route when exception occurs"""
        mock_managers['doc_manager'].get_stats.side_effect = Exception('Database error')
        
        with patch('web_app.init_managers', return_value=True):
            web_app.doc_manager = mock_managers['doc_manager']
            
            response = client.get('/')
            
            assert response.status_code == 200
            # Should handle exception gracefully
    
    def test_api_documents_list(self, client, mock_managers):
        """Test API documents list endpoint"""
        mock_response = {
            'count': 2,
            'results': [
                {'id': '1', 'title': 'Doc 1'},
                {'id': '2', 'title': 'Doc 2'}
            ]
        }
        mock_managers['client'].list_documents.return_value = mock_response
        
        with patch('web_app.init_managers', return_value=True):
            web_app.client = mock_managers['client']
            
            response = client.get('/api/documents')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data == mock_response
    
    def test_api_documents_list_with_params(self, client, mock_managers):
        """Test API documents list with query parameters"""
        mock_response = {'count': 1, 'results': [{'id': '1'}]}
        mock_managers['client'].list_documents.return_value = mock_response
        
        with patch('web_app.init_managers', return_value=True):
            web_app.client = mock_managers['client']
            
            response = client.get('/api/documents?location=archive&category=article')
            
            assert response.status_code == 200
            # Check if parameters were passed
            mock_managers['client'].list_documents.assert_called_with(
                location='archive',
                category='article',
                limit=50
            )
    
    def test_api_document_get(self, client, mock_managers):
        """Test API get single document"""
        mock_document = {
            'id': '12345',
            'title': 'Test Document',
            'content': 'Test content'
        }
        mock_managers['client'].get_document.return_value = mock_document
        
        with patch('web_app.init_managers', return_value=True):
            web_app.client = mock_managers['client']
            
            response = client.get('/api/documents/12345')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data == mock_document
    
    def test_api_document_update(self, client, mock_managers):
        """Test API update document"""
        mock_response = {'id': '12345', 'status': 'updated'}
        mock_managers['client'].update_document.return_value = mock_response
        
        with patch('web_app.init_managers', return_value=True):
            web_app.client = mock_managers['client']
            
            update_data = {
                'title': 'Updated Title',
                'notes': 'Updated notes'
            }
            
            response = client.patch(
                '/api/documents/12345',
                data=json.dumps(update_data),
                content_type='application/json'
            )
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data == mock_response
    
    def test_api_document_delete(self, client, mock_managers):
        """Test API delete document"""
        mock_managers['client'].delete_document.return_value = True
        
        with patch('web_app.init_managers', return_value=True):
            web_app.client = mock_managers['client']
            
            response = client.delete('/api/documents/12345')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
    
    def test_api_document_delete_failure(self, client, mock_managers):
        """Test API delete document failure"""
        mock_managers['client'].delete_document.return_value = False
        
        with patch('web_app.init_managers', return_value=True):
            web_app.client = mock_managers['client']
            
            response = client.delete('/api/documents/12345')
            
            assert response.status_code == 400
            data = json.loads(response.data)
            assert 'error' in data
    
    def test_api_tags_list(self, client, mock_managers):
        """Test API tags list endpoint"""
        mock_tags = [
            {'key': 'python', 'name': 'Python'},
            {'key': 'testing', 'name': 'Testing'}
        ]
        mock_managers['client'].get_all_tags.return_value = mock_tags
        
        with patch('web_app.init_managers', return_value=True):
            web_app.client = mock_managers['client']
            
            response = client.get('/api/tags')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data == mock_tags
    
    def test_api_save_document(self, client, mock_managers):
        """Test API save document endpoint"""
        mock_response = {
            'id': '12345',
            'url': 'https://example.com',
            'title': 'Saved Document'
        }
        mock_managers['client'].save_document.return_value = mock_response
        
        with patch('web_app.init_managers', return_value=True):
            web_app.client = mock_managers['client']
            
            save_data = {
                'url': 'https://example.com',
                'title': 'Saved Document',
                'tags': ['test']
            }
            
            response = client.post(
                '/api/save',
                data=json.dumps(save_data),
                content_type='application/json'
            )
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data == mock_response
    
    def test_api_search_documents(self, client, mock_managers):
        """Test API search documents endpoint"""
        mock_results = [
            {'id': '1', 'title': 'Python Tutorial'},
            {'id': '2', 'title': 'Python Guide'}
        ]
        mock_managers['doc_manager'].search_documents.return_value = mock_results
        
        with patch('web_app.init_managers', return_value=True):
            web_app.doc_manager = mock_managers['doc_manager']
            
            response = client.get('/api/search?q=python')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data == mock_results
    
    def test_api_statistics(self, client, mock_managers):
        """Test API statistics endpoint"""
        mock_stats = {
            'total': 100,
            'locations': {'new': 50, 'archive': 50},
            'categories': {'article': 100}
        }
        mock_managers['doc_manager'].get_statistics.return_value = mock_stats
        
        with patch('web_app.init_managers', return_value=True):
            web_app.doc_manager = mock_managers['doc_manager']
            
            response = client.get('/api/statistics')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data == mock_stats
    
    def test_api_error_handling(self, client, mock_managers):
        """Test API error handling"""
        mock_managers['client'].get_document.side_effect = Exception('API Error')
        
        with patch('web_app.init_managers', return_value=True):
            web_app.client = mock_managers['client']
            
            response = client.get('/api/documents/12345')
            
            assert response.status_code == 500
            data = json.loads(response.data)
            assert 'error' in data
            assert 'API Error' in data['error']