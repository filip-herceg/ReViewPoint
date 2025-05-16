from fastapi import APIRouter
from schemas.upload import UploadRequest
from schemas.module_result import ModuleResult
from services.module_runner import run_mock_module
from loguru import logger

router = APIRouter()

@router.get("/ping", tags=["meta"])
def ping():
    return {"message": "pong"}

@router.post("/upload", response_model=ModuleResult, tags=["core"])
def upload_doc(upload: UploadRequest):
    logger.info(f"Received document: {upload.title} by {upload.author}")
    logger.debug(f"Content size: {len(upload.content)} chars")
    result = run_mock_module()
    return result
