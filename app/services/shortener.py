import secrets
from app.storage.redis_store import get_store

def generate_shortened_code(long_url: str) -> str:
    """Generate a unique short code for the given URL."""
    store = get_store()
    
    # Try up to 10 times to generate a unique code
    for _ in range(10):
        short_url_code = secrets.token_urlsafe(8)
        if not store.exists(short_url_code):
            store.set_url(short_url_code, long_url)
            return short_url_code
    
    raise RuntimeError("Failed to generate unique short code after 10 attempts")

def shorten_url(url: str) -> str:
    """
    Shorten a URL and return the shortened URL.
    If the URL has already been shortened, return the existing short code.
    """
    store = get_store()
    
    # Check if this URL has already been shortened
    existing_code = store.get_short_code(url)
    if existing_code:
        short_url_code = existing_code
    else:
        # Generate new short code and store both mappings
        short_url_code = generate_shortened_code(url)
        store.set_reverse_mapping(url, short_url_code)
    
    return f"http://localhost:3000/{short_url_code}"
        
def reverse_url(short_url_code: str) -> str | None:
    """Retrieve the original URL for a given short code."""
    store = get_store()
    return store.get_url(short_url_code)