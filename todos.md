## Features that are needed to be implemented
 - [x] Testings initial
 ~~ - [x] Deduplication on Readwise ~~
    ~~ - [x] Not only by title, but also checks metadata to determine which is more "accurate", "correct" ~~
    - [x] Smart URL normalization (removes tracking parameters)
    ~~ - [x] Title similarity detection using sequence matching ~~
    ~~ - [x] Metadata quality scoring system (title, author, summary, tags, etc.) ~~
    ~~ - [x] CLI integration with analysis and execution modes ~~
    ~~ - [x] Comprehensive test coverage ~~
 - [x] Auto save output into CSV
    - List from Readwise
    - Execution results
 - [x] Deduplication method: should based on the list result of CSV
    - [x] Compare the source_url without http/https
    - [x] Save duplicate list into CSV
 - [ ] WebUI