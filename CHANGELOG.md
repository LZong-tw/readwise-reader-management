# Changelog

All notable changes to this project are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- `analyze-csv-duplicates` gains a new `--mode {standard,intermediate,advanced}` flag.
  - `intermediate` groups documents whose `source_url` is identical after stripping
    the protocol, query string, fragment, and trailing slash. Title similarity is
    NOT considered, so similar titles on different URL paths stay separate.
  - Resolves [#8](https://github.com/LZong-tw/readwise-reader-management/issues/8) — provides a middle ground
    between the standard mode (URL lowercased + scheme/trailing-slash stripped)
    and the advanced mode (URL + title similarity).
- `DocumentDeduplicator.find_csv_duplicates_intermediate()` powering the new mode.
- Auto-generated export filenames now carry an `_intermediate_` suffix when the
  intermediate analyzer was used.

### Changed
- `--advanced` is preserved as a backward-compatible alias for `--mode advanced`.
  Specifying `--mode` explicitly always wins over `--advanced`.
- `cli.main()` now delegates parser construction to `cli.build_parser()` so the
  argparse surface can be exercised in tests without invoking the full CLI flow.
- The `match_reason` field exported by advanced-mode analyses (in CSV via
  `export_csv_duplicates` and JSON via `export_analysis_report`) is now a
  **category aggregate** with bounded cardinality (at most three components),
  emitted in a fixed order (URL-only first, then URL+title, then title-only)
  and joined with ` | `. Each rule category appears at most once per group
  regardless of how many edges contributed to it. Components draw from:
    - `Same URL (no query)` — URL match only (new value, previously unreachable)
    - `Same URL (no query) + title similarity: <pct>` or `…: <min%>–<max%>` — URL match plus a title match
    - `Title similarity: <pct>` or `Title similarity: <min%>–<max%>` — title match only
  When a category is fed by more than one edge, the title-similarity percentage
  is collapsed to a min–max range; otherwise a single percentage is shown.
  If both endpoints round identically at one decimal place, the range collapses
  to a single percentage so consumers never see a degenerate `X%–X%` form.
  Downstream tools that string-match `match_reason` should split on ` | ` and
  inspect each component. The rule-text source of truth is
  `document_deduplicator.ADVANCED_RULE_SENTENCE`.

### Fixed
- `find_csv_duplicates_advanced` Rule 2 ("same normalized URL") is now reachable.
  Previously the rule additionally required `title similarity > 50%`, which made
  it strictly subsumed by Rule 1 — meaning advanced mode never grouped pairs
  that shared a URL but had divergent titles. Rule 2 now triggers on URL match
  alone, matching the documented behavior.
- `find_csv_duplicates_advanced` no longer drops `match_reason` for groups whose
  matching pair was found early in the inner scan. The variable was being reset
  on every inner-loop iteration and the value stored on the group was whatever
  the last (often non-matching) iteration left behind — typically an empty
  string. Reasons are now collected across every duplicate edge and aggregated
  on the group (see the `Changed` entry above).
