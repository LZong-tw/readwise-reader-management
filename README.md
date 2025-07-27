# Readwise Reader Management Tool

A comprehensive Readwise Reader API management tool that provides both command-line interface and web interface to manage your documents stored in Readwise Reader.

## Features

- ✅ **Document Management**: Add, list, search, update, delete documents
- ✅ **Tag Management**: List tags, search tags, get tag statistics
- ✅ **Document Deduplication**: CSV-based duplicate analysis with simple URL comparison
- ✅ **Advanced Deduplication**: Smart duplicate detection and removal with quality scoring (legacy)
- ✅ **Multiple Interfaces**: Command Line Interface (CLI) and Web Interface
- ✅ **Document Organization**: Support for new, later, archive, feed location management
- ✅ **Statistics**: Document and tag usage statistics
- ✅ **Export**: Export documents to JSON and CSV formats with complete metadata
- ✅ **Real-time Progress**: Live progress display for large document operations
- ✅ **Smart CSV Output**: Automatic CSV export for large result sets (200+ documents)
- ✅ **Search**: Title-based document search
- ✅ **Comprehensive Testing**: Unit tests with coverage reporting

## Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd readwise-reader-management
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Setup API Token

Get your API token from [Readwise Access Token](https://readwise.io/access_token), then choose one of the following methods to configure it:

**Method 1: Environment Variable**
```bash
export READWISE_TOKEN=your_api_token_here
```

**Method 2: Configuration File**
```bash
echo "your_api_token_here" > .readwise_token
```

**Method 3: CLI Tool Setup**
```bash
python cli.py setup-token --token your_api_token_here
```

## Testing

### Running Tests

The project includes comprehensive unit tests for all major components.

**Run all tests with coverage report:**
```bash
python -m pytest
```

**Run specific test file:**
```bash
python -m pytest tests/test_config.py -v
```

**Run tests with detailed output:**
```bash
python -m pytest -vv
```

**Run only unit tests (skip integration tests):**
```bash
python -m pytest -m "not integration"
```

**Use the test runner script:**
```bash
chmod +x run_tests.sh
./run_tests.sh
```

### Test Coverage

The tests cover:
- Configuration management
- API client operations
- Document management functions
- Tag management operations
- CLI commands
- Web application routes

View the HTML coverage report:
```bash
# After running tests, open the coverage report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

## Usage

### Command Line Interface (CLI)

#### Verify API Connection
```bash
python cli.py verify
```

#### Document Management

**Add Article**
```bash
python cli.py add "https://example.com/article" --title "Article Title" --tags "tag1,tag2"
```

**List Documents**
```bash
# List all documents (shows real-time progress for large collections)
python cli.py list

# List documents in specific location
python cli.py list --location later

# Limit count (helpful for testing or preview)
python cli.py list --limit 10

# Verbose mode with detailed information
python cli.py list --verbose

# Different output formats
python cli.py list --format text     # Default: terminal output
python cli.py list --format json     # JSON format
python cli.py list --format csv      # CSV file export

# Disable progress display (for scripting)
python cli.py list --no-progress

# Large collections are automatically exported to CSV
# When result count > 200, output automatically switches to CSV
```

**Search Documents**
```bash
python cli.py search "keyword"
```

**Update Document**
```bash
# Move document to different location
python cli.py update DOCUMENT_ID --location archive

# Update document metadata
python cli.py update DOCUMENT_ID --title "New Title" --author "New Author"
```

**Delete Document**
```bash
python cli.py delete DOCUMENT_ID
```

#### Tag Management

**List Tags**
```bash
python cli.py tags
```

**Search Tags**
```bash
python cli.py tags --search "tag keyword"
```

**Tag Statistics**
```bash
python cli.py tag-stats
```

#### Statistics and Export

**Show Statistics**
```bash
python cli.py stats --include-tags
```

**Export Documents**
```bash
# Export all documents to JSON
python cli.py export

# Export documents from specific location to JSON
python cli.py export --location archive --output my_archive.json

# Export documents to CSV with complete metadata (23 fields)
python cli.py list --format csv

# Export specific location to CSV
python cli.py list --location archive --format csv

# Large collections (>200 docs) automatically export to CSV
python cli.py list  # Auto-creates CSV if >200 results
```

#### Document Deduplication

##### CSV-Based Duplicate Analysis (Recommended)

This method analyzes duplicate documents in your exported CSV files by comparing `source_url` without http/https protocols. This is the current preferred method for duplicate detection.

**Analyze CSV File for Duplicates**
```bash
# Basic analysis of CSV file
python cli.py analyze-csv-duplicates readwise_documents_20250727_153630.csv

# Show detailed duplicate groups
python cli.py analyze-csv-duplicates your_file.csv --verbose

# Export duplicate list to CSV file
python cli.py analyze-csv-duplicates your_file.csv --export duplicates_result.csv

# Combined: detailed analysis with export
python cli.py analyze-csv-duplicates your_file.csv --verbose --export duplicates_result.csv
```

**CSV Duplicate Analysis Features:**
- **Simple URL Comparison**: Compares `source_url` after removing http/https protocols
- **Fast Processing**: Analyzes large CSV files without API calls
- **CSV Export**: Saves duplicate groups with metadata for further processing
- **Group Organization**: Groups duplicates by normalized URL with row numbers
- **Complete Metadata**: Includes id, title, author, created_at, location for each duplicate

**Workflow Example:**
```bash
# 1. First, export your documents to CSV
python cli.py list --format csv

# 2. Analyze the CSV file for duplicates
python cli.py analyze-csv-duplicates readwise_documents_20250727_153630.csv --verbose --export duplicates.csv

# 3. Review the duplicates.csv file to see grouped duplicates
# 4. Manually review and clean up duplicates as needed
```

##### Legacy Deduplication Commands (Not Currently Recommended)

These advanced deduplication commands are available but not currently recommended for use. They provide more sophisticated analysis but are more complex and resource-intensive.

**Advanced Duplicate Analysis** (Legacy)
```bash
# Analyze all documents for duplicates (uses live API data)
python cli.py analyze-duplicates

# Analyze specific location only
python cli.py analyze-duplicates --location new

# Limit analysis for large collections
python cli.py analyze-duplicates --limit 100

# Export detailed analysis report
python cli.py analyze-duplicates --export analysis_report.json
```

**Advanced Duplicate Removal** (Legacy)
```bash
# Preview mode (shows what would be deleted)
python cli.py remove-duplicates

# Actually execute deletion (use with caution)
python cli.py remove-duplicates --execute

# Auto-confirm without prompting (use with extreme caution)
python cli.py remove-duplicates --execute --force
```

**Legacy Features:**
- **Smart Detection**: URL normalization (removes tracking parameters) and title similarity matching
- **Quality Scoring**: Evaluates documents based on title, author, summary, tags, and other metadata
- **Safe Operation**: Preview mode by default, requires confirmation before deletion

**⚠️ Important Notes for Legacy Commands:**
- These commands make live API calls and may be slow for large collections
- Use `--limit` parameter for testing with smaller batches
- Always use preview mode first before executing deletions
- Consider using the CSV-based method instead for better control

#### Progress Display and Large Collections

The tool provides real-time progress feedback for operations involving multiple API requests:

**Real-time Progress Features:**
- 📚 **Live Status**: Shows current operation status with emoji indicators
- ⏳ **Countdown Timers**: Real-time countdown for API rate limiting delays
- 📊 **Statistics**: Live updates of documents processed, elapsed time, and averages
- 🔗 **Batch Progress**: Clear indication of current batch and total progress
- 🛑 **Smart Limits**: Automatic stopping when reaching specified limits

**Smart CSV Export:**
- **Automatic**: When listing >200 documents, automatically exports to CSV instead of terminal output
- **Complete Metadata**: CSV includes all 23 Readwise API fields (id, title, author, summary, tags, timestamps, etc.)
- **Manual Export**: Use `--format csv` to force CSV output for any result size
- **UTF-8 Encoding**: Full Unicode support for international content
- **Clean Format**: Newlines converted to spaces for proper CSV compatibility

**CSV Fields Include:**
```
id, url, source_url, title, author, summary, site_name, word_count, 
published_date, image_url, notes, category, location, source, 
created_at, updated_at, saved_at, last_moved_at, first_opened_at, 
last_opened_at, reading_progress, parent_id, tags
```

**Usage Examples:**
```bash
# View progress for large operations
python cli.py list --location archive  # Shows real-time progress

# Disable progress for automation
python cli.py list --no-progress > script_output.txt

# Force CSV export
python cli.py list --limit 50 --format csv

# Large collection handling
python cli.py list  # Auto-exports to CSV if >200 results
```

### Web Interface

#### Start Web Server
```bash
python web_app.py
```

Then visit `http://localhost:5000` in your browser

#### Web Features

- **Home Page**: Display statistics and recent documents
- **Document Management**: Browse, search, add, edit documents
- **Tag Management**: View tag list and statistics
- **Statistics Page**: Detailed usage statistics
- **Export Feature**: One-click document export

## API Feature Mapping

This tool implements all features of the [Readwise Reader API](https://readwise.io/reader_api):

| API Endpoint | CLI Command | Web Feature |
|---------|---------|---------|
| POST /save/ | `add` | ✅ Add Document Page |
| GET /list/ | `list`, `search` (with CSV export) | ✅ Document List Page |
| PATCH /update/ | `update` | ✅ Edit Document Feature |
| DELETE /delete/ | `delete`, `remove-duplicates` | ✅ Delete Document Feature |
| GET /tags/ | `tags` | ✅ Tag Management Page |
| Custom | `analyze-duplicates` (legacy) | 🔄 Planned |
| Custom | `analyze-csv-duplicates` | 🔄 Planned |
| Custom | CSV Export (23 metadata fields) | 🔄 Planned |

## File Structure

```
readwise-reader-management/
├── config.py              # Configuration management
├── readwise_client.py     # API client
├── document_manager.py    # Document manager
├── document_deduplicator.py # Document deduplication
├── tag_manager.py         # Tag manager
├── cli.py                 # Command line interface
├── web_app.py             # Web application
├── requirements.txt       # Python dependencies
├── README.md              # Documentation
├── .readwise_token        # API token file (auto-generated)
├── pytest.ini             # Pytest configuration
├── .coveragerc            # Coverage configuration
├── run_tests.sh           # Test runner script
└── tests/                 # Test directory
    ├── __init__.py
    ├── test_config.py     # Configuration tests
    ├── test_readwise_client.py  # API client tests
    ├── test_document_manager.py # Document manager tests
    ├── test_document_deduplicator.py # Deduplication tests
    ├── test_tag_manager.py      # Tag manager tests
    ├── test_cli.py        # CLI tests
    └── test_web_app.py    # Web application tests
```

## FAQ

### Q: How to get Readwise API token?
A: Please visit [https://readwise.io/access_token](https://readwise.io/access_token) and log in to get your API token.

### Q: Are there API usage limits?
A: Yes, according to the official documentation:
- General endpoints: 20 requests per minute
- Document create/update endpoints: 50 requests per minute

### Q: What document categories are supported?
A: Supports article, email, rss, highlight, note, pdf, epub, tweet, video categories.

### Q: What document locations are supported?
A: Supports new (new documents), later (read later), archive (archived), feed (subscription content) four locations.

## Development

### Adding Features
1. Modify the corresponding manager class (`document_manager.py` or `tag_manager.py`)
2. Add corresponding command in CLI (`cli.py`)
3. Add corresponding route in Web interface (`web_app.py`)
4. Add corresponding tests in the `tests/` directory

### Running Tests During Development
```bash
# Run tests and watch for changes
python -m pytest --watch

# Run with debugging
python -m pytest -vv --pdb

# Run specific test function
python -m pytest tests/test_config.py::TestConfig::test_init_with_env_token
```

### Error Handling
All API calls include proper error handling and display meaningful error messages.

## License

This project is released under the MIT License.

## Contributing

Issues and Pull Requests are welcome to improve this tool! Please ensure all tests pass and maintain test coverage before submitting PRs. 