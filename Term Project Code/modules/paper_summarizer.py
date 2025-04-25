import pandas as pd
from openai import OpenAI
import asyncio
from typing import Dict, List, Optional
from config.config import Config
from utils.logger import get_logger

logger = get_logger(__name__)

class PaperSummarizer:
    def __init__(self):
        """Initialize the paper summarizer."""
        self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
        self.model = Config.LLM_MODEL

    async def process_all_papers(self, papers: List[Dict]) -> List[Dict]:
        """Process all papers to generate summaries."""
        try:
            processed_papers = []
            logger.info(f"Starting to process {len(papers)} papers")

            for idx, paper in enumerate(papers, 1):
                try:
                    logger.info(f"Processing paper {idx}/{len(papers)}: {paper.get('title', 'Unknown')}")
                    
                    paper_with_summaries = {
                        'title': paper.get('title', 'Unknown'),
                        'authors': paper.get('authors', []),
                        'url': paper.get('pdf_url', ''),
                        'local_path': paper.get('local_path', ''),
                        'processed_path': paper.get('processed_path', ''),
                        'summaries': {}
                    }

                    
                    summaries = await self.summarize_paper(paper)
                    if summaries:
                        paper_with_summaries['summaries'] = summaries
                        processed_papers.append(paper_with_summaries)
                        logger.info(f"Successfully processed paper {idx}/{len(papers)}")
                    else:
                        logger.warning(f"No summaries generated for paper {idx}/{len(papers)}")

                except Exception as e:
                    logger.error(f"Error processing paper {idx}/{len(papers)}: {str(e)}")
                    continue

            logger.info(f"Successfully processed {len(processed_papers)} out of {len(papers)} papers")
            return processed_papers

        except Exception as e:
            logger.error(f"Error in batch processing: {str(e)}")
            return []

    async def summarize_paper(self, paper: Dict) -> Optional[Dict[str, str]]:
        """Generate summaries for a single paper."""
        try:
            sections = paper.get('sections', {})
            if not sections:
                logger.warning(f"No sections found for paper: {paper.get('title', 'Unknown')}")
                return None

            summaries = {}
            
            
            for section_name, content in sections.items():
                if content and section_name != 'full_text':
                    summary = await self._generate_section_summary(content, section_name)
                    if summary:
                        summaries[f"{section_name}_summary"] = summary

           
            overall_summary = await self._generate_overall_summary(
                sections.get('title', ''),
                sections.get('abstract', ''),
                sections.get('introduction', '')
            )
            if overall_summary:
                summaries['overall_summary'] = overall_summary

            return summaries if summaries else None

        except Exception as e:
            logger.error(f"Error summarizing paper: {str(e)}")
            return None

    async def _generate_section_summary(self, text: str, section_name: str) -> Optional[str]:
        """Generate summary for a specific section."""
        try:
            if not text.strip():
                return None

            section_prompts = {
                'title': "Extract the main topic and key terms from this title:",
                'abstract': "Summarize this abstract in 2-3 sentences:",
                'introduction': "Summarize the key points of this introduction:",
                'methods': "Provide a clear summary of the methodology used:",
                'results': "Summarize the main results and findings:",
                'discussion': "Summarize the key points of discussion:",
                'conclusion': "Summarize the main conclusions and implications:"
            }
            
            prompt = section_prompts.get(section_name.lower(), "Summarize this section:")
            
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a research paper analysis assistant. Provide clear, concise summaries of academic content."},
                    {"role": "user", "content": f"{prompt}\n\n{text[:4000]}"}
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            return response.choices[0].message.content.strip() if response.choices else None

        except Exception as e:
            logger.error(f"Error generating summary for {section_name}: {str(e)}")
            return None

    async def _generate_overall_summary(self, title: str, abstract: str, introduction: str) -> Optional[str]:
        """Generate overall paper summary."""
        try:
            if not (abstract or introduction):
                return None

            prompt = f"""Provide a comprehensive summary of this research paper:

Title: {title}

Abstract:
{abstract[:2000]}

Introduction:
{introduction[:2000]}

Please include:
1. Main research objectives and motivation
2. Key methodology used
3. Principal findings and results
4. Major conclusions and implications
5. Significance and impact in the field
"""

            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a research paper analysis assistant. Provide clear, comprehensive summaries of academic papers."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1000
            )
            
            return response.choices[0].message.content.strip() if response.choices else None

        except Exception as e:
            logger.error(f"Error generating overall summary: {str(e)}")
            return None
    
    



async def evaluate_summaries(self, summaries: List[Dict]) -> pd.DataFrame:
    """Evaluate generated summaries using BERTScore."""
    try:
        evaluator = SummaryEvaluator()
        
        evaluation_data = []
        for summary in summaries:
            if 'summaries' in summary:
                evaluation_data.append({
                    'title': summary.get('title', 'Unknown'),
                    'generated_summary': summary['summaries'].get('overall_summary', ''),
                    'reference_summary': summary['summaries'].get('abstract_summary', '')
                })
        
        results = evaluator.evaluate_batch(evaluation_data)
        
        # Save results
        output_path = os.path.join(Config.SUMMARIES_DIR, 'evaluation_results.csv')
        evaluator.save_evaluation(results, output_path)
        
        return results
        
    except Exception as e:
        logger.error(f"Error evaluating summaries: {str(e)}")
        return pd.DataFrame()