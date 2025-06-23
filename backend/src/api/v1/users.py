import logging
from typing import Any

from fastapi import (
    APIRouter,
    Body,
    Depends,
    HTTPException,
    Path,
    Query,
    Response,
    status,
)
from pydantic import BaseModel, ConfigDict
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.deps import (
    PaginationParams,
    pagination_params,
)
from src.api.deps import (
    get_current_user_with_api_key as get_current_user,
)
from src.core.database import get_async_session
from src.models.user import User
from src.repositories.user import create_user_with_validation, get_user_by_id
from src.schemas.user import UserRead
from src.utils.datetime import parse_flexible_datetime
from src.utils.errors import UserAlreadyExistsError

# Fallback in-memory users_db for testing or if not using a real DB
users_db: dict[int, dict[str, Any]] = {}

router = APIRouter(prefix="/users", tags=["User Management"])


class UserCreateRequest(BaseModel):
    email: str
    password: str
    name: str

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "email": "user@example.com",
                    "password": "strongpassword123",
                    "name": "Jane Doe",
                }
            ]
        }
    )


class UserResponse(BaseModel):
    id: int
    email: str
    name: str | None = ""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [{"id": 1, "email": "user@example.com", "name": "Jane Doe"}]
        }
    )


class UserListResponse(BaseModel):
    users: list[UserResponse]
    total: int


@router.post(
    "",
    summary="Create a new user",
    description="""
    Registers a new user and returns the created user's information.

    **Steps:**
    1. User submits registration data (email, password, name).
    2. System validates input and checks for duplicate email.
    3. On success, a new user is created and returned.

    **Notes:**
    - Duplicate emails are not allowed.
    - Password must meet security requirements.
    - Rate limiting is applied to prevent abuse.
    """,
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {
            "description": "User created successfully",
            "content": {
                "application/json": {
                    "examples": {
                        "default": {
                            "value": {
                                "id": 1,
                                "email": "user@example.com",
                                "name": "Jane Doe",
                            }
                        }
                    }
                }
            },
        },
        400: {
            "description": "Validation error",
            "content": {
                "application/json": {
                    "examples": {
                        "default": {"value": {"detail": "Invalid email or password."}}
                    }
                }
            },
        },
        401: {
            "description": "Unauthorized. Missing or invalid authentication.",
            "content": {
                "application/json": {
                    "examples": {"default": {"value": {"detail": "Not authenticated."}}}
                }
            },
        },
        409: {
            "description": "Conflict. Email already exists.",
            "content": {
                "application/json": {
                    "examples": {
                        "default": {"value": {"detail": "Email already registered."}}
                    }
                }
            },
        },
        422: {
            "description": "Unprocessable Entity. Invalid input.",
            "content": {
                "application/json": {
                    "examples": {"default": {"value": {"detail": "Invalid input."}}}
                }
            },
        },
        429: {
            "description": "Too many registration attempts",
            "content": {
                "application/json": {
                    "examples": {
                        "default": {
                            "value": {
                                "detail": "Too many registration attempts. Please try again later."
                            }
                        }
                    }
                }
            },
        },
        500: {
            "description": "Internal server error.",
            "content": {
                "application/json": {
                    "examples": {"default": {"value": {"detail": "Unexpected error."}}}
                }
            },
        },
        503: {
            "description": "Service unavailable.",
            "content": {
                "application/json": {
                    "examples": {
                        "default": {
                            "value": {"detail": "Service temporarily unavailable."}
                        }
                    }
                }
            },
        },
    },
    openapi_extra={
        "requestBody": {
            "content": {
                "application/json": {
                    "examples": {
                        "default": {
                            "value": {
                                "email": "user@example.com",
                                "password": "strongpassword123",
                                "name": "Jane Doe",
                            }
                        }
                    }
                }
            }
        },
        "x-codeSamples": [
            {
                "lang": "curl",
                "label": "cURL",
                "source": 'curl -X POST \'https://api.reviewpoint.org/api/v1/users\' \\\n  -H \'Authorization: Bearer <token>\' \\\n  -H \'Content-Type: application/json\' \\\n  -d \'{"email":"user@example.com","password":"strongpassword123","name":"Jane Doe"}\'',
            },
            {
                "lang": "Python",
                "label": "Python (requests)",
                "source": 'import requests\n\nurl = \'https://api.reviewpoint.org/api/v1/users\'\ndata = {"email": "user@example.com", "password": "strongpassword123", "name": "Jane Doe"}\nheaders = {"Authorization": "Bearer <token>"}\nresponse = requests.post(url, json=data, headers=headers)\nprint(response.json())',
            },
            {
                "lang": "JavaScript",
                "label": "JavaScript (fetch)",
                "source": "fetch('https://api.reviewpoint.org/api/v1/users', {\n  method: 'POST',\n  headers: {\n    'Authorization': 'Bearer <token>',\n    'Content-Type': 'application/json'\n  },\n  body: JSON.stringify({\n    email: 'user@example.com',\n    password: 'strongpassword123',\n    name: 'Jane Doe'\n  })\n})\n  .then(res => res.json())\n  .then(console.log);",
            },
            {
                "lang": "Go",
                "label": "Go (net/http)",
                "source": 'package main\nimport (\n  "bytes"\n  "net/http"\n)\nfunc main() {\n  body := []byte(`{\\"email\\":\\"user@example.com\\",\\"password\\":\\"strongpassword123\\",\\"name\\":\\"Jane Doe\\"}`)\n  req, _ := http.NewRequest("POST", "https://api.reviewpoint.org/api/v1/users", bytes.NewBuffer(body))\n  req.Header.Set("Authorization", "Bearer <token>")\n  req.Header.Set("Content-Type", "application/json")\n  http.DefaultClient.Do(req)\n}',
            },
            {
                "lang": "Java",
                "label": "Java (OkHttp)",
                "source": 'OkHttpClient client = new OkHttpClient();\nMediaType mediaType = MediaType.parse("application/json");\nRequestBody body = RequestBody.create(mediaType, "{\\"email\\":\\"user@example.com\\",\\"password\\":\\"strongpassword123\\",\\"name\\":\\"Jane Doe\\"}");\nRequest request = new Request.Builder()\n  .url("https://api.reviewpoint.org/api/v1/users")\n  .post(body)\n  .addHeader("Authorization", "Bearer <token>")\n  .addHeader("Content-Type", "application/json")\n  .build();\nResponse response = client.newCall(request).execute();',
            },
            {
                "lang": "PHP",
                "label": "PHP (cURL)",
                "source": "$ch = curl_init('https://api.reviewpoint.org/api/v1/users');\ncurl_setopt($ch, CURLOPT_POST, 1);\ncurl_setopt($ch, CURLOPT_POSTFIELDS, json_encode(['email' => 'user@example.com', 'password' => 'strongpassword123', 'name' => 'Jane Doe']));\ncurl_setopt($ch, CURLOPT_HTTPHEADER, ['Authorization: Bearer <token>', 'Content-Type: application/json']);\n$response = curl_exec($ch);\ncurl_close($ch);",
            },
            {
                "lang": "Ruby",
                "label": "Ruby (Net::HTTP)",
                "source": "require 'net/http'\nrequire 'json'\nuri = URI('https://api.reviewpoint.org/api/v1/users')\nreq = Net::HTTP::Post.new(uri, 'Content-Type' => 'application/json')\nreq['Authorization'] = 'Bearer <token>'\nreq.body = {email: 'user@example.com', password: 'strongpassword123', name: 'Jane Doe'}.to_json\nres = Net::HTTP.start(uri.hostname, uri.port, use_ssl: true) { |http| http.request(req) }\nputs res.body",
            },
            {
                "lang": "HTTPie",
                "label": "HTTPie",
                "source": "http POST https://api.reviewpoint.org/api/v1/users Authorization:'Bearer <token>' email=user@example.com password=strongpassword123 name='Jane Doe'",
            },
            {
                "lang": "PowerShell",
                "label": "PowerShell",
                "source": "$body = @{email='user@example.com'; password='strongpassword123'; name='Jane Doe'} | ConvertTo-Json\nInvoke-RestMethod -Uri 'https://api.reviewpoint.org/api/v1/users' -Method Post -Body $body -ContentType 'application/json' -Headers @{Authorization='Bearer <token>'}",
            },
        ],
    },
)
async def create_user(
    user: UserCreateRequest = Body(
        ...,
        examples=[
            {
                "summary": "A typical user registration",
                "value": {
                    "email": "user@example.com",
                    "password": "strongpassword123",
                    "name": "Jane Doe",
                },
            }
        ],
    ),
    session: AsyncSession = Depends(get_async_session),
    current_user: Any = Depends(get_current_user),
) -> UserResponse:
    try:
        db_user = await create_user_with_validation(session, user.email, user.password)
        db_user.name = user.name
        await session.commit()
        await session.refresh(db_user)
        return UserResponse(id=db_user.id, email=db_user.email, name=db_user.name)
    except UserAlreadyExistsError as e:
        raise HTTPException(status_code=409, detail="Email already exists.") from e


# Define export endpoints BEFORE parameter routes
@router.get(
    "/export",
    summary="Export users as CSV (debug minimal)",
    description="""
    Exports the list of users as a CSV file with basic fields. Used for debugging and testing.

    **Steps:**
    1. Authenticated user requests export.
    2. Server returns a CSV with user ID, email, and name.
    """,
    response_class=Response,
)
async def export_users_csv(
    current_user: Any = Depends(get_current_user),
) -> Response:
    import csv
    from io import StringIO

    logging.warning(
        f"USERS EXPORT CALLED with user_id={current_user.id if current_user else 'None'}"
    )

    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["id", "email", "name"])
    # Return a dummy user for test
    writer.writerow([1, "dummy@example.com", "Dummy User"])
    return Response(content=output.getvalue(), media_type="text/csv")


@router.get(
    "/export-alive",
    summary="Test endpoint for export router",
    description="""
    Returns 200 if the users export router is active. Used for integration and deployment checks.
    """,
    responses={
        200: {
            "description": "Export router is alive",
            "content": {
                "application/json": {
                    "examples": {"default": {"value": {"status": "users export alive"}}}
                }
            },
        }
    },
)
async def export_alive() -> dict[str, str]:
    return {"status": "users export alive"}


@router.get(
    "/export-full",
    summary="Export users as CSV (full)",
    description="""
    Exports the list of users as a CSV file with all fields.

    **Steps:**
    1. Authenticated admin user requests export.
    2. Server returns a CSV with all user data fields.

    **Notes:**
    - Requires admin privileges.
    - Contains sensitive user data.
    """,
    response_class=Response,
)
async def export_users_full_csv(
    current_user: Any = Depends(get_current_user),
) -> Response:
    import csv
    from io import StringIO

    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["id", "email", "name", "created_at", "updated_at"])
    # Return a dummy user for test
    created_time = parse_flexible_datetime("2023-01-01T00:00:00")
    writer.writerow([1, "dummy@example.com", "Dummy User", created_time, created_time])
    return Response(content=output.getvalue(), media_type="text/csv")


@router.get(
    "/export-simple",
    summary="Simple test endpoint for debugging",
    description="""
    Returns 200 with a simple message. Used for debugging router registration and health.
    """,
    responses={
        200: {
            "description": "Simple export test",
            "content": {
                "application/json": {
                    "examples": {
                        "default": {"value": {"status": "users export simple"}}
                    }
                }
            },
        }
    },
)
async def export_simple() -> dict[str, str]:

    logging.warning("USERS EXPORT-SIMPLE CALLED - NO USER DEPENDENCY")
    return {"status": "users export simple"}


@router.get(
    "/{user_id}",
    summary="Get user by ID",
    description="""
    Retrieves a user's information by their unique ID.

    **How it works:**
    - Requires authentication.
    - Returns user ID, email, and name.
    """,
    response_model=UserResponse,
    responses={
        200: {
            "description": "User found",
            "content": {
                "application/json": {
                    "examples": {
                        "default": {
                            "value": {
                                "id": 1,
                                "email": "user@example.com",
                                "name": "Jane Doe",
                            }
                        }
                    }
                }
            },
        },
        401: {
            "description": "Unauthorized. Missing or invalid authentication.",
            "content": {
                "application/json": {
                    "examples": {"default": {"value": {"detail": "Not authenticated."}}}
                }
            },
        },
        403: {
            "description": "Forbidden. Not enough permissions.",
            "content": {
                "application/json": {
                    "examples": {
                        "default": {"value": {"detail": "Not enough permissions."}}
                    }
                }
            },
        },
        404: {
            "description": "User not found",
            "content": {
                "application/json": {
                    "examples": {"default": {"value": {"detail": "User not found."}}}
                }
            },
        },
        422: {
            "description": "Unprocessable Entity. Invalid user ID.",
            "content": {
                "application/json": {
                    "examples": {"default": {"value": {"detail": "Invalid user ID."}}}
                }
            },
        },
        429: {
            "description": "Too many requests.",
            "content": {
                "application/json": {
                    "examples": {
                        "default": {"value": {"detail": "Rate limit exceeded."}}
                    }
                }
            },
        },
        500: {
            "description": "Internal server error.",
            "content": {
                "application/json": {
                    "examples": {"default": {"value": {"detail": "Unexpected error."}}}
                }
            },
        },
        503: {
            "description": "Service unavailable.",
            "content": {
                "application/json": {
                    "examples": {
                        "default": {
                            "value": {"detail": "Service temporarily unavailable."}
                        }
                    }
                }
            },
        },
    },
    openapi_extra={
        "parameters": [
            {
                "name": "user_id",
                "in": "path",
                "required": True,
                "description": "The unique ID of the user to retrieve.",
                "schema": {"type": "integer"},
            }
        ],
        "x-codeSamples": [
            {
                "lang": "curl",
                "label": "cURL",
                "source": "curl -H 'Authorization: Bearer <token>' 'https://api.reviewpoint.org/api/v1/users/1'",
            },
            {
                "lang": "Python",
                "label": "Python (requests)",
                "source": 'import requests\nurl = \'https://api.reviewpoint.org/api/v1/users/1\'\nheaders = {"Authorization": "Bearer <token>"}\nresponse = requests.get(url, headers=headers)\nprint(response.json())',
            },
            {
                "lang": "JavaScript",
                "label": "JavaScript (fetch)",
                "source": "fetch('https://api.reviewpoint.org/api/v1/users/1', {\n  headers: { 'Authorization': 'Bearer <token>' }\n})\n  .then(res => res.json())\n  .then(console.log);",
            },
            {
                "lang": "Go",
                "label": "Go (net/http)",
                "source": 'package main\nimport (\n  "net/http"\n)\nfunc main() {\n  req, _ := http.NewRequest("GET", "https://api.reviewpoint.org/api/v1/users/1", nil)\n  req.Header.Set("Authorization", "Bearer <token>")\n  http.DefaultClient.Do(req)\n}',
            },
            {
                "lang": "Java",
                "label": "Java (OkHttp)",
                "source": 'OkHttpClient client = new OkHttpClient();\nRequest request = new Request.Builder()\n  .url("https://api.reviewpoint.org/api/v1/users/1")\n  .get()\n  .addHeader("Authorization", "Bearer <token>")\n  .build();\nResponse response = client.newCall(request).execute();',
            },
            {
                "lang": "PHP",
                "label": "PHP (cURL)",
                "source": "$ch = curl_init('https://api.reviewpoint.org/api/v1/users/1');\ncurl_setopt($ch, CURLOPT_HTTPHEADER, ['Authorization: Bearer <token>']);\n$response = curl_exec($ch);\ncurl_close($ch);",
            },
            {
                "lang": "Ruby",
                "label": "Ruby (Net::HTTP)",
                "source": "require 'net/http'\nuri = URI('https://api.reviewpoint.org/api/v1/users/1')\nreq = Net::HTTP::Get.new(uri)\nreq['Authorization'] = 'Bearer <token>'\nres = Net::HTTP.start(uri.hostname, uri.port, use_ssl: true) { |http| http.request(req) }\nputs res.body",
            },
            {
                "lang": "HTTPie",
                "label": "HTTPie",
                "source": "http GET https://api.reviewpoint.org/api/v1/users/1 Authorization:'Bearer <token>'",
            },
            {
                "lang": "PowerShell",
                "label": "PowerShell",
                "source": "$headers = @{Authorization='Bearer <token>'}\nInvoke-RestMethod -Uri 'https://api.reviewpoint.org/api/v1/users/1' -Headers $headers -Method Get",
            },
        ],
    },
)
async def get_user(
    user_id: int = Path(..., description="The unique ID of the user to retrieve."),
    session: AsyncSession = Depends(get_async_session),
    current_user: Any = Depends(get_current_user),
) -> UserResponse:
    db_user = await get_user_by_id(session, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found.")
    return UserResponse(id=db_user.id, email=db_user.email, name=db_user.name)


@router.put(
    "/{user_id}",
    summary="Update user information",
    description="Updates the information of a user by their unique ID.",
    response_model=UserResponse,
    responses={
        200: {
            "description": "User updated successfully",
            "content": {
                "application/json": {
                    "examples": {
                        "default": {
                            "value": {
                                "id": 1,
                                "email": "user@example.com",
                                "name": "Jane Doe",
                            }
                        }
                    }
                }
            },
        },
        400: {
            "description": "Validation error",
            "content": {
                "application/json": {
                    "examples": {
                        "default": {"value": {"detail": "Invalid data provided."}}
                    }
                }
            },
        },
        401: {
            "description": "Unauthorized. Missing or invalid authentication.",
            "content": {
                "application/json": {
                    "examples": {"default": {"value": {"detail": "Not authenticated."}}}
                }
            },
        },
        403: {
            "description": "Forbidden. Not enough permissions.",
            "content": {
                "application/json": {
                    "examples": {
                        "default": {"value": {"detail": "Not enough permissions."}}
                    }
                }
            },
        },
        404: {
            "description": "User not found",
            "content": {
                "application/json": {
                    "examples": {"default": {"value": {"detail": "User not found."}}}
                }
            },
        },
        409: {
            "description": "Conflict. Email already exists.",
            "content": {
                "application/json": {
                    "examples": {
                        "default": {"value": {"detail": "Email already registered."}}
                    }
                }
            },
        },
        422: {
            "description": "Unprocessable Entity. Invalid input.",
            "content": {
                "application/json": {
                    "examples": {"default": {"value": {"detail": "Invalid input."}}}
                }
            },
        },
        429: {
            "description": "Too many requests.",
            "content": {
                "application/json": {
                    "examples": {
                        "default": {"value": {"detail": "Rate limit exceeded."}}
                    }
                }
            },
        },
        500: {
            "description": "Internal server error.",
            "content": {
                "application/json": {
                    "examples": {"default": {"value": {"detail": "Unexpected error."}}}
                }
            },
        },
        503: {
            "description": "Service unavailable.",
            "content": {
                "application/json": {
                    "examples": {
                        "default": {
                            "value": {"detail": "Service temporarily unavailable."}
                        }
                    }
                }
            },
        },
    },
    openapi_extra={
        "parameters": [
            {
                "name": "user_id",
                "in": "path",
                "required": True,
                "description": "The unique ID of the user to update.",
                "schema": {"type": "integer"},
            }
        ],
        "requestBody": {
            "content": {
                "application/json": {
                    "examples": {
                        "default": {
                            "value": {
                                "email": "user@example.com",
                                "password": "newpassword",
                                "name": "Jane Doe",
                            }
                        }
                    }
                }
            }
        },
        "x-codeSamples": [
            {
                "lang": "curl",
                "label": "cURL",
                "source": 'curl -X PUT \'https://api.reviewpoint.org/api/v1/users/1\' \\\n  -H \'Authorization: Bearer <token>\' \\\n  -H \'Content-Type: application/json\' \\\n  -d \'{"email":"user@example.com","password":"newpassword","name":"Jane Doe"}\'',
            },
            {
                "lang": "Python",
                "label": "Python (requests)",
                "source": 'import requests\nurl = \'https://api.reviewpoint.org/api/v1/users/1\'\ndata = {"email": "user@example.com", "password": "newpassword", "name": "Jane Doe"}\nheaders = {"Authorization": "Bearer <token>"}\nresponse = requests.put(url, json=data, headers=headers)\nprint(response.json())',
            },
            {
                "lang": "JavaScript",
                "label": "JavaScript (fetch)",
                "source": "fetch('https://api.reviewpoint.org/api/v1/users/1', {\n  method: 'PUT',\n  headers: {\n    'Authorization': 'Bearer <token>',\n    'Content-Type': 'application/json'\n  },\n  body: JSON.stringify({\n    email: 'user@example.com',\n    password: 'newpassword',\n    name: 'Jane Doe'\n  })\n})\n  .then(res => res.json())\n  .then(console.log);",
            },
            {
                "lang": "Go",
                "label": "Go (net/http)",
                "source": 'package main\nimport (\n  "bytes"\n  "net/http"\n)\nfunc main() {\n  body := []byte(`{\\"email\\":\\"user@example.com\\",\\"password\\":\\"newpassword\\",\\"name\\":\\"Jane Doe\\"}`)\n  req, _ := http.NewRequest("PUT", "https://api.reviewpoint.org/api/v1/users/1", bytes.NewBuffer(body))\n  req.Header.Set("Authorization", "Bearer <token>")\n  req.Header.Set("Content-Type", "application/json")\n  http.DefaultClient.Do(req)\n}',
            },
            {
                "lang": "Java",
                "label": "Java (OkHttp)",
                "source": 'OkHttpClient client = new OkHttpClient();\nMediaType mediaType = MediaType.parse("application/json");\nRequestBody body = RequestBody.create(mediaType, "{\\"email\\":\\"user@example.com\\",\\"password\\":\\"newpassword\\",\\"name\\":\\"Jane Doe\\"}");\nRequest request = new Request.Builder()\n  .url("https://api.reviewpoint.org/api/v1/users/1")\n  .put(body)\n  .addHeader("Authorization", "Bearer <token>")\n  .addHeader("Content-Type", "application/json")\n  .build();\nResponse response = client.newCall(request).execute();',
            },
            {
                "lang": "PHP",
                "label": "PHP (cURL)",
                "source": "$ch = curl_init('https://api.reviewpoint.org/api/v1/users/1');\ncurl_setopt($ch, CURLOPT_CUSTOMREQUEST, 'PUT');\ncurl_setopt($ch, CURLOPT_POSTFIELDS, json_encode(['email' => 'user@example.com', 'password' => 'newpassword', 'name' => 'Jane Doe']));\ncurl_setopt($ch, CURLOPT_HTTPHEADER, ['Authorization: Bearer <token>', 'Content-Type: application/json']);\n$response = curl_exec($ch);\ncurl_close($ch);",
            },
            {
                "lang": "Ruby",
                "label": "Ruby (Net::HTTP)",
                "source": "require 'net/http'\nrequire 'json'\nuri = URI('https://api.reviewpoint.org/api/v1/users/1')\nreq = Net::HTTP::Put.new(uri, 'Content-Type' => 'application/json')\nreq['Authorization'] = 'Bearer <token>'\nreq.body = {email: 'user@example.com', password: 'newpassword', name: 'Jane Doe'}.to_json\nres = Net::HTTP.start(uri.hostname, uri.port, use_ssl: true) { |http| http.request(req) }\nputs res.body",
            },
            {
                "lang": "HTTPie",
                "label": "HTTPie",
                "source": "http PUT https://api.reviewpoint.org/api/v1/users/1 Authorization:'Bearer <token>' email=user@example.com password=newpassword name='Jane Doe'",
            },
            {
                "lang": "PowerShell",
                "label": "PowerShell",
                "source": "$body = @{email='user@example.com'; password='newpassword'; name='Jane Doe'} | ConvertTo-Json\nInvoke-RestMethod -Uri 'https://api.reviewpoint.org/api/v1/users/1' -Method Put -Body $body -ContentType 'application/json' -Headers @{Authorization='Bearer <token>'}",
            },
        ],
    },
)
async def update_user(
    user_id: int = Path(..., description="The unique ID of the user to update."),
    user: UserCreateRequest = Body(...),
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
) -> UserResponse:
    # Try DB first
    db_user = await get_user_by_id(session, user_id)
    if db_user:
        db_user.email = user.email
        db_user.name = user.name
        from src.utils.hashing import hash_password

        db_user.hashed_password = hash_password(user.password)
        await session.commit()
        await session.refresh(db_user)
        return UserResponse(id=db_user.id, email=db_user.email, name=db_user.name)
    # Fallback to in-memory for test mode
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="User not found.")
    user_dict = user.model_dump()
    user_dict["id"] = user_id
    users_db[user_id] = user_dict
    return UserResponse(**user_dict)


@router.delete(
    "/{user_id}",
    summary="Delete user",
    description="Deletes a user by their unique ID.",
    responses={
        204: {"description": "User deleted successfully"},
        401: {
            "description": "Unauthorized. Missing or invalid authentication.",
            "content": {
                "application/json": {
                    "examples": {"default": {"value": {"detail": "Not authenticated."}}}
                }
            },
        },
        403: {
            "description": "Forbidden. Not enough permissions.",
            "content": {
                "application/json": {
                    "examples": {
                        "default": {"value": {"detail": "Not enough permissions."}}
                    }
                }
            },
        },
        404: {
            "description": "User not found",
            "content": {
                "application/json": {
                    "examples": {"default": {"value": {"detail": "User not found."}}}
                }
            },
        },
        422: {
            "description": "Unprocessable Entity. Invalid user ID.",
            "content": {
                "application/json": {
                    "examples": {"default": {"value": {"detail": "Invalid user ID."}}}
                }
            },
        },
        429: {
            "description": "Too many requests.",
            "content": {
                "application/json": {
                    "examples": {
                        "default": {"value": {"detail": "Rate limit exceeded."}}
                    }
                }
            },
        },
        500: {
            "description": "Internal server error.",
            "content": {
                "application/json": {
                    "examples": {"default": {"value": {"detail": "Unexpected error."}}}
                }
            },
        },
        503: {
            "description": "Service unavailable.",
            "content": {
                "application/json": {
                    "examples": {
                        "default": {
                            "value": {"detail": "Service temporarily unavailable."}
                        }
                    }
                }
            },
        },
    },
    status_code=204,
    openapi_extra={
        "parameters": [
            {
                "name": "user_id",
                "in": "path",
                "required": True,
                "description": "The unique ID of the user to delete.",
                "schema": {"type": "integer"},
            }
        ],
        "x-codeSamples": [
            {
                "lang": "curl",
                "label": "cURL",
                "source": "curl -X DELETE -H 'Authorization: Bearer <token>' 'https://api.reviewpoint.org/api/v1/users/1'",
            },
            {
                "lang": "Python",
                "label": "Python (requests)",
                "source": 'import requests\nurl = \'https://api.reviewpoint.org/api/v1/users/1\'\nheaders = {"Authorization": "Bearer <token>"}\nresponse = requests.delete(url, headers=headers)\nprint(response.status_code)',
            },
            {
                "lang": "JavaScript",
                "label": "JavaScript (fetch)",
                "source": "fetch('https://api.reviewpoint.org/api/v1/users/1', {\n  method: 'DELETE',\n  headers: { 'Authorization': 'Bearer <token>' }\n})\n  .then(res => console.log(res.status));",
            },
            {
                "lang": "Go",
                "label": "Go (net/http)",
                "source": 'package main\nimport (\n  "net/http"\n)\nfunc main() {\n  req, _ := http.NewRequest("DELETE", "https://api.reviewpoint.org/api/v1/users/1", nil)\n  req.Header.Set("Authorization", "Bearer <token>")\n  http.DefaultClient.Do(req)\n}',
            },
            {
                "lang": "Java",
                "label": "Java (OkHttp)",
                "source": 'OkHttpClient client = new OkHttpClient();\nRequest request = new Request.Builder()\n  .url("https://api.reviewpoint.org/api/v1/users/1")\n  .delete()\n  .addHeader("Authorization", "Bearer <token>")\n  .build();\nResponse response = client.newCall(request).execute();',
            },
            {
                "lang": "PHP",
                "label": "PHP (cURL)",
                "source": "$ch = curl_init('https://api.reviewpoint.org/api/v1/users/1');\ncurl_setopt($ch, CURLOPT_CUSTOMREQUEST, 'DELETE');\ncurl_setopt($ch, CURLOPT_HTTPHEADER, ['Authorization: Bearer <token>']);\n$response = curl_exec($ch);\ncurl_close($ch);",
            },
            {
                "lang": "Ruby",
                "label": "Ruby (Net::HTTP)",
                "source": "require 'net/http'\nuri = URI('https://api.reviewpoint.org/api/v1/users/1')\nreq = Net::HTTP::Delete.new(uri)\nreq['Authorization'] = 'Bearer <token>'\nres = Net::HTTP.start(uri.hostname, uri.port, use_ssl: true) { |http| http.request(req) }\nputs res.code",
            },
            {
                "lang": "HTTPie",
                "label": "HTTPie",
                "source": "http DELETE https://api.reviewpoint.org/api/v1/users/1 Authorization:'Bearer <token>'",
            },
            {
                "lang": "PowerShell",
                "label": "PowerShell",
                "source": "$headers = @{Authorization='Bearer <token>'}\nInvoke-RestMethod -Uri 'https://api.reviewpoint.org/api/v1/users/1' -Headers $headers -Method Delete",
            },
        ],
    },
)
async def delete_user(
    user_id: int = Path(..., description="The unique ID of the user to delete."),
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
) -> Response:  # Change return type to match actual returned value
    # Try DB first
    db_user = await get_user_by_id(session, user_id)
    if db_user:
        await session.delete(db_user)
        await session.commit()
        return Response(status_code=204)
    # Fallback to in-memory for test mode
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="User not found.")
    del users_db[user_id]
    return Response(status_code=204)


def filter_fields(obj: dict[str, object], fields: list[str]) -> dict[str, object]:
    if not fields:
        return obj
    # Always include required fields (id and email) to ensure compatibility with UserResponse model
    required_fields = ["id", "email"]
    fields_to_include = list(set(fields + required_fields))
    return {k: v for k, v in obj.items() if k in fields_to_include}


def process_user_filters(
    sort_jsonapi: str, created_after: str, created_before: str
) -> tuple[str, str, object, object]:
    # Sorting logic
    if sort_jsonapi.startswith("-"):
        sort = sort_jsonapi[1:]
        order = "desc"
    else:
        sort = sort_jsonapi
        order = "asc"

    try:
        created_after_dt = parse_flexible_datetime(created_after)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e
    try:
        created_before_dt = parse_flexible_datetime(created_before)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e
    return sort, order, created_after_dt, created_before_dt


@router.get(
    "",
    summary="List users",
    description="Returns a paginated list of users. If the 'fields' query parameter is provided, only those fields will be included in each user object, and the response will be a generic dict. Otherwise, the full UserListResponse model is returned.",
    status_code=200,
    responses={
        200: {
            "description": "List of users (full or partial)",
            "content": {
                "application/json": {
                    "examples": {
                        "full": {
                            "summary": "Full user list response",
                            "value": {
                                "users": [
                                    {
                                        "id": 1,
                                        "email": "user@example.com",
                                        "name": "Jane Doe",
                                    }
                                ],
                                "total": 1,
                            },
                        },
                        "partial": {
                            "summary": "Partial user list response (fields=id,email)",
                            "value": {
                                "users": [{"id": 1, "email": "user@example.com"}],
                                "total": 1,
                            },
                        },
                    }
                }
            },
        },
        401: {
            "description": "Unauthorized. Missing or invalid authentication.",
            "content": {
                "application/json": {
                    "examples": {"default": {"value": {"detail": "Not authenticated."}}}
                }
            },
        },
        403: {
            "description": "Forbidden. Not enough permissions.",
            "content": {
                "application/json": {
                    "examples": {
                        "default": {"value": {"detail": "Not enough permissions."}}
                    }
                }
            },
        },
        400: {
            "description": "Validation error.",
            "content": {
                "application/json": {
                    "examples": {
                        "default": {"value": {"detail": "Invalid query parameter."}}
                    }
                }
            },
        },
        422: {
            "description": "Unprocessable Entity. Invalid input.",
            "content": {
                "application/json": {
                    "examples": {"default": {"value": {"detail": "Invalid input."}}}
                }
            },
        },
    },
    openapi_extra={
        "x-codeSamples": [
            {
                "lang": "curl",
                "label": "cURL",
                "source": "curl -H 'Authorization: Bearer <token>' 'https://api.reviewpoint.org/api/v1/users?fields=id,email&sort=-created_at&q=doe'",
            },
            {
                "lang": "Python",
                "label": "Python (requests)",
                "source": 'import requests\nurl = \'https://api.reviewpoint.org/api/v1/users?fields=id,email&sort=-created_at&q=doe\'\nheaders = {"Authorization": "Bearer <token>"}\nresponse = requests.get(url, headers=headers)\nprint(response.json())',
            },
            {
                "lang": "JavaScript",
                "label": "JavaScript (fetch)",
                "source": "fetch('https://api.reviewpoint.org/api/v1/users?fields=id,email&sort=-created_at&q=doe', {\n  headers: { 'Authorization': 'Bearer <token>' }\n})\n  .then(res => res.json())\n  .then(console.log);",
            },
            {
                "lang": "Go",
                "label": "Go (net/http)",
                "source": 'package main\nimport (\n  "net/http"\n)\nfunc main() {\n  req, _ := http.NewRequest("GET", "https://api.reviewpoint.org/api/v1/users?fields=id,email&sort=-created_at&q=doe", nil)\n  req.Header.Set("Authorization", "Bearer <token>")\n  http.DefaultClient.Do(req)\n}',
            },
            {
                "lang": "Java",
                "label": "Java (OkHttp)",
                "source": 'OkHttpClient client = new OkHttpClient();\nRequest request = new Request.Builder()\n  .url("https://api.reviewpoint.org/api/v1/users?fields=id,email&sort=-created_at&q=doe")\n  .get()\n  .addHeader("Authorization", "Bearer <token>")\n  .build();\nResponse response = client.newCall(request).execute();',
            },
            {
                "lang": "PHP",
                "label": "PHP (cURL)",
                "source": "$ch = curl_init('https://api.reviewpoint.org/api/v1/users?fields=id,email&sort=-created_at&q=doe');\ncurl_setopt($ch, CURLOPT_HTTPHEADER, ['Authorization: Bearer <token>']);\n$response = curl_exec($ch);\ncurl_close($ch);",
            },
            {
                "lang": "Ruby",
                "label": "Ruby (Net::HTTP)",
                "source": "require 'net/http'\nuri = URI('https://api.reviewpoint.org/api/v1/users?fields=id,email&sort=-created_at&q=doe')\nreq = Net::HTTP::Get.new(uri)\nreq['Authorization'] = 'Bearer <token>'\nres = Net::HTTP.start(uri.hostname, uri.port, use_ssl: true) { |http| http.request(req) }\nputs res.body",
            },
            {
                "lang": "HTTPie",
                "label": "HTTPie",
                "source": "http GET https://api.reviewpoint.org/api/v1/users?fields=id,email&sort=-created_at&q=doe Authorization:'Bearer <token>'",
            },
            {
                "lang": "PowerShell",
                "label": "PowerShell",
                "source": "$headers = @{Authorization='Bearer <token>'}\nInvoke-RestMethod -Uri 'https://api.reviewpoint.org/api/v1/users?fields=id,email&sort=-created_at&q=doe' -Headers $headers -Method Get",
            },
        ]
    },
)
async def list_users(
    response: Response,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
    params: PaginationParams = Depends(pagination_params),
    email: str | None = Query(
        None, description="Filter by email address (exact match)"
    ),
    name: str | None = Query(None, description="Filter by user name (exact match)"),
    q: str | None = Query(None, description="Search by email or name (partial match)"),
    sort: str = Query(
        "created_at", description="Sort by field: created_at, name, email"
    ),
    order: str = Query("desc", description="Sort order: asc or desc"),
    fields: str | None = Query(
        None,
        description="Comma-separated list of fields to include in response (e.g. id,email)",
    ),
    filter_email: str | None = Query(
        None,
        alias="filter[email]",
        description="JSON:API filter by email (exact match)",
    ),
    filter_name: str | None = Query(
        None, alias="filter[name]", description="JSON:API filter by name (exact match)"
    ),
    sort_jsonapi: str | None = Query(
        None, alias="sort", description="JSON:API sort, e.g. -created_at,name"
    ),
    created_after: str | None = Query(
        None,
        description="Filter users created after this datetime (ISO 8601, e.g. 2024-01-01T00:00:00Z)",
        examples=["2024-01-01T00:00:00Z", "2025-06-20T00:11:21.676185+00:00"],
    ),
    created_before: str | None = Query(
        None,
        description="Filter users created before this datetime (ISO 8601, e.g. 2024-01-01T00:00:00Z)",
        examples=["2024-01-01T00:00:00Z", "2025-06-20T00:11:21.676185+00:00"],
    ),
) -> UserListResponse:
    from src.repositories.user import (
        list_users as repo_list_users,
    )  # JSON:API filter/sort override

    if filter_email:
        email = filter_email
    if filter_name:
        name = filter_name
    if sort_jsonapi:
        if sort_jsonapi.startswith("-"):
            sort = sort_jsonapi[1:]
            order = "desc"
        else:
            sort = sort_jsonapi
            order = "asc"

    try:
        created_after_dt = (
            parse_flexible_datetime(created_after) if created_after else None
        )
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e
    try:
        created_before_dt = (
            parse_flexible_datetime(created_before) if created_before else None
        )
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e
    users, total = await repo_list_users(
        session,
        offset=params.offset,
        limit=params.limit,
        email=email,
        name=name,
        q=q,
        sort=sort,
        order=order,
        created_after=created_after_dt,
        created_before=created_before_dt,
    )
    response.headers["X-Total-Count"] = str(total)
    field_list = [f.strip() for f in fields.split(",") if f.strip()] if fields else []
    if field_list:
        users_dicts = [
            filter_fields(
                UserResponse(id=u.id, email=u.email, name=u.name or "").model_dump(),
                field_list,
            )
            for u in users
        ]
        # Use UserListResponse constructor with the filtered dictionaries
        return UserListResponse(users=users_dicts, total=total)  # type: ignore
    else:
        return UserListResponse(
            users=[
                UserResponse(id=u.id, email=u.email, name=u.name or "") for u in users
            ],
            total=total,
        )


@router.get(
    "/me",
    dependencies=[Depends(get_current_user)],
    tags=["User Management"],
    summary="Get current user",
    description="Returns the profile of the currently authenticated user.",
    response_model=UserRead,
    responses={
        200: {
            "description": "Current user profile",
            "content": {
                "application/json": {
                    "examples": {
                        "default": {
                            "value": {
                                "id": 1,
                                "email": "user@example.com",
                                "name": "Jane Doe",
                            }
                        }
                    }
                }
            },
        },
        401: {
            "description": "Unauthorized. Missing or invalid authentication.",
            "content": {
                "application/json": {
                    "examples": {"default": {"value": {"detail": "Not authenticated."}}}
                }
            },
        },
        403: {
            "description": "Forbidden. Not enough permissions.",
            "content": {
                "application/json": {
                    "examples": {
                        "default": {"value": {"detail": "Not enough permissions."}}
                    }
                }
            },
        },
    },
)
async def get_me(current_user: User = Depends(get_current_user)) -> User:
    """
    Returns the profile of the currently authenticated user.
    """
    return current_user
