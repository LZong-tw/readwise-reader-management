# Readwise Reader Management Tool

A comprehensive Readwise Reader API management tool that provides both command-line interface and web interface to manage your documents stored in Readwise Reader.

## Features

- ✅ **Document Management**: Add, list, search, update, delete documents
- ✅ **Tag Management**: List tags, search tags, get tag statistics
- ✅ **Duplicate Detection**: CSV-based analysis and smart deletion planning
- ✅ **Multiple Interfaces**: Command Line Interface (CLI) and Web Interface
- ✅ **Export**: JSON and CSV formats with complete metadata (auto-export for large sets)
- ✅ **Testing**: Comprehensive unit test coverage

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

#### Duplicate Detection and Management

**Step 1: Find Duplicates**
```bash
# Export your documents to CSV first
python cli.py list --format csv

# Find duplicates in the CSV file
python cli.py analyze-csv-duplicates your_file.csv --export duplicates.csv
```

**Step 2: Create Deletion Plan**
```bash
# Generate smart deletion plan based on priority rules
python cli.py plan-deletion duplicates.csv --export deletion_plan.csv

# View detailed analysis
python cli.py plan-deletion duplicates.csv --verbose
```

**Priority Rules for Keeping Documents:**
1. **Documents with NOTES** (if only some have notes)
2. **Documents with TAGS** (if only some have tags)  
3. **Older Documents** (earliest `created_at` time)

**Output:** The deletion plan generates a CSV file with KEEP/DELETE actions and reasons for each document.

⚠️ **Safety:** Always review the generated plan before executing any deletions.

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

| API Endpoint | CLI Command | Web Feature |
|---------|---------|---------|
| POST /save/ | `add` | ✅ Add Document Page |
| GET /list/ | `list`, `search` | ✅ Document List Page |
| PATCH /update/ | `update` | ✅ Edit Document Feature |
| DELETE /delete/ | `delete` | ✅ Delete Document Feature |
| GET /tags/ | `tags` | ✅ Tag Management Page |
| Custom | `analyze-csv-duplicates`, `plan-deletion` | 🔄 Planned |

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

## Legacy Commands

The following commands are available but not recommended for new users:

```bash
# Legacy duplicate analysis (slow, uses live API)
python cli.py analyze-duplicates --limit 100

# Legacy duplicate removal (complex, requires manual confirmation)
python cli.py remove-duplicates --dry-run
```

**Note:** Use the CSV-based workflow instead for better performance and control.

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