import re
from typing import Dict
import unicodedata

class TextProcessor:
    """Utility class for text processing operations."""
    
    @staticmethod
    def clean_text(text: str) -> str:
        """Clean and normalize text."""
        # Normalize unicode characters
        text = unicodedata.normalize('NFKC', text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters
        text = re.sub(r'[^\w\s\.\,\;\:\!\?\-\']', '', text)
        
        return text.strip()
    
    @staticmethod
    def extract_sections(text: str) -> Dict[str, str]:
        """Extract sections from text using common headers."""
        sections = {
            'abstract': '',
            'introduction': '',
            'methods': '',
            'results': '',
            'discussion': '',
            'conclusion': '',
            'references': ''
        }
        
        patterns = {
            'abstract': r'abstract(.+?)(?=introduction|\n\n)',
            'introduction': r'introduction(.+?)(?=methods|methodology|materials|\n\n)',
            'methods': r'(?:methods|methodology|materials)(.+?)(?=results|\n\n)',
            'results': r'results(.+?)(?=discussion|\n\n)',
            'discussion': r'discussion(.+?)(?=conclusion|references|\n\n)',
            'conclusion': r'conclusion(.+?)(?=references|\n\n)',
            'references': r'references(.+?)(?=\n\n|$)'
        }
        
        for section, pattern in patterns.items():
            match = re.search(pattern, text.lower(), re.DOTALL | re.IGNORECASE)
            if match:
                sections[section] = match.group(1).strip()
        
        return sections