# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python-based Readwise Reader API management tool that provides both CLI and web interfaces for managing documents and tags in Readwise Reader. The tool implements all features of the Readwise Reader API.

## Development Commands

### Setup and Dependencies
```bash
# Install dependencies
pip install -r requirements.txt

# Setup API token (choose one method)
export READWISE_TOKEN=your_api_token_here
echo "your_api_token_here" > .readwise_token
python cli.py setup-token --token your_api_token_here
```

### Running the Application
```bash
# Run CLI interface
python cli.py verify  # Verify API connection
python cli.py --help  # Show all available commands

# Run web interface
python web_app.py  # Starts Flask server at http://localhost:5000
```

### Testing
```bash
# Run all tests with coverage
python3 -m pytest

# Run specific test file
python3 -m pytest tests/test_config.py -v

# Run with detailed output
python3 -m pytest -vv

# Run only unit tests
python3 -m pytest -m "not integration"

# Run tests and show coverage report
python3 -m pytest --cov=. --cov-report=html
open htmlcov/index.html  # View coverage report

# Use the test runner script
./run_tests.sh
```

### Common CLI Commands
```bash
# Document management
python cli.py add "https://example.com" --title "Title" --tags "tag1,tag2"
python cli.py list --location later --limit 10 --verbose
python cli.py search "keyword"
python cli.py update DOCUMENT_ID --location archive
python cli.py delete DOCUMENT_ID

# Tag management  
python cli.py tags --search "keyword"
python cli.py tag-stats

# Statistics and export
python cli.py stats --include-tags
python cli.py export --location archive --output filename.json
```

## Architecture

### Core Components

- **`config.py`**: Configuration management with API token handling from environment variables or `.readwise_token` file
- **`readwise_client.py`**: Low-level Readwise Reader API client with all HTTP endpoints
- **`document_manager.py`**: High-level document operations (add, list, search, update, delete, stats, export)
- **`tag_manager.py`**: High-level tag operations (list, search, statistics, usage analysis)
- **`cli.py`**: Command-line interface with argparse-based subcommands
- **`web_app.py`**: Flask web application providing browser-based interface

### Testing Architecture

- **`tests/`**: Test directory containing unit tests for all components
- **`pytest.ini`**: PyTest configuration with test paths and coverage settings
- **`.coveragerc`**: Coverage configuration excluding test files and virtual environments
- **`run_tests.sh`**: Shell script for running tests with various options

Each component has corresponding test files:
- `test_config.py`: Tests configuration loading and token management
- `test_readwise_client.py`: Tests API client with mocked HTTP responses
- `test_document_manager.py`: Tests document operations
- `test_tag_manager.py`: Tests tag operations
- `test_cli.py`: Tests CLI commands and argument parsing
- `test_web_app.py`: Tests Flask routes and web endpoints

Tests use:
- `pytest` for test framework
- `pytest-mock` for mocking
- `pytest-cov` for coverage reporting
- `responses` for mocking HTTP requests

### API Integration

The tool implements all Readwise Reader API endpoints:
- `POST /save/` - Add documents
- `GET /list/` - List/search documents with pagination
- `PATCH /update/` - Update document metadata
- `DELETE /delete/` - Delete documents  
- `GET /tags/` - List tags with pagination

### Data Flow

1. Config loads API token from environment or file
2. ReadwiseClient handles HTTP requests with proper authentication
3. Manager classes provide business logic and error handling
4. CLI/Web interfaces provide user interaction

### Document Locations

The system supports four document locations:
- `new` - New documents
- `later` - Read later queue
- `archive` - Archived documents  
- `feed` - RSS/subscription content

### API Rate Limits

- General endpoints: 20 requests per minute
- Document create/update: 50 requests per minute

## Key Implementation Details

- All API responses include pagination handling via `nextPageCursor`
- Tag search is performed client-side by filtering all tags
- Document search is title-based and performed client-side
- Statistics are calculated by aggregating API responses
- Export functionality saves documents as JSON with timestamps
- Error handling includes API rate limit and network error recovery
- Tests mock external API calls to ensure reliable testing without API token
- Coverage reporting helps maintain code quality and identify untested code paths