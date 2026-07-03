from typing import List
from loguru import logger
from langchain_core.documents import Document
from rag.vector_store import vector_store_manager
from utils.exceptions import DatabaseEmptyException, VectorStoreException


class KnowledgeRetriever:
    """
    Handles similarity retrieval mechanics inside the RAG lifecycle.
    Queries the underlying ChromaDB index using localized SentenceTransformer embeddings,
    applying safe threshold assertions to handle empty database conditions.
    """

    def __init__(self, k_documents: int = 4) -> None:
        self.k_documents = k_documents
        logger.info(f"[RETRIEVER] Initializing KnowledgeRetriever with k={self.k_documents}")

    def retrieve_relevant_chunks(self, query: str) -> List[Document]:
        """
        Queries ChromaDB for the most contextually relevant document segments.

        Args:
            query (str): The search query or question.

        Returns:
            List[Document]: A list of relevant LangChain Document chunks.
        """
        logger.info(f"[RETRIEVER] Executing vector similarity search for query: '{query}'")
        
        try:
            # Fetch the active, shared vector database instance
            vector_store = vector_store_manager.get_vector_store()
            
            # Verify if the database actually contains documents before running the query
            try:
                collection_data = vector_store.get(limit=1)
                if not collection_data or not collection_data.get("ids"):
                    logger.warning("[RETRIEVER] ChromaDB collection contains zero indexed elements.")
                    raise DatabaseEmptyException(
                        message="The system knowledge base is currently completely empty. Please upload a PDF first."
                    )
            except DatabaseEmptyException as dee:
                raise dee
            except Exception as check_err:
                # If checking collection elements throws an error, the database likely doesn't exist yet
                logger.warning(f"[RETRIEVER] Error checking database status: {str(check_err)}")
                raise DatabaseEmptyException(
                    message="The vector index does not exist yet. Please upload a PDF file to initialize the workspace."
                )

            # Perform the core similarity search via LangChain
            results: List[Document] = vector_store.similarity_search(query, k=self.k_documents)
            logger.info(f"[RETRIEVER] Found {len(results)} matching document fragments in vector index.")
            
            for index, doc in enumerate(results):
                page_num = doc.metadata.get("page", "Unknown")
                logger.debug(f"[RETRIEVER] Match #{index + 1} -> Page: {page_num} | Length: {len(doc.page_content)} characters")
                
            return results

        except DatabaseEmptyException as dee:
            raise dee
        except Exception as e:
            logger.exception("[RETRIEVER] Unexpected crash during vector similarity matching processes.")
            raise VectorStoreException(
                message="Failed to retrieve matching segments from the semantic index database.",
                details={"underlying_error": str(e), "query_length": len(query)}
            )


# Instantiate retriever service globally for multi-agent or direct pipeline usage
knowledge_retriever = KnowledgeRetriever()