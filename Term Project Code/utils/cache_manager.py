import pickle
from pathlib import Path
from typing import Any, Optional
import time
from datetime import datetime, timedelta

class CacheManager:
    """Manage caching of research results."""
    
    def __init__(self, cache_dir: str = ".cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_cache_path(self, key: str) -> Path:
        """Get cache file path for key."""
        filename = hashlib.md5(key.encode()).hexdigest() + '.pickle'
        return self.cache_dir / filename
    
    def get(self, key: str, ttl: Optional[int] = None) -> Optional[Any]:
        """
        Get value from cache.
        
        Args:
            key: Cache key
            ttl: Time to live in seconds
            
        Returns:
            Cached value or None if not found/expired
        """
        cache_path = self._get_cache_path(key)
        
        if not cache_path.exists():
            return None
            
        try:
            with open(cache_path, 'rb') as f:
                timestamp, value = pickle.load(f)
                
            if ttl and time.time() - timestamp > ttl:
                cache_path.unlink()
                return None
                
            return value
            
        except Exception:
            return None
    
    def set(self, key: str, value: Any):
        """Set value in cache."""
        cache_path = self._get_cache_path(key)
        
        with open(cache_path, 'wb') as f:
            pickle.dump((time.time(), value), f)
    
    def clear(self, older_than: Optional[timedelta] = None):
        """
        Clear cache files.
        
        Args:
            older_than: Only clear files older than this
        """
        for cache_file in self.cache_dir.glob('*.pickle'):
            if older_than:
                mtime = datetime.fromtimestamp(cache_file.stat().st_mtime)
                if datetime.now() - mtime > older_than:
                    cache_file.unlink()
            else:
                cache_file.unlink()
