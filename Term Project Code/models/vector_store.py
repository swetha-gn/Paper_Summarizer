# models/vector_store.py
from typing import List, Dict, Optional
from langchain_community.vectorstores import FAISS
from langchain.docstore.document import Document
from langchain_openai import OpenAIEmbeddings
from pathlib import Path
import pickle
from config.config import Config
from utils.logger import get_logger

logger = get_logger(__name__)

class VectorStore:
    def __init__(self):
        """Initialize the vector store."""
        self.embeddings = OpenAIEmbeddings(openai_api_key=Config.OPENAI_API_KEY)
        self.index_path = Path(Config.VECTOR_STORE_PATH) / "faiss_index"
        self.store = self._load_or_create_store()

    def _load_or_create_store(self) -> FAISS:
        """Load existing vector store or create a new one."""
        try:
            if (self.index_path / "index.faiss").exists() and (self.index_path / "index.pkl").exists():
                logger.info("Loading existing FAISS index")
                return FAISS.load_local(
                    str(self.index_path),
                    self.embeddings
                )
            else:
                logger.info("Creating new FAISS index")
                return FAISS.from_texts(
                    [""], 
                    self.embeddings,
                    metadatas=[{}]
                )
        except Exception as e:
            logger.error(f"Error loading/creating vector store: {str(e)}")
            raise

    async def store_embeddings(self, texts: List[str], metadata: List[Dict]) -> None:
        """Store documents with their metadata."""
        try:
            
            new_store = FAISS.from_texts(
                texts,
                self.embeddings,
                metadatas=metadata
            )
            
            
            if self.store is not None:
                self.store.merge_from(new_store)
            else:
                self.store = new_store
            
    
            self._save_store()
            
            logger.info(f"Successfully stored {len(texts)} documents")
            
        except Exception as e:
            logger.error(f"Error storing documents: {str(e)}")
            raise

    async def search_similar(self, query: str, limit: int = 5) -> List[Dict]:
        """Search for similar documents."""
        try:
            if self.store is None:
                logger.warning("No documents in vector store")
                return []
            
            results = self.store.similarity_search_with_relevance_scores(
                query,
                k=limit
            )
            
            return [
                {
                    'metadata': doc.metadata,
                    'score': score  
                }
                for doc, score in results
            ]
            
        except Exception as e:
            logger.error(f"Error searching documents: {str(e)}")
            return []

    def _save_store(self) -> None:
        """Save the vector store to disk."""
        try:
            self.index_path.mkdir(parents=True, exist_ok=True)
            self.store.save_local(str(self.index_path))
            logger.info(f"Saved vector store to {self.index_path}")
        except Exception as e:
            logger.error(f"Error saving vector store: {str(e)}")
            raise

    def clear_store(self) -> None:
        """Clear the vector store."""
        try:
            if self.index_path.exists():
                for file in self.index_path.glob("*"):
                    file.unlink()
                self.index_path.rmdir()
            self.store = self._load_or_create_store()
            logger.info("Cleared vector store")
        except Exception as e:
            logger.error(f"Error clearing vector store: {str(e)}")
            raise