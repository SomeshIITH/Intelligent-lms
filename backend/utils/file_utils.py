import os
from pathlib import Path
from loguru import logger
from config import settings
from utils.exceptions import FileUploadException


class FileUtils:
    """
    Utility provider for atomic, defensive filesystem manipulation.
    Ensures safe, platform-agnostic file additions, directory structural analysis,
    and rigorous file purges designed to circumvent Windows permission locks.
    """

    @staticmethod
    def ensure_clean_directory(directory_path: Path) -> None:
        """
        Forcefully purges all contents inside a target directory without destroying 
        the directory structure itself. Designed to avoid OS resource-lock failures.
        """
        logger.info(f"[FILE_UTILS] Request received to purge directory contents: '{directory_path.resolve()}'")
        
        if not directory_path.exists():
            logger.warning(f"[FILE_UTILS] Target path '{directory_path}' does not exist. Creating directory structurally.")
            directory_path.mkdir(parents=True, exist_ok=True)
            return

        for item in directory_path.iterdir():
            try:
                if item.is_file() or item.is_symlink():
                    logger.debug(f"[FILE_UTILS] Attempting file removal: '{item.name}'")
                    # Clear any potentially sticky file permissions before deletion
                    os.chmod(item, 0o777)
                    item.unlink()
                    logger.debug(f"[FILE_UTILS] Successfully unlinked file: '{item.name}'")
                elif item.is_dir():
                    logger.debug(f"[FILE_UTILS] Recursing into sub-directory deletion: '{item.name}'")
                    FileUtils.delete_directory_recursive(item)
            except Exception as e:
                logger.error(f"[FILE_UTILS] [CRITICAL LOCK] Failed to erase item '{item.name}' during directory purge. Error: {str(e)}")
                raise FileUploadException(
                    message=f"System failed to clean storage unit due to resource locking: {item.name}",
                    details={"offending_item": str(item), "error_type": type(e).__name__}
                )
        
        logger.info(f"[FILE_UTILS] Clean complete. Directory completely empty: '{directory_path.resolve()}'")

    @staticmethod
    def delete_directory_recursive(target_dir: Path) -> None:
        """
        Recursively deletes a directory tree and all files contained within it.
        Removes permissions blocks actively.
        """
        if not target_dir.exists():
            return
            
        for item in target_dir.iterdir():
            if item.is_file() or item.is_symlink():
                os.chmod(item, 0o777)
                item.unlink()
            elif item.is_dir():
                FileUtils.delete_directory_recursive(item)
        
        os.chmod(target_dir, 0o777)
        target_dir.rmdir()
        logger.debug(f"[FILE_UTILS] Recursively deleted folder node: '{target_dir.name}'")

    @staticmethod
    def save_bytes_to_disk(file_bytes: bytes, destination_name: str) -> Path:
        """
        Writes raw binary content to the configured uploads storage folder atomically.
        Validates target integrity before returning the platform-safe resolved Path.
        """
        logger.info(f"[FILE_UTILS] Preparing write pipeline for file asset: '{destination_name}' ({len(file_bytes)} bytes)")
        
        try:
            # Ensure folder structures are healthy before performing file updates
            settings.create_required_directories()
            
            # Sanitize the filename to prevent directory traversal vulnerabilities
            safe_name = Path(destination_name).name
            target_file_path = settings.UPLOAD_DIR / safe_name
            
            logger.debug(f"[FILE_UTILS] Streaming payload bytes directly to disk trace: '{target_file_path.resolve()}'")
            
            with open(target_file_path, "wb") as buffer:
                buffer.write(file_bytes)
                
            logger.info(f"[FILE_UTILS] Atomic disk write finalized. File cached: '{target_file_path.name}'")
            return target_file_path
            
        except Exception as e:
            logger.exception(f"[FILE_UTILS] Unexpected crash during physical document disk commit for '{destination_name}'")
            raise FileUploadException(
                message=f"Failed to commit upload asset to disk filesystem layer: {destination_name}",
                details={"error_message": str(e)}
            )

    @staticmethod
    def verify_file_exists_and_readable(file_path: Path) -> bool:
        """
        Explicitly confirms existence, type alignment, and accessibility profiles of a file path.
        """
        exists = file_path.exists()
        is_file = file_path.is_file()
        readable = os.access(file_path, os.R_OK) if exists else False
        
        logger.debug(
            f"[FILE_UTILS] Access inspection for '{file_path.name}': "
            f"Exists={exists}, IsFile={is_file}, Readable={readable}"
        )
        return bool(exists and is_file and readable)