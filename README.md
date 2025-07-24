# Readwise Reader Management Tool

A comprehensive Readwise Reader API management tool that provides both command-line interface and web interface to manage your documents stored in Readwise Reader.

## Features

- ✅ **Document Management**: Add, list, search, update, delete documents
- ✅ **Tag Management**: List tags, search tags, get tag statistics
- ✅ **Multiple Interfaces**: Command Line Interface (CLI) and Web Interface
- ✅ **Document Organization**: Support for new, later, archive, feed location management
- ✅ **Statistics**: Document and tag usage statistics
- ✅ **Export**: Export documents to JSON format
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
# List all documents
python cli.py list

# List documents in specific location
python cli.py list --location later

# Limit count
python cli.py list --limit 10

# Verbose mode
python cli.py list --verbose
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
# Export all documents
python cli.py export

# Export documents from specific location
python cli.py export --location archive --output my_archive.json
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
| GET /list/ | `list`, `search` | ✅ Document List Page |
| PATCH /update/ | `update` | ✅ Edit Document Feature |
| DELETE /delete/ | `delete` | ✅ Delete Document Feature |
| GET /tags/ | `tags` | ✅ Tag Management Page |

## File Structure

```
readwise-reader-management/
├── config.py              # Configuration management
├── readwise_client.py     # API client
├── document_manager.py    # Document manager
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