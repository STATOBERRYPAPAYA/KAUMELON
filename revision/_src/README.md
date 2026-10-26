# Textbook-only revision sources

The educational content in `agstat/*.html` is selected from the matching chapter of `STATOBERRYPAPAYA/TextbookofAgstat`. Do not add new explanations, datasets, examples, exercises, answers, or general advice to these sheets.

`agstat/book-sources.json` records the textbook commit, chapter checksums, source line ranges and exact Markdown excerpts used. Layout, headings that identify source sections, navigation, branding and watermarks are presentation only.

To refresh from a local textbook checkout:

```
python scripts/sync-revision-from-book.py --book-path /path/to/TextbookofAgstat
python scripts/build-revision.py
node scripts/revision-pdf.cjs
```

The synchronizer reads the book without changing it. It retains the chapter's complete Quick revision section and Important formulae (or Important concepts), selects four existing fill-in-the-blank questions and their matching answer-key entries, and includes a complete short worked example only when one exists in that chapter. It does not generate educational text. Review the source manifest and PDF previews after refreshing.

The Basics poster additionally uses verified excerpts from the main chapter and its original `csv/c1e1.csv` frequency table. `scripts/compose-basics-poster.py` records those exact excerpts and the table checksum in the source manifest. Its flowchart and tables rearrange only those source passages.
