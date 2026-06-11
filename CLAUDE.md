# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Flask-based web application with two main components:

1. **Talkdesk API Explorer** - Interactive UI to explore and execute any Talkdesk API endpoint
2. **Prompts Administration** - Specialized interface for managing Contact Center audio prompts

The application reads an OpenAPI specification file (`openapi.yaml`) and provides both generic API exploration and domain-specific administration tools.

## Architecture

### Core Components

**Shared Client Module** (`talkdesk_client.py`)
Reusable API client classes that can be imported by both the Flask app and CLI scripts. Uses the stdlib `logging` module — no `print()` calls.

**TalkdeskGenericClient** (`talkdesk_client.py`)
- OpenAPI-driven generic API client
- Handles OAuth2 client credentials authentication against Talkdesk ID server
- Dynamically parses OpenAPI spec to discover available endpoints
- Manages dual base URLs:
  - `https://{account_name}.talkdeskid.com` for authentication (`/oauth/token`) - configured via `TALKDESK_ACCOUNT_NAME` env var
  - `https://api.talkdeskapp.com` for all other API calls
- Supports GET, POST, PATCH, and DELETE methods
- Extracts path parameters from endpoint paths using regex

**PromptsManager** (`talkdesk_client.py`)
- Specialized manager for Talkdesk Prompts API
- Methods for CRUD operations on audio prompts
- Handles upload workflow: request link → upload file → create/update prompt
- Supports bulk operations and usage tracking
- `upload_prompt_file()` method for file-based uploads (used by CLI)

**Flask Web Application** (`main.py`)
- **API Explorer** (`/`) - Generic endpoint testing interface with:
  - Auto-discovery of endpoints from OpenAPI spec
  - Tag-based filtering and path/summary search
  - Expandable endpoint cards with form inputs
  - Path parameter inputs and JSON request body textarea
  - Execute button triggers async fetch to `/execute` endpoint
  - Formatted JSON response display
- **Prompts Admin** (`/prompts-admin`) - Full-featured prompts management UI with:
  - Grid-based prompt library with search and filtering
  - HTML5 audio player for each prompt
  - Single file upload with drag-and-drop
  - **Bulk Upload modal** for uploading multiple files at once
  - Real-time progress indicators
  - Bulk selection and deletion
  - Download functionality

**Bulk Upload CLI** (`bulk_upload.py`)
- Command-line script for batch uploading audio files
- Supports directory scanning with optional recursion
- Configurable name prefix/suffix and description
- Dry-run mode for previewing uploads
- Progress display and error reporting

### Authentication Flow

#### App Login (main.py)

All routes are gated by `_require_login()` via `@app.before_request`. When `APP_PASSWORD` is set:
- Unauthenticated browser requests redirect to `/login`
- Unauthenticated API/AJAX requests return `401 Unauthorized`
- Successful login sets `session['authenticated'] = True`
- Passwords are compared with `hmac.compare_digest()` to prevent timing attacks
- If `APP_PASSWORD` is not set, the gate is inactive (local dev convenience)

#### Talkdesk OAuth (talkdesk_client.py)

The client uses OAuth2 client credentials grant:
1. Base64-encodes `CLIENT_ID:CLIENT_SECRET`
2. POSTs to `https://{account_name}.talkdeskid.com/oauth/token` with Basic auth
3. Caches access token and expiry for subsequent API requests
4. Auto-authenticates (and refreshes when expired) before any API call

### Security Controls

All hardening was done against the OWASP Top 10 (2025). Key implementation details:

- **Session cookies**: `SESSION_COOKIE_HTTPONLY = True`, `SESSION_COOKIE_SAMESITE = 'Lax'` — set in `main.py` app config. Add `SESSION_COOKIE_SECURE = True` when serving over HTTPS.
- **Rate limiting**: `flask-limiter` with in-memory storage; limits applied per-IP via `get_remote_address`. Decorated directly on route functions — `/login` (10/min), `/execute` (60/min), `/api/prompts/upload` (30/min), `/api/token/refresh` (5/min).
- **Upload size**: `MAX_CONTENT_LENGTH = 10 * 1024 * 1024` enforced server-side; Flask returns `413` automatically.
- **Security headers**: `@app.after_request` hook in `main.py` sets `X-Content-Type-Options`, `X-Frame-Options: DENY`, `Referrer-Policy`, and `Content-Security-Policy` on every response.
- **XSS prevention**: All user-controlled values inserted into `innerHTML` are wrapped with the `escapeHtml()` JS helper defined in each page.
- **Debug mode**: Controlled via `FLASK_DEBUG` env var (defaults `false`). Never hardcode `debug=True`.

### Important Implementation Details

- **Dual URL Handling**: The app distinguishes between auth server (`talkdeskid.com`) and API server (`talkdeskapp.com`). See `execute_request()` method in `talkdesk_client.py` for base URL selection logic.
- **Path Parameter Substitution**: Frontend JavaScript replaces `{param}` placeholders with user input before sending to backend.
- **OpenAPI Dependency**: The app reads `openapi.yaml` in the project root containing the Talkdesk API OpenAPI specification.
- **Shared Module**: API client classes are in `talkdesk_client.py` for reuse by both web app and CLI tools.
- **Logging**: Use `logging.getLogger(__name__)` in any new module. Never use `print()` for diagnostics. Access-control denials are logged at `WARNING` with IP, method, and path.

### UI/CSS Implementation Notes

The application uses a custom design system with CSS variables for theming. Key CSS considerations:

- **Z-index Layering**: Cards use `::before` pseudo-elements for hover effects. Interactive content (forms, buttons, audio players) must have `position: relative` and `z-index: 2` or higher to remain clickable above these overlays.
- **Async Form Handlers**: Form `onsubmit` handlers use `async` functions. Always use `onsubmit="asyncFunction(event); return false;"` pattern since returning a Promise (truthy) won't prevent form submission.
- **Modal System**: Modals use `.modal.active` class toggle for visibility with `z-index: 1050`.
- **Dark Theme**: Uses ocean/teal gradient theme with CSS custom properties (`--gradient-color-*`, `--color-*`).

## Environment Setup

### Environment Variables

Set these in a `.env` file (already gitignored):

**Talkdesk credentials (required)**
- `TALKDESK_CLIENT_ID` - Your Talkdesk OAuth client ID
- `TALKDESK_CLIENT_SECRET` - Your Talkdesk OAuth client secret
- `TALKDESK_ACCOUNT_NAME` - Your Talkdesk account name (subdomain prefix, e.g., `mycompany` for `mycompany.talkdeskid.com`)
- `TALKDESK_SCOPES` - OAuth scopes (default: `account:read users:read`)

**App security (required when accessible beyond localhost)**
- `APP_PASSWORD` - Password protecting all routes via the login page
- `FLASK_SECRET_KEY` - Random 32+ character string used to sign session cookies

**Server settings (optional)**
- `FLASK_DEBUG` - Set to `true` to enable the Werkzeug debugger (default: `false`)
- `FLASK_HOST` - Bind address (default: `127.0.0.1`)
- `FLASK_PORT` - Port (default: `5000`)

### Python Version

This project uses Python 3.12 (see `.python-version`).

## Development Commands

### Setting Up the Virtual Environment

```bash
uv venv --python 3.12
source .venv/bin/activate
```

### Installing Dependencies

```bash
pip install flask flask-limiter python-dotenv pyyaml requests werkzeug urllib3
```

Or use the lockfile for a reproducible install:
```bash
uv sync
```

Required dependencies (see `pyproject.toml` for pinned versions):
- `flask` — web framework
- `flask-limiter` — per-IP rate limiting
- `python-dotenv` — `.env` file loading
- `pyyaml` — OpenAPI spec parsing
- `requests` — outbound HTTP to Talkdesk API
- `werkzeug` — WSGI utilities (Flask dependency, pinned for CVE fixes)
- `urllib3` — HTTP transport (transitive, pinned for CVE fixes)

### Checking for Vulnerabilities

```bash
pip install pip-audit
pip-audit
```

### Running the Application

```bash
source .venv/bin/activate
python main.py
```

The Flask development server will start on `http://localhost:5000`.

## Application Routes

### Authentication
- `GET /login` - Login page (shown when `APP_PASSWORD` is set)
- `POST /login` - Submit password (rate-limited: 10/min per IP)
- `GET /logout` - Clear session and redirect to login

### API Explorer
- `GET /` - Main UI displaying all discovered API endpoints from OpenAPI spec
- `POST /execute` - Backend proxy that executes API requests with authentication (rate-limited: 60/min)

### Prompts Administration
- `GET /prompts-admin` - Prompts management interface with upload, playback, and bulk operations
- `GET /api/prompts` - List prompts with pagination and search
- `POST /api/prompts` - Create new prompt
- `GET /api/prompts/{id}` - Get prompt by ID
- `PATCH /api/prompts/{id}` - Update prompt metadata
- `DELETE /api/prompts/{id}` - Delete prompt
- `POST /api/prompts/upload` - Upload audio file (MP3/WAV, max 10 MB server-enforced; rate-limited: 30/min)
- `GET /api/prompts/{id}/download` - Get download link
- `GET /api/prompts/{id}/usage` - Get usage statistics
- `GET /api/prompts/{id}/flows` - Get associated Studio flows
- `POST /api/prompts/bulk` - Bulk operations (delete, update)

### Token Management
- `GET /api/token/status` - Check OAuth token validity and time remaining
- `POST /api/token/refresh` - Force token refresh (rate-limited: 5/min)

## Logging

The application uses Python's stdlib `logging` module throughout. Log levels:

| Level | Examples |
|-------|---------|
| `DEBUG` | Outbound request URLs, token refresh triggers |
| `INFO` | Successful authentication |
| `WARNING` | Auth failures, access-control denials (includes IP + path) |
| `ERROR` | Network errors, exceptions |

`logging.basicConfig` is called at startup in `main.py` with `level=INFO` and a timestamp format. To see `DEBUG` logs set `level=logging.DEBUG` there, or set `FLASK_DEBUG=true`.

## Bulk Upload

### CLI Usage

The `bulk_upload.py` script uploads multiple audio files from a directory:

```bash
# Basic usage - upload all MP3/WAV files from a directory
python bulk_upload.py /path/to/audio/files

# Add prefix to prompt names
python bulk_upload.py /path/to/audio/files --prefix "IVR_"

# Add description to all prompts
python bulk_upload.py /path/to/audio/files --description "Auto-uploaded prompts"

# Preview without uploading (dry run)
python bulk_upload.py /path/to/audio/files --dry-run

# Search subdirectories for audio files
python bulk_upload.py /path/to/audio/files --recursive

# Full example with all options
python bulk_upload.py ./prompts --prefix "IVR_" --suffix "_v2" --description "IVR prompts" --delay 500
```

**CLI Options:**
- `--prefix` - Add prefix to prompt names
- `--suffix` - Add suffix to prompt names
- `--description` - Set description for all prompts
- `--dry-run` - Show what would be uploaded without actually uploading
- `--recursive`, `-r` - Search subdirectories for audio files
- `--delay` - Delay between uploads in ms (default: 300)

### Web UI Bulk Upload

1. Navigate to `/prompts-admin`
2. Click "Bulk Upload" button
3. Select multiple MP3/WAV files (or drag-and-drop)
4. Optionally set name prefix/suffix and description
5. Click "Upload All"
6. Monitor progress in real-time log
