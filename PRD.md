# Product Requirements Document (PRD)
# Readwise Reader Management Tool

**Version:** 2.0
**Last Updated:** January 22, 2026
**Status:** Active Development
**Document Owner:** Product Team

---

## Executive Summary

The Readwise Reader Management Tool is a comprehensive API management solution that enables users to efficiently organize, deduplicate, and manage their Readwise Reader document collection. The tool provides both command-line and web interfaces, with a focus on intelligent duplicate detection and bulk operations that are not available in the native Readwise Reader interface.

### Key Differentiators
- **Advanced Duplicate Detection**: Smart URL normalization and title similarity matching
- **CSV-Based Workflow**: Efficient batch processing for large collections (1000+ documents)
- **Cross-Platform Safety**: Graceful interruption handling and resume capabilities
- **Dual Interface**: CLI for power users and automation, Web UI for casual users

---

## Product Vision

**Mission Statement:**
Empower Readwise Reader users to maintain a clean, organized, and duplicate-free reading collection through intelligent automation and user-friendly interfaces.

**Target Audience:**
1. **Power Users**: Researchers, content curators, and knowledge workers with 500+ saved articles
2. **Casual Users**: General readers who want simple duplicate cleanup without technical complexity
3. **Automation Enthusiasts**: Users who want to integrate document management into scripts/workflows

---

## Problem Statement

### Current Pain Points
1. **Duplicate Accumulation**: Users save the same article multiple times from different sources (newsletters, social media, RSS feeds)
2. **No Native Deduplication**: Readwise Reader lacks built-in duplicate detection
3. **Manual Review Burden**: Identifying duplicates in large collections (1000+ articles) is time-consuming
4. **Tracking Parameter Pollution**: URLs with `?utm_source=`, `?ref=`, etc. create false duplicates
5. **Bulk Operations Limitation**: Native interface doesn't support efficient bulk actions

### User Scenarios
- **Scenario A**: Sarah has 2,500 saved articles with ~400 duplicates from various newsletters
- **Scenario B**: Mike wants to archive all articles older than 6 months but keep important tagged items
- **Scenario C**: Lisa needs to export her reading list to analyze reading patterns

---

## Core Features

### 1. Document Management (✅ Implemented)

#### 1.1 Add Documents
- **Requirements:**
  - Support URL-based article saving
  - Optional metadata: title, author, summary, tags
  - Support for multiple document categories (article, email, pdf, etc.)
- **API Mapping:** `POST /save/`
- **Interfaces:** CLI ✅ | Web ❌

#### 1.2 List & Search Documents
- **Requirements:**
  - List all documents with pagination support
  - Filter by location: new, later, archive, feed
  - Search by title (client-side filtering)
  - Export formats: JSON, CSV (23 metadata fields)
  - Progress tracking for large collections (200+ documents)
  - Auto-export to CSV when result count > 200
- **API Mapping:** `GET /list/`
- **Interfaces:** CLI ✅ | Web ❌

#### 1.3 Update Documents
- **Requirements:**
  - Modify document metadata (title, author, summary)
  - Change document location (archive, later, etc.)
  - Bulk update support via CSV
- **API Mapping:** `PATCH /update/`
- **Interfaces:** CLI ✅ | Web ❌

#### 1.4 Delete Documents
- **Requirements:**
  - Single document deletion
  - Bulk deletion with confirmation
  - Dry-run mode for safety
- **API Mapping:** `DELETE /delete/`
- **Interfaces:** CLI ✅ | Web ❌

---

### 2. Tag Management (✅ Implemented)

#### 2.1 List & Search Tags
- **Requirements:**
  - Display all tags with document counts
  - Client-side tag search/filtering
  - Pagination support
- **API Mapping:** `GET /tags/`
- **Interfaces:** CLI ✅ | Web ❌

#### 2.2 Tag Statistics
- **Requirements:**
  - Total tag count
  - Most used tags (top 10)
  - Tag distribution analysis
  - Export capabilities
- **Interfaces:** CLI ✅ | Web ❌

---

### 3. Duplicate Detection & Management (✅ CLI | ❌ Web)

#### 3.1 CSV-Based Duplicate Analysis
**Status:** Fully implemented in CLI

**Requirements:**
- **Input:** CSV export from document list
- **Output:** Duplicate analysis CSV with groupings

**Standard Mode:**
- Normalize URLs: remove `http://`, `https://`, trailing slashes
- Group documents with identical normalized URLs
- Export duplicate groups to CSV

**Advanced Mode:**
- Remove query strings from URLs (e.g., `?utm_source=`, `?ref=`)
- Calculate title similarity using sequence matching
- Flag duplicates when:
  - Title similarity > 50% (regardless of URL)
  - OR same URL after query removal + title similarity > 50%

**Export Fields:**
- Document ID, Title, Author, URL
- Created date, Reading progress
- Tags, Notes presence
- Duplicate group ID
- Match reason (URL match, Title similarity)

#### 3.2 Smart Deletion Planning
**Status:** Fully implemented in CLI

**Requirements:**
- **Input:** Duplicate analysis CSV
- **Output:** Deletion plan CSV with keep/delete decisions

**Priority Rules (in order):**
1. **Keep documents with notes** (user has added commentary)
2. **Keep documents with tags** (user has categorized)
3. **Keep by date:**
   - Default: Keep oldest document (likely more complete/original)
   - Optional: Keep newest document (`--prefer-newer` flag)

**Safety Features:**
- Dry-run mode (default)
- Explicit execution confirmation (type "DELETE")
- Batch processing (respects API rate limits: 20 req/min)
- Progress tracking with ETA

#### 3.3 Deletion Execution
**Status:** Fully implemented in CLI

**Requirements:**
- Execute deletion plan with safety confirmations
- Real-time progress display
- Graceful interruption support:
  - **All platforms:** Ctrl+C
  - **Linux/macOS:** Terminal close detection
  - **Windows:** Only Ctrl+C (window close = immediate termination)
- Auto-resume: Generate updated plan after interruption
- Execution reports (JSON format with results)

**Error Handling:**
- Continue on individual failures
- Log all errors to report
- Rate limit detection and backoff

---

### 4. Statistics & Analytics (✅ Implemented)

#### 4.1 Collection Statistics
- **Requirements:**
  - Total document count
  - Breakdown by location (new, later, archive, feed)
  - Tag statistics (optional)
  - Export to JSON

---

### 5. Configuration Management (✅ Implemented)

#### 5.1 API Token Setup
- **Requirements:**
  - Support environment variable: `READWISE_TOKEN`
  - Support config file: `.readwise_token`
  - CLI setup command: `setup-token`
  - Token validation endpoint

**Priority Order:**
1. Environment variable
2. Config file

---

### 6. Web User Interface (🔄 Planned - Phase 2.0)

#### 6.1 Phase 1: Core Infrastructure (Priority: High)
**Status:** ❌ Not Started

**Requirements:**
- Flask application structure (✅ Exists in `web_app.py`)
- Base HTML template with navigation
- Responsive design (mobile-friendly)
- Error handling pages
- API token configuration page

**Templates Needed:**
- `base.html` - Base layout with navigation
- `setup.html` - API token configuration
- `index.html` - Dashboard with statistics
- `error.html` - Error display page

**Success Criteria:**
- User can configure API token via web interface
- Dashboard displays collection statistics
- All tests pass for web routes

#### 6.2 Phase 2: Document Management UI (Priority: High)
**Status:** ❌ Not Started

**Requirements:**
- **Documents List Page:**
  - Table view with sorting and filtering
  - Pagination controls
  - Location filter dropdown (new/later/archive/feed)
  - Search box (client-side filtering)
  - Bulk selection checkboxes
  - Export buttons (JSON/CSV)

- **Add Document Form:**
  - URL input (required)
  - Title, author, summary fields (optional)
  - Tags input with autocomplete
  - Location selector
  - Form validation

- **Edit Document Page:**
  - Pre-populated form with current metadata
  - Update confirmation
  - Success/error feedback

- **Delete Operations:**
  - Confirmation modal for single delete
  - Bulk delete with confirmation
  - Undo capability (if feasible)

**Templates Needed:**
- `documents/list.html`
- `documents/add.html`
- `documents/edit.html`
- `documents/delete_confirm.html`

#### 6.3 Phase 3: Tag Management UI (Priority: Medium)
**Status:** ❌ Not Started

**Requirements:**
- Tag list with document counts
- Tag search/filter
- Tag statistics visualization (charts/graphs)
- Tag merge/rename functionality (future)

**Templates Needed:**
- `tags/list.html`
- `tags/stats.html`

#### 6.4 Phase 4: Duplicate Detection UI (Priority: High - Key Differentiator)
**Status:** ❌ Not Started

**Requirements:**

**Step 1: Data Input**
- Option A: Upload CSV file (from CLI export)
- Option B: Fetch documents directly via API
- Loading indicator for API fetch

**Step 2: Analysis Configuration**
- Mode selector: Standard vs Advanced
- Advanced mode explanation tooltip
- "Analyze" button with progress indicator

**Step 3: Results Display**
- Duplicate groups displayed as expandable cards
- Each group shows:
  - All duplicate documents side-by-side
  - Metadata comparison (title, author, tags, notes)
  - URL comparison with differences highlighted
  - Match reason (URL match vs title similarity)
  - Reading progress indicator
- Visual indicators:
  - 🏆 Recommended document to keep (highlighted)
  - 🗑️ Documents marked for deletion
- Total duplicates found count
- Total documents to delete count
- Estimated storage savings

**Step 4: Deletion Planning**
- Toggle switches to override recommended keeps
- "Generate Deletion Plan" button
- Plan preview with statistics
- Export plan to CSV option

**Step 5: Execution**
- Dry-run mode toggle (default: ON)
- Confirmation modal (must type "DELETE")
- Real-time progress bar with:
  - Current document being processed
  - Documents deleted / Total count
  - ETA remaining
  - Pause/Cancel button (graceful interrupt)
- Post-execution report:
  - Success count
  - Failure count
  - Error details
  - Download execution report (JSON)

**Advanced Features:**
- Filter duplicate groups by match type
- Sort groups by size, date, quality score
- Save/load analysis sessions
- Compare documents side-by-side in detail view

**Templates Needed:**
- `duplicates/upload.html`
- `duplicates/analyze.html`
- `duplicates/results.html`
- `duplicates/plan.html`
- `duplicates/execute.html`
- `duplicates/report.html`

#### 6.5 Phase 5: Advanced Features (Priority: Low)
**Status:** ❌ Not Started

**Requirements:**
- **Reading Analytics:**
  - Reading progress charts
  - Articles read over time
  - Most read tags/topics

- **Batch Operations:**
  - Bulk location changes
  - Bulk tag operations
  - Bulk export by criteria

- **Automation Rules:**
  - Auto-archive articles after X days
  - Auto-tag by URL pattern
  - Scheduled duplicate detection

---

## Technical Specifications

### Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     User Interfaces                      │
├───────────────────────────┬──────────────────────────────┤
│     CLI Interface         │      Web Interface           │
│       (cli.py)            │      (web_app.py)            │
└───────────┬───────────────┴──────────┬───────────────────┘
            │                          │
            ▼                          ▼
┌─────────────────────────────────────────────────────────┐
│                  Business Logic Layer                    │
├──────────────────┬──────────────────┬───────────────────┤
│ DocumentManager  │  TagManager      │ Deduplicator      │
│ (document_       │ (tag_            │ (document_        │
│  manager.py)     │  manager.py)     │  deduplicator.py) │
└────────┬─────────┴────────┬─────────┴─────────┬─────────┘
         │                  │                   │
         └──────────────────┼───────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────┐
│                 API Client Layer                         │
│              ReadwiseClient (readwise_client.py)         │
└─────────────────────────┬───────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│              Readwise Reader API (External)              │
│              https://readwise.io/api_deets              │
└─────────────────────────────────────────────────────────┘
```

### Technology Stack

**Backend:**
- **Language:** Python 3.7+
- **Web Framework:** Flask 2.3.0+
- **HTTP Client:** requests 2.28.0+
- **Date Handling:** python-dateutil 2.8.0+

**Frontend (Web UI - To Be Implemented):**
- **HTML5** with semantic markup
- **CSS Framework:** Bootstrap 5 or Tailwind CSS (TBD)
- **JavaScript:** Vanilla JS or Alpine.js (for interactivity)
- **Charts:** Chart.js (for analytics visualizations)

**Testing:**
- **Framework:** pytest 7.4.0+
- **Mocking:** pytest-mock 3.11.0+, responses 0.23.0+
- **Coverage:** pytest-cov 4.1.0+ (Target: 80%+)

**Development Tools:**
- **Version Control:** Git
- **Dependency Management:** pip + requirements.txt
- **Documentation:** Markdown (README.md, CLAUDE.md, PRD.md)

### API Integration

**Readwise Reader API Endpoints:**
| Endpoint | Method | Purpose | Rate Limit |
|----------|--------|---------|------------|
| `/save/` | POST | Add documents | 50 req/min |
| `/list/` | GET | List/search documents | 20 req/min |
| `/update/` | PATCH | Update metadata | 50 req/min |
| `/delete/` | DELETE | Delete documents | 20 req/min |
| `/tags/` | GET | List tags | 20 req/min |

**Error Handling:**
- Automatic retry with exponential backoff
- Rate limit detection and waiting
- Network error recovery
- User-friendly error messages

### Data Models

**Document (from API):**
```python
{
    "id": str,                    # Unique document ID
    "url": str,                   # Source URL
    "title": str,                 # Document title
    "author": str,                # Author name
    "source": str,                # Source domain
    "category": str,              # article/email/pdf/etc.
    "location": str,              # new/later/archive/feed
    "tags": List[str],            # User tags
    "site_name": str,             # Website name
    "word_count": int,            # Word count
    "created_at": str,            # ISO datetime
    "updated_at": str,            # ISO datetime
    "published_date": str,        # ISO datetime
    "summary": str,               # Article summary
    "image_url": str,             # Cover image
    "reading_progress": float,    # 0.0 to 1.0
    "notes": str,                 # User notes
    # ... additional fields
}
```

**CSV Export Format (23 fields):**
```
id, url, title, author, source, category, location, tags,
site_name, word_count, created_at, updated_at, published_date,
summary, image_url, reading_progress, notes, first_opened_at,
last_opened_at, saved_using, is_public, parent_id, highlights
```

### File Structure

```
readwise-reader-management/
├── cli.py                      # CLI entry point
├── web_app.py                  # Flask web application
├── config.py                   # Configuration management
├── readwise_client.py          # API client layer
├── document_manager.py         # Document business logic
├── tag_manager.py              # Tag business logic
├── document_deduplicator.py    # Deduplication engine
├── requirements.txt            # Python dependencies
├── pytest.ini                  # Test configuration
├── .coveragerc                 # Coverage configuration
├── run_tests.sh                # Test runner script
├── README.md                   # User documentation
├── CLAUDE.md                   # AI assistant guidance
├── PRD.md                      # This document
├── todos.md                    # Development tasks
├── .gitignore                  # Git ignore rules
├── .readwise_token             # API token (gitignored)
├── tests/                      # Test suite
│   ├── __init__.py
│   ├── test_cli.py
│   ├── test_config.py
│   ├── test_document_manager.py
│   ├── test_document_deduplicator.py
│   ├── test_tag_manager.py
│   ├── test_readwise_client.py
│   └── test_web_app.py
└── templates/                  # HTML templates (TO BE CREATED)
    ├── base.html
    ├── setup.html
    ├── index.html
    ├── error.html
    ├── documents/
    │   ├── list.html
    │   ├── add.html
    │   ├── edit.html
    │   └── delete_confirm.html
    ├── tags/
    │   ├── list.html
    │   └── stats.html
    └── duplicates/
        ├── upload.html
        ├── analyze.html
        ├── results.html
        ├── plan.html
        ├── execute.html
        └── report.html
```

---

## Success Metrics

### User Engagement Metrics
- **CLI Usage:**
  - Command execution frequency
  - Most used commands
  - Average documents processed per session

- **Web UI Usage (Post-Launch):**
  - Daily/Monthly Active Users
  - Session duration
  - Pages per session
  - Duplicate detection feature usage rate

### Functional Metrics
- **Duplicate Detection Effectiveness:**
  - Average duplicates found per analysis
  - User acceptance rate of recommendations
  - False positive rate (< 5% target)
  - Time saved vs manual review (target: 90%+ reduction)

- **Bulk Operation Efficiency:**
  - Average documents processed per minute
  - Success rate of deletions (target: > 99%)
  - Time to process 1000 documents (target: < 10 minutes)

### Quality Metrics
- **Test Coverage:** > 80% (current: 47%)
- **API Error Rate:** < 1%
- **User-Reported Bugs:** < 5 per month
- **Documentation Completeness:** 100%

### Performance Metrics
- **Web UI Response Times:**
  - Page load: < 2 seconds
  - API calls: < 1 second
  - Duplicate analysis (1000 docs): < 30 seconds

---

## User Stories

### Epic 1: Document Management
**US-1.1** As a user, I want to add articles from URLs so that I can save content for later reading.
**US-1.2** As a user, I want to list all my documents so that I can see what I've saved.
**US-1.3** As a user, I want to search documents by title so that I can find specific articles quickly.
**US-1.4** As a user, I want to archive old documents so that I can keep my reading queue clean.
**US-1.5** As a user, I want to export documents to CSV so that I can analyze my reading habits.

### Epic 2: Tag Management
**US-2.1** As a user, I want to see all my tags so that I can understand my categorization system.
**US-2.2** As a user, I want to search tags so that I can find specific topics quickly.
**US-2.3** As a user, I want to see tag statistics so that I can understand which topics I save most.

### Epic 3: Duplicate Detection
**US-3.1** As a user with 1000+ articles, I want to automatically find duplicates so that I don't waste time on manual review.
**US-3.2** As a user, I want to remove tracking parameters from URLs so that articles from different sources are properly matched.
**US-3.3** As a user, I want smart recommendations on which duplicate to keep so that I don't accidentally delete important content.
**US-3.4** As a user, I want to preview deletions before executing so that I can verify the plan is correct.
**US-3.5** As a user, I want to interrupt long-running operations safely so that I don't lose progress or corrupt data.

### Epic 4: Web User Interface
**US-4.1** As a casual user, I want a visual interface so that I don't need to use command-line tools.
**US-4.2** As a user, I want to see my collection statistics on a dashboard so that I can understand my reading habits at a glance.
**US-4.3** As a user, I want to visualize duplicate groups so that I can make informed decisions about what to keep.
**US-4.4** As a user, I want to see real-time progress during bulk operations so that I know how long I need to wait.
**US-4.5** As a user, I want to configure my API token via web interface so that setup is easier for non-technical users.

---

## Roadmap

### Phase 1: Foundation (✅ Complete)
**Timeline:** Completed
**Status:** 100% Complete

- [x] Core API client implementation
- [x] Document manager with CRUD operations
- [x] Tag manager with search and statistics
- [x] CLI interface with all commands
- [x] Configuration management
- [x] Comprehensive test suite
- [x] Documentation (README, CLAUDE.md)

**Deliverables:**
- Fully functional CLI tool
- 84/99 tests passing (84.8%)
- 47% code coverage

### Phase 2: Advanced Deduplication (✅ Complete)
**Timeline:** Completed
**Status:** 100% Complete

- [x] CSV-based duplicate detection
- [x] Standard URL normalization
- [x] Advanced URL normalization (query string removal)
- [x] Title similarity matching (sequence matching algorithm)
- [x] Metadata quality scoring
- [x] Smart deletion planning with priority rules
- [x] Batch execution with progress tracking
- [x] Graceful interruption and resume support
- [x] Execution reports

**Deliverables:**
- Production-ready deduplication system
- CSV workflow documentation
- Safety features (dry-run, confirmations)

### Phase 3: Web UI - Core Infrastructure (🔄 In Planning)
**Timeline:** Q1 2026 (4-6 weeks)
**Status:** Not Started
**Priority:** HIGH

**Milestones:**
- Week 1-2: Template infrastructure and base layout
  - [x] Create templates directory structure
  - [ ] Implement base.html with responsive navigation
  - [ ] Create setup.html for API token configuration
  - [ ] Create index.html dashboard with statistics
  - [ ] Create error.html for error handling
  - [ ] Add CSS framework integration (Bootstrap/Tailwind)
  - [ ] Fix all 14 failing web app tests

- Week 3-4: Document management UI
  - [ ] Implement documents/list.html with table view
  - [ ] Create documents/add.html form
  - [ ] Create documents/edit.html form
  - [ ] Add AJAX endpoints for real-time operations
  - [ ] Implement pagination and filtering

- Week 5-6: Tag management UI
  - [ ] Implement tags/list.html
  - [ ] Create tags/stats.html with visualizations
  - [ ] Add Chart.js for statistics graphs

**Success Criteria:**
- All web app tests pass (99/99 tests passing)
- User can perform all CRUD operations via web interface
- Responsive design works on mobile/tablet/desktop
- Code coverage > 60%

### Phase 4: Web UI - Duplicate Detection (🔄 Planned)
**Timeline:** Q2 2026 (6-8 weeks)
**Status:** Not Started
**Priority:** HIGH (Key Differentiator)

**Milestones:**
- Week 1-2: Data input and analysis UI
  - [ ] Create duplicates/upload.html (CSV upload + API fetch)
  - [ ] Create duplicates/analyze.html (mode selection + progress)
  - [ ] Implement real-time analysis progress updates (WebSocket or SSE)

- Week 3-4: Results display and planning
  - [ ] Create duplicates/results.html (expandable duplicate groups)
  - [ ] Implement side-by-side document comparison
  - [ ] Create duplicates/plan.html (deletion planning interface)
  - [ ] Add interactive keep/delete toggles

- Week 5-6: Execution and reporting
  - [ ] Create duplicates/execute.html (progress tracking)
  - [ ] Implement real-time execution progress (WebSocket)
  - [ ] Create duplicates/report.html (execution summary)
  - [ ] Add pause/cancel functionality with graceful interrupt

- Week 7-8: Polish and testing
  - [ ] Implement filters and sorting for duplicate groups
  - [ ] Add "save session" functionality
  - [ ] Comprehensive UI testing
  - [ ] User acceptance testing

**Success Criteria:**
- User can complete full duplicate detection workflow via web
- Real-time progress updates work smoothly
- Interrupt/resume functionality works reliably
- User feedback: "Easier than CLI" rating > 80%

### Phase 5: Advanced Features (📋 Future)
**Timeline:** Q3 2026 and beyond
**Status:** Backlog
**Priority:** MEDIUM to LOW

**Potential Features:**
- [ ] Reading analytics dashboard
- [ ] Automation rules engine
- [ ] Batch tag operations
- [ ] Tag merge/rename functionality
- [ ] Browser extension for one-click save
- [ ] Mobile responsive improvements
- [ ] Dark mode theme
- [ ] API rate limit dashboard
- [ ] Export to other services (Notion, Obsidian, etc.)
- [ ] Scheduled deduplication jobs
- [ ] Email notifications for completed operations

**To Be Prioritized Based On:**
- User feedback and feature requests
- Usage analytics
- Competitive analysis

---

## Dependencies and Risks

### External Dependencies
- **Readwise Reader API:** Changes to API may require updates
- **Python Ecosystem:** Dependency updates may introduce breaking changes
- **Browser Compatibility:** Web UI must support modern browsers (Chrome, Firefox, Safari, Edge)

### Technical Risks

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| API rate limiting issues | High | Medium | Implement intelligent batching and caching |
| Large collection performance | High | Medium | Add pagination, lazy loading, and worker processes |
| Data loss during deletion | High | Low | Robust dry-run, confirmations, and undo mechanism |
| Cross-browser compatibility | Medium | Low | Use standard web technologies and test on multiple browsers |
| Template rendering performance | Medium | Low | Use template caching and optimize Jinja2 templates |

### Business Risks

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Low user adoption of web UI | Medium | Low | Conduct user testing during development |
| Readwise API changes | High | Low | Monitor API changelog and maintain backwards compatibility |
| Competing tools | Low | Medium | Focus on unique features (advanced deduplication) |

---

## Open Questions

### Technical Decisions
- [ ] **CSS Framework Choice:** Bootstrap 5 vs Tailwind CSS vs Custom CSS?
  - **Recommendation:** Bootstrap 5 (faster development, good documentation)

- [ ] **Real-time Updates:** WebSocket vs Server-Sent Events vs Polling?
  - **Recommendation:** Server-Sent Events (simpler, unidirectional, sufficient for progress updates)

- [ ] **Session Management:** Flask-Session vs JWT vs Simple cookies?
  - **Recommendation:** Flask-Session (local tool, simple authentication)

- [ ] **Frontend State Management:** Vanilla JS vs Alpine.js vs Vue.js?
  - **Recommendation:** Alpine.js (lightweight, easy to integrate with Flask templates)

### Product Decisions
- [ ] **Pricing Model:** Free open-source vs Paid hosted version vs Donations?
  - **Current:** Free open-source (MIT License)

- [ ] **Multi-user Support:** Single-user vs Multi-tenant hosted service?
  - **Current:** Single-user tool (simplifies architecture)

- [ ] **Mobile App:** Native mobile app vs Progressive Web App?
  - **Decision:** Defer until Phase 5, focus on responsive web first

---

## Appendices

### Appendix A: API Rate Limits Reference

| Endpoint Category | Limit | Window |
|-------------------|-------|--------|
| General (GET) | 20 requests | per minute |
| Create/Update (POST/PATCH) | 50 requests | per minute |
| Delete | 20 requests | per minute |

### Appendix B: Glossary

- **Document:** An article, email, PDF, or other content saved to Readwise Reader
- **Location:** The inbox category (new, later, archive, feed)
- **Duplicate Group:** A set of 2+ documents that match duplicate detection criteria
- **Metadata Quality Score:** Calculated score based on completeness of title, author, summary, tags, etc.
- **Normalized URL:** URL with protocol, query strings, and trailing slashes removed
- **Title Similarity:** Percentage match calculated using sequence matching algorithm
- **Dry-run:** Execution mode that previews operations without making actual changes

### Appendix C: Changelog

**Version 2.0 (Current)**
- Added comprehensive PRD document
- Defined Phase 3 (Web UI Core) and Phase 4 (Duplicate Detection UI)
- Updated roadmap with specific milestones

**Version 1.2**
- Advanced duplicate detection with title similarity
- Graceful interruption and resume support
- CSV-based workflow fully implemented

**Version 1.1**
- Comprehensive test suite
- Document and tag statistics
- Export functionality (JSON and CSV)

**Version 1.0**
- Initial CLI implementation
- Basic CRUD operations
- API client layer

---

## Approval and Sign-off

**Document Status:** Draft for Review

**Stakeholders:**
- [ ] Product Owner
- [ ] Engineering Lead
- [ ] QA Lead
- [ ] UX/UI Designer (for Phase 3-4)

**Next Review Date:** TBD

---

**End of PRD**
