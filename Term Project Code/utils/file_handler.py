import os
import json
import hashlib
from pathlib import Path
from typing import Dict, Any, Union
from datetime import datetime

class FileHandler:
    """Utility class for file operations."""
    
    def __init__(self, base_dir: str = "."):
        self.base_dir = Path(base_dir)
        
    def ensure_directory(self, path: Union[str, Path]) -> Path:
        """Create directory if it doesn't exist."""
        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)
        return path
    
    def safe_filename(self, filename: str) -> str:
        """Create safe filename from string."""
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '')
        return filename.strip()
    
    def get_unique_filename(self, directory: Path, filename: str) -> Path:
        """Get unique filename by adding number if file exists."""
        stem = Path(filename).stem
        suffix = Path(filename).suffix
        counter = 1
        
        while True:
            if counter == 1:
                new_filename = f"{stem}{suffix}"
            else:
                new_filename = f"{stem}_{counter}{suffix}"
            
            full_path = directory / new_filename
            if not full_path.exists():
                return full_path
            counter += 1
    
    def save_json(self, data: Dict[str, Any], filepath: Union[str, Path], indent: int = 2):
        """Save data as JSON file."""
        filepath = Path(filepath)
        self.ensure_directory(filepath.parent)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=indent)
    
    def load_json(self, filepath: Union[str, Path]) -> Dict[str, Any]:
        """Load data from JSON file."""
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)