from pathlib import Path
from typing import List
from loguru import logger
from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from rag.vector_store import vector_store_manager
from utils.exceptions import FileUploadException


class DocumentIngestionPipeline:
    """
    Orchestrates the granular, end-to-end ingestion pipeline for documents.
    Handles physical parsing, recursive character chunk slicing, and database registration.
    Enforces the single-document rule by purging previous stores before processing.
    """

    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 150) -> None:
        logger.info(f"[INGEST] Initializing Ingestion Pipeline (ChunkSize: {chunk_size}, Overlap: {chunk_overlap})")
        self._text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            is_separator_regex=False
        )

    def process_pdf(self, file_path: Path) -> int:
        """
        Executes the extraction and indexing workflow on a specified PDF asset.
        
        Args:
            file_path (Path): Path pointing to the target local file.
            
        Returns:
            int: The absolute count of structural chunks successfully registered.
        """
        resolved_path = file_path.resolve()
        logger.info(f"[INGEST] Starting document ingestion stream for file: '{resolved_path}'")

        if not resolved_path.exists():
            logger.critical(f"[INGEST] Target file asset does not exist on disk: '{resolved_path}'")
            raise FileUploadException(
                message="Target parsing source asset cannot be resolved on disk layer.",
                details={"provided_path": str(resolved_path)}
            )

        try:
            # 1. Enforce strict single-document rules by completely wiping out old states first
            logger.warning("[INGEST] Invoking downstream database and workspace cache reset.")
            vector_store_manager.purge_vector_store()

            # 2. Extract textual data from raw layout streams using PyPDFLoader
            logger.info(f"[INGEST] Parsing layout pages from target stream: '{resolved_path.name}'")
            loader = PyPDFLoader(str(resolved_path))
            raw_documents: List[Document] = loader.load()
            
            logger.info(f"[INGEST] Successfully extracted {len(raw_documents)} raw page document slices.")
            if not raw_documents:
                raise FileUploadException(
                    message="Target PDF document contains no renderable text layers or pages.",
                    details={"filename": resolved_path.name}
                )

            # 3. Standardize and inject uniform 1-indexed page bounds into chunk descriptors
            for page_index, doc in enumerate(raw_documents):
                # Ensure structural pages carry clear indicators for citations
                doc.metadata["page"] = doc.metadata.get("page", page_index + 1)
                doc.metadata["source_filename"] = resolved_path.name

            # 4. Partition massive page nodes into tightly bounded contexts
            logger.debug(f"[INGEST] Segmenting {len(raw_documents)} pages into atomic chunks.")
            split_chunks: List[Document] = self._text_splitter.split_documents(raw_documents)
            logger.info(f"[INGEST] Generated {len(split_chunks)} discrete textual contexts for embedding.")

            # 5. Populate pristine vector records back into the persistent framework
            logger.info("[INGEST] Streaming segments to the persistent Chroma collection instance.")
            vector_store = vector_store_manager.get_vector_store()
            vector_store.add_documents(documents=split_chunks)
            
            logger.info(f"[INGEST] Processing finalized. Added {len(split_chunks)} elements to ChromaDB successfully.")
            return len(split_chunks)

        except FileUploadException as fe:
            # Pass custom domain errors up cleanly without re-wrapping
            raise fe
        except Exception as e:
            logger.exception(f"[INGEST] [PIPELINE CRASH] Unhandled failure during compilation of '{resolved_path.name}'")
            raise FileUploadException(
                message="Unexpected failure encountered during document semantic ingestion phases.",
                details={"error_message": str(e), "filename": resolved_path.name}
            )


# Instantiate pipeline singleton for shared access across upload endpoints
document_ingestion_pipeline = DocumentIngestionPipeline()