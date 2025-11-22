"""Tests for the Redis storage layer."""
import pytest
from unittest.mock import MagicMock, patch
from app.storage.redis_store import RedisStore, get_store
import redis


class TestRedisStoreInit:
    """Tests for RedisStore initialization."""
    
    @patch('app.storage.redis_store.redis.Redis')
    def test_init_with_defaults(self, mock_redis_class):
        """Test initialization with default parameters."""
        store = RedisStore()
        
        assert store.host == 'localhost'
        assert store.port == 6379
        assert store.db == 0
        mock_redis_class.assert_called_once_with(
            host='localhost',
            port=6379,
            db=0,
            decode_responses=True
        )
    
    @patch('app.storage.redis_store.redis.Redis')
    def test_init_with_custom_params(self, mock_redis_class):
        """Test initialization with custom parameters."""
        store = RedisStore(host='redis-server', port=6380, db=1)
        
        assert store.host == 'redis-server'
        assert store.port == 6380
        assert store.db == 1
        mock_redis_class.assert_called_once_with(
            host='redis-server',
            port=6380,
            db=1,
            decode_responses=True
        )
    
    @patch('app.storage.redis_store.redis.Redis')
    @patch.dict('os.environ', {'REDIS_HOST': 'env-redis-host'})
    def test_init_with_env_variable(self, mock_redis_class):
        """Test that REDIS_HOST environment variable is used."""
        store = RedisStore()
        
        assert store.host == 'env-redis-host'
        mock_redis_class.assert_called_once_with(
            host='env-redis-host',
            port=6379,
            db=0,
            decode_responses=True
        )


class TestRedisStoreSetUrl:
    """Tests for the set_url method."""
    
    @patch('app.storage.redis_store.redis.Redis')
    def test_set_url(self, mock_redis_class, sample_urls):
        """Test setting a URL mapping with TTL."""
        mock_client = MagicMock()
        mock_redis_class.return_value = mock_client
        
        store = RedisStore()
        store.set_url(sample_urls["short_code_1"], sample_urls["long_url_1"])
        
        mock_client.setex.assert_called_once_with(
            f"url:{sample_urls['short_code_1']}",
            600,  # Default TTL
            sample_urls["long_url_1"]
        )
    
    @patch('app.storage.redis_store.redis.Redis')
    def test_set_multiple_urls(self, mock_redis_class, sample_urls):
        """Test setting multiple URL mappings."""
        mock_client = MagicMock()
        mock_redis_class.return_value = mock_client
        
        store = RedisStore()
        store.set_url(sample_urls["short_code_1"], sample_urls["long_url_1"])
        store.set_url(sample_urls["short_code_2"], sample_urls["long_url_2"])
        
        assert mock_client.setex.call_count == 2
    
    @patch('app.storage.redis_store.redis.Redis')
    def test_set_url_with_custom_ttl(self, mock_redis_class, sample_urls):
        """Test setting a URL mapping with custom TTL."""
        mock_client = MagicMock()
        mock_redis_class.return_value = mock_client
        
        store = RedisStore()
        custom_ttl = 300  # 5 minutes
        store.set_url(sample_urls["short_code_1"], sample_urls["long_url_1"], ttl=custom_ttl)
        
        mock_client.setex.assert_called_once_with(
            f"url:{sample_urls['short_code_1']}",
            custom_ttl,
            sample_urls["long_url_1"]
        )


class TestRedisStoreGetUrl:
    """Tests for the get_url method."""
    
    @patch('app.storage.redis_store.redis.Redis')
    def test_get_existing_url(self, mock_redis_class, sample_urls):
        """Test getting an existing URL."""
        mock_client = MagicMock()
        mock_client.get.return_value = sample_urls["long_url_1"]
        mock_redis_class.return_value = mock_client
        
        store = RedisStore()
        result = store.get_url(sample_urls["short_code_1"])
        
        assert result == sample_urls["long_url_1"]
        mock_client.get.assert_called_once_with(f"url:{sample_urls['short_code_1']}")
    
    @patch('app.storage.redis_store.redis.Redis')
    def test_get_non_existent_url(self, mock_redis_class):
        """Test getting a non-existent URL returns None."""
        mock_client = MagicMock()
        mock_client.get.return_value = None
        mock_redis_class.return_value = mock_client
        
        store = RedisStore()
        result = store.get_url("nonexistent")
        
        assert result is None
        mock_client.get.assert_called_once_with("url:nonexistent")


class TestRedisStoreReverseMapping:
    """Tests for reverse mapping methods."""
    
    @patch('app.storage.redis_store.redis.Redis')
    def test_set_reverse_mapping(self, mock_redis_class, sample_urls):
        """Test setting a reverse mapping with TTL."""
        mock_client = MagicMock()
        mock_redis_class.return_value = mock_client
        
        store = RedisStore()
        store.set_reverse_mapping(sample_urls["long_url_1"], sample_urls["short_code_1"])
        
        mock_client.setex.assert_called_once_with(
            f"reverse:{sample_urls['long_url_1']}",
            600,  # Default TTL
            sample_urls["short_code_1"]
        )
    
    @patch('app.storage.redis_store.redis.Redis')
    def test_get_existing_short_code(self, mock_redis_class, sample_urls):
        """Test getting an existing short code for a URL."""
        mock_client = MagicMock()
        mock_client.get.return_value = sample_urls["short_code_1"]
        mock_redis_class.return_value = mock_client
        
        store = RedisStore()
        result = store.get_short_code(sample_urls["long_url_1"])
        
        assert result == sample_urls["short_code_1"]
        mock_client.get.assert_called_once_with(f"reverse:{sample_urls['long_url_1']}")
    
    @patch('app.storage.redis_store.redis.Redis')
    def test_get_non_existent_short_code(self, mock_redis_class):
        """Test getting a short code for a URL that hasn't been shortened."""
        mock_client = MagicMock()
        mock_client.get.return_value = None
        mock_redis_class.return_value = mock_client
        
        store = RedisStore()
        result = store.get_short_code("https://new-url.com")
        
        assert result is None


class TestRedisStoreExists:
    """Tests for the exists method."""
    
    @patch('app.storage.redis_store.redis.Redis')
    def test_exists_returns_true(self, mock_redis_class, sample_urls):
        """Test exists returns True when short code exists."""
        mock_client = MagicMock()
        mock_client.exists.return_value = 1
        mock_redis_class.return_value = mock_client
        
        store = RedisStore()
        result = store.exists(sample_urls["short_code_1"])
        
        assert result is True
        mock_client.exists.assert_called_once_with(f"url:{sample_urls['short_code_1']}")
    
    @patch('app.storage.redis_store.redis.Redis')
    def test_exists_returns_false(self, mock_redis_class):
        """Test exists returns False when short code doesn't exist."""
        mock_client = MagicMock()
        mock_client.exists.return_value = 0
        mock_redis_class.return_value = mock_client
        
        store = RedisStore()
        result = store.exists("nonexistent")
        
        assert result is False
        mock_client.exists.assert_called_once_with("url:nonexistent")
    
    @patch('app.storage.redis_store.redis.Redis')
    def test_exists_multiple_keys(self, mock_redis_class):
        """Test exists with multiple keys (Redis can return > 1)."""
        mock_client = MagicMock()
        mock_client.exists.return_value = 2
        mock_redis_class.return_value = mock_client
        
        store = RedisStore()
        result = store.exists("some_code")
        
        # Should still return True for any value > 0
        assert result is True


class TestRedisStorePing:
    """Tests for the ping method."""
    
    @patch('app.storage.redis_store.redis.Redis')
    def test_ping_success(self, mock_redis_class):
        """Test successful ping."""
        mock_client = MagicMock()
        mock_client.ping.return_value = True
        mock_redis_class.return_value = mock_client
        
        store = RedisStore()
        result = store.ping()
        
        assert result is True
        mock_client.ping.assert_called_once()
    
    @patch('app.storage.redis_store.redis.Redis')
    def test_ping_connection_error(self, mock_redis_class):
        """Test ping returns False on connection error."""
        mock_client = MagicMock()
        mock_client.ping.side_effect = redis.ConnectionError("Connection failed")
        mock_redis_class.return_value = mock_client
        
        store = RedisStore()
        result = store.ping()
        
        assert result is False


class TestRedisStoreTTL:
    """Tests for TTL functionality."""
    
    @patch('app.storage.redis_store.redis.Redis')
    def test_get_ttl_existing_key(self, mock_redis_class, sample_urls):
        """Test getting TTL for an existing key."""
        mock_client = MagicMock()
        mock_client.ttl.return_value = 500  # 500 seconds remaining
        mock_redis_class.return_value = mock_client
        
        store = RedisStore()
        result = store.get_ttl(sample_urls["short_code_1"])
        
        assert result == 500
        mock_client.ttl.assert_called_once_with(f"url:{sample_urls['short_code_1']}")
    
    @patch('app.storage.redis_store.redis.Redis')
    def test_get_ttl_non_existent_key(self, mock_redis_class):
        """Test getting TTL for a non-existent key returns -2."""
        mock_client = MagicMock()
        mock_client.ttl.return_value = -2
        mock_redis_class.return_value = mock_client
        
        store = RedisStore()
        result = store.get_ttl("nonexistent")
        
        assert result == -2
    
    @patch('app.storage.redis_store.redis.Redis')
    def test_get_ttl_key_without_expiry(self, mock_redis_class, sample_urls):
        """Test getting TTL for a key without expiry returns -1."""
        mock_client = MagicMock()
        mock_client.ttl.return_value = -1
        mock_redis_class.return_value = mock_client
        
        store = RedisStore()
        result = store.get_ttl(sample_urls["short_code_1"])
        
        assert result == -1
    
    @patch('app.storage.redis_store.redis.Redis')
    def test_ttl_constant_value(self, mock_redis_class):
        """Test that URL_TTL constant is set to 600 seconds (10 minutes)."""
        store = RedisStore()
        assert store.URL_TTL == 600



class TestGetStore:
    """Tests for the get_store singleton function."""
    
    @patch('app.storage.redis_store.RedisStore')
    def test_get_store_creates_instance(self, mock_redis_store_class):
        """Test that get_store creates a RedisStore instance."""
        # Reset the global store
        import app.storage.redis_store as store_module
        store_module._store = None
        
        mock_instance = MagicMock()
        mock_redis_store_class.return_value = mock_instance
        
        result = get_store()
        
        assert result == mock_instance
        mock_redis_store_class.assert_called_once()
    
    @patch('app.storage.redis_store.RedisStore')
    def test_get_store_returns_same_instance(self, mock_redis_store_class):
        """Test that get_store returns the same instance on multiple calls."""
        # Reset the global store
        import app.storage.redis_store as store_module
        store_module._store = None
        
        mock_instance = MagicMock()
        mock_redis_store_class.return_value = mock_instance
        
        result1 = get_store()
        result2 = get_store()
        
        assert result1 is result2
        # Should only create once
        assert mock_redis_store_class.call_count == 1


class TestRedisStoreIntegration:
    """Integration-style tests for RedisStore (still mocked but testing workflows)."""
    
    @patch('app.storage.redis_store.redis.Redis')
    def test_full_url_shortening_workflow(self, mock_redis_class, sample_urls):
        """Test complete workflow of shortening and retrieving a URL."""
        mock_client = MagicMock()
        mock_redis_class.return_value = mock_client
        
        # Setup mock responses
        mock_client.exists.return_value = 0  # Code doesn't exist
        mock_client.get.side_effect = [None, sample_urls["long_url_1"]]  # No reverse, then get URL
        
        store = RedisStore()
        
        # Check if URL already shortened (should be None)
        existing = store.get_short_code(sample_urls["long_url_1"])
        assert existing is None
        
        # Check if code exists (should be False)
        code_exists = store.exists(sample_urls["short_code_1"])
        assert code_exists is False
        
        # Store the mapping
        store.set_url(sample_urls["short_code_1"], sample_urls["long_url_1"])
        store.set_reverse_mapping(sample_urls["long_url_1"], sample_urls["short_code_1"])
        
        # Retrieve the URL
        retrieved = store.get_url(sample_urls["short_code_1"])
        assert retrieved == sample_urls["long_url_1"]
