import pytest
import sys
from unittest.mock import Mock, patch, MagicMock
from io import StringIO
import argparse
from cli import ReadwiseCLI


class TestReadwiseCLI:
    """Test cases for ReadwiseCLI"""
    
    @pytest.fixture
    def mock_dependencies(self):
        """Mock all CLI dependencies"""
        with patch('cli.Config') as mock_config, \
             patch('cli.ReadwiseClient') as mock_client, \
             patch('cli.DocumentManager') as mock_doc_manager, \
             patch('cli.TagManager') as mock_tag_manager:
            
            # Create mock instances
            mock_config_instance = Mock()
            mock_client_instance = Mock()
            mock_doc_manager_instance = Mock()
            mock_tag_manager_instance = Mock()
            
            # Configure constructors
            mock_config.return_value = mock_config_instance
            mock_client.return_value = mock_client_instance
            mock_doc_manager.return_value = mock_doc_manager_instance
            mock_tag_manager.return_value = mock_tag_manager_instance
            
            yield {
                'config': mock_config_instance,
                'client': mock_client_instance,
                'doc_manager': mock_doc_manager_instance,
                'tag_manager': mock_tag_manager_instance,
                'Config': mock_config,
                'ReadwiseClient': mock_client,
                'DocumentManager': mock_doc_manager,
                'TagManager': mock_tag_manager
            }
    
    def test_init_success(self, mock_dependencies):
        """Test successful CLI initialization"""
        cli = ReadwiseCLI()
        
        assert cli.config == mock_dependencies['config']
        assert cli.client == mock_dependencies['client']
        assert cli.doc_manager == mock_dependencies['doc_manager']
        assert cli.tag_manager == mock_dependencies['tag_manager']
    
    def test_init_failure(self):
        """Test CLI initialization failure"""
        with patch('cli.Config', side_effect=ValueError('No token found')):
            with pytest.raises(SystemExit) as exc_info:
                ReadwiseCLI()
            assert exc_info.value.code == 1
    
    def test_verify_connection_success(self, mock_dependencies):
        """Test successful connection verification"""
        mock_dependencies['client'].verify_token.return_value = True
        
        cli = ReadwiseCLI()
        result = cli.verify_connection()
        
        assert result is True
        mock_dependencies['client'].verify_token.assert_called_once()
    
    def test_verify_connection_failure(self, mock_dependencies, capsys):
        """Test failed connection verification"""
        mock_dependencies['client'].verify_token.return_value = False
        
        cli = ReadwiseCLI()
        result = cli.verify_connection()
        
        assert result is False
        captured = capsys.readouterr()
        assert "Error: API token invalid" in captured.out
    
    def test_add_article(self, mock_dependencies, capsys):
        """Test adding an article"""
        mock_dependencies['doc_manager'].add_article.return_value = {
            'id': '12345',
            'url': 'https://example.com'
        }
        
        cli = ReadwiseCLI()
        
        # Create mock args
        args = Mock()
        args.url = 'https://example.com'
        args.title = 'Test Article'
        args.tags = 'python,testing'
        args.location = 'new'
        
        cli.add_article(args)
        
        # Verify the call
        mock_dependencies['doc_manager'].add_article.assert_called_once_with(
            url='https://example.com',
            title='Test Article',
            tags=['python', 'testing'],
            location='new'
        )
        
        captured = capsys.readouterr()
        assert "Successfully added article: https://example.com" in captured.out
    
    def test_add_article_no_tags(self, mock_dependencies):
        """Test adding an article without tags"""
        mock_dependencies['doc_manager'].add_article.return_value = {
            'id': '12345',
            'url': 'https://example.com'
        }
        
        cli = ReadwiseCLI()
        
        args = Mock()
        args.url = 'https://example.com'
        args.title = None
        args.tags = None
        args.location = 'new'
        
        cli.add_article(args)
        
        mock_dependencies['doc_manager'].add_article.assert_called_once_with(
            url='https://example.com',
            title=None,
            tags=None,
            location='new'
        )
    
    def test_add_article_exception(self, mock_dependencies, capsys):
        """Test adding article with exception"""
        mock_dependencies['doc_manager'].add_article.side_effect = Exception('Network error')
        
        cli = ReadwiseCLI()
        
        args = Mock()
        args.url = 'https://example.com'
        args.title = None
        args.tags = None
        args.location = 'new'
        
        cli.add_article(args)
        
        captured = capsys.readouterr()
        assert "Failed to add article: Network error" in captured.out
    
    def test_list_documents(self, mock_dependencies):
        """Test listing documents"""
        cli = ReadwiseCLI()
        
        args = Mock()
        args.location = 'new'
        args.category = 'article'
        args.limit = 10
        
        cli.list_documents(args)
        
        mock_dependencies['doc_manager'].list_documents.assert_called_once_with(
            location='new',
            category='article',
            limit=10
        )
    
    def test_search_documents(self, mock_dependencies):
        """Test searching documents"""
        cli = ReadwiseCLI()
        
        args = Mock()
        args.query = 'python tutorial'
        
        cli.search_documents(args)
        
        mock_dependencies['doc_manager'].search_documents.assert_called_once_with('python tutorial')
    
    def test_delete_document(self, mock_dependencies):
        """Test deleting a document"""
        cli = ReadwiseCLI()
        
        args = Mock()
        args.document_id = '12345'
        
        cli.delete_document(args)
        
        mock_dependencies['doc_manager'].delete_document.assert_called_once_with('12345')
    
    def test_update_document(self, mock_dependencies):
        """Test updating a document"""
        cli = ReadwiseCLI()
        
        args = Mock()
        args.document_id = '12345'
        args.title = 'New Title'
        args.location = 'archive'
        args.category = None
        args.notes = 'Updated notes'
        
        cli.update_document(args)
        
        mock_dependencies['doc_manager'].update_document.assert_called_once_with(
            document_id='12345',
            title='New Title',
            location='archive',
            category=None,
            notes='Updated notes'
        )
    
    def test_export_documents(self, mock_dependencies):
        """Test exporting documents"""
        cli = ReadwiseCLI()
        
        args = Mock()
        args.output = 'export.json'
        args.location = 'all'
        args.category = None
        
        cli.export_documents(args)
        
        mock_dependencies['doc_manager'].export_documents.assert_called_once_with(
            'export.json',
            location='all',
            category=None
        )
    
    def test_list_tags(self, mock_dependencies):
        """Test listing tags"""
        cli = ReadwiseCLI()
        
        args = Mock()
        args.sort = 'name'
        
        cli.list_tags(args)
        
        mock_dependencies['tag_manager'].print_tags.assert_called_once_with(sort_by='name')
    
    def test_search_tags(self, mock_dependencies):
        """Test searching tags"""
        cli = ReadwiseCLI()
        
        args = Mock()
        args.keyword = 'python'
        
        cli.search_tags(args)
        
        mock_dependencies['tag_manager'].search_tags.assert_called_once_with('python')
    
    def test_tag_stats(self, mock_dependencies):
        """Test tag statistics"""
        cli = ReadwiseCLI()
        
        args = Mock()
        
        cli.tag_stats(args)
        
        mock_dependencies['tag_manager'].print_tag_statistics.assert_called_once()
    
    def test_tag_documents(self, mock_dependencies):
        """Test listing documents by tag"""
        cli = ReadwiseCLI()
        
        args = Mock()
        args.tag = 'python'
        
        cli.tag_documents(args)
        
        mock_dependencies['tag_manager'].print_documents_for_tag.assert_called_once_with('python')
    
    def test_setup_token(self, mock_dependencies, capsys):
        """Test setting up token"""
        cli = ReadwiseCLI()
        
        args = Mock()
        args.token = 'new_test_token'
        
        cli.setup_token(args)
        
        mock_dependencies['config'].save_token.assert_called_once_with('new_test_token')
        
        captured = capsys.readouterr()
        assert "Token saved successfully" in captured.out
    
    def test_stats(self, mock_dependencies):
        """Test document statistics"""
        cli = ReadwiseCLI()
        
        args = Mock()
        
        cli.stats(args)
        
        mock_dependencies['doc_manager'].get_statistics.assert_called_once()
    
    @patch('cli.argparse.ArgumentParser')
    def test_main_function(self, mock_parser_class, mock_dependencies):
        """Test main function argument parsing"""
        # Mock the parser and subparsers
        mock_parser = Mock()
        mock_subparsers = Mock()
        mock_parser.add_subparsers.return_value = mock_subparsers
        mock_parser_class.return_value = mock_parser
        
        # Import and patch the main function
        from cli import main
        
        # Mock parse_args to return args with a func attribute
        mock_args = Mock()
        mock_args.func = Mock()
        mock_parser.parse_args.return_value = mock_args
        
        # Run main
        with patch('cli.ReadwiseCLI') as mock_cli_class:
            mock_cli_instance = Mock()
            mock_cli_class.return_value = mock_cli_instance
            mock_cli_instance.verify_connection.return_value = True
            
            main()
            
            # Verify CLI was created and connection was verified
            mock_cli_class.assert_called_once()
            mock_cli_instance.verify_connection.assert_called_once()
            
            # Verify the function was called
            mock_args.func.assert_called_once_with(mock_cli_instance, mock_args)