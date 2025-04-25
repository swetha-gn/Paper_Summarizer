import fitz  
import re
import logging
import os
from typing import Dict, List, Optional
from pathlib import Path
import asyncio
from utils.logger import get_logger
from utils.text_processor import TextProcessor
from utils.error_handler import handle_errors
from config.config import Config

logger = get_logger(__name__)

class PDFProcessor:
    def __init__(self, papers_dir: str = Config.PAPERS_DIR):
        """Initialize the PDF processor."""
        self.papers_dir = Path(papers_dir)
        self.processed_dir = self.papers_dir / "processed"
        self.ensure_directories()
        self.text_processor = TextProcessor()

    def ensure_directories(self):
        """Create necessary directories if they don't exist."""
        try:
            self.papers_dir.mkdir(parents=True, exist_ok=True)
            self.processed_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created/verified directories: {self.papers_dir}, {self.processed_dir}")
        except Exception as e:
            logger.error(f"Error creating directories: {str(e)}")
            raise

    async def batch_process_papers(self, papers: List[Dict]) -> List[Dict]:
        """Process multiple papers concurrently."""
        try:
            processed_papers = []
            for paper in papers:
                try:
                    processed_paper = await self.process_paper(paper)
                    if processed_paper:
                        processed_papers.append(processed_paper)
                except Exception as e:
                    logger.error(f"Error processing paper {paper.get('title', 'Unknown')}: {str(e)}")
                    continue
            
            logger.info(f"Successfully processed {len(processed_papers)} out of {len(papers)} papers")
            return processed_papers

        except Exception as e:
            logger.error(f"Error in batch processing: {str(e)}")
            return []

    async def process_paper(self, paper: Dict) -> Optional[Dict]:
        """Process a single paper."""
        try:
            local_path = paper.get('local_path')
            if not local_path or not Path(local_path).exists():
                logger.error(f"Invalid PDF path for paper: {paper.get('title', 'Unknown')}")
                return None

            logger.info(f"Processing paper: {Path(local_path).name}")

            
            sections = await self._extract_text(local_path)
            
            
            cleaned_sections = {
                section: self.text_processor.clean_text(content)
                for section, content in sections.items()
            }

            
            output_file = self.processed_dir / f"{Path(local_path).stem}_processed.txt"
            await self._save_processed_text(output_file, cleaned_sections)

            paper.update({
                'processed_path': str(output_file),
                'sections': cleaned_sections
            })

            return paper

        except Exception as e:
            logger.error(f"Error processing paper {paper.get('title', 'Unknown')}: {str(e)}")
            return None

    async def _extract_text(self, pdf_path: str) -> Dict[str, str]:
        """Extract text from PDF with section identification."""
        try:
            doc = fitz.open(pdf_path)
            
            sections = {
                'title': '',
                'abstract': '',
                'introduction': '',
                'methods': '',
                'results': '',
                'discussion': '',
                'conclusion': '',
                'references': '',
                'full_text': ''
            }
            
            full_text = []
            current_section = None

            for page_num in range(len(doc)):
                page = doc[page_num]
                text = await asyncio.to_thread(page.get_text)
                full_text.append(text)
                
                
                if page_num == 0:
                    sections['title'] = self._extract_title(text)
                    sections['abstract'] = self._extract_abstract(text)

            
                section_markers = self._identify_section_markers(text.lower())
                
                
                for marker in section_markers:
                    current_section = marker
                    
                
                if current_section and current_section in sections:
                    sections[current_section] += f"\n{text}"

            
            sections['full_text'] = '\n'.join(full_text)
            
    
            doc.close()
            
            return sections

        except Exception as e:
            logger.error(f"Error extracting text from {pdf_path}: {str(e)}")
            raise

    def _extract_title(self, text: str) -> str:
        """Extract title from first page text."""
        try:
            lines = text.split('\n')
            for line in lines[:3]:
                if len(line.strip()) > 10 and not line.lower().startswith(('abstract', 'introduction')):
                    return line.strip()
            return ""
        except Exception as e:
            logger.warning(f"Error extracting title: {str(e)}")
            return ""

    def _extract_abstract(self, text: str) -> str:
        """Extract abstract from text."""
        try:
            match = re.search(
                r'abstract[:\s]+(.*?)(?=\n\s*(?:introduction|1\.|\n{2,}))',
                text.lower(),
                re.DOTALL | re.IGNORECASE
            )
            if match:
                return match.group(1).strip()
            return ""
        except Exception as e:
            logger.warning(f"Error extracting abstract: {str(e)}")
            return ""

    def _identify_section_markers(self, text: str) -> List[str]:
        """Identify section markers in text."""
        markers = []
        section_patterns = {
            'introduction': r'\b(?:introduction|1\.?\s+introduction)\b',
            'methods': r'\b(?:methods|methodology|materials\s+and\s+methods|experimental|2\.?\s+methods)\b',
            'results': r'\b(?:results|findings|3\.?\s+results)\b',
            'discussion': r'\b(?:discussion|4\.?\s+discussion)\b',
            'conclusion': r'\b(?:conclusion|conclusions|5\.?\s+conclusion)\b',
            'references': r'\b(?:references|bibliography)\b'
        }

        for section, pattern in section_patterns.items():
            if re.search(pattern, text, re.IGNORECASE):
                markers.append(section)

        return markers

    async def _save_processed_text(self, output_file: Path, sections: Dict[str, str]):
        """Save processed text to file."""
        try:

            with open(output_file, 'w', encoding='utf-8') as f:
                for section, content in sections.items():
                    f.write(f"=== {section.upper()} ===\n")
                    f.write(content)
                    f.write('\n\n')
                    
            logger.info(f"Saved processed text to: {output_file}")

        except Exception as e:
            logger.error(f"Error saving processed text: {str(e)}")
            raise

async def main():
    """Test function for PDF processor."""
    try:
        processor = PDFProcessor()
        
        
        paper = {
            'title': 'Example Paper',
            'local_path': 'path_to_your_test.pdf' 
        }
        

        result = await processor.process_paper(paper)
        
        if result:
            print(f"Successfully processed paper: {result['title']}")
            print("Sections found:")
            for section, content in result['sections'].items():
                if content:
                    print(f"\n{section.upper()}:")
                    print(content[:200] + "..." if len(content) > 200 else content)
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())