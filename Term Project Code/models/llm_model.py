from openai import OpenAI
import asyncio
from typing import Dict, List
from config.config import Config
from utils.logger import get_logger

logger = get_logger(__name__)

class LLMModel:
    def __init__(self):
        """Initialize the LLM model."""
        self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
        self.model = Config.LLM_MODEL

    async def generate_research_response(self, query: str, similar_papers: List[Dict]) -> str:
        """Generate a comprehensive research response."""
        try:
            papers_text = ""
            for i, paper in enumerate(similar_papers, 1):
                papers_text += f"\nPaper {i}:\n"
                papers_text += f"Title: {paper['metadata'].get('title', 'N/A')}\n"
                papers_text += f"Summary: {paper['metadata'].get('summary', 'N/A')}\n"
                papers_text += f"Relevance Score: {paper.get('score', 0):.2f}\n"
                papers_text += "---\n"

            prompt = f"""Based on the research question: "{query}"

Here are the relevant papers and their summaries:

{papers_text}

Please provide a comprehensive response that:
1. Summarizes the main findings relevant to the research question
2. Identifies key methodologies used in the field
3. Points out any gaps or areas needing further research
4. Suggests potential research directions
5. Lists the most significant papers and their contributions

Structure the response in a clear, academic format."""

            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a research assistant specializing in analyzing and synthesizing academic papers."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=2000
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            logger.error(f"Error generating research response: {str(e)}")
            return "I apologize, but I encountered an error while generating the research response. Please try again."