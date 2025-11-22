"""Tests for the FastAPI endpoints in main.py."""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app.main import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


class TestHealthCheck:
    """Tests for the healthcheck endpoint."""
    
    def test_healthcheck_returns_200(self, client):
        """Test that healthcheck endpoint returns 200 status."""
        response = client.get("/healthcheck")
        assert response.status_code == 200
    
    def test_healthcheck_returns_correct_message(self, client):
        """Test that healthcheck returns the expected message."""
        response = client.get("/healthcheck")
        assert response.json() == {"message": "Healthcheck"}


class TestShortenEndpoint:
    """Tests for the /short endpoint."""
    
    @patch('app.main.shorten_url')
    def test_shorten_url_success(self, mock_shorten, client, sample_urls):
        """Test successful URL shortening."""
        mock_shorten.return_value = f"http://localhost:3000/{sample_urls['short_code_1']}"
        
        response = client.post(
            "/short",
            json={"long_url": sample_urls["long_url_1"]}
        )
        
        assert response.status_code == 200
        assert "short_url" in response.json()
        assert response.json()["short_url"] == f"http://localhost:3000/{sample_urls['short_code_1']}"
        mock_shorten.assert_called_once_with(sample_urls["long_url_1"])
    
    @patch('app.main.shorten_url')
    def test_shorten_multiple_urls(self, mock_shorten, client, sample_urls):
        """Test shortening multiple different URLs."""
        test_cases = [
            (sample_urls["long_url_1"], sample_urls["short_code_1"]),
            (sample_urls["long_url_2"], sample_urls["short_code_2"]),
        ]
        
        for long_url, short_code in test_cases:
            mock_shorten.return_value = f"http://localhost:3000/{short_code}"
            response = client.post("/short", json={"long_url": long_url})
            
            assert response.status_code == 200
            assert response.json()["short_url"] == f"http://localhost:3000/{short_code}"
    
    def test_shorten_missing_url(self, client):
        """Test that missing URL returns 422 validation error."""
        response = client.post("/short", json={})
        assert response.status_code == 422
    
    def test_shorten_invalid_json(self, client):
        """Test that invalid JSON returns 422 error."""
        response = client.post(
            "/short",
            data="not a json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422
    
    @patch('app.main.shorten_url')
    def test_shorten_empty_url(self, mock_shorten, client):
        """Test shortening an empty URL string."""
        mock_shorten.return_value = "http://localhost:3000/test123"
        response = client.post("/short", json={"long_url": ""})
        
        # Should still process, validation is at service layer
        assert response.status_code == 200


class TestReverseEndpoint:
    """Tests for the /reverse endpoint."""
    
    @patch('app.main.reverse_url')
    def test_reverse_url_success(self, mock_reverse, client, sample_urls):
        """Test successful URL reversal."""
        mock_reverse.return_value = sample_urls["long_url_1"]
        
        response = client.post(
            "/reverse",
            json={"short_url": f"http://localhost:3000/{sample_urls['short_code_1']}"}
        )
        
        assert response.status_code == 200
        assert "long_url" in response.json()
        assert response.json()["long_url"] == sample_urls["long_url_1"]
        mock_reverse.assert_called_once_with(sample_urls["short_code_1"])
    
    @patch('app.main.reverse_url')
    def test_reverse_url_not_found(self, mock_reverse, client):
        """Test reversing a non-existent short URL."""
        mock_reverse.return_value = None
        
        response = client.post(
            "/reverse",
            json={"short_url": "http://localhost:3000/notfound"}
        )
        
        assert response.status_code == 200
        assert response.json()["long_url"] is None
    
    @patch('app.main.reverse_url')
    def test_reverse_extracts_code_from_url(self, mock_reverse, client, sample_urls):
        """Test that the endpoint correctly extracts short code from full URL."""
        mock_reverse.return_value = sample_urls["long_url_1"]
        
        response = client.post(
            "/reverse",
            json={"short_url": f"http://localhost:3000/{sample_urls['short_code_1']}"}
        )
        
        # Verify the short code was extracted correctly
        mock_reverse.assert_called_once_with(sample_urls["short_code_1"])
    
    @patch('app.main.reverse_url')
    def test_reverse_with_just_code(self, mock_reverse, client, sample_urls):
        """Test reversing with just the short code (no domain)."""
        mock_reverse.return_value = sample_urls["long_url_1"]
        
        response = client.post(
            "/reverse",
            json={"short_url": sample_urls["short_code_1"]}
        )
        
        assert response.status_code == 200
        mock_reverse.assert_called_once_with(sample_urls["short_code_1"])
    
    def test_reverse_missing_url(self, client):
        """Test that missing short_url returns 422 validation error."""
        response = client.post("/reverse", json={})
        assert response.status_code == 422
    
    @patch('app.main.reverse_url')
    def test_reverse_with_path_segments(self, mock_reverse, client, sample_urls):
        """Test reversing URL with multiple path segments (only first is used)."""
        mock_reverse.return_value = sample_urls["long_url_1"]
        
        response = client.post(
            "/reverse",
            json={"short_url": f"http://localhost:3000/{sample_urls['short_code_1']}/extra/path"}
        )
        
        # Should extract the first path segment
        assert response.status_code == 200
