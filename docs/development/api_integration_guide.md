# API Integration Guide

This guide provides comprehensive examples and best practices for integrating with the ReViewPoint Core API.

## Authentication

### JWT Bearer Token (Recommended)

For user-centric applications, use JWT Bearer tokens:

```python
import requests
from datetime import datetime, timedelta

class ReViewPointClient:
    def __init__(self, base_url="https://api.reviewpoint.org"):
        self.base_url = base_url
        self.access_token = None
        self.refresh_token = None
        self.token_expires = None
    
    def login(self, email: str, password: str) -> dict:
        """Login and store tokens"""
        response = requests.post(
            f"{self.base_url}/api/v1/auth/login",
            json={"email": email, "password": password}
        )
        response.raise_for_status()
        
        data = response.json()
        self.access_token = data["access_token"]
        self.refresh_token = data["refresh_token"]
        self.token_expires = datetime.now() + timedelta(seconds=data["expires_in"])
        
        return data
    
    def get_headers(self) -> dict:
        """Get headers with current access token"""
        if not self.access_token:
            raise ValueError("Not authenticated. Call login() first.")
        
        return {"Authorization": f"Bearer {self.access_token}"}
    
    def refresh_access_token(self) -> dict:
        """Refresh access token using refresh token"""
        if not self.refresh_token:
            raise ValueError("No refresh token available")
        
        response = requests.post(
            f"{self.base_url}/api/v1/auth/refresh",
            json={"refresh_token": self.refresh_token}
        )
        response.raise_for_status()
        
        data = response.json()
        self.access_token = data["access_token"]
        self.token_expires = datetime.now() + timedelta(seconds=data["expires_in"])
        
        return data

# Usage
client = ReViewPointClient()
client.login("user@example.com", "password")

# Make authenticated requests
response = requests.get(
    "https://api.reviewpoint.org/api/v1/users/me",
    headers=client.get_headers()
)
```

### API Key Authentication

For server-to-server communication:

```python
import requests

class ReViewPointServiceClient:
    def __init__(self, api_key: str, base_url="https://api.reviewpoint.org"):
        self.api_key = api_key
        self.base_url = base_url
    
    def get_headers(self) -> dict:
        """Get headers with API key"""
        return {
            "X-API-Key": self.api_key,
            "Content-Type": "application/json"
        }
    
    def list_users(self, page: int = 1, size: int = 20) -> dict:
        """List users with pagination"""
        response = requests.get(
            f"{self.base_url}/api/v1/users",
            headers=self.get_headers(),
            params={"page": page, "size": size}
        )
        response.raise_for_status()
        return response.json()

# Usage
service_client = ReViewPointServiceClient("your-api-key")
users = service_client.list_users(page=1, size=50)
```

## File Upload Operations

### Simple File Upload

```python
def upload_file(client: ReViewPointClient, file_path: str, description: str = None) -> dict:
    """Upload a file with optional description"""
    
    with open(file_path, "rb") as file:
        files = {"file": (file_path, file, get_content_type(file_path))}
        data = {}
        
        if description:
            data["description"] = description
        
        response = requests.post(
            f"{client.base_url}/api/v1/uploads",
            files=files,
            data=data,
            headers=client.get_headers()
        )
        response.raise_for_status()
        return response.json()

def get_content_type(file_path: str) -> str:
    """Get content type based on file extension"""
    import mimetypes
    content_type, _ = mimetypes.guess_type(file_path)
    return content_type or "application/octet-stream"

# Usage
file_info = upload_file(client, "research_paper.pdf", "Draft research paper")
print(f"Uploaded file ID: {file_info['id']}")
print(f"Download URL: {file_info['download_url']}")
```

### Bulk File Upload with Progress

```python
import asyncio
import aiohttp
from typing import List, Callable
from pathlib import Path

async def upload_files_bulk(
    client: ReViewPointClient,
    file_paths: List[str],
    progress_callback: Callable[[int, int], None] = None
) -> List[dict]:
    """Upload multiple files asynchronously with progress tracking"""
    
    results = []
    
    async with aiohttp.ClientSession() as session:
        tasks = []
        
        for i, file_path in enumerate(file_paths):
            task = upload_file_async(session, client, file_path)
            tasks.append(task)
        
        for i, task in enumerate(asyncio.as_completed(tasks)):
            result = await task
            results.append(result)
            
            if progress_callback:
                progress_callback(i + 1, len(file_paths))
    
    return results

async def upload_file_async(
    session: aiohttp.ClientSession,
    client: ReViewPointClient,
    file_path: str
) -> dict:
    """Upload a single file asynchronously"""
    
    with open(file_path, "rb") as file:
        data = aiohttp.FormData()
        data.add_field("file", file, filename=Path(file_path).name)
        
        async with session.post(
            f"{client.base_url}/api/v1/uploads",
            data=data,
            headers=client.get_headers()
        ) as response:
            response.raise_for_status()
            return await response.json()

# Usage
async def main():
    file_paths = ["doc1.pdf", "doc2.pdf", "doc3.pdf"]
    
    def show_progress(completed: int, total: int):
        print(f"Progress: {completed}/{total} files uploaded")
    
    results = await upload_files_bulk(client, file_paths, show_progress)
    print(f"Uploaded {len(results)} files successfully")

# Run the async upload
asyncio.run(main())
```

## User Management Operations

### User Registration with Validation

```python
from pydantic import BaseModel, EmailStr, validator
import re

class UserRegistration(BaseModel):
    email: EmailStr
    password: str
    name: str
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain lowercase letter')
        if not re.search(r'[0-9]', v):
            raise ValueError('Password must contain digit')
        return v
    
    @validator('name')
    def validate_name(cls, v):
        if len(v.strip()) < 2:
            raise ValueError('Name must be at least 2 characters')
        return v.strip()

def register_user(client: ReViewPointClient, user_data: UserRegistration) -> dict:
    """Register a new user with validation"""
    
    response = requests.post(
        f"{client.base_url}/api/v1/auth/register",
        json=user_data.dict(),
        headers={"X-API-Key": "your-api-key"}  # Registration requires API key
    )
    
    if response.status_code == 409:
        raise ValueError("Email already registered")
    elif response.status_code == 422:
        errors = response.json()["detail"]
        raise ValueError(f"Validation errors: {errors}")
    
    response.raise_for_status()
    return response.json()

# Usage
try:
    user_data = UserRegistration(
        email="newuser@example.com",
        password="SecurePass123!",
        name="John Doe"
    )
    result = register_user(client, user_data)
    print(f"User registered successfully: {result['user']['id']}")
except ValueError as e:
    print(f"Registration failed: {e}")
```

### User Search and Filtering

```python
def search_users(
    client: ReViewPointClient,
    query: str = None,
    active_only: bool = True,
    admin_only: bool = False,
    page: int = 1,
    size: int = 20
) -> dict:
    """Search users with advanced filtering"""
    
    params = {
        "page": page,
        "size": size
    }
    
    if query:
        params["q"] = query
    if active_only:
        params["active"] = "true"
    if admin_only:
        params["admin"] = "true"
    
    response = requests.get(
        f"{client.base_url}/api/v1/users",
        headers=client.get_headers(),
        params=params
    )
    response.raise_for_status()
    return response.json()

# Usage
# Search for active users with "john" in name or email
results = search_users(client, query="john", active_only=True)
print(f"Found {results['total']} users")

for user in results['users']:
    print(f"- {user['name']} ({user['email']})")
```

## Error Handling and Retry Logic

### Robust Error Handling

```python
import time
import random
from typing import Optional
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

class ReViewPointError(Exception):
    """Base exception for ReViewPoint API errors"""
    def __init__(self, message: str, status_code: Optional[int] = None, response_data: Optional[dict] = None):
        self.message = message
        self.status_code = status_code
        self.response_data = response_data
        super().__init__(message)

class RateLimitError(ReViewPointError):
    """Raised when rate limit is exceeded"""
    pass

class AuthenticationError(ReViewPointError):
    """Raised when authentication fails"""
    pass

class ReViewPointClientRobust(ReViewPointClient):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.session = self._create_session()
    
    def _create_session(self) -> requests.Session:
        """Create session with retry strategy"""
        session = requests.Session()
        
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS", "POST", "PUT", "DELETE"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        return session
    
    def _make_request(self, method: str, url: str, **kwargs) -> requests.Response:
        """Make request with error handling and token refresh"""
        
        # Add authentication headers
        if "headers" not in kwargs:
            kwargs["headers"] = {}
        kwargs["headers"].update(self.get_headers())
        
        try:
            response = self.session.request(method, url, **kwargs)
            
            # Handle specific error cases
            if response.status_code == 401:
                # Try to refresh token and retry once
                try:
                    self.refresh_access_token()
                    kwargs["headers"].update(self.get_headers())
                    response = self.session.request(method, url, **kwargs)
                except Exception:
                    raise AuthenticationError("Authentication failed")
            
            elif response.status_code == 429:
                # Rate limited - extract retry-after header
                retry_after = response.headers.get("Retry-After", "60")
                raise RateLimitError(
                    f"Rate limit exceeded. Retry after {retry_after} seconds",
                    status_code=429,
                    response_data=response.json()
                )
            
            elif 400 <= response.status_code < 500:
                # Client error
                error_data = response.json() if response.content else {}
                raise ReViewPointError(
                    error_data.get("detail", f"Client error: {response.status_code}"),
                    status_code=response.status_code,
                    response_data=error_data
                )
            
            elif response.status_code >= 500:
                # Server error
                raise ReViewPointError(
                    f"Server error: {response.status_code}",
                    status_code=response.status_code
                )
            
            response.raise_for_status()
            return response
            
        except requests.exceptions.RequestException as e:
            raise ReViewPointError(f"Request failed: {str(e)}")
    
    def upload_file_with_retry(self, file_path: str, max_retries: int = 3) -> dict:
        """Upload file with automatic retry on rate limits"""
        
        for attempt in range(max_retries):
            try:
                with open(file_path, "rb") as file:
                    files = {"file": (file_path, file)}
                    response = self._make_request(
                        "POST",
                        f"{self.base_url}/api/v1/uploads",
                        files=files
                    )
                    return response.json()
                    
            except RateLimitError as e:
                if attempt < max_retries - 1:
                    # Wait with exponential backoff + jitter
                    wait_time = (2 ** attempt) + random.uniform(0, 1)
                    print(f"Rate limited. Waiting {wait_time:.1f}s before retry {attempt + 1}")
                    time.sleep(wait_time)
                    continue
                else:
                    raise
            
            except ReViewPointError as e:
                if e.status_code in [500, 502, 503, 504] and attempt < max_retries - 1:
                    # Retry server errors
                    wait_time = (2 ** attempt) + random.uniform(0, 1)
                    print(f"Server error. Retrying in {wait_time:.1f}s")
                    time.sleep(wait_time)
                    continue
                else:
                    raise

# Usage
robust_client = ReViewPointClientRobust()
robust_client.login("user@example.com", "password")

try:
    result = robust_client.upload_file_with_retry("large_file.pdf")
    print(f"Upload successful: {result['id']}")
except RateLimitError as e:
    print(f"Still rate limited after retries: {e.message}")
except AuthenticationError as e:
    print(f"Authentication failed: {e.message}")
except ReViewPointError as e:
    print(f"API error: {e.message} (Status: {e.status_code})")
```

## Pagination and Large Dataset Handling

### Efficient Pagination

```python
from typing import Iterator, Generator

def get_all_users(client: ReViewPointClient, page_size: int = 100) -> Generator[dict, None, None]:
    """Generator that yields all users with automatic pagination"""
    
    page = 1
    
    while True:
        response = requests.get(
            f"{client.base_url}/api/v1/users",
            headers=client.get_headers(),
            params={"page": page, "size": page_size}
        )
        response.raise_for_status()
        
        data = response.json()
        
        # Yield each user
        for user in data.get("users", []):
            yield user
        
        # Check if we have more pages
        if not data.get("has_next", False):
            break
        
        page += 1

def export_all_users_to_csv(client: ReViewPointClient, filename: str):
    """Export all users to CSV efficiently"""
    import csv
    
    with open(filename, "w", newline="", encoding="utf-8") as csvfile:
        writer = None
        
        for user in get_all_users(client):
            if writer is None:
                # Initialize CSV writer with headers from first user
                fieldnames = user.keys()
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
            
            writer.writerow(user)

# Usage
# This will efficiently handle thousands of users without loading all into memory
export_all_users_to_csv(client, "all_users.csv")
```

## WebSocket Integration

### Real-time Notifications

```python
import asyncio
import websockets
import json

class ReViewPointWebSocket:
    def __init__(self, access_token: str, base_url: str = "wss://api.reviewpoint.org"):
        self.access_token = access_token
        self.base_url = base_url
        self.websocket = None
        self.handlers = {}
    
    async def connect(self):
        """Connect to WebSocket with authentication"""
        uri = f"{self.base_url}/api/v1/ws"
        headers = {"Authorization": f"Bearer {self.access_token}"}
        
        self.websocket = await websockets.connect(uri, extra_headers=headers)
        
        # Start listening for messages
        asyncio.create_task(self._listen_for_messages())
    
    async def _listen_for_messages(self):
        """Listen for incoming WebSocket messages"""
        try:
            async for message in self.websocket:
                data = json.loads(message)
                await self._handle_message(data)
        except websockets.exceptions.ConnectionClosed:
            print("WebSocket connection closed")
    
    async def _handle_message(self, data: dict):
        """Handle incoming messages by type"""
        message_type = data.get("type")
        handler = self.handlers.get(message_type)
        
        if handler:
            await handler(data)
        else:
            print(f"No handler for message type: {message_type}")
    
    def on(self, event_type: str):
        """Decorator to register event handlers"""
        def decorator(func):
            self.handlers[event_type] = func
            return func
        return decorator
    
    async def send(self, message_type: str, data: dict):
        """Send message to server"""
        message = {
            "type": message_type,
            "data": data
        }
        await self.websocket.send(json.dumps(message))
    
    async def disconnect(self):
        """Disconnect from WebSocket"""
        if self.websocket:
            await self.websocket.close()

# Usage
async def websocket_example():
    # Assume we have an access token
    ws = ReViewPointWebSocket(access_token="your_jwt_token")
    
    @ws.on("file_uploaded")
    async def handle_file_upload(data):
        print(f"File uploaded: {data['data']['filename']}")
    
    @ws.on("user_registered")
    async def handle_user_registration(data):
        print(f"New user registered: {data['data']['email']}")
    
    @ws.on("notification")
    async def handle_notification(data):
        print(f"Notification: {data['data']['message']}")
    
    await ws.connect()
    
    # Subscribe to specific events
    await ws.send("subscribe", {"events": ["file_uploaded", "user_registered"]})
    
    # Keep connection alive
    try:
        await asyncio.Future()  # Run forever
    except KeyboardInterrupt:
        await ws.disconnect()

# Run WebSocket client
asyncio.run(websocket_example())
```

## Best Practices

### 1. Connection Pooling and Session Management

```python
import requests
from urllib3.util import connection
from urllib3.poolmanager import PoolManager

# Use session for connection pooling
session = requests.Session()
session.mount('https://', requests.adapters.HTTPAdapter(pool_maxsize=20))

# Set reasonable timeouts
session.timeout = (5, 30)  # (connect, read) timeouts
```

### 2. Caching and Rate Limit Management

```python
import time
from functools import wraps
from typing import Dict, Any
import redis

# Simple in-memory cache
_cache: Dict[str, Any] = {}

def cache_response(ttl: int = 300):
    """Cache responses for specified TTL (seconds)"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # Check cache
            if cache_key in _cache:
                cached_data, cached_time = _cache[cache_key]
                if time.time() - cached_time < ttl:
                    return cached_data
            
            # Call function and cache result
            result = func(*args, **kwargs)
            _cache[cache_key] = (result, time.time())
            
            return result
        return wrapper
    return decorator

# Rate limiting with token bucket
class TokenBucket:
    def __init__(self, capacity: int, refill_rate: float):
        self.capacity = capacity
        self.tokens = capacity
        self.refill_rate = refill_rate
        self.last_refill = time.time()
    
    def consume(self, tokens: int = 1) -> bool:
        self._refill()
        
        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        return False
    
    def _refill(self):
        now = time.time()
        tokens_to_add = (now - self.last_refill) * self.refill_rate
        self.tokens = min(self.capacity, self.tokens + tokens_to_add)
        self.last_refill = now

# Usage with client
class RateLimitedClient(ReViewPointClient):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.rate_limiter = TokenBucket(capacity=100, refill_rate=1.0)  # 100 requests, refill 1/sec
    
    @cache_response(ttl=300)
    def get_user_profile(self, user_id: int) -> dict:
        """Get user profile with caching"""
        if not self.rate_limiter.consume():
            raise RateLimitError("Client-side rate limit exceeded")
        
        response = requests.get(
            f"{self.base_url}/api/v1/users/{user_id}",
            headers=self.get_headers()
        )
        response.raise_for_status()
        return response.json()
```

### 3. Configuration Management

```python
import os
from dataclasses import dataclass
from typing import Optional

@dataclass
class APIConfig:
    base_url: str = "https://api.reviewpoint.org"
    api_key: Optional[str] = None
    timeout: int = 30
    max_retries: int = 3
    rate_limit_requests: int = 100
    rate_limit_window: int = 60
    
    @classmethod
    def from_env(cls) -> "APIConfig":
        """Load configuration from environment variables"""
        return cls(
            base_url=os.getenv("REVIEWPOINT_API_URL", cls.base_url),
            api_key=os.getenv("REVIEWPOINT_API_KEY"),
            timeout=int(os.getenv("REVIEWPOINT_TIMEOUT", cls.timeout)),
            max_retries=int(os.getenv("REVIEWPOINT_MAX_RETRIES", cls.max_retries)),
            rate_limit_requests=int(os.getenv("REVIEWPOINT_RATE_LIMIT_REQUESTS", cls.rate_limit_requests)),
            rate_limit_window=int(os.getenv("REVIEWPOINT_RATE_LIMIT_WINDOW", cls.rate_limit_window)),
        )

# Usage
config = APIConfig.from_env()
client = ReViewPointClient(base_url=config.base_url)
```

This integration guide provides comprehensive examples for working with the ReViewPoint Core API, including authentication, file operations, error handling, real-time communication, and best practices for production use.
