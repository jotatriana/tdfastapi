"""
Talkdesk API Client Module

This module provides reusable API client classes for interacting with the Talkdesk API.
It can be used by both the Flask web application and CLI scripts.
"""

import os
import yaml
import requests
import base64
import re
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def extract_hal_link(data, link_name):
    """
    Extract a URL from HAL-formatted API response.

    HAL links can be either a dict with 'href' key, a string URL, or a fallback 'url' key.
    """
    links = data.get('_links', {})
    link = links.get(link_name, {})

    if isinstance(link, dict):
        return link.get('href')
    if isinstance(link, str):
        return link
    return data.get('url')


# --- CONFIGURATION ---
CLIENT_ID = os.getenv('TALKDESK_CLIENT_ID', 'YOUR_CLIENT_ID')
CLIENT_SECRET = os.getenv('TALKDESK_CLIENT_SECRET', 'YOUR_CLIENT_SECRET')
SCOPES = os.getenv('TALKDESK_SCOPES', 'account:read users:read')
ACCOUNT_NAME = os.getenv('TALKDESK_ACCOUNT_NAME', 'your-account-name')
AUTH_HOST = f"https://{ACCOUNT_NAME}.talkdeskid.com"


class TalkdeskGenericClient:
    """Generic API client for Talkdesk that supports any endpoint defined in the OpenAPI spec."""

    def __init__(self, openapi_path='openapi.yaml'):
        self.openapi_path = openapi_path
        self.spec = self._load_spec()
        self.base_url = self._get_base_url()
        self.token = None
        self.token_expires_at = None
        self.token_obtained_at = None

    def _load_spec(self):
        try:
            with open(self.openapi_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"Error loading YAML: {e}")
            return {}

    def _get_base_url(self):
        """
        Returns the Base URL for API calls.
        Forces the standard Talkdesk API URL to avoid 'Invalid URL' errors.
        """
        return "https://api.talkdeskapp.com"

    def authenticate(self):
        """Authenticate using OAuth2 client credentials grant."""
        auth_path = "/oauth/token"
        auth_url = f"{AUTH_HOST.rstrip('/')}{auth_path}"

        credentials = f"{CLIENT_ID}:{CLIENT_SECRET}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()

        headers = {
            'Authorization': f'Basic {encoded_credentials}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        data = {
            'grant_type': 'client_credentials',
            'scope': SCOPES
        }

        print(f"Authenticating against: {auth_url}")
        print(f"headers: {headers}")
        try:
            response = requests.post(auth_url, headers=headers, data=data)

            if response.status_code != 200:
                print(f"Auth Failed: {response.status_code}")
                print(f"Response: {response.text}")
                return False

            token_data = response.json()
            self.token = token_data.get('access_token')
            self.token_obtained_at = time.time()
            # expires_in is typically in seconds, default to 3600 (1 hour) if not provided
            expires_in = token_data.get('expires_in', 3600)
            self.token_expires_at = self.token_obtained_at + expires_in
            print(f"Authentication Successful! Token expires in {expires_in} seconds")
            return True

        except Exception as e:
            print(f"Auth Error: {e}")
            return False

    def is_token_valid(self):
        """Check if the current token exists and is not expired."""
        if not self.token or not self.token_expires_at:
            return False
        # Add 60 second buffer to refresh before actual expiration
        return time.time() < (self.token_expires_at - 60)

    def get_token_status(self):
        """Get detailed token status information."""
        if not self.token:
            return {
                'valid': False,
                'has_token': False,
                'message': 'No token available'
            }

        current_time = time.time()
        if not self.token_expires_at:
            return {
                'valid': False,
                'has_token': True,
                'message': 'Token exists but expiration time unknown'
            }

        time_remaining = self.token_expires_at - current_time
        is_valid = time_remaining > 60  # 60 second buffer

        return {
            'valid': is_valid,
            'has_token': True,
            'obtained_at': self.token_obtained_at,
            'expires_at': self.token_expires_at,
            'time_remaining_seconds': max(0, int(time_remaining)),
            'message': 'Token is valid' if is_valid else 'Token expired or expiring soon'
        }

    def refresh_token(self):
        """Force refresh the authentication token."""
        self.token = None
        self.token_expires_at = None
        self.token_obtained_at = None
        return self.authenticate()

    def get_tags(self):
        """Extract all unique tags from the OpenAPI spec."""
        tags = set()
        paths = self.spec.get('paths', {})

        for path, methods in paths.items():
            for method in ['get', 'post']:
                if method in methods:
                    details = methods[method]
                    endpoint_tags = details.get('tags', [])
                    tags.update(endpoint_tags)

        return sorted(list(tags))

    def get_endpoints(self):
        """Scans spec for GET and POST, extracting path params and tags."""
        endpoints = []
        paths = self.spec.get('paths', {})

        for path, methods in paths.items():
            path_params = re.findall(r'\{([^\}]+)\}', path)

            for method in ['get', 'post']:
                if method in methods:
                    details = methods[method]
                    endpoint_info = {
                        'method': method.upper(),
                        'path': path,
                        'params': path_params,
                        'summary': details.get('summary', details.get('description', 'No summary')),
                        'has_body': method == 'post',
                        'tags': details.get('tags', [])
                    }
                    endpoints.append(endpoint_info)
        return endpoints

    def execute_request(self, method, path, body=None):
        """Execute an API request with automatic authentication."""
        if '/oauth/token' not in path:
            if not self.is_token_valid():
                print("Token missing or expired, re-authenticating...")
                if not self.authenticate():
                    return {'error': 'Authentication failed'}

        # Dynamic Base URL Selection
        current_base = "https://api.talkdeskapp.com"
        if '/oauth/token' in path:
            current_base = AUTH_HOST

        base = current_base.rstrip('/')
        endpoint = path.lstrip('/')
        url = f"{base}/{endpoint}"

        print(f"Executing {method} request to: {url}")

        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

        if '/oauth/token' not in path:
            headers['Authorization'] = f'Bearer {self.token}'

        try:
            if method == 'GET':
                response = requests.get(url, headers=headers)
            elif method == 'POST':
                response = requests.post(url, headers=headers, json=body)
            elif method == 'PATCH':
                response = requests.patch(url, headers=headers, json=body)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers)
            else:
                return {'error': 'Method not supported'}

            try:
                data = response.json()
            except:
                data = response.text

            return {
                'status': response.status_code,
                'url': url,
                'data': data
            }
        except Exception as e:
            print(f"Request Error: {e}")
            return {'error': str(e)}


class PromptsManager:
    """Specialized manager for Talkdesk Prompts API operations."""

    def __init__(self, api_client):
        self.client = api_client

    def list_prompts(self, page=1, per_page=50, search=None):
        """List all prompts with optional pagination and search."""
        params = f"?page={page}&per_page={per_page}"
        if search:
            params += f"&q={search}"
        return self.client.execute_request('GET', f'/prompts{params}')

    def get_prompt(self, prompt_id):
        """Get a specific prompt by ID."""
        return self.client.execute_request('GET', f'/prompts/{prompt_id}')

    def create_prompt(self, name, description=None, request_id=None, file_name=None):
        """Create a new prompt."""
        body = {'name': name}
        if description:
            body['description'] = description
        if request_id:
            body['request_id'] = request_id
        if file_name:
            body['file_name'] = file_name
        return self.client.execute_request('POST', '/prompts', body=body)

    def update_prompt(self, prompt_id, name=None, description=None):
        """Update prompt metadata."""
        body = {}
        if name:
            body['name'] = name
        if description:
            body['description'] = description
        return self.client.execute_request('PATCH', f'/prompts/{prompt_id}', body=body)

    def delete_prompt(self, prompt_id):
        """Delete a prompt."""
        return self.client.execute_request('DELETE', f'/prompts/{prompt_id}')

    def get_download_link(self, prompt_id):
        """Generate a download link for a prompt."""
        return self.client.execute_request('GET', f'/prompts/{prompt_id}/download-link')

    def request_upload_link(self, content_type='audio/mpeg'):
        """Request an upload link for a new audio file."""
        allowed_types = ['audio/wav'] if content_type == 'audio/wav' else ['audio/mp3', 'audio/mpeg']
        body = {'validation_constraints': {'allowed_mime_types': allowed_types}}
        return self.client.execute_request('POST', '/prompts-requests', body=body)

    def get_prompt_usage(self, prompt_ids):
        """Get usage statistics for prompts."""
        if isinstance(prompt_ids, list):
            ids_param = '&'.join([f'id={pid}' for pid in prompt_ids])
        else:
            ids_param = f'id={prompt_ids}'
        return self.client.execute_request('GET', f'/prompts-usage?{ids_param}')

    def get_prompt_flows(self, prompt_id, page=1, per_page=50):
        """Get list of flows using a specific prompt."""
        return self.client.execute_request('GET', f'/prompts/{prompt_id}/flows?page={page}&per_page={per_page}')

    def bulk_operation(self, operation, requests_list):
        """Perform bulk operations on prompts."""
        body = {
            'operation': operation,
            'requests': requests_list
        }
        return self.client.execute_request('POST', '/prompts/bulk', body=body)

    def upload_prompt_file(self, file_path, name, description=None):
        """
        Upload a prompt file from disk.

        Args:
            file_path: Path to the audio file (MP3 or WAV)
            name: Name for the prompt
            description: Optional description

        Returns:
            dict with success status and result or error
        """
        if not os.path.exists(file_path):
            return {'success': False, 'error': f'File not found: {file_path}'}

        file_ext = os.path.splitext(file_path)[1].lower()
        if file_ext not in ['.mp3', '.wav']:
            return {'success': False, 'error': 'Only MP3 and WAV files are allowed'}

        content_type = 'audio/mpeg' if file_ext == '.mp3' else 'audio/wav'

        try:
            # Step 1: Request upload link
            upload_link_result = self.request_upload_link(content_type)

            if upload_link_result.get('status') not in [200, 201]:
                return {'success': False, 'error': 'Failed to get upload link', 'details': upload_link_result}

            upload_data = upload_link_result.get('data', {})
            upload_url = extract_hal_link(upload_data, 'upload_link')

            if not upload_url:
                return {'success': False, 'error': 'No upload URL received', 'response': upload_data}

            # Step 2: Upload file to signed URL
            with open(file_path, 'rb') as f:
                file_content = f.read()

            upload_response = requests.put(
                upload_url,
                data=file_content,
                headers={'Content-Type': content_type}
            )

            if upload_response.status_code not in [200, 201, 204]:
                return {'success': False, 'error': 'File upload failed', 'status': upload_response.status_code}

            # Step 3: Create prompt with the request_id
            result = self.create_prompt(
                name=name,
                description=description,
                request_id=upload_data.get('id'),
                file_name=os.path.basename(file_path)
            )

            if result.get('status') in [200, 201]:
                return {'success': True, 'result': result}
            return {'success': False, 'error': 'Failed to create prompt', 'details': result}

        except Exception as e:
            return {'success': False, 'error': str(e)}
