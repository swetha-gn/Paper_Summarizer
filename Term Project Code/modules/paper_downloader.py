import arxiv
import aiohttp
import asyncio
import os
from typing import List, Dict
from pathlib import Path
from utils.logger import get_logger
from utils.error_handler import handle_errors
from config.config import Config

logger = get_logger(__name__)

class PaperDownloader:
    def __init__(self):
        """Initialize the PaperDownloader."""
        self.output_dir = Config.PAPERS_DIR
        self.ensure_directories()

    def ensure_directories(self):
        """Create necessary directories if they don't exist."""
        try:
            os.makedirs(self.output_dir, exist_ok=True)
            logger.info(f"Created/verified output directory: {self.output_dir}")
        except Exception as e:
            logger.error(f"Error creating directories: {str(e)}")
            raise

    async def search_papers(self, query: str, max_results: int = 50) -> List[Dict]:
        """Search for papers on arXiv."""
        try:
            client = arxiv.Client()
            search = arxiv.Search(
                query=query,
                max_results=max_results,
                sort_by=arxiv.SortCriterion.Relevance
            )

            papers = []
            results = list(client.results(search))
            
            for result in results:
                papers.append({
                    'title': result.title,
                    'authors': [author.name for author in result.authors],
                    'abstract': result.summary,
                    'pdf_url': result.pdf_url,
                    'arxiv_id': result.entry_id.split('/')[-1],
                    'published_date': result.published.strftime('%Y-%m-%d'),
                })

            logger.info(f"Successfully found {len(papers)} papers matching the query")
            return papers

        except Exception as e:
            logger.error(f"Error searching papers: {str(e)}")
            raise

    async def download_paper(self, session: aiohttp.ClientSession, paper: Dict) -> Dict:
        """Download a single paper."""
        try:
            filename = f"{paper['arxiv_id']}.pdf"
            filepath = os.path.join(self.output_dir, filename)

            
            if os.path.exists(filepath):
                paper['local_path'] = filepath
                logger.info(f"Paper already exists: {filename}")
                return paper

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }

           
            for attempt in range(Config.MAX_RETRIES):
                try:
                    async with session.get(paper['pdf_url'], headers=headers, timeout=Config.DOWNLOAD_TIMEOUT) as response:
                        if response.status == 200:
                            with open(filepath, 'wb') as f:
                                while True:
                                    chunk = await response.content.read(8192)
                                    if not chunk:
                                        break
                                    f.write(chunk)
                            
                            paper['local_path'] = filepath
                            logger.info(f"Successfully downloaded: {filename}")
                            return paper
                        else:
                            logger.warning(f"Failed to download {filename}: {response.status}")
                            
                except asyncio.TimeoutError:
                    if attempt < Config.MAX_RETRIES - 1:
                        await asyncio.sleep(Config.RETRY_DELAY * (attempt + 1))
                        continue
                    logger.error(f"Timeout downloading {filename} after {Config.MAX_RETRIES} attempts")
                    return None
                    
                except Exception as e:
                    if attempt < Config.MAX_RETRIES - 1:
                        await asyncio.sleep(Config.RETRY_DELAY * (attempt + 1))
                        continue
                    logger.error(f"Error downloading {filename}: {str(e)}")
                    return None

            return None

        except Exception as e:
            logger.error(f"Error downloading {paper.get('title', 'Unknown')}: {str(e)}")
            return None

    async def download_papers(self, query: str, max_results: int = 10) -> List[Dict]:
        """Download multiple papers based on query."""
        try:
            # Search for papers
            papers = await self.search_papers(query, max_results)
            if not papers:
                logger.warning("No papers found matching the query")
                return []

            # Download papers concurrently
            async with aiohttp.ClientSession() as session:
                tasks = [
                    self.download_paper(session, paper)
                    for paper in papers
                ]
                results = await asyncio.gather(*tasks)

            # Filter out failed downloads
            successful_downloads = [paper for paper in results if paper is not None]
            
            logger.info(f"Successfully downloaded {len(successful_downloads)} out of {len(papers)} papers")
            return successful_downloads

        except Exception as e:
            logger.error(f"Error downloading papers: {str(e)}")
            raise

async def main():
    """Test the paper downloader."""
    try:
        downloader = PaperDownloader()
        query = "machine learning"
        papers = await downloader.download_papers(query, max_results=2)
        
        print(f"\nDownloaded {len(papers)} papers:")
        for paper in papers:
            print(f"\nTitle: {paper['title']}")
            print(f"Authors: {', '.join(paper['authors'])}")
            print(f"Local path: {paper['local_path']}")
            
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())