from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from app.services.ppt_processor import process_ppt

router = APIRouter()

@router.post("/process-ppt")
async def process_ppt_endpoint(
    file: UploadFile = File(...),
    max_slides: int = Query(default=1, ge=1, le=10),
):
    if not file.filename.endswith(".pptx"):
        raise HTTPException(status_code=400, detail="Only .pptx files are allowed")

    contents = await file.read()
    if not contents:
        raise HTTPException(status_code=400, detail="Empty file uploaded")

    # Save temporarily
    temp_path = f"/tmp/{file.filename}"
    with open(temp_path, "wb") as f:
        f.write(contents)

    results = process_ppt(temp_path)

    return {
        "filename": file.filename,
        "slides": results
    }

