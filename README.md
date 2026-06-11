# Talkdesk API Tools

A Flask-based web application for exploring and managing Talkdesk APIs, with specialized tools for audio prompt administration.

## Features

- **API Explorer** - Interactive UI to explore and execute any Talkdesk API endpoint
- **Prompts Administration** - Full-featured interface for managing Contact Center audio prompts
- **Bulk Upload** - Upload multiple audio files via CLI or web UI

## Quick Start

### Prerequisites

- Python 3.12+
- Talkdesk API credentials (Client ID and Secret)

### Installation

```bash
# Clone the repository
git clone https://github.com/jotatriana/tdfastapi.git
cd tdfastapi

# Create virtual environment
uv venv --python 3.12
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies from the lockfile (recommended)
uv sync

# Or install manually
pip install flask flask-limiter python-dotenv pyyaml requests werkzeug urllib3
```

### Configuration

Create a `.env` file in the project root (see `.env.sample`):

```env
TALKDESK_CLIENT_ID=your_client_id
TALKDESK_CLIENT_SECRET=your_client_secret
TALKDESK_ACCOUNT_NAME=your_account_name
TALKDESK_SCOPES=account:read users:read prompts:read prompts:write

# App authentication (required when accessible beyond localhost)
APP_PASSWORD=choose_a_strong_password
FLASK_SECRET_KEY=random_32_plus_char_string

# Server settings (optional)
FLASK_DEBUG=false
FLASK_HOST=127.0.0.1
FLASK_PORT=5000
```

The `TALKDESK_ACCOUNT_NAME` is your Talkdesk subdomain prefix (e.g., `mycompany` for `mycompany.talkdeskid.com`).

### Running the Application

```bash
python main.py
```

The server starts at `http://localhost:5000`

## Authentication

### App Login

When `APP_PASSWORD` is set in `.env`, all routes are protected by a password login page. Set this whenever the app is reachable beyond your own machine.

- Browser requests redirect to `/login`
- API/AJAX requests return `401` when not authenticated
- `/logout` clears the session

If `APP_PASSWORD` is not set, the login gate is inactive (convenient for local-only use).

### Talkdesk OAuth

The application authenticates to Talkdesk using OAuth2 client credentials:

1. Authenticates against `https://{account_name}.talkdeskid.com/oauth/token`
2. Uses `https://api.talkdeskapp.com` for all API calls
3. Automatically refreshes tokens as needed

## Usage

### Web Interface

| Route | Description |
|-------|-------------|
| `/` | API Explorer — test any Talkdesk API endpoint |
| `/prompts-admin` | Prompts Administration — manage audio prompts |
| `/login` | Login page (active when `APP_PASSWORD` is set) |
| `/logout` | Clear session |

### API Explorer Features

- Auto-discovers all endpoints from OpenAPI specification
- Filter endpoints by tag (category) or search by path/description
- Expandable endpoint cards with parameter inputs
- Execute GET, POST, PATCH, DELETE requests
- View formatted JSON responses
- Supports path parameters and JSON request bodies

### Prompts Administration Features

- Browse all prompts with search and filtering
- Play audio directly in browser
- Upload single or multiple audio files (drag-and-drop supported)
- Download prompts
- Bulk selection and delete operations
- View prompt usage statistics

### Bulk Upload

#### Web UI

1. Navigate to `/prompts-admin`
2. Click **Bulk Upload**
3. Select multiple MP3/WAV files
4. (Optional) Set name prefix/suffix and description
5. Click **Upload All**

#### Command Line

```bash
# Basic usage
python bulk_upload.py /path/to/audio/files

# With options
python bulk_upload.py ./prompts --prefix "IVR_" --description "IVR prompts"

# Preview without uploading
python bulk_upload.py ./prompts --dry-run

# Search subdirectories
python bulk_upload.py ./prompts --recursive
```

**CLI Options:**

| Option | Description |
|--------|-------------|
| `--prefix` | Add prefix to prompt names |
| `--suffix` | Add suffix to prompt names |
| `--description` | Set description for all prompts |
| `--dry-run` | Preview uploads without executing |
| `--recursive`, `-r` | Search subdirectories |
| `--delay` | Delay between uploads in ms (default: 300) |

## Project Structure

```
tdfastapi/
├── main.py                # Flask web application
├── talkdesk_client.py     # Reusable API client classes
├── bulk_upload.py         # CLI bulk upload script
├── openapi.yaml           # Talkdesk OpenAPI specification
├── uv.lock                # Pinned dependency lockfile
├── pyproject.toml         # Project metadata and dependencies
├── .env                   # Environment variables (not in git)
├── .env.sample            # Environment variable template
├── CLAUDE.md              # Development documentation
└── README.md              # This file
```

## REST API Endpoints

### Prompts API

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/prompts` | List prompts with pagination |
| POST | `/api/prompts` | Create new prompt |
| GET | `/api/prompts/{id}` | Get prompt by ID |
| PATCH | `/api/prompts/{id}` | Update prompt metadata |
| DELETE | `/api/prompts/{id}` | Delete prompt |
| POST | `/api/prompts/upload` | Upload audio file (MP3/WAV, max 10 MB) |
| GET | `/api/prompts/{id}/download` | Get download link |
| GET | `/api/prompts/{id}/usage` | Get usage statistics |
| POST | `/api/prompts/bulk` | Bulk operations |

### Token Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/token/status` | Check OAuth token validity |
| POST | `/api/token/refresh` | Force token refresh |

## Security

The application has been hardened against the OWASP Top 10 (2025):

| Control | Detail |
|---------|--------|
| **Authentication** | All routes gated by `APP_PASSWORD` session login; unauthenticated API calls return `401` |
| **Session cookies** | `HttpOnly`, `SameSite=Lax` — inaccessible to JS and blocked from cross-site requests |
| **Rate limiting** | Per-IP limits via `flask-limiter`: `/login` 10/min, `/execute` 60/min, `/api/prompts/upload` 30/min, `/api/token/refresh` 5/min |
| **Upload size** | 10 MB hard limit enforced server-side (`MAX_CONTENT_LENGTH`) |
| **Security headers** | Every response includes `X-Content-Type-Options`, `X-Frame-Options: DENY`, `Referrer-Policy`, and `Content-Security-Policy` |
| **XSS prevention** | All user-controlled strings inserted into `innerHTML` are passed through `escapeHtml()` |
| **Debug mode** | Controlled via `FLASK_DEBUG` env var; defaults to `false` |
| **Dependencies** | Pinned in `uv.lock` for reproducible installs; run `pip-audit` to check for new CVEs |

> **Note:** Set `SESSION_COOKIE_SECURE=True` in `app.config` when serving over HTTPS.

## Development

See [CLAUDE.md](CLAUDE.md) for detailed development documentation.

## License

MIT
