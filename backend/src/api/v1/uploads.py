import asyncio
import csv
import logging
from collections.abc import Iterator, Mapping, Sequence
from datetime import datetime
from io import StringIO
from typing import (
    Final,
    Literal,
    TypedDict,
    cast,
)

from fastapi import (
    APIRouter,
    Depends,
    Path,
    Query,
    Request,
    Response,
    UploadFile,
    status,
)
from fastapi import (
    File as FastAPIFile,  # Renamed to avoid conflict
)
from fastapi.responses import StreamingResponse
from loguru import logger
from pydantic import BaseModel, ConfigDict
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.deps import (
    get_current_user_with_api_key as get_current_user,
)
from src.api.deps import (
    get_request_id,
    pagination_params,
    require_api_key,
    require_feature,
)
from src.core.database import get_async_session
from src.models.file import File as DBFile  # Renamed to avoid conflict
from src.models.user import User
from src.repositories.file import (
    create_file,
    delete_file,
    get_file_by_filename,
)
from src.repositories.file import (
    list_files as repo_list_files,
)
from src.utils.datetime import parse_flexible_datetime
from src.utils.file import is_safe_filename, sanitize_filename
from src.utils.http_error import ExtraLogInfo, http_error

# --- TypedDicts for strict typing ---


class FileDict(TypedDict, total=False):
    filename: str
    url: str


# --- Constants ---


ROUTER_PREFIX: Final[Literal["/uploads"]] = "/uploads"
ROUTER_TAGS: Final[Sequence[Literal["File"]]] = ("File",)
FileInDB: type = DBFile
router: APIRouter = APIRouter(prefix=ROUTER_PREFIX, tags=list(ROUTER_TAGS))

# ----------------------------------------
# DATA MODELS - MUST BE DEFINED BEFORE ROUTES
# ----------------------------------------


class FileUploadResponse(BaseModel):
    filename: str
    url: str
    model_config: ConfigDict = ConfigDict(
        json_schema_extra={
            "example": {"filename": "document.pdf", "url": "/uploads/document.pdf"}
        }
    )


class FileListResponse(BaseModel):
    files: Sequence[FileDict]
    total: int
    model_config: ConfigDict = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "files": [
                        {"filename": "document.pdf", "url": "/uploads/document.pdf"},
                        {"filename": "image.jpg", "url": "/uploads/image.jpg"},
                        {"filename": "only_filename.pdf"},
                    ],
                    "total": 3,
                }
            ]
        }
    )


# Response models


class FileResponse(BaseModel):
    filename: str
    url: str
    content_type: str | None = None
    size: int | None = None
    created_at: datetime | None = None
    model_config: ConfigDict = ConfigDict(
        json_schema_extra={
            "example": {
                "filename": "document.pdf",
                "url": "/uploads/document.pdf",
                "content_type": "application/pdf",
                "size": 1024,
                "created_at": "2025-06-20T12:00:00Z",
            }
        }
    )


def ensure_nonempty_filename(file: UploadFile = FastAPIFile(...)) -> UploadFile:
    """
    Ensures the uploaded file has a non-empty filename.
    Raises:
        HTTPException: If the filename is empty.
    """
    if not file.filename:
        http_error(
            400,
            "Invalid file.",
            logger.warning,
            cast(ExtraLogInfo, {"filename": str(file.filename)}),
        )
    return file


_log_msg_router: Final[str] = "Creating uploads router with export routes first"
logging.warning(_log_msg_router)

# ----------------------------------------
# IMPORTANT: DIAGNOSTIC ROUTES FIRST
# ----------------------------------------


@router.get(
    "/root-test",
    summary="Root level test endpoint",
    description="""
    **Diagnostic Endpoint**

    Checks if the uploads router is registered and responding. Useful for debugging router registration issues.

    **Returns:**
    - JSON status and router name.
    """,
    operation_id="uploads_main_root_test",
    tags=["File"],
    responses={
        200: {
            "description": "Root test successful",
            "content": {
                "application/json": {
                    "examples": {
                        "default": {
                            "value": {
                                "status": "uploads root test",
                                "router": "uploads",
                            }
                        }
                    }
                }
            },
        }
    },
)
def _root_test_response() -> Mapping[str, str]:
    return {"status": "uploads root test", "router": "uploads"}


async def root_test() -> Mapping[str, str]:
    logging.warning("UPLOADS ROOT-TEST CALLED")
    return _root_test_response()


@router.get(
    "/test-alive",
    summary="Test endpoint for router registration",
    description="""
    **Health Check**

    Confirms the uploads router is active and properly registered. Returns a simple status JSON object.

    **Use case:**
    - Health checks
    - Integration tests
    """,
    tags=["File"],
    responses={
        200: {
            "description": "Router is alive",
            "content": {
                "application/json": {
                    "examples": {"default": {"value": {"status": "alive"}}}
                }
            },
        }
    },
)
def _test_alive_response() -> Mapping[str, str]:
    return {"status": "alive"}


async def test_alive() -> Mapping[str, str]:
    logging.warning("UPLOADS TEST-ALIVE CALLED")
    return _test_alive_response()


@router.get(
    "/export-alive",
    summary="Test endpoint for export router",
    description="""
    **Export Router Health Check**

    Returns 200 if the uploads export router is active. Used for integration and deployment checks.
    """,
    tags=["File"],
    responses={
        200: {
            "description": "Export router is alive",
            "content": {
                "application/json": {
                    "examples": {
                        "default": {"value": {"status": "uploads export alive"}}
                    }
                }
            },
        }
    },
)
def _export_alive_response() -> Mapping[str, str]:
    return {"status": "uploads export alive"}


async def export_alive() -> Mapping[str, str]:
    logging.warning("UPLOADS EXPORT-ALIVE CALLED")
    return _export_alive_response()


@router.get(
    "/export-test",
    summary="Test endpoint for export router",
    description="""
    **Export Router Test**

    Returns 200 if the uploads export router is active. Requires authentication.

    **Returns:**
    - JSON status
    - Current user ID (if authenticated)
    """,
    tags=["File"],
    responses={
        200: {
            "description": "Export router test successful",
            "content": {
                "application/json": {
                    "examples": {
                        "default": {"value": {"status": "uploads export test"}}
                    }
                }
            },
        }
    },
)
async def export_test(
    current_user: User | None = Depends(get_current_user),
) -> Mapping[str, str]:
    logging.warning(
        f"UPLOADS EXPORT-TEST CALLED with user_id={current_user.id if current_user else 'None'}"
    )
    return {"status": "uploads export test"}


# ----------------------------------------
# EXPORT ENDPOINTS
# ----------------------------------------


@router.get(
    "/export",
    summary="Export files as CSV",
    description="""
    **Export Operation**

    Exports the list of uploaded files as a CSV file.

    **Steps:**
    1. Authenticated user requests export.
    2. Server filters and sorts files as requested.
    3. Returns a CSV with filename and URL columns.

    **Notes:**
    - Supports filtering by creation date and filename.
    - Rate limiting and authentication required.
    """,
    responses={
        200: {
            "description": "Files exported as CSV",
            "content": {
                "text/csv": {
                    "examples": {
                        "default": {
                            "value": "filename,url\ndocument.pdf,/uploads/document.pdf"
                        }
                    }
                }
            },
        },
        401: {
            "description": "Unauthorized. Missing or invalid authentication.",
            "content": {
                "application/json": {"example": {"detail": "Not authenticated."}}
            },
        },
        403: {
            "description": "Forbidden. Not enough permissions.",
            "content": {
                "application/json": {"example": {"detail": "Not enough permissions."}}
            },
        },
        422: {
            "description": "Unprocessable Entity. Invalid input.",
            "content": {"application/json": {"example": {"detail": "Invalid input."}}},
        },
        429: {
            "description": "Too many requests.",
            "content": {
                "application/json": {"example": {"detail": "Rate limit exceeded."}}
            },
        },
        500: {
            "description": "Internal server error.",
            "content": {
                "application/json": {"example": {"detail": "Unexpected error."}}
            },
        },
        503: {
            "description": "Service unavailable.",
            "content": {
                "application/json": {
                    "example": {"detail": "Service temporarily unavailable."}
                }
            },
        },
    },
    openapi_extra={
        "x-codeSamples": [
            {
                "lang": "curl",
                "label": "cURL",
                "source": "curl -H 'Authorization: Bearer <token>' 'https://api.reviewpoint.org/api/v1/uploads/export'",
            },
            {
                "lang": "Python",
                "label": "Python (requests)",
                "source": "import requests\nurl = 'https://api.reviewpoint.org/api/v1/uploads/export'\nheaders = {'Authorization': 'Bearer <token>'}\nresponse = requests.get(url, headers=headers)\nprint(response.content.decode())",
            },
            {
                "lang": "JavaScript",
                "label": "JavaScript (fetch)",
                "source": "fetch('https://api.reviewpoint.org/api/v1/uploads/export', {\n  headers: { 'Authorization': 'Bearer <token>' }\n})\n  .then(res => res.text())\n  .then(console.log);",
            },
            {
                "lang": "Go",
                "label": "Go (net/http)",
                "source": 'package main\nimport (\n  "net/http"\n)\nfunc main() {\n  req, _ := http.NewRequest("GET", "https://api.reviewpoint.org/api/v1/uploads/export", nil)\n  req.Header.Set("Authorization", "Bearer <token>")\n  http.DefaultClient.Do(req)\n}',
            },
            {
                "lang": "Java",
                "label": "Java (OkHttp)",
                "source": 'OkHttpClient client = new OkHttpClient();\nRequest request = new Request.Builder()\n  .url("https://api.reviewpoint.org/api/v1/uploads/export")\n  .get()\n  .addHeader("Authorization", "Bearer <token>")\n  .build();\nResponse response = client.newCall(request).execute();',
            },
            {
                "lang": "PHP",
                "label": "PHP (cURL)",
                "source": "$ch = curl_init('https://api.reviewpoint.org/api/v1/uploads/export');\ncurl_setopt($ch, CURLOPT_HTTPHEADER, ['Authorization: Bearer <token>']);\n$response = curl_exec($ch);\ncurl_close($ch);",
            },
            {
                "lang": "Ruby",
                "label": "Ruby (Net::HTTP)",
                "source": "require 'net/http'\nuri = URI('https://api.reviewpoint.org/api/v1/uploads/export')\nreq = Net::HTTP::Get.new(uri)\nreq['Authorization'] = 'Bearer <token>'\nres = Net::HTTP.start(uri.hostname, uri.port, use_ssl: true) { |http| http.request(req) }\nputs res.body",
            },
            {
                "lang": "HTTPie",
                "label": "HTTPie",
                "source": "http GET https://api.reviewpoint.org/api/v1/uploads/export Authorization:'Bearer <token>'",
            },
            {
                "lang": "PowerShell",
                "label": "PowerShell",
                "source": "$headers = @{Authorization='Bearer <token>'}\nInvoke-RestMethod -Uri 'https://api.reviewpoint.org/api/v1/uploads/export' -Headers $headers -Method Get",
            },
        ]
    },
)
async def export_files_csv(
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
    params: object = Depends(pagination_params),
    q: str | None = Query(None, description="Search by filename (partial match)"),
    sort: Literal["created_at", "filename"] = Query(
        "created_at", description="Sort by field: created_at, filename"
    ),
    order: Literal["desc", "asc"] = Query(
        "desc", description="Sort order: asc or desc"
    ),
    fields: str | None = Query(
        None,
        description="Comma-separated list of fields to include in response (e.g. filename,url)",
    ),
    created_before: str | None = Query(
        None,
        description="Filter files created before this datetime (ISO 8601, e.g. 2024-01-01T00:00:00Z)",
    ),
    created_after: str | None = Query(
        None,
        description="Filter files created after this datetime (ISO 8601, e.g. 2024-01-01T00:00:00Z)",
    ),
    request_id: str = Depends(get_request_id),
    feature_flag_ok: bool = Depends(require_feature("uploads:export")),
    api_key_ok: None = Depends(require_api_key),
) -> StreamingResponse:
    """
    Export the list of uploaded files as a CSV file.
    Raises:
        HTTPException: If date parsing fails.
    """
    logging.info(
        f"UPLOADS EXPORT CALLED with user_id={getattr(current_user, 'id', None)}"
    )

    def _generate_csv(files: Sequence[DBFile], columns: Sequence[str]) -> Iterator[str]:
        output: StringIO = StringIO()
        writer = csv.writer(output)  # type: ignore[var-annotated]
        writer.writerow(columns)
        for f in files:
            row: list[str] = []
            if "filename" in columns:
                row.append(f.filename)
            if "url" in columns:
                row.append(f"/uploads/{f.filename}")
            writer.writerow(row)
        yield output.getvalue()

    created_after_dt: datetime | None
    created_before_dt: datetime | None
    try:
        created_after_dt = (
            parse_flexible_datetime(created_after) if created_after else None
        )
    except ValueError as e:
        logger.error(f"Invalid created_after: {e}")
        http_error(
            422,
            str(e),
            logger.error,
            cast(ExtraLogInfo, {"created_after": created_after or ""}),
            e,
        )
    try:
        created_before_dt = (
            parse_flexible_datetime(created_before) if created_before else None
        )
    except ValueError as e:
        logger.error(f"Invalid created_before: {e}")
        http_error(
            422,
            str(e),
            logger.error,
            cast(ExtraLogInfo, {"created_before": created_before or ""}),
            e,
        )
    files: Sequence[DBFile]
    _total: int
    files, _total = await repo_list_files(
        session,
        current_user.id,
        offset=getattr(params, "offset", 0),
        limit=getattr(params, "limit", 10000),  # Large limit for export
        q=q,
        sort=sort,
        order=order,
        created_after=created_after_dt,
        created_before=created_before_dt,
    )
    columns: list[str] = ["filename", "url"]
    if fields:
        requested: list[str] = [
            f.strip() for f in fields.split(",") if f.strip() in columns
        ]
        if requested:
            columns = requested
    return StreamingResponse(
        _generate_csv(files, columns),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=uploads_export.csv"},
    )


# ----------------------------------------
# REGULAR CRUD ENDPOINTS
# ----------------------------------------


@router.post(
    "",
    summary="Upload a file",
    description="""
    **File Upload**

    Uploads a file and returns its filename and URL.

    **How it works:**
    1. User sends a file using multipart/form-data.
    2. The server validates the file type and size.
    3. If valid, the file is saved and a URL is returned.

    **Notes:**
    - Only certain file types may be allowed (e.g., PDF, images).
    - File size limits and rate limiting may apply.
    - Use the returned URL to access or download the file.
    """,
    response_model=FileUploadResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {
            "description": "File uploaded successfully",
            "content": {
                "application/json": {
                    "example": {
                        "filename": "document.pdf",
                        "url": "/uploads/document.pdf",
                    }
                }
            },
        },
        400: {
            "description": "Invalid file",
            "content": {
                "application/json": {"example": {"detail": "File type not allowed."}}
            },
        },
        401: {
            "description": "Unauthorized. Missing or invalid authentication.",
            "content": {
                "application/json": {"example": {"detail": "Not authenticated."}}
            },
        },
        413: {
            "description": "File too large.",
            "content": {
                "application/json": {"example": {"detail": "File size exceeds limit."}}
            },
        },
        415: {
            "description": "Unsupported Media Type.",
            "content": {
                "application/json": {"example": {"detail": "Unsupported file type."}}
            },
        },
        422: {
            "description": "Unprocessable Entity. Invalid input.",
            "content": {"application/json": {"example": {"detail": "Invalid input."}}},
        },
        429: {
            "description": "Too many requests.",
            "content": {
                "application/json": {"example": {"detail": "Rate limit exceeded."}}
            },
        },
        500: {
            "description": "Internal server error.",
            "content": {
                "application/json": {"example": {"detail": "Unexpected error."}}
            },
        },
        503: {
            "description": "Service unavailable.",
            "content": {
                "application/json": {
                    "example": {"detail": "Service temporarily unavailable."}
                }
            },
        },
    },
    openapi_extra={
        "requestBody": {
            "content": {
                "multipart/form-data": {
                    "example": {"file": "(binary file, e.g. document.pdf)"}
                }
            }
        },
        "x-codeSamples": [
            {
                "lang": "curl",
                "label": "cURL",
                "source": "curl -X POST 'https://api.reviewpoint.org/api/v1/uploads' \\\n  -H 'Authorization: Bearer <token>' \\\n  -F 'file=@document.pdf'",
            },
            {
                "lang": "Python",
                "label": "Python (requests)",
                "source": "import requests\nurl = 'https://api.reviewpoint.org/api/v1/uploads'\nheaders = {'Authorization': 'Bearer <token>'}\nfiles = {'file': open('document.pdf', 'rb')}\nresponse = requests.post(url, headers=headers, files=files)\nprint(response.json())",
            },
            {
                "lang": "JavaScript",
                "label": "JavaScript (fetch)",
                "source": "const form = new FormData();\nform.append('file', fileInput.files[0]);\nfetch('https://api.reviewpoint.org/api/v1/uploads', {\n  method: 'POST',\n  headers: { 'Authorization': 'Bearer <token>' },\n  body: form\n})\n  .then(res => res.json())\n  .then(console.log);",
            },
            {
                "lang": "Go",
                "label": "Go (net/http)",
                "source": 'package main\nimport (\n  "bytes"\n  "mime/multipart"\n  "net/http"\n  "os"\n)\nfunc main() {\n  file, _ := os.Open("document.pdf")\n  defer file.Close()\n  body := &bytes.Buffer{}\n  writer := multipart.NewWriter(body)\n  part, _ := writer.CreateFormFile("file", "document.pdf")\n  io.Copy(part, file)\n  writer.Close()\n  req, _ := http.NewRequest("POST", "https://api.reviewpoint.org/api/v1/uploads", body)\n  req.Header.Set("Authorization", "Bearer <token>")\n  req.Header.Set("Content-Type", writer.FormDataContentType())\n  http.DefaultClient.Do(req)\n}',
            },
            {
                "lang": "Java",
                "label": "Java (OkHttp)",
                "source": 'OkHttpClient client = new OkHttpClient();\nMediaType mediaType = MediaType.parse("application/pdf");\nFile file = new File("document.pdf");\nRequestBody fileBody = RequestBody.create(mediaType, file);\nMultipartBody requestBody = new MultipartBody.Builder()\n  .setType(MultipartBody.FORM)\n  .addFormDataPart("file", file.getName(), fileBody)\n  .build();\nRequest request = new Request.Builder()\n  .url("https://api.reviewpoint.org/api/v1/uploads")\n  .post(requestBody)\n  .addHeader("Authorization", "Bearer <token>")\n  .build();\nResponse response = client.newCall(request).execute();',
            },
            {
                "lang": "PHP",
                "label": "PHP (cURL)",
                "source": "$ch = curl_init('https://api.reviewpoint.org/api/v1/uploads');\ncurl_setopt($ch, CURLOPT_POST, 1);\ncurl_setopt($ch, CURLOPT_POSTFIELDS, ['file' => new CURLFile('document.pdf')]);\ncurl_setopt($ch, CURLOPT_HTTPHEADER, ['Authorization: Bearer <token>']);\n$response = curl_exec($ch);\ncurl_close($ch);",
            },
            {
                "lang": "Ruby",
                "label": "Ruby (Net::HTTP)",
                "source": "require 'net/http'\nrequire 'uri'\nrequire 'json'\nuri = URI('https://api.reviewpoint.org/api/v1/uploads')\nrequest = Net::HTTP::Post.new(uri)\nrequest['Authorization'] = 'Bearer <token>'\nform_data = [['file', File.open('document.pdf')]]\nrequest.set_form form_data, 'multipart/form-data'\nresponse = Net::HTTP.start(uri.hostname, uri.port, use_ssl: true) do |http|\n  http.request(request)\nend\nputs response.body",
            },
            {
                "lang": "HTTPie",
                "label": "HTTPie",
                "source": "http -f POST https://api.reviewpoint.org/api/v1/uploads Authorization:'Bearer <token>' file@document.pdf",
            },
            {
                "lang": "PowerShell",
                "label": "PowerShell",
                "source": "$file = Get-Item .\\document.pdf\n$Form = @{file = $file}\nInvoke-RestMethod -Uri 'https://api.reviewpoint.org/api/v1/uploads' -Method Post -Form $Form -Headers @{Authorization='Bearer <token>'}",
            },
        ],
    },
)
async def upload_file(
    file: UploadFile = FastAPIFile(
        ..., description="The file to upload. Must be a valid file type."
    ),
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
    request_id: str = Depends(get_request_id),
    feature_flag_ok: bool = Depends(require_feature("uploads:upload")),
    api_key_ok: None = Depends(require_api_key),
    # type: ignore[return]
) -> FileUploadResponse:
    """
    Uploads a file and returns its filename and URL.
    Raises:
        HTTPException: If file is invalid or upload fails.
    """
    if not file.filename:
        http_error(
            400,
            "Invalid file.",
            logger.warning,
            cast(ExtraLogInfo, {"filename": str(file.filename)}),
        )

    filename_str: str = file.filename if file.filename is not None else ""
    if not is_safe_filename(filename_str):
        http_error(
            400,
            "Invalid filename. Path traversal attempts are not allowed.",
            logger.warning,
            cast(ExtraLogInfo, {"filename": filename_str}),
        )

    safe_filename: str = sanitize_filename(filename_str)
    original_filename: str = filename_str
    file.filename = safe_filename

    if original_filename != safe_filename:
        logging.warning(
            f"Filename sanitized from '{original_filename}' to '{safe_filename}'"
        )

    max_retries: Final[int] = 3
    last_exception: Exception | None = None

    for attempt in range(max_retries):
        try:
            # Create a new session for each attempt to avoid SQLAlchemy IllegalStateChangeError
            async with session.begin_nested():
                db_file: DBFile = await create_file(
                    session,
                    file.filename,
                    file.content_type or "application/octet-stream",
                    user_id=current_user.id,
                )

            await session.commit()
            return FileUploadResponse(
                filename=db_file.filename, url=f"/uploads/{db_file.filename}"
            )
        except Exception as e:
            last_exception = e
            try:
                await session.rollback()
            except Exception as rollback_error:
                logging.error(f"Error during session rollback: {rollback_error}")
            error_str: str = str(e).lower()

            if attempt < max_retries - 1 and (
                "database is locked" in error_str
                or "unique constraint failed" in error_str
                or "illegal state change" in error_str
            ):
                wait_time: float = 0.1 * (2**attempt)
                await asyncio.sleep(wait_time)
                continue

            if "unique constraint failed" in error_str:
                http_error(
                    409,
                    "File with same name already exists or concurrent upload conflict",
                    logger.warning,
                    cast(
                        ExtraLogInfo,
                        {
                            "filename": (
                                file.filename if file.filename is not None else ""
                            )
                        },
                    ),
                    e,
                )

            logging.error(f"Failed to upload file on attempt {attempt+1}: {str(e)}")

    if last_exception:
        if "illegal state change" in str(last_exception).lower():
            http_error(
                500,
                "Database concurrency conflict. Please try again.",
                logger.error,
                cast(
                    ExtraLogInfo,
                    {"filename": file.filename if file.filename is not None else ""},
                ),
                last_exception,
            )
        http_error(
            500,
            f"Failed to upload file: {str(last_exception)}",
            logger.error,
            cast(
                ExtraLogInfo,
                {"filename": file.filename if file.filename is not None else ""},
            ),
            last_exception,
        )
    http_error(
        500,
        "Failed to upload file after multiple retries",
        logger.error,
        cast(
            ExtraLogInfo,
            {"filename": file.filename if file.filename is not None else ""},
        ),
    )

    # Defensive: static type checkers require a return, but this is unreachable
    raise RuntimeError(
        "Unreachable: all code paths in upload_file should raise or return"
    )


# ----------------------------------------
# PARAMETERIZED ROUTES - THESE MUST COME AFTER THE FIXED ROUTES
# ----------------------------------------


@router.get(
    "/{filename}",
    summary="Get uploaded file info",
    description="Retrieves metadata for an uploaded file by filename.",
    response_model=FileUploadResponse,
    responses={
        200: {
            "description": "File found",
            "content": {
                "application/json": {
                    "example": {
                        "filename": "document.pdf",
                        "url": "/uploads/document.pdf",
                    }
                }
            },
        },
        401: {
            "description": "Unauthorized. Missing or invalid authentication.",
            "content": {
                "application/json": {"example": {"detail": "Not authenticated."}}
            },
        },
        403: {
            "description": "Forbidden. Not enough permissions.",
            "content": {
                "application/json": {"example": {"detail": "Not enough permissions."}}
            },
        },
        404: {
            "description": "File not found",
            "content": {"application/json": {"example": {"detail": "File not found."}}},
        },
        422: {
            "description": "Unprocessable Entity. Invalid filename.",
            "content": {
                "application/json": {"example": {"detail": "Invalid filename."}}
            },
        },
        429: {
            "description": "Too many requests.",
            "content": {
                "application/json": {"example": {"detail": "Rate limit exceeded."}}
            },
        },
        500: {
            "description": "Internal server error.",
            "content": {
                "application/json": {"example": {"detail": "Unexpected error."}}
            },
        },
        503: {
            "description": "Service unavailable.",
            "content": {
                "application/json": {
                    "example": {"detail": "Service temporarily unavailable."}
                }
            },
        },
    },
)
async def get_file(
    filename: str = Path(..., description="The name of the file to retrieve."),
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
) -> FileUploadResponse:
    """
    Retrieves metadata for an uploaded file by filename.
    Raises:
        HTTPException: If file is not found.
    """
    logging.warning(f"GET FILE BY FILENAME CALLED: {filename}")
    db_file: DBFile | None = await get_file_by_filename(session, filename)
    if db_file is None:
        http_error(
            404,
            "File not found.",
            logger.warning,
            cast(ExtraLogInfo, {"filename": filename}),
        )
    return FileUploadResponse(
        filename=getattr(db_file, "filename", filename),
        url=f"/uploads/{getattr(db_file, 'filename', filename)}",
    )


@router.delete(
    "/{filename}",
    summary="Delete uploaded file",
    description="Deletes an uploaded file by filename.",
    responses={
        204: {
            "description": "File deleted successfully",
            "content": {"application/json": {"examples": {"default": {"value": {}}}}},
        },
        401: {
            "description": "Unauthorized. Missing or invalid authentication.",
            "content": {
                "application/json": {"example": {"detail": "Not authenticated."}}
            },
        },
        403: {
            "description": "Forbidden. Not enough permissions.",
            "content": {
                "application/json": {"example": {"detail": "Not enough permissions."}}
            },
        },
        404: {
            "description": "File not found",
            "content": {"application/json": {"example": {"detail": "File not found."}}},
        },
        422: {
            "description": "Unprocessable Entity. Invalid filename.",
            "content": {
                "application/json": {"example": {"detail": "Invalid filename."}}
            },
        },
        429: {
            "description": "Too many requests.",
            "content": {
                "application/json": {"example": {"detail": "Rate limit exceeded."}}
            },
        },
        500: {
            "description": "Internal server error.",
            "content": {
                "application/json": {"example": {"detail": "Unexpected error."}}
            },
        },
        503: {
            "description": "Service unavailable.",
            "content": {
                "application/json": {
                    "example": {"detail": "Service temporarily unavailable."}
                }
            },
        },
    },
)
async def delete_file_by_filename(
    filename: str = Path(..., description="The name of the file to delete."),
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
    request_id: str = Depends(get_request_id),
    feature_flag_ok: bool = Depends(require_feature("uploads:delete")),
    api_key_ok: None = Depends(require_api_key),
) -> Response:
    """
    Deletes an uploaded file by filename.
    Raises:
        HTTPException: If file is not found.
    """
    db_file: bool = await delete_file(session, filename)
    if not db_file:
        http_error(
            404,
            "File not found.",
            logger.warning,
            cast(ExtraLogInfo, {"filename": filename}),
        )
    await session.commit()  # Explicitly commit the transaction
    return Response(status_code=204)


# ----------------------------------------
# CATCH-ALL ROUTE - MUST BE LAST
# ----------------------------------------


# !!! KEEP THIS ROUTE LAST - IT WILL CATCH ALL OTHER REQUESTS !!!
@router.api_route(
    "/{path:path}",
    methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    include_in_schema=False,
)
async def catch_all_uploads(path: str, request: Request) -> Response:
    """
    Catch-all route for uploads. Always returns status 418.
    """
    logging.warning(f"UPLOADS CATCH-ALL: path={path}, method={request.method}")
    return Response(content=f"uploads catch-all: {path}", status_code=418)


# ----------------------------------------
# LIST FILES ENDPOINT
# ----------------------------------------


@router.get(
    "",
    summary="List all uploaded files",
    description="""
    **File Listing**

    Returns a paginated list of all uploaded files for the current user.

    **How it works:**
    1. The server retrieves files uploaded by the current user.
    2. Files can be filtered and sorted.
    3. Returns a list of files with pagination information.

    **Notes:**
    - Supports filtering by filename and creation date.
    - Supports sorting by creation date or filename.
    - Supports field selection to limit the returned data.
    """,
    response_model=FileListResponse,
    responses={
        200: {
            "description": "Files found",
            "content": {
                "application/json": {
                    "examples": {
                        "default": {
                            "value": {
                                "files": [
                                    {
                                        "filename": "document.pdf",
                                        "url": "/uploads/document.pdf",
                                    }
                                ],
                                "total": 1,
                            }
                        }
                    }
                }
            },
        },
        401: {
            "description": "Unauthorized. Missing or invalid authentication.",
            "content": {
                "application/json": {"example": {"detail": "Not authenticated."}}
            },
        },
    },
)
async def list_files(
    params: object = Depends(pagination_params),
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
    request_id: str = Depends(get_request_id),
    feature_flag_ok: bool = Depends(require_feature("uploads:list")),
    api_key_ok: None = Depends(require_api_key),
    q: str | None = Query(None, description="Search term across all fields"),
    fields: str | None = Query(
        None, description="Comma-separated list of fields to include"
    ),
    sort: Literal["created_at", "filename"] = Query(
        "created_at", description="Field to sort by"
    ),
    order: Literal["desc", "asc"] = Query(
        "desc", description="Sort order (asc or desc)"
    ),
    created_after: str | None = Query(
        None, description="Filter by creation date (ISO format)"
    ),
    created_before: str | None = Query(
        None, description="Filter by creation date (ISO format)"
    ),
) -> FileListResponse:
    """
    List all uploaded files with pagination and filtering options.
    Raises:
        HTTPException: If date parsing fails.
    """
    created_after_dt: datetime | None = None
    created_before_dt: datetime | None = None
    if created_after:
        created_after_dt = parse_flexible_datetime(created_after)
    if created_before:
        created_before_dt = parse_flexible_datetime(created_before)
    files: Sequence[DBFile]
    total: int
    files, total = await repo_list_files(
        session,
        current_user.id,
        offset=getattr(params, "offset", 0),
        limit=getattr(params, "limit", 100),
        q=q,
        sort=sort,
        order=order,
        created_after=created_after_dt,
        created_before=created_before_dt,
    )

    selected_fields: Sequence[str] | None = None
    if fields:
        selected_fields = [f.strip() for f in fields.split(",")]

    file_responses: list[FileDict] = []
    for file in files:
        file_data: FileDict = {
            "filename": file.filename,
            "url": f"/uploads/{file.filename}",
        }
        if selected_fields:
            # Use cast to FileDict for type safety
            file_data = cast(
                FileDict, {k: v for k, v in file_data.items() if k in selected_fields}
            )
        file_responses.append(file_data)

    return FileListResponse(files=file_responses, total=total)
