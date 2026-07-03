from pathlib import Path
from loguru import logger
from fastapi import UploadFile
from config import settings
from rag.ingest import document_ingestion_pipeline
from schemas.upload import UploadResponse, UploadMetadata
from utils.file_utils import FileUtils
from utils.exceptions import FileUploadException


class UploadService:
    """
    Coordinates file validation, storage updates, and vector base swaps.
    Fulfills the zero-retention architecture rule by clearing old files and databases
    on each new upload, while protecting against Windows file access locks.
    """

    def __init__(self) -> None:
        logger.info("[UPLOAD_SERVICE] Initializing central file ingest coordinator.")

    async def handle_pdf_upload(self, file: UploadFile) -> UploadResponse:
        """
        Validates an incoming file, clears existing assets and vector spaces,
        saves the file to disk, and runs it through the ingestion pipeline.
        """
        filename = file.filename or "unknown_source.pdf"
        logger.info(f"[UPLOAD_SERVICE] Intercepted stream request for file: '{filename}'")

        # 1. Enforce validation rule checking for standard PDF extensions
        if not filename.lower().endswith(".pdf"):
            logger.error(f"[UPLOAD_SERVICE] Format rejection. Received invalid target: '{filename}'")
            raise FileUploadException(
                message="Invalid document format. The Intelligent LMS strictly processes PDF payloads.",
                details={"rejected_filename": filename}
            )

        try:
            # 2. Enforce the single-document rule by clearing previous files on disk
            logger.warning("[UPLOAD_SERVICE] Clearing out old files in the upload directory.")
            FileUtils.ensure_clean_directory(settings.UPLOAD_DIR)

            # 3. Read the incoming byte stream from the file wrapper
            logger.debug(f"[UPLOAD_SERVICE] Reading byte chunks from stream: {filename}")
            file_bytes = await file.read()
            file_size = len(file_bytes)

            if file_size == 0:
                logger.error("[UPLOAD_SERVICE] Empty file payload rejected.")
                raise FileUploadException(
                    message="The uploaded PDF file contains no data bytes.",
                    details={"filename": filename}
                )

            # 4. Save the raw binary payload to disk as a single reference asset
            logger.info(f"[UPLOAD_SERVICE] Committing {file_size} bytes to disk storage.")
            saved_file_path = FileUtils.save_bytes_to_disk(
                file_bytes=file_bytes,
                destination_name=filename
            )

            # 5. Process the file through the vector index pipeline
            # This triggers a full wipe of the previous ChromaDB collection internally
            logger.info(f"[UPLOAD_SERVICE] Transferring file control to vector indexing pipeline: '{saved_file_path.name}'")
            chunk_count = document_ingestion_pipeline.process_pdf(saved_file_path)

            logger.info(f"[UPLOAD_SERVICE] Success. Knowledge base replaced with '{saved_file_path.name}' ({chunk_count} chunks).")
            
            return UploadResponse(
                success=True,
                message="Knowledge base completely refreshed. Previous knowledge structures dropped cleanly.",
                data=UploadMetadata(
                    filename=saved_file_path.name,
                    file_size_bytes=file_size,
                    chunk_count=chunk_count
                ),
                metadata={"indexing_strategy": "recursive_character_splitter"}
            )

        except FileUploadException as fe:
            raise fe
        except Exception as e:
            logger.exception(f"[UPLOAD_SERVICE] Critical failure during file processing for '{filename}'")
            raise FileUploadException(
                message="The service encountered an unhandled error while updating the knowledge base.",
                details={"error_message": str(e)}
            )
        finally:
            # Ensure the temporary upload stream handle is closed cleanly
            await file.close()


# Instantiate service singleton for shared application access
upload_service = UploadService()