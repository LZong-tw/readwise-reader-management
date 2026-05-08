import unittest
from unittest.mock import Mock, patch, MagicMock
import json
from document_deduplicator import DocumentDeduplicator

class TestDocumentDeduplicator(unittest.TestCase):
    """DocumentDeduplicator tests"""
    
    def setUp(self):
        """Set up test environment"""
        self.mock_client = Mock()
        self.deduplicator = DocumentDeduplicator(self.mock_client)
        
        # Create test document data
        self.test_documents = [
            {
                "id": "doc1",
                "title": "Python Programming Guide for Beginners",
                "author": "John Doe",
                "source_url": "https://example.com/python-guide",
                "summary": "This is a detailed Python programming guide for beginners, covering basic syntax and advanced concepts.",
                "location": "new",
                "created_at": "2024-01-15T10:00:00Z",
                "updated_at": "2024-01-15T10:00:00Z",
                "tags": [{"name": "python"}, {"name": "programming"}]
            },
            {
                "id": "doc2", 
                "title": "Python Programming Guide",
                "author": "",
                "source_url": "https://example.com/python-guide?utm_source=facebook",
                "summary": "",
                "location": "new",
                "created_at": "2024-01-14T09:00:00Z",
                "updated_at": "2024-01-14T09:00:00Z",
                "tags": []
            },
            {
                "id": "doc3",
                "title": "JavaScript Basics Tutorial",
                "author": "Jane Smith",
                "source_url": "https://example.com/js-tutorial",
                "summary": "Learn the basics of JavaScript programming.",
                "location": "new",
                "created_at": "2024-01-16T11:00:00Z",
                "updated_at": "2024-01-16T11:00:00Z",
                "tags": [{"name": "javascript"}]
            },
            {
                "id": "doc4",
                "title": "Machine Learning in Practice",
                "author": "Bob Wilson",
                "source_url": "https://example.com/ml-practical",
                "summary": "Practical applications and case studies in machine learning.",
                "location": "later",
                "created_at": "2024-01-17T12:00:00Z",
                "updated_at": "2024-01-17T12:00:00Z",
                "tags": [{"name": "ml"}, {"name": "ai"}, {"name": "data"}]
            }
        ]
    
    def test_normalize_url(self):
        """Test URL normalization functionality"""
        # Test removing tracking parameters
        url_with_tracking = "https://example.com/article?utm_source=google&utm_medium=email&ref=newsletter"
        normalized = self.deduplicator.normalize_url(url_with_tracking)
        self.assertEqual(normalized, "https://example.com/article")
        
        # Test preserving valid parameters
        url_with_valid_params = "https://example.com/search?q=python&lang=en"
        normalized = self.deduplicator.normalize_url(url_with_valid_params)
        self.assertEqual(normalized, "https://example.com/search?lang=en&q=python")
        
        # Test empty URL
        self.assertEqual(self.deduplicator.normalize_url(""), "")
        self.assertEqual(self.deduplicator.normalize_url(None), "")

    def test_normalize_url_advanced(self):
        """Test advanced URL normalization"""
        # Test query string removal
        test_cases = [
            ("https://example.com/article?utm_source=twitter", "example.com/article"),
            ("https://example.com/article?ref=newsletter", "example.com/article"),
            ("https://example.com/article?utm_campaign=social&utm_source=facebook", "example.com/article"),
            ("https://example.com/article#section1", "example.com/article"),
            ("https://example.com/article?source=rss#top", "example.com/article"),
            ("http://example.com/page", "example.com/page"),
            ("https://example.com/page/", "example.com/page"),
            ("HTTPS://EXAMPLE.COM/Article", "example.com/article"),
            ("", ""),  # Empty URL
        ]
        
        for input_url, expected in test_cases:
            with self.subTest(url=input_url):
                result = self.deduplicator.normalize_url_advanced(input_url)
                self.assertEqual(result, expected, f"Failed for {input_url}")
    
    def test_normalize_url_advanced_fallback(self):
        """Test advanced URL normalization fallback to simple method"""
        # Mock urlparse to raise an exception to trigger fallback
        with patch('urllib.parse.urlparse', side_effect=Exception("Parse error")):
            with patch.object(self.deduplicator, 'normalize_url_simple', return_value='fallback_result') as mock_simple:
                # This should trigger the exception and fallback
                result = self.deduplicator.normalize_url_advanced("test-url")
                self.assertEqual(result, 'fallback_result')
                mock_simple.assert_called_once_with("test-url")
    
    def test_calculate_title_similarity(self):
        """Test title similarity calculation"""
        # Test identical titles
        similarity = self.deduplicator.calculate_title_similarity(
            "Python Programming", "Python Programming"
        )
        self.assertEqual(similarity, 1.0)
        
        # Test similar titles
        similarity = self.deduplicator.calculate_title_similarity(
            "Python Programming Guide", "Python Programming Tutorial"
        )
        self.assertGreater(similarity, 0.3)  # Should have some similarity
        
        # Test different titles
        similarity = self.deduplicator.calculate_title_similarity(
            "Python Programming", "JavaScript Basics"
        )
        self.assertLess(similarity, 0.5)  # Similarity should be low
        
        # Test empty titles
        similarity = self.deduplicator.calculate_title_similarity("", "Python")
        self.assertEqual(similarity, 0.0)
    
    def test_calculate_metadata_quality_score(self):
        """Test metadata quality scoring"""
        # Test high-quality document
        high_quality_doc = self.test_documents[0]
        score = self.deduplicator.calculate_metadata_quality_score(high_quality_doc)
        self.assertGreater(score, 70)  # High-quality document should have high score
        
        # Test low-quality document
        low_quality_doc = self.test_documents[1]
        score = self.deduplicator.calculate_metadata_quality_score(low_quality_doc)
        self.assertLess(score, 50)  # Low-quality document should have lower score
        
        # Test empty document
        empty_doc = {"id": "empty"}
        score = self.deduplicator.calculate_metadata_quality_score(empty_doc)
        self.assertEqual(score, 0.0)
    
    def test_find_duplicate_groups(self):
        """Test duplicate document group identification"""
        # Create test data with duplicates
        documents_with_duplicates = [
            {
                "id": "doc1",
                "title": "Python Programming Guide",
                "source_url": "https://example.com/python-guide",
                "author": "John Doe",
                "summary": "Detailed guide"
            },
            {
                "id": "doc2",
                "title": "Python Programming Tutorial", 
                "source_url": "https://example.com/python-guide?utm_source=fb",
                "author": "",
                "summary": ""
            },
            {
                "id": "doc3",
                "title": "JavaScript Tutorial",
                "source_url": "https://example.com/js-tutorial", 
                "author": "Jane Smith",
                "summary": "JS basics"
            }
        ]
        
        duplicate_groups = self.deduplicator.find_duplicate_groups(documents_with_duplicates)
        
        # Should find one duplicate group (doc1 and doc2)
        self.assertEqual(len(duplicate_groups), 1)
        self.assertEqual(len(duplicate_groups[0]), 2)
        
        # Check that the group contains the correct documents
        group_ids = {doc["id"] for doc in duplicate_groups[0]}
        self.assertIn("doc1", group_ids)
        self.assertIn("doc2", group_ids)
    
    def test_select_best_document(self):
        """Test best document selection"""
        # Use the first two test documents (duplicates)
        duplicate_docs = self.test_documents[:2]
        
        best_doc, duplicates_to_remove = self.deduplicator.select_best_document(duplicate_docs)
        
        # The first document should be selected as best (has more complete metadata)
        self.assertEqual(best_doc["id"], "doc1")
        self.assertEqual(len(duplicates_to_remove), 1)
        self.assertEqual(duplicates_to_remove[0]["id"], "doc2")
    
    @patch('document_manager.DocumentManager')
    def test_analyze_duplicates(self, mock_doc_manager_class):
        """Test duplicate analysis functionality"""
        # Set up mock
        mock_doc_manager = Mock()
        mock_doc_manager.get_documents.return_value = self.test_documents
        mock_doc_manager_class.return_value = mock_doc_manager
        
        # Execute analysis
        analysis = self.deduplicator.analyze_duplicates()
        
        # Check analysis result structure
        self.assertIn("total_documents", analysis)
        self.assertIn("duplicate_groups", analysis)
        self.assertIn("total_duplicates", analysis)
        self.assertIn("groups", analysis)
        
        # Check total document count
        self.assertEqual(analysis["total_documents"], 4)
    
    def test_analyze_duplicates_with_no_documents(self):
        """Test analysis with no documents"""
        analysis = self.deduplicator.analyze_duplicates([])
        self.assertIn("error", analysis)
    
    @patch('document_manager.DocumentManager')
    def test_remove_duplicates_dry_run(self, mock_doc_manager_class):
        """Test deduplication preview mode"""
        # Set up mock
        mock_doc_manager = Mock()
        mock_doc_manager.get_documents.return_value = self.test_documents
        mock_doc_manager_class.return_value = mock_doc_manager
        
        # Execute preview
        result = self.deduplicator.remove_duplicates(dry_run=True)
        
        # Check results
        self.assertTrue(result.get("dry_run"))
        self.assertEqual(result.get("removed_count"), 0)
        
        # Confirm delete API was not called
        self.mock_client.delete_document.assert_not_called()
    
    def test_export_analysis_report(self):
        """Test analysis report export"""
        analysis_data = {
            "total_documents": 10,
            "duplicate_groups": 2,
            "total_duplicates": 3,
            "groups": []
        }
        
        with patch('builtins.open', create=True) as mock_open:
            with patch('json.dump') as mock_json_dump:
                filename = self.deduplicator.export_analysis_report(analysis_data, "test_report.json")
                
                # Check filename
                self.assertEqual(filename, "test_report.json")
                
                # Check that file write was called
                mock_open.assert_called_once_with("test_report.json", 'w', encoding='utf-8')
                mock_json_dump.assert_called_once()

    def test_find_csv_duplicates_advanced(self):
        """Test advanced CSV duplicate analysis"""
        import tempfile
        import csv
        import os
        
        # Create test CSV data
        test_csv_data = [
            {
                'id': '1',
                'title': 'Python Programming Guide for Beginners',
                'source_url': 'https://example.com/python-guide?utm_source=twitter',
                'author': 'John Doe',
                'notes': '',
                'tags': 'python,programming',
                'created_at': '2024-01-01T10:00:00Z',
                'location': 'new'
            },
            {
                'id': '2',
                'title': 'Python Programming Tutorial for Beginners',  # High similarity to #1
                'source_url': 'https://example.com/python-guide?ref=newsletter',  # Same base URL as #1
                'author': 'Jane Smith',
                'notes': '',
                'tags': 'python',
                'created_at': '2024-01-02T10:00:00Z',
                'location': 'new'
            },
            {
                'id': '3',
                'title': 'JavaScript Complete Guide',
                'source_url': 'https://example.com/js-guide',
                'author': 'Bob Wilson',
                'notes': '',
                'tags': 'javascript',
                'created_at': '2024-01-03T10:00:00Z',
                'location': 'new'
            },
            {
                'id': '4',
                'title': 'JavaScript Comprehensive Guide',  # High similarity to #3
                'source_url': 'https://different-site.com/js-tutorial',  # Different URL from #3
                'author': 'Alice Brown',
                'notes': '',
                'tags': 'js',
                'created_at': '2024-01-04T10:00:00Z',
                'location': 'new'
            }
        ]
        
        # Create temporary CSV file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=test_csv_data[0].keys())
            writer.writeheader()
            writer.writerows(test_csv_data)
            temp_csv_path = f.name
        
        try:
            # Test advanced analysis
            analysis = self.deduplicator.find_csv_duplicates_advanced(temp_csv_path)
            
            # Verify analysis structure
            self.assertIn("csv_file", analysis)
            self.assertIn("mode", analysis)
            self.assertIn("total_documents", analysis)
            self.assertIn("duplicate_groups", analysis)
            self.assertIn("total_duplicates", analysis)
            self.assertIn("groups", analysis)
            self.assertIn("warning", analysis)
            
            # Check mode
            self.assertEqual(analysis["mode"], "advanced")
            
            # Check document count
            self.assertEqual(analysis["total_documents"], 4)
            
            # Should find 2 duplicate groups
            self.assertEqual(analysis["duplicate_groups"], 2)
            self.assertEqual(analysis["total_duplicates"], 2)
            
            # Check groups structure
            for group in analysis["groups"]:
                self.assertIn("normalized_url", group)
                self.assertIn("documents", group)
                self.assertIn("count", group)
                self.assertIn("example_urls", group)
                self.assertIn("example_titles", group)
                self.assertIn("match_reason", group)
                self.assertEqual(group["count"], 2)  # Each group should have 2 documents
            
        finally:
            # Clean up
            os.unlink(temp_csv_path)

    def test_advanced_match_reason_exact_values(self):
        """Pin the exact match_reason strings emitted into CSV/JSON.

        Downstream consumers may key off these values. Any change here is a
        breaking change and must land alongside a CHANGELOG note.
        """
        import tempfile
        import csv
        import os

        rows = [
            # Pair A: title-only match (different URL paths, similar titles)
            {'id': 'A1', 'title': 'Python Programming Guide for Beginners',
             'source_url': 'https://a.example.com/article-one',
             'author': '', 'notes': '', 'tags': '',
             'created_at': '2024-01-01T00:00:00Z', 'location': 'new'},
            {'id': 'A2', 'title': 'Python Programming Guide for Beginnerz',
             'source_url': 'https://b.example.com/article-two',
             'author': '', 'notes': '', 'tags': '',
             'created_at': '2024-01-02T00:00:00Z', 'location': 'new'},
            # Pair B: URL-only match (same path, totally unrelated titles)
            {'id': 'B1', 'title': 'Quarterly Earnings Report 2024',
             'source_url': 'https://example.com/cool-piece?utm=x',
             'author': '', 'notes': '', 'tags': '',
             'created_at': '2024-01-03T00:00:00Z', 'location': 'new'},
            {'id': 'B2', 'title': 'Knitting Patterns For Cats',
             'source_url': 'https://example.com/cool-piece?ref=y',
             'author': '', 'notes': '', 'tags': '',
             'created_at': '2024-01-04T00:00:00Z', 'location': 'new'},
            # Pair C: both URL and title match
            {'id': 'C1', 'title': 'Identical Title Here',
             'source_url': 'https://example.com/both?utm=x',
             'author': '', 'notes': '', 'tags': '',
             'created_at': '2024-01-05T00:00:00Z', 'location': 'new'},
            {'id': 'C2', 'title': 'Identical Title Here',
             'source_url': 'https://example.com/both?ref=y',
             'author': '', 'notes': '', 'tags': '',
             'created_at': '2024-01-06T00:00:00Z', 'location': 'new'},
        ]

        with tempfile.NamedTemporaryFile(
            mode='w', suffix='.csv', delete=False, encoding='utf-8', newline=''
        ) as f:
            writer = csv.DictWriter(f, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)
            temp_path = f.name

        try:
            # Sanity-check the test premise: pair B titles must be below Rule 1
            # threshold so any URL-only match isn't accidentally a title match.
            b_sim = self.deduplicator.calculate_title_similarity(
                rows[2]['title'], rows[3]['title']
            )
            self.assertLessEqual(
                b_sim, 0.5,
                f"Test premise broken: pair B title similarity {b_sim:.2%} "
                "exceeds Rule 1 threshold; choose more dissimilar titles."
            )

            analysis = self.deduplicator.find_csv_duplicates_advanced(temp_path)
            reasons_by_first_id = {
                group['documents'][0]['data']['id']: group['match_reason']
                for group in analysis['groups']
            }

            # Title-only pair → reason starts with "Title similarity: "
            self.assertIn('A1', reasons_by_first_id)
            self.assertTrue(
                reasons_by_first_id['A1'].startswith('Title similarity: '),
                reasons_by_first_id['A1']
            )
            # URL-only pair → exact "Same URL (no query)"
            self.assertIn('B1', reasons_by_first_id)
            self.assertEqual(reasons_by_first_id['B1'], 'Same URL (no query)')
            # Both → "Same URL (no query) + title similarity: <pct>"
            self.assertIn('C1', reasons_by_first_id)
            self.assertTrue(
                reasons_by_first_id['C1'].startswith('Same URL (no query) + title similarity: '),
                reasons_by_first_id['C1']
            )
        finally:
            os.unlink(temp_path)

    def test_render_match_reason_collapses_equal_rounded_endpoints(self):
        """Two distinct similarities that round to the same .1% must collapse.

        Otherwise we emit a meaningless `73.1%–73.1%` form that forces every
        downstream consumer to handle a degenerate range case.
        """
        # Two distinct floats that both render as 73.1%. Sanity-check the
        # premise inside the test so a future format-spec change fails loudly.
        a, b = 0.73111, 0.73149
        self.assertEqual(f"{a:.1%}", "73.1%")
        self.assertEqual(f"{b:.1%}", "73.1%")
        rendered = self.deduplicator._render_match_reason(
            url_only_seen=False,
            url_and_title_sims=[],
            title_only_sims=[a, b],
        )
        self.assertEqual(rendered, "Title similarity: 73.1%")
        self.assertNotIn('–', rendered)

        # Sanity: when endpoints round differently, range form is preserved.
        ranged = self.deduplicator._render_match_reason(
            url_only_seen=False,
            url_and_title_sims=[],
            title_only_sims=[0.60, 0.95],
        )
        self.assertIn('–', ranged)

    def test_advanced_match_reason_aggregates_mixed_group(self):
        """4-doc group: seed matches two title-only members at different similarity
        percentages and one URL-only member.

        The exported match_reason must:
        1. Surface BOTH rule categories (so reviewers see every rule that fired).
        2. Emit each category exactly ONCE — varying similarity percentages must
           not multiply the title-similarity component (proves cardinality is
           bounded by category, not by edge).
        """
        import tempfile
        import csv
        import os

        rows = [
            # Seed
            {'id': 'S', 'title': 'Quarterly Operations Review FY2024',
             'source_url': 'https://example.com/operations-review',
             'author': '', 'notes': '', 'tags': '',
             'created_at': '2024-01-01T00:00:00Z', 'location': 'new'},
            # Title-only match #1 — high similarity (just punctuation diff)
            {'id': 'T1', 'title': 'Quarterly Operations Review FY2024.',
             'source_url': 'https://other.example.org/some-other-path',
             'author': '', 'notes': '', 'tags': '',
             'created_at': '2024-01-02T00:00:00Z', 'location': 'new'},
            # Title-only match #2 — moderate similarity (added suffix word)
            {'id': 'T2', 'title': 'Quarterly Operations Review FY2024 Summary',
             'source_url': 'https://yet-another.example.net/p/123',
             'author': '', 'notes': '', 'tags': '',
             'created_at': '2024-01-03T00:00:00Z', 'location': 'new'},
            # URL-only match (totally different title, same normalized path)
            {'id': 'U', 'title': 'Knitting Patterns For Cats',
             'source_url': 'https://example.com/operations-review?utm=newsletter',
             'author': '', 'notes': '', 'tags': '',
             'created_at': '2024-01-04T00:00:00Z', 'location': 'new'},
        ]

        with tempfile.NamedTemporaryFile(
            mode='w', suffix='.csv', delete=False, encoding='utf-8', newline=''
        ) as f:
            writer = csv.DictWriter(f, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)
            temp_path = f.name

        try:
            sim_t1 = self.deduplicator.calculate_title_similarity(rows[0]['title'], rows[1]['title'])
            sim_t2 = self.deduplicator.calculate_title_similarity(rows[0]['title'], rows[2]['title'])
            sim_u = self.deduplicator.calculate_title_similarity(rows[0]['title'], rows[3]['title'])
            # Premise: both T1 and T2 fire title rule
            self.assertGreater(sim_t1, 0.5, f"Test premise: seed/T1 sim {sim_t1:.2%}")
            self.assertGreater(sim_t2, 0.5, f"Test premise: seed/T2 sim {sim_t2:.2%}")
            # Premise: T1 and T2 produce different similarity percentages
            # (otherwise the test wouldn't exercise the cardinality bound)
            self.assertNotAlmostEqual(sim_t1, sim_t2, places=2,
                msg=f"Test premise: T1 ({sim_t1:.2%}) and T2 ({sim_t2:.2%}) similarities should differ")
            # Premise: seed/U is URL-only
            self.assertLessEqual(sim_u, 0.5, f"Test premise: seed/U sim {sim_u:.2%}")

            analysis = self.deduplicator.find_csv_duplicates_advanced(temp_path)
            self.assertEqual(analysis['duplicate_groups'], 1)
            group = analysis['groups'][0]
            self.assertEqual(group['count'], 4)
            reasons = group['match_reason'].split(' | ')

            # URL-only category appears exactly once.
            self.assertEqual(reasons.count('Same URL (no query)'), 1, group['match_reason'])
            # Title-only category appears exactly once even though TWO edges fed
            # it at different percentages (this is the cardinality bound).
            title_reasons = [r for r in reasons if r.startswith('Title similarity: ')]
            self.assertEqual(len(title_reasons), 1, group['match_reason'])
            # That single title component must surface BOTH percentages via a
            # min–max range so reviewers don't lose information.
            self.assertIn('–', title_reasons[0],
                f"Expected min–max range when multiple title edges fired: {title_reasons[0]!r}")
            # Stable order: URL-only must appear before the title component.
            self.assertLess(reasons.index('Same URL (no query)'),
                            reasons.index(title_reasons[0]),
                            f"URL component must precede title component: {group['match_reason']!r}")
        finally:
            os.unlink(temp_path)

    def test_advanced_url_only_match_with_different_titles(self):
        """Advanced Rule 2: same normalized URL must group rows even if titles differ."""
        import tempfile
        import csv
        import os

        rows = [
            {
                'id': '1',
                'title': 'Cool Article: The Definitive Guide',
                'source_url': 'https://example.com/cool-article?utm=twitter',
                'author': '', 'notes': '', 'tags': '',
                'created_at': '2024-01-01T10:00:00Z', 'location': 'new'
            },
            {
                'id': '2',
                # Completely different surface title (e.g., slug-only fallback) but same URL
                'title': 'cool-article',
                'source_url': 'https://example.com/cool-article?ref=newsletter',
                'author': '', 'notes': '', 'tags': '',
                'created_at': '2024-01-02T10:00:00Z', 'location': 'new'
            }
        ]

        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)
            temp_path = f.name

        try:
            # Sanity check: titles are NOT similar enough to trigger Rule 1
            similarity = self.deduplicator.calculate_title_similarity(
                rows[0]['title'], rows[1]['title']
            )
            self.assertLessEqual(similarity, 0.5,
                "Test premise broken: titles should not exceed Rule 1 threshold")

            analysis = self.deduplicator.find_csv_duplicates_advanced(temp_path)

            self.assertEqual(analysis["duplicate_groups"], 1,
                "Same normalized URL should group rows even when titles diverge (Rule 2)")
            group = analysis["groups"][0]
            self.assertEqual(group["count"], 2)
            self.assertIn("Same URL", group["match_reason"])
        finally:
            os.unlink(temp_path)

    def test_advanced_matching_rules(self):
        """Test advanced duplicate matching rules"""
        # Test Rule 1: Title similarity > 50% (regardless of URL)
        title1 = "Python Programming Guide"
        title2 = "Python Programming Tutorial"
        similarity = self.deduplicator.calculate_title_similarity(title1, title2)
        self.assertGreater(similarity, 0.5, "Should match on title similarity >50%")
        
        # Test Rule 2: Same normalized URL + title similarity > 50%
        url1 = "https://example.com/article?utm_source=twitter"
        url2 = "https://example.com/article?ref=newsletter"
        normalized1 = self.deduplicator.normalize_url_advanced(url1)
        normalized2 = self.deduplicator.normalize_url_advanced(url2)
        self.assertEqual(normalized1, normalized2, "URLs should normalize to same value")
        
        # These titles should have high similarity
        title3 = "JavaScript Complete Guide"
        title4 = "JavaScript Comprehensive Guide"
        similarity2 = self.deduplicator.calculate_title_similarity(title3, title4)
        self.assertGreater(similarity2, 0.5, "Should have sufficient title similarity")

    def test_advanced_csv_export(self):
        """Test advanced mode CSV export with extra fields"""
        # Mock analysis data with advanced mode
        analysis_data = {
            "csv_file": "test.csv",
            "mode": "advanced",
            "total_documents": 4,
            "duplicate_groups": 1,
            "total_duplicates": 1,
            "groups": [{
                "normalized_url": "example.com/article",
                "documents": [
                    {"row_number": 1, "data": {"id": "1", "title": "Test Article", "source_url": "https://example.com/article?utm=1"}},
                    {"row_number": 2, "data": {"id": "2", "title": "Test Article Copy", "source_url": "https://example.com/article?ref=2"}}
                ],
                "count": 2,
                "example_urls": ["https://example.com/article?utm=1", "https://example.com/article?ref=2"],
                "example_titles": ["Test Article", "Test Article Copy"],
                "match_reason": "Title similarity: 85%"
            }],
            "warning": "Advanced mode warning"
        }
        
        with patch('builtins.open', create=True) as mock_open:
            with patch('csv.DictWriter') as mock_writer_class:
                mock_writer = Mock()
                mock_writer_class.return_value = mock_writer
                
                filename = self.deduplicator.export_csv_duplicates(analysis_data, "test_advanced.csv")
                
                # Check filename
                self.assertEqual(filename, "test_advanced.csv")
                
                # Check that advanced mode fields were included
                mock_writer_class.assert_called_once()
                call_args = mock_writer_class.call_args[1]
                fieldnames = call_args['fieldnames']
                
                # Advanced mode should have extra fields
                self.assertIn('match_reason', fieldnames)
                self.assertIn('example_urls', fieldnames)
                self.assertIn('example_titles', fieldnames)

    def test_advanced_analysis_progress_tracking(self):
        """Test that advanced analysis shows progress messages"""
        import tempfile
        import csv
        import os
        from unittest.mock import patch
        
        # Create test data with enough documents to trigger progress messages
        test_csv_data = []
        for i in range(120):  # Create 120 documents to test progress tracking
            test_csv_data.append({
                'id': str(i + 1),
                'title': f'Test Document {i + 1}',
                'source_url': f'https://example.com/doc{i + 1}',
                'author': f'Author {i + 1}',
                'notes': '',
                'tags': 'test',
                'created_at': f'2024-01-{(i % 30) + 1:02d}T10:00:00Z',
                'location': 'new'
            })
        
        # Create temporary CSV file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=test_csv_data[0].keys())
            writer.writeheader()
            writer.writerows(test_csv_data)
            temp_csv_path = f.name
        
        try:
            # Capture safe_print output to verify progress messages
            with patch('document_deduplicator.safe_print') as mock_safe_print:
                # Test advanced analysis
                analysis = self.deduplicator.find_csv_duplicates_advanced(temp_csv_path)
                
                # Verify analysis completed successfully
                self.assertIn("total_documents", analysis)
                self.assertEqual(analysis["total_documents"], 120)
                
                # Check that progress messages were displayed
                progress_calls = [call for call in mock_safe_print.call_args_list 
                                if 'Progress:' in str(call) or 'Processing complete:' in str(call)]
                
                # Should have progress messages (at least initial processing message and completion)
                self.assertGreater(len(progress_calls), 0, "Should display progress messages")
                
                # Check for specific progress-related messages
                all_messages = [str(call) for call in mock_safe_print.call_args_list]
                processing_messages = [msg for msg in all_messages if 'Processing' in msg and 'documents' in msg]
                completion_messages = [msg for msg in all_messages if 'Processing complete:' in msg]
                
                self.assertGreater(len(processing_messages), 0, "Should show processing start message")
                self.assertGreater(len(completion_messages), 0, "Should show completion message")
                
        finally:
            # Clean up
            os.unlink(temp_csv_path)

    def test_find_csv_duplicates_intermediate(self):
        """Test intermediate CSV duplicate analysis - URL match ignoring query strings"""
        import tempfile
        import csv
        import os

        test_csv_data = [
            {
                'id': '1',
                'title': 'Python Programming Guide for Beginners',
                'source_url': 'https://example.com/python-guide?utm_source=twitter',
                'author': 'John Doe',
                'notes': '',
                'tags': 'python',
                'created_at': '2024-01-01T10:00:00Z',
                'location': 'new'
            },
            {
                'id': '2',
                'title': 'Totally Different Title Here',
                'source_url': 'https://example.com/python-guide?ref=newsletter#section-2',
                'author': 'Jane Smith',
                'notes': '',
                'tags': '',
                'created_at': '2024-01-02T10:00:00Z',
                'location': 'new'
            },
            {
                'id': '3',
                'title': 'JavaScript Complete Guide',
                'source_url': 'https://example.com/js-guide',
                'author': 'Bob',
                'notes': '',
                'tags': 'js',
                'created_at': '2024-01-03T10:00:00Z',
                'location': 'new'
            },
            {
                'id': '4',
                'title': 'JavaScript Comprehensive Guide',
                'source_url': 'https://different-site.com/js-tutorial',
                'author': 'Alice',
                'notes': '',
                'tags': 'js',
                'created_at': '2024-01-04T10:00:00Z',
                'location': 'new'
            }
        ]

        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=test_csv_data[0].keys())
            writer.writeheader()
            writer.writerows(test_csv_data)
            temp_csv_path = f.name

        try:
            analysis = self.deduplicator.find_csv_duplicates_intermediate(temp_csv_path)

            self.assertEqual(analysis["mode"], "intermediate")
            self.assertEqual(analysis["total_documents"], 4)
            # Doc1+Doc2 share python-guide URL once query/fragment are stripped.
            # Doc3 and Doc4 have different paths (and titles aren't compared), so
            # only one duplicate group is expected.
            self.assertEqual(analysis["duplicate_groups"], 1)
            self.assertEqual(analysis["total_duplicates"], 1)

            group = analysis["groups"][0]
            self.assertEqual(group["count"], 2)
            doc_ids = {doc["data"]["id"] for doc in group["documents"]}
            self.assertEqual(doc_ids, {"1", "2"})
            # Intermediate mode should not emit advanced-only fields.
            self.assertNotIn("match_reason", group)
            self.assertNotIn("example_titles", group)
        finally:
            os.unlink(temp_csv_path)

    def test_intermediate_mode_export_filename_suffix(self):
        """Intermediate analyses get an _intermediate suffix when no path is given"""
        analysis_data = {
            "csv_file": "input.csv",
            "mode": "intermediate",
            "total_documents": 2,
            "duplicate_groups": 1,
            "total_duplicates": 1,
            "groups": [{
                "normalized_url": "example.com/article",
                "documents": [
                    {"row_number": 1, "data": {"id": "1", "title": "T1", "source_url": "https://example.com/article?a=1"}},
                    {"row_number": 2, "data": {"id": "2", "title": "T2", "source_url": "https://example.com/article?b=2"}}
                ],
                "count": 2
            }]
        }

        with patch('builtins.open', create=True), \
             patch('csv.DictWriter') as mock_writer_class:
            mock_writer_class.return_value = Mock()
            filename = self.deduplicator.export_csv_duplicates(analysis_data)

        self.assertIn("_intermediate_", filename)
        # Intermediate exports use the standard fieldnames (no advanced extras).
        fieldnames = mock_writer_class.call_args[1]['fieldnames']
        self.assertNotIn('match_reason', fieldnames)
        self.assertNotIn('example_urls', fieldnames)
        self.assertNotIn('example_titles', fieldnames)


if __name__ == '__main__':
    unittest.main() 