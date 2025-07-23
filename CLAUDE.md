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