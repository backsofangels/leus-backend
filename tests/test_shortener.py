"""Tests for the URL shortener service functions."""
import pytest
from unittest.mock import patch, MagicMock
from app.services.shortener import generate_shortened_code, shorten_url, reverse_url


class TestGenerateShortenedCode:
    """Tests for the generate_shortened_code function."""
    
    @patch('app.services.shortener.get_store')
    @patch('app.services.shortener.secrets.token_urlsafe')
    def test_generate_unique_code_first_attempt(self, mock_token, mock_get_store, mock_redis_store, sample_urls):
        """Test generating a unique code on the first attempt."""
        mock_get_store.return_value = mock_redis_store
        mock_token.return_value = sample_urls["short_code_1"]
        mock_redis_store.exists.side_effect = None
        mock_redis_store.exists.return_value = False
        
        result = generate_shortened_code(sample_urls["long_url_1"])
        
        assert result == sample_urls["short_code_1"]
        mock_redis_store.set_url.assert_called_once_with(
            sample_urls["short_code_1"], 
            sample_urls["long_url_1"]
        )
        mock_token.assert_called_once_with(8)
    
    @patch('app.services.shortener.get_store')
    @patch('app.services.shortener.secrets.token_urlsafe')
    def test_generate_code_with_collision(self, mock_token, mock_get_store, mock_redis_store, sample_urls):
        """Test generating a code when first attempt collides."""
        mock_get_store.return_value = mock_redis_store
        
        # First code exists, second doesn't
        mock_token.side_effect = ["collision", sample_urls["short_code_1"]]
        mock_redis_store.exists.side_effect = [True, False]
        
        result = generate_shortened_code(sample_urls["long_url_1"])
        
        assert result == sample_urls["short_code_1"]
        assert mock_token.call_count == 2
        mock_redis_store.set_url.assert_called_once_with(
            sample_urls["short_code_1"],
            sample_urls["long_url_1"]
        )
    
    @patch('app.services.shortener.get_store')
    @patch('app.services.shortener.secrets.token_urlsafe')
    def test_generate_code_max_retries_exceeded(self, mock_token, mock_get_store, mock_redis_store):
        """Test that RuntimeError is raised after 10 failed attempts."""
        mock_get_store.return_value = mock_redis_store
        mock_token.return_value = "collision"
        # Reset side_effect and set return_value
        mock_redis_store.exists.side_effect = None
        mock_redis_store.exists.return_value = True  # Always exists
        
        with pytest.raises(RuntimeError) as exc_info:
            generate_shortened_code("https://example.com")
        
        assert "Failed to generate unique short code after 10 attempts" in str(exc_info.value)
        assert mock_token.call_count == 10
    
    @patch('app.services.shortener.get_store')
    @patch('app.services.shortener.secrets.token_urlsafe')
    def test_generate_code_stores_mapping(self, mock_token, mock_get_store, mock_redis_store, sample_urls):
        """Test that the generated code is properly stored."""
        mock_get_store.return_value = mock_redis_store
        mock_token.return_value = sample_urls["short_code_1"]
        mock_redis_store.exists.return_value = False
        
        generate_shortened_code(sample_urls["long_url_1"])
        
        # Verify the mapping was stored
        assert mock_redis_store.url_mappings[sample_urls["short_code_1"]] == sample_urls["long_url_1"]


class TestShortenUrl:
    """Tests for the shorten_url function."""
    
    @patch('app.services.shortener.get_store')
    @patch('app.services.shortener.generate_shortened_code')
    def test_shorten_new_url(self, mock_generate, mock_get_store, mock_redis_store, sample_urls):
        """Test shortening a URL that hasn't been shortened before."""
        mock_get_store.return_value = mock_redis_store
        mock_redis_store.get_short_code.return_value = None
        mock_generate.return_value = sample_urls["short_code_1"]
        
        result = shorten_url(sample_urls["long_url_1"])
        
        assert result == f"http://localhost:3000/{sample_urls['short_code_1']}"
        mock_generate.assert_called_once_with(sample_urls["long_url_1"])
        mock_redis_store.set_reverse_mapping.assert_called_once_with(
            sample_urls["long_url_1"],
            sample_urls["short_code_1"]
        )
    
    @patch('app.services.shortener.get_store')
    @patch('app.services.shortener.generate_shortened_code')
    def test_shorten_existing_url(self, mock_generate, mock_get_store, mock_redis_store, sample_urls):
        """Test shortening a URL that has already been shortened."""
        mock_get_store.return_value = mock_redis_store
        mock_redis_store.get_short_code.side_effect = None
        mock_redis_store.get_short_code.return_value = sample_urls["short_code_1"]
        
        result = shorten_url(sample_urls["long_url_1"])
        
        assert result == f"http://localhost:3000/{sample_urls['short_code_1']}"
        # Should not generate a new code
        mock_generate.assert_not_called()
        # Should not set reverse mapping again
        mock_redis_store.set_reverse_mapping.assert_not_called()
    
    @patch('app.services.shortener.get_store')
    @patch('app.services.shortener.generate_shortened_code')
    def test_shorten_url_format(self, mock_generate, mock_get_store, mock_redis_store, sample_urls):
        """Test that the shortened URL has the correct format."""
        mock_get_store.return_value = mock_redis_store
        mock_redis_store.get_short_code.return_value = None
        mock_generate.return_value = "test123"
        
        result = shorten_url("https://example.com")
        
        assert result.startswith("http://localhost:3000/")
        assert result.endswith("test123")
    
    @patch('app.services.shortener.get_store')
    @patch('app.services.shortener.generate_shortened_code')
    def test_shorten_multiple_different_urls(self, mock_generate, mock_get_store, mock_redis_store, sample_urls):
        """Test shortening multiple different URLs."""
        mock_get_store.return_value = mock_redis_store
        mock_redis_store.get_short_code.return_value = None
        
        urls = [sample_urls["long_url_1"], sample_urls["long_url_2"], sample_urls["long_url_3"]]
        codes = [sample_urls["short_code_1"], sample_urls["short_code_2"], "code3"]
        
        for url, code in zip(urls, codes):
            mock_generate.return_value = code
            result = shorten_url(url)
            assert result == f"http://localhost:3000/{code}"
    
    @patch('app.services.shortener.get_store')
    @patch('app.services.shortener.generate_shortened_code')
    def test_shorten_idempotency(self, mock_generate, mock_get_store, mock_redis_store, sample_urls):
        """Test that shortening the same URL multiple times returns the same code."""
        mock_get_store.return_value = mock_redis_store
        
        # First call - no existing code
        mock_redis_store.get_short_code.return_value = None
        mock_generate.return_value = sample_urls["short_code_1"]
        result1 = shorten_url(sample_urls["long_url_1"])
        
        # Second call - existing code found
        mock_redis_store.get_short_code.return_value = sample_urls["short_code_1"]
        result2 = shorten_url(sample_urls["long_url_1"])
        
        assert result1 == result2
        # generate_shortened_code should only be called once
        assert mock_generate.call_count == 1


class TestReverseUrl:
    """Tests for the reverse_url function."""
    
    @patch('app.services.shortener.get_store')
    def test_reverse_existing_code(self, mock_get_store, mock_redis_store, sample_urls):
        """Test reversing an existing short code."""
        mock_get_store.return_value = mock_redis_store
        mock_redis_store.get_url.side_effect = None
        mock_redis_store.get_url.return_value = sample_urls["long_url_1"]
        
        result = reverse_url(sample_urls["short_code_1"])
        
        assert result == sample_urls["long_url_1"]
        mock_redis_store.get_url.assert_called_once_with(sample_urls["short_code_1"])
    
    @patch('app.services.shortener.get_store')
    def test_reverse_non_existent_code(self, mock_get_store, mock_redis_store):
        """Test reversing a non-existent short code."""
        mock_get_store.return_value = mock_redis_store
        mock_redis_store.get_url.side_effect = None
        mock_redis_store.get_url.return_value = None
        
        result = reverse_url("nonexistent")
        
        assert result is None
        mock_redis_store.get_url.assert_called_once_with("nonexistent")
    
    @patch('app.services.shortener.get_store')
    def test_reverse_multiple_codes(self, mock_get_store, mock_redis_store, sample_urls):
        """Test reversing multiple different short codes."""
        mock_get_store.return_value = mock_redis_store
        
        test_cases = [
            (sample_urls["short_code_1"], sample_urls["long_url_1"]),
            (sample_urls["short_code_2"], sample_urls["long_url_2"]),
            ("code3", sample_urls["long_url_3"]),
        ]
        
        # Use side_effect to return different values for each call
        mock_redis_store.get_url.side_effect = [expected_url for _, expected_url in test_cases]
        
        for short_code, expected_url in test_cases:
            result = reverse_url(short_code)
            assert result == expected_url
    
    @patch('app.services.shortener.get_store')
    def test_reverse_empty_code(self, mock_get_store, mock_redis_store):
        """Test reversing an empty short code."""
        mock_get_store.return_value = mock_redis_store
        mock_redis_store.get_url.side_effect = None
        mock_redis_store.get_url.return_value = None
        
        result = reverse_url("")
        
        assert result is None
        mock_redis_store.get_url.assert_called_once_with("")
