import os
from pathlib import Path
from loguru import logger
from langchain_chroma import Chroma
import chromadb
from config import settings
from rag.embedding_service import embedding_service
from utils.exceptions import VectorStoreException


class VectorStoreManager:
    """
    Handles initialization, updates, and safe tear-down cycles for ChromaDB.
    Guarantees that only one active collection context exists at any time.
    Uses clean collection drop strategies to prevent running SQLite connection panics on macOS.
    """

    def __init__(self) -> None:
        self.collection_name = "intelligent_lms_collection"
        logger.info(f"[VECTOR_STORE] Initializing VectorStoreManager with collection: '{self.collection_name}'")
        self._db_path = Path(settings.CHROMA_DB_DIR).resolve()

    def get_vector_store(self) -> Chroma:
        """
        Retrieves or initializes the operational persistent Chroma index instance.
        """
        logger.debug(f"[VECTOR_STORE] Fetching persistent Chroma link at: '{self._db_path}'")
        try:
            store = Chroma(
                collection_name=self.collection_name,
                embedding_function=embedding_service.get_client(),
                persist_directory=str(self._db_path)
            )
            logger.debug("[VECTOR_STORE] Persistent Chroma instance successfully instantiated.")
            return store
        except Exception as e:
            logger.exception("[VECTOR_STORE] [CRITICAL] Failed to link or boot persistent Chroma engine.")
            raise VectorStoreException(
                message="Could not link or connect to persistent vector storage framework.",
                details={"db_path": str(self._db_path), "error": str(e)}
            )

    def purge_vector_store(self) -> None:
        """
        Safely clears out all vectors from the database by dropping the active collection.
        Avoids physical unlinking of database files while the server process has active open file handles.
        """
        logger.warning(f"[VECTOR_STORE] Starting safe runtime purge of vector repository data hooks at: '{self._db_path}'")
        
        try:
            # Re-verify that the required base container directory paths are in place
            settings.create_required_directories()
            
            # Initialize a lightweight native PersistentClient to execute an atomic drop
            client = chromadb.PersistentClient(path=str(self._db_path))
            
            try:
                # Check if our target collection exists before attempting to delete it
                existing_collections = [c.name for c in client.list_collections()]
                if self.collection_name in existing_collections:
                    logger.debug(f"[VECTOR_STORE] Dropping existing collection collection schema: '{self.collection_name}'")
                    client.delete_collection(name=self.collection_name)
                    logger.info("[VECTOR_STORE] Collection completely dropped from the storage engine.")
                else:
                    logger.debug("[VECTOR_STORE] No matching pre-existing collection detected to purge.")
            except Exception as e:
                logger.warning(f"[VECTOR_STORE] Direct native client cleanup step skipped or unneeded: {str(e)}")

            # Create a brand new clean collection space inside the existing safe database instance
            client.get_or_create_collection(name=self.collection_name)
            logger.info("[VECTOR_STORE] Pristine database storage tracks successfully restored.")

        except Exception as e:
            logger.exception("[VECTOR_STORE] [PURGE ERROR] Failed to wipe collection context structures securely.")
            raise VectorStoreException(
                message="Failed to drop and reset previous database engine storage structures.",
                details={"db_path": str(self._db_path), "error_type": type(e).__name__}
            )


# Instantiate vector database manager globally for unified pipeline integration
vector_store_manager = VectorStoreManager()