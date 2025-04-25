import pandas as pd
import asyncio
import sys
from pathlib import Path
from typing import List, Dict
from bert_score import score
import torch

project_root = Path(__file__).parent
sys.path.append(str(project_root))

from models.embedding_model import EmbeddingModel
from models.vector_store import VectorStore
from models.llm_model import LLMModel
from modules.paper_downloader import PaperDownloader
from modules.pdf_processor import PDFProcessor
from modules.paper_summarizer import PaperSummarizer
from config.config import Config
from utils.logger import get_logger

logger = get_logger(__name__)

class ResearchAssistant:
    def __init__(self):
        """Initialize components of the Research Assistant."""
        try:
            logger.info("Initializing Research Assistant...")
            self.vector_store = VectorStore()
            self.llm_model = LLMModel()
            self.downloader = PaperDownloader()
            self.processor = PDFProcessor()
            self.summarizer = PaperSummarizer()
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
            logger.info("Research Assistant initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing Research Assistant: {str(e)}")
            raise

    async def evaluate_summaries(self, summaries: List[Dict]) -> pd.DataFrame:
        """Evaluate summaries using BERTScore."""
        try:
            evaluation_results = []
            generated_summaries = []
            reference_summaries = []
            titles = []
            
            for summary in summaries:
                if 'summaries' in summary:
                    generated = summary['summaries'].get('overall_summary', '')
                    reference = summary['summaries'].get('abstract_summary', '')
                    
                    if generated and reference:
                        generated_summaries.append(generated)
                        reference_summaries.append(reference)
                        titles.append(summary.get('title', 'Unknown'))
            
            if generated_summaries:
                # Calculate BERTScore
                P, R, F1 = score(
                    cands=generated_summaries,
                    refs=reference_summaries,
                    lang='en',
                    model_type='microsoft/deberta-xlarge-mnli',
                    device=self.device
                )
                
                # Create results for each summary
                for i in range(len(titles)):
                    result = {
                        'title': titles[i],
                        'bertscore_precision': P[i].item(),
                        'bertscore_recall': R[i].item(),
                        'bertscore_f1': F1[i].item()
                    }
                    evaluation_results.append(result)
            
            # Create DataFrame and calculate averages
            df = pd.DataFrame(evaluation_results)
            if not df.empty:
                averages = df.select_dtypes(include=['float64']).mean()
                averages['title'] = 'AVERAGE'
                df = pd.concat([df, pd.DataFrame([averages])], ignore_index=True)
            
            # Save results
            results_path = Path(Config.SUMMARIES_DIR) / "evaluation_results.csv"
            df.to_csv(results_path, index=False)
            logger.info(f"Saved evaluation results to {results_path}")
            
            return df
            
        except Exception as e:
            logger.error(f"Error evaluating summaries: {str(e)}")
            return pd.DataFrame()

    async def process_research_query(self, query: str) -> str:
        """Process a research query and return structured response."""
        try:
            logger.info(f"Processing research query: {query}")
            
            similar_papers = await self.vector_store.search_similar(query, limit=Config.MAX_RESULTS)
            logger.info(f"Found {len(similar_papers)} similar papers")
            
            if len(similar_papers) < Config.MAX_PAPERS:
                logger.info("Downloading additional papers...")
                papers = await self.downloader.download_papers(query, Config.MAX_PAPERS)
                logger.info(f"Downloaded {len(papers)} new papers")
                
                if papers:
                    processed_papers = await self.processor.batch_process_papers(papers)
                    logger.info(f"Processed {len(processed_papers)} papers")
                    
                    summaries = await self.summarizer.process_all_papers(processed_papers)
                    logger.info(f"Generated summaries for {len(summaries)} papers")
                    
                    if summaries:
                        # Evaluate summaries
                        logger.info("Evaluating summaries...")
                        evaluation_results = await self.evaluate_summaries(summaries)
                        
                        if not evaluation_results.empty:
                            print("\nSummary Evaluation Results:")
                            print("-------------------------")
                            print(f"BERTScore P: {evaluation_results['bertscore_precision'].mean():.4f}")
                            print(f"BERTScore R: {evaluation_results['bertscore_recall'].mean():.4f}")
                            print(f"BERTScore F1: {evaluation_results['bertscore_f1'].mean():.4f}")
                        
                        # Store embeddings
                        texts = []
                        metadata = []
                        
                        for summary in summaries:
                            if 'summaries' in summary and 'overall_summary' in summary['summaries']:
                                texts.append(summary['summaries']['overall_summary'])
                                metadata.append({
                                    'title': summary.get('title', 'Unknown'),
                                    'authors': summary.get('authors', []),
                                    'url': summary.get('url', ''),
                                    'summary': summary['summaries']['overall_summary']
                                })
                        
                        if texts:
                            await self.vector_store.store_embeddings(texts, metadata)
                            logger.info("Stored documents in vector store")
                            
                            similar_papers = await self.vector_store.search_similar(
                                query, 
                                limit=Config.MAX_RESULTS
                            )
                            logger.info(f"Found {len(similar_papers)} papers after update")
            
            if similar_papers:
                try:
                    response = await self.llm_model.generate_research_response(
                        query, 
                        similar_papers
                    )
                    logger.info("Generated research response")
                    return response
                except Exception as e:
                    logger.error(f"Error generating research response: {str(e)}")
                    return self._generate_fallback_response(similar_papers)
            else:
                logger.warning("No relevant papers found")
                return ("I couldn't find any relevant papers for your query. "
                       "Please try a different search term or topic.")
            
        except Exception as e:
            logger.error(f"Error processing research query: {str(e)}")
            raise

    def _generate_fallback_response(self, papers: List[Dict]) -> str:
        """Generate a basic response when LLM fails."""
        try:
            response = "Here are the most relevant papers I found:\n\n"
            
            for i, paper in enumerate(papers, 1):
                metadata = paper['metadata']
                response += f"{i}. {metadata['title']}\n"
                if metadata.get('authors'):
                    response += f"   Authors: {', '.join(metadata['authors'])}\n"
                if metadata.get('summary'):
                    summary = metadata['summary'][:300] + "..." if len(metadata['summary']) > 300 else metadata['summary']
                    response += f"   Summary: {summary}\n"
                if metadata.get('url'):
                    response += f"   URL: {metadata['url']}\n"
                response += "\n"
                
            return response
            
        except Exception as e:
            logger.error(f"Error generating fallback response: {str(e)}")
            return ("I found some relevant papers but encountered an error processing them. "
                   "Please try your query again.")

async def main():
    """Main function to run the Research Assistant."""
    try:
        assistant = ResearchAssistant()
        logger.info("Research Assistant initialized")
        
        print("\nWelcome to the Research Paper Assistant!")
        print("----------------------------------------")
        query = input("\nEnter your research topic or question: ")
        
        print("\nProcessing your query... This may take a few minutes.")
        print("(The assistant will search for relevant papers and generate a comprehensive response)")
        
        response = await assistant.process_research_query(query)
        
        print("\nResearch Analysis:")
        print("------------------")
        print(response)
        
    except Exception as e:
        print(f"\nAn error occurred: {str(e)}")
        logger.error(f"Error in main: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())