# Web UI User Guide

This guide provides instructions for running and using the web interface for the Readwise Reader Management Tool.

## Table of Contents
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [Available Pages](#available-pages)
- [Features Guide](#features-guide)
- [Troubleshooting](#troubleshooting)
- [Development Notes](#development-notes)

---

## Quick Start

### Prerequisites
- Python 3.7 or higher
- Dependencies installed: `pip install -r requirements.txt`
- Readwise Reader API token from https://readwise.io/access_token

### Running in 3 Steps

1. **Configure your API token** (choose one method):
   ```bash
   # Method 1: Create token file
   echo "your_api_token_here" > .readwise_token

   # Method 2: Set environment variable (PowerShell)
   $env:READWISE_TOKEN = "your_api_token_here"

   # Method 3: Use CLI tool
   python cli.py setup-token --token your_api_token_here
   ```

2. **Start the web server:**
   ```bash
   python web_app.py
   ```

3. **Open your browser:**
   - Visit: **http://localhost:5000**
   - Or: **http://127.0.0.1:5000**

4. **Stop the server when done:**
   - Press `Ctrl+C` in the terminal

---

## Configuration

### API Token Setup

The web application requires a Readwise Reader API token to function. You can configure it using any of these methods:

#### Method 1: Configuration File (Recommended)

Create a `.readwise_token` file in the project root:

**Windows (PowerShell):**
```powershell
echo your_api_token_here > .readwise_token
```

**Linux/macOS:**
```bash
echo "your_api_token_here" > .readwise_token
```

#### Method 2: Environment Variable

**Windows (PowerShell):**
```powershell
$env:READWISE_TOKEN = "your_api_token_here"
python web_app.py
```

**Windows (Command Prompt):**
```cmd
set READWISE_TOKEN=your_api_token_here
python web_app.py
```

**Linux/macOS:**
```bash
export READWISE_TOKEN=your_api_token_here
python web_app.py
```

#### Method 3: CLI Tool

```bash
python cli.py setup-token --token your_api_token_here
```

This automatically creates the `.readwise_token` file for you.

### Priority Order
If you have multiple configurations, the priority order is:
1. Environment variable (`READWISE_TOKEN`)
2. Configuration file (`.readwise_token`)

---

## Running the Application

### Starting the Server

```bash
python web_app.py
```

**Expected Console Output:**
```
Starting Readwise Reader Management Tool...
Visit http://localhost:5000
 * Serving Flask app 'web_app'
 * Debug mode: on
WARNING: This is a development server. Do not use it in a production deployment.
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:5000
 * Running on http://192.168.x.x:5000
Press CTRL+C to quit
```

**Note:** The "development server" warning is normal - this tool is intended for local use only.

### Accessing the Web Interface

Open your web browser and navigate to:
- **Primary URL:** http://localhost:5000
- **Alternative:** http://127.0.0.1:5000
- **Network Access:** http://[your-local-ip]:5000 (from other devices on your network)

### Stopping the Server

Press `Ctrl+C` in the terminal where the server is running.

---

## Available Pages

### 1. Dashboard (Home)
**URL:** http://localhost:5000/

**Features:**
- Collection statistics overview
  - Total documents count
  - Breakdown by location (New, Later, Archive, Feed)
- Recent documents (last 10 added)
- Quick action buttons:
  - Add Document
  - Browse Documents
  - Export Collection
- Getting started information
- CLI tools reference

**What You'll See:**
- If API token is **not configured**: Setup page with configuration instructions
- If API token **is configured**: Dashboard with your collection statistics

### 2. Documents
**URL:** http://localhost:5000/documents

**Features:**
- Browse all documents in your collection
- Filter by:
  - **Location:** New, Later, Archive, Feed
  - **Category:** Article, Email, PDF, EPUB, Video, Tweet
  - **Search:** Search by title
- Document cards showing:
  - Title and URL
  - Author, source, and creation date
  - Word count
  - Summary (if available)
  - Tags
  - Location badge
  - Reading progress (if started)
- Actions per document:
  - View Details
  - Delete (with confirmation)

### 3. Add Document
**URL:** http://localhost:5000/add_document

**Features:**
- Add new documents to your Readwise Reader
- Form fields:
  - **URL** (required): The article URL to save
  - **Title** (optional): Custom title (auto-fetched if not provided)
  - **Tags** (optional): Comma-separated tags
  - **Location** (optional): Choose where to save (New/Later/Archive)
- Tips section with best practices
- Cancel button to return to documents list

### 4. Document Detail
**URL:** http://localhost:5000/document/<document_id>

**Features:**
- View complete document metadata:
  - Title and full URL
  - Author, source, category
  - Word count and reading progress
  - Summary and notes
  - All tags
  - Timestamps (created, updated, published, opened)
- Actions:
  - Read on Readwise (opens original URL)
  - Move to different location (New/Later/Archive)
  - Delete document
  - Return to documents list
- Side panel with detailed information

### 5. Tags
**URL:** http://localhost:5000/tags

**Features:**
- Browse all tags in your collection
- Search tags by keyword
- Tag cards showing:
  - Tag name
  - Document count (how many documents have this tag)
- Click any tag to view all associated documents
- Information about tag management

### 6. Tag Detail
**URL:** http://localhost:5000/tag/<tag_key>

**Features:**
- View all documents with a specific tag
- Breadcrumb navigation
- Document list showing:
  - All documents tagged with this tag
  - Full document metadata
  - Links to view details or read
- Return to all tags button

### 7. Statistics
**URL:** http://localhost:5000/stats

**Features:**
- Document statistics:
  - Total documents
  - Breakdown by location (New, Later, Archive, Feed)
  - Breakdown by category (Article, Email, PDF, etc.)
- Popular tags:
  - Top 10 most used tags
  - Visual progress bars showing usage
  - Document count per tag
- Quick action buttons:
  - View All Documents
  - View All Tags
  - Export Collection

---

## Features Guide

### Document Management

#### Adding Documents

1. Click **"Add Document"** from the dashboard or navigation
2. Enter the article URL (required)
3. Optionally add:
   - Custom title (auto-fetched if blank)
   - Tags (comma-separated, e.g., "python, tutorial, programming")
   - Location (New/Later/Archive)
4. Click **"Add Document"**
5. You'll be redirected to the documents list with a success message

**Tips:**
- Only the URL is required - metadata is auto-fetched
- Tags help organize documents for later discovery
- Use "Later" for articles you plan to read soon
- Use "Archive" for reference materials

#### Browsing Documents

1. Navigate to **Documents** page
2. Use filters to narrow results:
   - **Location dropdown:** Filter by New/Later/Archive/Feed
   - **Category dropdown:** Filter by type (Article/PDF/etc.)
   - **Search box:** Search by title
3. Click **"View"** on any document to see full details
4. Click **"Delete"** to remove a document (with confirmation)

#### Viewing Document Details

1. Click **"View"** on any document
2. View complete metadata, tags, notes, and reading progress
3. Actions available:
   - **"Read on Readwise":** Opens the original article
   - **"Move to [Location]":** Change document location
   - **"Delete":** Remove the document
   - **"Back to List":** Return to documents list

#### Moving Documents

**From Document Detail Page:**
1. In the right sidebar, click one of the location buttons:
   - **New**
   - **Later**
   - **Archive**
2. Confirm the action in the dialog
3. Page will reload showing updated location

#### Deleting Documents

1. Click **"Delete"** button on any document
2. Confirm the action in the dialog
   - Warning: "This action cannot be undone"
3. Document is permanently removed from Readwise Reader

### Tag Management

#### Browsing Tags

1. Navigate to **Tags** page
2. See all tags with document counts
3. Use search box to find specific tags
4. Click **"View"** on any tag to see all documents with that tag

#### Viewing Documents by Tag

1. Click on any tag from the Tags page
2. See all documents that have this tag
3. Click on any document to view details
4. Use breadcrumb navigation to return to all tags

#### Searching Tags

1. On the Tags page, enter a keyword in the search box
2. Click **"Search"**
3. Results show all tags matching your keyword (case-insensitive)
4. Click **"Clear"** to see all tags again

### Statistics and Analytics

#### Viewing Statistics

1. Navigate to **Statistics** page
2. View collection overview:
   - Total document count
   - Breakdown by location
   - Breakdown by category
3. See popular tags with usage visualization
4. Use quick action buttons for common tasks

#### Exporting Collection

1. Click **"Export Collection"** from dashboard or statistics page
2. Documents are exported to a JSON file with timestamp
3. Success message shows the filename
4. File is saved in the project directory

**Export File Format:** `readwise_export_YYYYMMDD_HHMMSS.json`

---

## Troubleshooting

### Common Issues

#### 1. "API Token Required" Page Shows

**Problem:** The application can't find your API token.

**Solutions:**
- Check if `.readwise_token` file exists in project root
- Verify the file contains your actual token (not empty)
- Try setting environment variable before starting server
- Make sure to restart the web server after configuring token

**Verify token file:**
```bash
# Check if file exists
ls -la .readwise_token

# View contents (Windows PowerShell)
Get-Content .readwise_token

# View contents (Linux/macOS)
cat .readwise_token
```

#### 2. Port Already in Use

**Problem:** Error message: "Address already in use"

**Solutions:**

**Option A - Use Different Port:**
Edit `web_app.py` line 406:
```python
app.run(debug=True, host='0.0.0.0', port=5001)  # Change 5000 to 5001
```

**Option B - Find and Kill Process Using Port 5000:**

**Windows (PowerShell):**
```powershell
# Find process
netstat -ano | findstr :5000

# Kill process (replace PID with actual process ID)
taskkill /PID <PID> /F
```

**Linux/macOS:**
```bash
# Find process
lsof -i :5000

# Kill process (replace PID with actual process ID)
kill -9 <PID>
```

#### 3. Template Not Found Errors

**Problem:** Error message: "TemplateNotFound: [template_name].html"

**Solutions:**
- Verify `templates/` directory exists in project root
- Check that all template files are present:
  ```bash
  ls templates/
  # Should show: base.html, setup.html, index.html, error.html, etc.
  ```
- If templates are missing, they may not have been created properly

#### 4. Can't Connect to Server

**Problem:** Browser shows "This site can't be reached" or connection refused.

**Solutions:**
- Verify the server is running (check terminal for "Running on..." message)
- Try alternative URL: http://127.0.0.1:5000 instead of localhost
- Check your firewall isn't blocking port 5000
- Make sure you're not using a VPN that blocks local connections

#### 5. No Documents Showing

**Problem:** Dashboard or documents page shows "No documents found"

**Solutions:**
- Verify API token is correct and has proper permissions
- Check your Readwise Reader account actually has documents
- Look for error messages in the terminal where web server is running
- Try adding a document through the web interface to test

#### 6. Import Errors

**Problem:** Error message: "ModuleNotFoundError: No module named '...'"

**Solutions:**
```bash
# Reinstall dependencies
pip install -r requirements.txt

# Verify installation
pip list | grep -i flask
pip list | grep -i requests
```

#### 7. API Connection Errors

**Problem:** Error messages about API failures or timeouts

**Solutions:**
- Check your internet connection
- Verify Readwise API is operational (https://readwise.io)
- Check API rate limits (20 requests/minute for most endpoints)
- Review API token permissions on Readwise website
- Look at terminal output for detailed error messages

### Getting Debug Information

When reporting issues, include:

1. **Console output** from the terminal where `web_app.py` is running
2. **Browser console** errors (F12 → Console tab)
3. **Python version:** `python --version`
4. **Dependencies versions:** `pip list`
5. **Operating system** and browser being used

---

## Development Notes

### Server Configuration

The web application runs in **debug mode** by default, which means:
- Auto-reload on code changes
- Detailed error pages in browser
- Flask debug toolbar available
- **Not suitable for production deployment**

**Configuration in `web_app.py`:**
```python
app.run(debug=True, host='0.0.0.0', port=5000)
```

**Parameters:**
- `debug=True`: Enable debug mode
- `host='0.0.0.0'`: Listen on all network interfaces
- `port=5000`: Use port 5000 (change if needed)

### Making Changes

The application uses **Flask's debug mode** which automatically reloads when you make changes to:
- Python files (`web_app.py`, managers, etc.)
- Template files (`.html` in `templates/` directory)

**No need to restart the server** for most changes!

### File Structure

```
readwise-reader-management/
├── web_app.py              # Flask application (main server)
├── templates/              # HTML templates
│   ├── base.html           # Base layout
│   ├── setup.html          # API token setup
│   ├── index.html          # Dashboard
│   ├── error.html          # Error pages
│   ├── documents.html      # Document list
│   ├── add_document.html   # Add document form
│   ├── document_detail.html # Document details
│   ├── tags.html           # Tag list
│   ├── tag_detail.html     # Tag details
│   └── stats.html          # Statistics
├── static/                 # Static files (CSS, JS, images)
│   └── (none yet - using CDN for Bootstrap)
├── config.py               # Configuration management
├── readwise_client.py      # API client
├── document_manager.py     # Document operations
├── tag_manager.py          # Tag operations
└── .readwise_token         # API token (gitignored)
```

### API Endpoints

The following RESTful API endpoints are available for programmatic access:

- `GET /api/documents` - List documents (with filters)
- `GET /api/documents/<id>` - Get single document
- `PATCH /api/documents/<id>` - Update document
- `DELETE /api/documents/<id>` - Delete document
- `GET /api/tags` - List all tags
- `POST /api/save` - Save new document
- `GET /api/search?q=<query>` - Search documents
- `GET /api/statistics` - Get collection statistics
- `POST /api/verify` - Verify API connection

**Example API Usage:**
```bash
# Get all documents
curl http://localhost:5000/api/documents

# Search documents
curl http://localhost:5000/api/search?q=python

# Get statistics
curl http://localhost:5000/api/statistics
```

### Technology Stack

**Backend:**
- Flask 2.3.0+ (Python web framework)
- Python 3.7+

**Frontend:**
- HTML5 with Jinja2 templating
- Bootstrap 5.3.0 (CSS framework via CDN)
- Bootstrap Icons 1.11.0 (icons via CDN)
- Vanilla JavaScript (for interactivity)

**No database required** - all data comes from Readwise Reader API

---

## Security Notes

### Local Use Only

This web application is designed for **local use only**:
- Default server binds to all interfaces (`0.0.0.0`)
- No authentication/authorization beyond API token
- Debug mode enabled by default
- **DO NOT expose to the internet**

### API Token Security

Your Readwise API token is sensitive:
- ✅ **Stored locally** in `.readwise_token` file
- ✅ **Never shared** or sent to third parties
- ✅ **Gitignored** (won't be committed to version control)
- ⚠️ **Keep it secret** - don't share in screenshots or logs

### Production Deployment

If you need to deploy this for production use:
1. Disable debug mode: `app.run(debug=False)`
2. Use a production WSGI server (gunicorn, uWSGI)
3. Add authentication/authorization
4. Use HTTPS (SSL/TLS)
5. Set up proper logging
6. Configure firewall rules
7. Use environment variables for all secrets

**This is beyond the scope of this guide.**

---

## Tips and Best Practices

### Performance

1. **Large Collections (1000+ documents):**
   - Use filters to narrow results
   - Consider using CLI for bulk operations
   - CSV export workflow is more efficient for analysis

2. **API Rate Limits:**
   - General endpoints: 20 requests/minute
   - Create/Update: 50 requests/minute
   - The app handles rate limiting automatically

### Workflow Recommendations

1. **Daily Use:**
   - Use web UI for browsing and organizing
   - Quick document additions via web form
   - Tag management and statistics viewing

2. **Bulk Operations:**
   - Use CLI for batch operations
   - CSV workflow for duplicate detection
   - Export via CLI for large collections

3. **Organization:**
   - Tag documents as you save them
   - Use "Later" for reading queue
   - Archive completed articles
   - Regularly review statistics

### Keyboard Shortcuts

While in browser:
- `Ctrl+Click` on links: Open in new tab
- `F5`: Refresh page
- `F12`: Open browser developer tools (for debugging)
- `Ctrl+W`: Close current tab

---

## Getting Help

### Resources

- **README.md:** General project documentation
- **CLAUDE.md:** Development guidance
- **PRD.md:** Product requirements and roadmap
- **GitHub Issues:** https://github.com/LZong-tw/readwise-reader-management/issues

### Command-Line Alternative

If the web interface isn't working, you can always use the CLI:

```bash
# Verify connection
python cli.py verify

# List documents
python cli.py list

# Add document
python cli.py add "https://example.com" --tags "tag1,tag2"

# View help
python cli.py --help
```

### Reporting Issues

When reporting issues, please include:
1. Operating system and version
2. Python version: `python --version`
3. Browser and version
4. Steps to reproduce the issue
5. Error messages from terminal
6. Screenshots (hide your API token!)

---

## What's Next?

### Current Status (Phase 3 Complete)

✅ Core web UI infrastructure
✅ Document management interface
✅ Tag management interface
✅ Statistics and analytics
✅ Responsive design
✅ All tests passing

### Coming Soon (Phase 4)

🔄 **Duplicate Detection Web UI** - The key differentiator feature:
- CSV upload and API fetch interface
- Visual duplicate groups display
- Smart deletion planning
- Real-time execution progress
- Execution reports

See **PRD.md** for complete roadmap and feature details.

---

**Last Updated:** January 22, 2026
**Version:** 2.0 (Phase 3 Complete)
