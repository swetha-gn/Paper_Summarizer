from openai import OpenAI
import asyncio
from typing import List
from config.config import Config
from utils.logger import get_logger
from utils.error_handler import handle_errors

logger = get_logger(__name__)

class EmbeddingModel:
    def __init__(self):
        """Initialize the embedding model with OpenAI client."""
        self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
        self.model = Config.EMBEDDING_MODEL

    @handle_errors(logger=logger)
    async def get_embedding(self, text: str) -> List[float]:
        """Generate embedding for a single text."""
        try:
            response = await asyncio.to_thread(
                self.client.embeddings.create,
                model=self.model,
                input=[text]  
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Error generating embedding: {str(e)}")
            raise

    @handle_errors(logger=logger)
    async def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts."""
        try:
            if not texts:
                return []
            
            response = await asyncio.to_thread(
                self.client.embeddings.create,
                model=self.model,
                input=texts
            )
            return [data.embedding for data in response.data]
        except Exception as e:
            logger.error(f"Error generating embeddings: {str(e)}")
            raise