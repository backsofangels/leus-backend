"""Pytest configuration and shared fixtures."""
import pytest
from unittest.mock import MagicMock
from app.storage.redis_store import RedisStore


@pytest.fixture
def mock_redis_store():
    """Create a mock RedisStore for testing."""
    store = MagicMock(spec=RedisStore)
    store.url_mappings = {}  # short_code -> long_url
    store.reverse_mappings = {}  # long_url -> short_code
    
    def set_url(short_code: str, long_url: str):
        store.url_mappings[short_code] = long_url
    
    def get_url(short_code: str):
        return store.url_mappings.get(short_code)
    
    def set_reverse_mapping(long_url: str, short_code: str):
        store.reverse_mappings[long_url] = short_code
    
    def get_short_code(long_url: str):
        return store.reverse_mappings.get(long_url)
    
    def exists(short_code: str):
        return short_code in store.url_mappings
    
    def ping():
        return True
    
    # Set side_effect for methods that maintain state
    store.set_url.side_effect = set_url
    store.set_reverse_mapping.side_effect = set_reverse_mapping
    store.ping.return_value = True
    
    # For get methods and exists, set default behavior but allow override
    # by using Mock's default behavior (tests can override with return_value or side_effect)
    store.get_url.side_effect = get_url
    store.get_short_code.side_effect = get_short_code
    store.exists.side_effect = exists
    
    return store


@pytest.fixture
def sample_urls():
    """Sample URLs for testing."""
    return {
        "long_url_1": "https://www.example.com/very/long/path/to/resource",
        "long_url_2": "https://www.google.com/search?q=test",
        "long_url_3": "https://github.com/user/repo/issues/123",
        "short_code_1": "abc123",
        "short_code_2": "xyz789",
    }
