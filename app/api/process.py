import tempfile
import asyncio
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException, Query, Form, BackgroundTasks
from app.services.ppt_processor import process_ppt
from app.services.ppt_video_processor import process_ppt_to_video
from app.services.job_manager import job_manager
from app.services.async_processor import run_processing_job
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter(tags=["Process"])

# Ensure temp upload directory exists
UPLOAD_DIR = Path(settings.upload_dir)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

SUPPORTED_LANGUAGES = {"en", "fr", "hi"}


@router.post("/process")
async def process_ppt_async_endpoint(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    language: str = Form("en"),
    max_slides: int = Form(default=5),
    generate_video: bool = Form(default=True),
    generate_mcqs: bool = Form(default=True),
):
    """
    Upload and process a PowerPoint file asynchronously.
    
    Returns a job_id that can be used to track progress via WebSocket
    or polling the /jobs/{job_id}/status endpoint.
    """
    # Validate language
    if language not in SUPPORTED_LANGUAGES:
        raise HTTPException(
            status_code=400,
            detail=f"Language must be one of: {', '.join(SUPPORTED_LANGUAGES)}"
        )
    
    # Validate file type
    if not file.filename.endswith((".pptx", ".ppt")):
        raise HTTPException(
            status_code=400,
            detail="Only .ppt and .pptx files are allowed"
        )
    
    contents = await file.read()
    if not contents:
        raise HTTPException(status_code=400, detail="Empty file uploaded")
    
    # Check file size
    if len(contents) > settings.max_file_size_mb * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size is {settings.max_file_size_mb}MB"
        )
    
    # Save file
    temp_path = UPLOAD_DIR / file.filename
    with open(temp_path, "wb") as f:
        f.write(contents)
    
    # Create job with all required parameters
    try:
        job_id = job_manager.create_job(
            filename=file.filename,
            language=language,
            max_slides=max_slides,
            generate_video=generate_video,
            generate_mcqs=generate_mcqs,
        )
        logger.info(f"Created job {job_id} for file {file.filename}")
    except Exception as e:
        logger.error(f"Failed to create job: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create job: {str(e)}")
    
    # Start background processing
    background_tasks.add_task(
        run_processing_job,
        job_id=job_id,
        ppt_path=str(temp_path),
        language=language,
        max_slides=max_slides,
        generate_video=generate_video,
        generate_mcqs=generate_mcqs,
    )
    
    return {
        "job_id": job_id,
        "status": "processing",
        "message": f"Processing started for {file.filename}"
    }


@router.post("/process-ppt")
async def process_ppt_endpoint(
    file: UploadFile = File(...),
    max_slides: int = Query(default=1, ge=1, le=5),
    language: str = Form("en"),
):
    # Validate language
    if language not in SUPPORTED_LANGUAGES:
        raise HTTPException(
            status_code=400,
            detail="language must be one of: en, fr, hi"
        )

    # Validate file type
    if not file.filename.endswith(".pptx"):
        raise HTTPException(
            status_code=400,
            detail="Only .pptx files are allowed"
        )

    contents = await file.read()
    if not contents:
        raise HTTPException(
            status_code=400,
            detail="Empty file uploaded"
        )

    # Save temporarily (cross-platform)
    temp_path = UPLOAD_DIR / file.filename
    with open(temp_path, "wb") as f:
        f.write(contents)

    results = process_ppt(
        ppt_path=str(temp_path),
        language=language,
        max_slides=max_slides
    )

    return {
        "filename": file.filename,
        "language": language,
        "slides": results
    }

@router.post("/process-ppt-video")
async def process_ppt_video_endpoint(
    file: UploadFile = File(...),
    language: str = Form("en"),
    max_slides: int = Query(default=5, ge=1, le=10),
):
    if not file.filename.endswith(".pptx"):
        raise HTTPException(status_code=400, detail="Only .pptx files are allowed")

    contents = await file.read()
    if not contents:
        raise HTTPException(status_code=400, detail="Empty file uploaded")

    temp_path = UPLOAD_DIR / file.filename
    with open(temp_path, "wb") as f:
        f.write(contents)

    result = process_ppt_to_video(str(temp_path), language=language, max_slides=max_slides)

    return {
        "filename": file.filename,
        "language": language,
        **result
    }