import os
import redis
from typing import Optional

class RedisStore:
    """Redis storage layer for URL shortener service."""
    
    def __init__(self, host: str = None, port: int = 6379, db: int = 0):
        """
        Initialize Redis connection.
        
        Args:
            host: Redis host (defaults to REDIS_HOST env var or 'localhost')
            port: Redis port (defaults to 6379)
            db: Redis database number (defaults to 0)
        """
        self.host = host or os.getenv('REDIS_HOST', 'localhost')
        self.port = port
        self.db = db
        self.client = redis.Redis(
            host=self.host,
            port=self.port,
            db=self.db,
            decode_responses=True  # Automatically decode bytes to strings
        )
    
    def set_url(self, short_code: str, long_url: str) -> None:
        """
        Store a URL mapping (short code -> long URL).
        
        Args:
            short_code: The shortened URL code
            long_url: The original long URL
        """
        self.client.set(f"url:{short_code}", long_url)
    
    def get_url(self, short_code: str) -> Optional[str]:
        """
        Retrieve the original URL for a given short code.
        
        Args:
            short_code: The shortened URL code
            
        Returns:
            The original long URL, or None if not found
        """
        return self.client.get(f"url:{short_code}")
    
    def set_reverse_mapping(self, long_url: str, short_code: str) -> None:
        """
        Store a reverse mapping (long URL -> short code).
        
        Args:
            long_url: The original long URL
            short_code: The shortened URL code
        """
        self.client.set(f"reverse:{long_url}", short_code)
    
    def get_short_code(self, long_url: str) -> Optional[str]:
        """
        Check if a URL has already been shortened.
        
        Args:
            long_url: The original long URL
            
        Returns:
            The short code if it exists, or None if not found
        """
        return self.client.get(f"reverse:{long_url}")
    
    def exists(self, short_code: str) -> bool:
        """
        Check if a short code already exists.
        
        Args:
            short_code: The shortened URL code
            
        Returns:
            True if the short code exists, False otherwise
        """
        return self.client.exists(f"url:{short_code}") > 0
    
    def ping(self) -> bool:
        """
        Test Redis connection.
        
        Returns:
            True if connection is successful, False otherwise
        """
        try:
            return self.client.ping()
        except redis.ConnectionError:
            return False


# Global instance
_store = None

def get_store() -> RedisStore:
    """Get or create the global RedisStore instance."""
    global _store
    if _store is None:
        _store = RedisStore()
    return _store
