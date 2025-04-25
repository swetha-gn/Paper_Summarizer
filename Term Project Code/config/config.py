import os
from pathlib import Path
from dotenv import load_dotenv


load_dotenv()

class Config:
    """Configuration settings for the Research Assistant."""
    
    
    ROOT_DIR = Path(__file__).parent.parent
    DATA_DIR = ROOT_DIR / "data"
    PAPERS_DIR = ROOT_DIR / "research_papers"
    PROCESSED_DIR = PAPERS_DIR / "processed"
    SUMMARIES_DIR = PAPERS_DIR / "summaries"
    VECTOR_STORE_PATH = ROOT_DIR / "vector_store"
    
    
    for directory in [DATA_DIR, PAPERS_DIR, PROCESSED_DIR, SUMMARIES_DIR, VECTOR_STORE_PATH]:
        directory.mkdir(parents=True, exist_ok=True)
    
    
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    if not OPENAI_API_KEY:
        raise ValueError("OpenAI API key not found in environment variables")
    
    
    EMBEDDING_MODEL = "text-embedding-ada-002"
    LLM_MODEL = "gpt-3.5-turbo"
    
    
    SIMILARITY_THRESHOLD = 0.8
    MAX_RESULTS = 5
    
    
    MAX_PAPERS = 10
    DOWNLOAD_TIMEOUT = 30
    MAX_RETRIES = 3
    RETRY_DELAY = 5