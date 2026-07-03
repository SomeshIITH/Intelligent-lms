from fastapi import APIRouter, UploadFile, File, status, Depends
from loguru import logger
from schemas.upload import UploadResponse
from services.upload_service import upload_service
from services.quiz_service import quiz_service

router = APIRouter(tags=["Knowledge Base Ingestion"])


@router.post(
    "/upload",
    response_model=UploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload a single PDF knowledge source",
    description="Validates and registers an incoming PDF file into the vector repository, completely replacing the previous document context.",
)
async def upload_pdf_document(
    file: UploadFile = File(..., description="The PDF document binary stream layer")
) -> UploadResponse:
    """
    Presentation endpoint accepting multi-part form data uploads.
    Triggers directory purges, writes files, and swaps out vector index contexts.
    """
    filename = file.filename or "unknown.pdf"
    logger.info(f"[UPLOAD_API] Intercepted upload request packet for file asset: '{filename}'")
    
    # 1. Dispatch file payload directly to the service layer for validation and storage updates
    response: UploadResponse = await upload_service.handle_pdf_upload(file)
    
    # 2. Reset the historical quiz logs to ensure student data aligns strictly with the new document context
    logger.warning(f"[UPLOAD_API] Flushing quiz history tracking systems to match new context: '{filename}'")
    quiz_service.flush_historical_telemetry()
    
    logger.info(f"[UPLOAD_API] Upload pipeline complete. Swapped workspace knowledge to: '{filename}'")
    return response