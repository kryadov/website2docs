# website2docs

Crawl a website and export its content to PDF, DOCX, or ODT.

This tool visits pages on the same domain as the start URL, extracts readable text and titles using simple heuristics, and assembles the content into a single document.

- Supports output formats: PDF, DOCX, ODT
- Stays within the same domain (ignores external links)
- Normalizes and deduplicates URLs (query strings/fragments ignored by default)
- Simple, dependency‑light crawler (no headless browser)


## Requirements
- Python 3.13+
- Install dependencies:
  - Quick way (all formats):
    - `pip install -r requirements.txt`
  - Or install only what you need (imports are lazy):
    - Crawling: `requests`, `beautifulsoup4`, `lxml` (falls back to Python’s html.parser if lxml not available)
    - DOCX export: `python-docx`
    - ODT export: `odfpy`
    - PDF export: `reportlab`


## Installation
```bash
python -m venv .venv
. .venv\Scripts\activate  # Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
```


## Usage
Basic examples:
```bash
# Export to PDF with explicit output path
python website2docs.py --url https://example.com --format pdf --output example.pdf

# Export to DOCX (format inferred by default when not specified -> DOCX)
python website2docs.py -u https://example.com

# Export to ODT with larger crawl limits
python website2docs.py -u https://example.com -f odt --max-pages 200 --max-depth 3
```

### Confluence Cloud Mode
Download content from Atlassian Confluence Cloud using the REST API. This requires an Email and an API Token (HTTP Basic Auth).
```bash
python website2docs.py \
  --url https://your-domain.atlassian.net/wiki/spaces/SPACE/pages/123456/Page+Title \
  --confluence-email your-email@example.com \
  --confluence-token YOUR_API_TOKEN \
  --format pdf
```
This mode:
- Uses the Confluence REST API v2 instead of HTML scraping.
- Downloads the page and its children recursively (respecting `--max-depth` and `--max-pages`).
- Preserves images by embedding them as data URIs using your credentials.

Behavior notes:
- If `--format` is omitted but `--output` is provided, the format is inferred from the output extension.
- If both `--format` and `--output` are omitted, the format defaults to DOCX and the output file name is derived from the domain: `<domain>.<fmt>` (e.g., `example.com.docx`).

All options:
- `--url, -u` (required): Start URL (e.g., https://example.com)
- `--format, -f {pdf,docx,odt}`: Output format. If omitted, inferred from `--output` extension; otherwise defaults to `docx`.
- `--output, -o`: Output file path. If omitted, a name is derived from the domain and format.
- `--max-pages` (int, default `100`): Maximum pages to crawl (`0` = unlimited).
- `--max-depth` (int, default `2`): Maximum crawl depth (`0` = only the start page).
- `--delay` (float, default `0.0`): Delay between requests in seconds (politeness).
- `--user-agent` (str): User-Agent header. Default: `website2docs/1.0 (+https://github.com/)`.
- `--keep-query` (flag): Do not strip query strings from URLs (may increase duplicates).
- `--timeout` (int, default `15`): HTTP request timeout in seconds.
- `--orientation {portrait, landscape}`: Page orientation for output. Default: `portrait`. 
- `--confluence-email`: Email for Confluence Cloud HTTP Basic Auth.
- `--confluence-token`: API Token for Confluence Cloud HTTP Basic Auth.

Program output includes progress logs, e.g.:
```
[website2docs] Starting crawl: https://example.com
[website2docs] Max pages: 100 | Max depth: 2 | Delay: 0.0s
[website2docs] Fetched N page(s). Writing PDF -> example.pdf
[website2docs] Done: example.pdf
```


## What gets exported
- Each page contributes:
  - Page title (from <title> or first H1/H2 as fallback)
  - Canonical URL
  - Body text and basic rich content (headings, lists, tables, images, and code blocks) extracted from the main content area using simple heuristics
- Non-content elements like scripts, nav/aside/footer/header are ignored. CSS styling is not preserved.

Format specifics:
- DOCX: Headings, paragraphs, lists, code blocks, images, and tables.
- ODT: Headings, paragraphs, lists, code blocks, tables, and images (basic).
- PDF: Headings, paragraphs, lists, code blocks, images, and tables; characters not supported by base PDF fonts are replaced with `?` (Latin‑1 encoding fallback).


## How it works (high level)
- Breadth‑first crawl within the same domain.
- Only follows HTTP(S) links; mailto/tel/javascript links are ignored.
- URLs are normalized (lower‑cased scheme/host, collapsed slashes, trailing slash removal, fragments removed). Query strings are stripped by default unless `--keep-query` is set.
- Only pages with `Content-Type` of `text/html` or `application/xhtml+xml` are considered.


## Limitations & notes
- Not a browser: no JavaScript execution or dynamic rendering.
- robots.txt is not consulted; please crawl responsibly and respect site policies. Use `--delay` if needed.
- CSS styling and attachments are not embedded; images are embedded on a best‑effort basis (SVG support may be limited).
- The text extraction is heuristic and may not perfectly reflect complex layouts.
- Because queries are stripped by default, parameterized pages may be merged/deduplicated; use `--keep-query` to keep them distinct.


## Troubleshooting
- Missing dependency errors (e.g., `reportlab is required for PDF output`): install the suggested package or run `pip install -r requirements.txt`.
- Empty or few pages:
  - Ensure the site serves HTML (some pages may redirect to non‑HTML content).
  - Increase `--max-pages`/`--max-depth`.
  - Some content is generated by JavaScript and won’t be captured.
- Blocked or 403 responses: try a custom `--user-agent`, add a `--delay`, or reduce request rate.
- Garbled characters in PDF: due to base font limitations; consider DOCX/ODT for full Unicode text.


## Development
Single‑file script: `website2docs.py`
Key functions:
- `crawl(start_url, max_depth, max_pages, delay, user_agent, keep_query, timeout)`
- `save_as_docx(...)`, `save_as_odt(...)`, `save_as_pdf(...)`

Run help:
```bash
python website2docs.py --help
```


## License
No license specified. Add your preferred license text here.


## Acknowledgments
Built with:
- requests
- beautifulsoup4 + lxml
- python-docx
- odfpy
- reportlab

Last updated: 2025-08-09
