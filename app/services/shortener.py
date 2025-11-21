import secrets

# The local cache is needed to store the dict
# shortened code <-> long url
lookup_cache = {}

# The reverse cache is needed to store the dict
# long url -> shortened code and to avoid double generation
reverse_lookup_cache = {}

def generate_shortened_code(long_url: str) -> str:
    while True:
        short_url_code = secrets.token_urlsafe(8)
        if short_url_code not in lookup_cache:
            lookup_cache[short_url_code] = long_url
            return short_url_code

def shorten_url(url: str) -> str:
    if url in reverse_lookup_cache:
        short_url_code = reverse_lookup_cache[url]
    else:
        short_url_code = generate_shortened_code(url)
        reverse_lookup_cache[url] = short_url_code
    
    return f"http://localhost:3000/{short_url_code}"
        
def reverse_url(short_url_code: str) -> str | None:
    return lookup_cache.get(short_url_code)