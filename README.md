# Talkdesk API Tools

A Flask-based web application for exploring and managing Talkdesk APIs, with specialized tools for audio prompt administration.

## Features

- **API Explorer** - Interactive UI to explore and execute any Talkdesk API endpoint
- **Prompts Administration** - Full-featured interface for managing Contact Center audio prompts
- **Bulk Upload** - Upload multiple audio files via CLI or web UI

## Quick Start

### Prerequisites

- Python 3.9+
- Talkdesk API credentials (Client ID and Secret)

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd tdfastapi

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install flask python-dotenv pyyaml requests
```

### Configuration

Create a `.env` file in the project root:

```env
TALKDESK_CLIENT_ID=your_client_id
TALKDESK_CLIENT_SECRET=your_client_secret
TALKDESK_SCOPES=account:read users:read prompts:read prompts:write
```

### Running the Application

```bash
python app.py
```

The server starts at `http://localhost:5000`

## Usage

### Web Interface

| Route | Description |
|-------|-------------|
| `/` | API Explorer - Test any Talkdesk API endpoint |
| `/prompts-admin` | Prompts Administration - Manage audio prompts |

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
├── app.py                 # Flask web application
├── talkdesk_client.py     # Reusable API client classes
├── bulk_upload.py         # CLI bulk upload script
├── openapi.yaml           # Talkdesk OpenAPI specification
├── .env                   # Environment variables (not in git)
├── CLAUDE.md              # Development documentation
└── README.md              # This file
```

## API Endpoints

### Prompts API

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/prompts` | List prompts with pagination |
| POST | `/api/prompts` | Create new prompt |
| GET | `/api/prompts/{id}` | Get prompt by ID |
| PATCH | `/api/prompts/{id}` | Update prompt metadata |
| DELETE | `/api/prompts/{id}` | Delete prompt |
| POST | `/api/prompts/upload` | Upload audio file |
| GET | `/api/prompts/{id}/download` | Get download link |
| GET | `/api/prompts/{id}/usage` | Get usage statistics |
| POST | `/api/prompts/bulk` | Bulk operations |

## Authentication

The application uses OAuth2 client credentials grant:

1. Authenticates against `https://my70ypxx.talkdeskid.com/oauth/token`
2. Uses `https://api.talkdeskapp.com` for all API calls
3. Automatically refreshes tokens as needed

## Development

See [CLAUDE.md](CLAUDE.md) for detailed development documentation.

## License

MIT
