# Leus - URL Shortener Service

**Leus** (from Italian _"L'ennesimo URL shortener"_ - "Yet another URL shortener") is a lightweight, high-performance URL shortening service built with FastAPI and Redis.

## 🚀 Features

- **Fast & Efficient**: Built on FastAPI for high-performance async operations
- **Persistent Storage**: Uses Redis for reliable, scalable data persistence
- **Automatic Expiration**: URLs expire after 10 minutes (configurable TTL)
- **Duplicate Prevention**: Automatically returns existing short URLs for previously shortened links
- **Containerized**: Fully containerized with Podman/Docker Compose for easy deployment
- **RESTful API**: Clean, well-documented API endpoints
- **Comprehensive Testing**: Full test suite covering all functionality

## 📋 Prerequisites

- Python 3.11+
- Podman or Docker with Compose support
- Redis (automatically provided via Docker Compose)

## 🛠️ Installation & Setup

### Using Docker/Podman Compose (Recommended)

1. **Clone the repository**
    ```bash
    git clone <repository-url>
    cd leus-backend
    ```

2. **Build and start the services**
    ```bash
    podman compose up --build
    ```

    Or with Docker:
    ```bash
    docker-compose up --build
    ```

3. **Access the API**
    - API: `http://localhost:3000`
    - Interactive API docs: `http://localhost:3000/docs`
    - Alternative docs: `http://localhost:3000/redoc`

### Local Development Setup

1. **Create a virtual environment**
    ```bash
    python -m venv venv
    venv\Scripts\activate  # Windows
    source venv/bin/activate  # Linux/Mac
    ```

2. **Install dependencies**
    ```bash
    pip install -r requirements.txt
    ```

3. **Start Redis** (required)
    ```bash
    podman run -d -p 6379:6379 redis:7-alpine
    ```

4. **Run the application**
    ```bash
    uvicorn app.main:app --port 3000 --reload
    ```

## 📚 API Documentation

### Endpoints

#### `GET /healthcheck`
Check if the service is running.

**Response:**
```json
{
  "message": "Healthcheck"
}
```

#### `POST /short`
Shorten a long URL.

**Request Body:**
```json
{
  "long_url": "https://www.example.com/very/long/url/path"
}
```

**Response:**
```json
{
  "short_url": "http://localhost:3000/YAfhdRx6R_o"
}
```

#### `POST /reverse`
Retrieve the original URL from a shortened URL.

**Request Body:**
```json
{
  "short_url": "http://localhost:3000/YAfhdRx6R_o"
}
```

**Response:**
```json
{
  "long_url": "https://www.example.com/very/long/url/path"
}
```

### Example Usage

**Using cURL:**

```bash
# Shorten a URL
curl -X POST "http://localhost:3000/short" \
  -H "Content-Type: application/json" \
  -d '{"long_url": "https://www.example.com/long/url"}'

# Reverse a shortened URL
curl -X POST "http://localhost:3000/reverse" \
  -H "Content-Type: application/json" \
  -d '{"short_url": "http://localhost:3000/ABC123"}'
```

**Using Python:**

```python
import requests

# Shorten a URL
response = requests.post(
    "http://localhost:3000/short",
    json={"long_url": "https://www.example.com/long/url"}
)
short_url = response.json()["short_url"]
print(f"Shortened URL: {short_url}")

# Reverse a shortened URL
response = requests.post(
    "http://localhost:3000/reverse",
    json={"short_url": short_url}
)
original_url = response.json()["long_url"]
print(f"Original URL: {original_url}")
```

## 🏗️ Project Structure

```
leus-backend/
├── app/
│   ├── main.py              # FastAPI application entry point
│   ├── models/
│   │   ├── requests.py      # Pydantic request models
│   │   └── responses.py     # Pydantic response models
│   ├── services/
│   │   └── shortener.py     # URL shortening business logic
│   └── storage/
│       └── redis_store.py   # Redis storage layer
├── tests/                   # Test suite
│   ├── conftest.py          # Test fixtures
│   ├── test_main.py         # API tests
│   ├── test_redis_store.py  # Storage tests
│   └── test_shortener.py    # Service tests
├── docker-compose.yml       # Docker Compose configuration
├── Dockerfile              # Container image definition
├── requirements.txt        # Python dependencies
├── requirements-test.txt   # Testing dependencies
└── README.md              # This file
```

## 🔧 Configuration

### Environment Variables

- `REDIS_HOST`: Redis server hostname (default: `localhost`, set to `redis` in Docker Compose)
- `REDIS_PORT`: Redis server port (default: `6379`)

### Docker Compose Services

- **redis**: Redis 7 (Alpine) with persistent storage
- **app**: FastAPI application with hot-reload enabled

## 🧪 Testing

The project includes a comprehensive test suite using `pytest`.

### Running Tests

1.  **Install test dependencies**
    ```bash
    pip install -r requirements-test.txt
    ```

2.  **Run all tests**
    ```bash
    pytest
    ```

3.  **Run with coverage**
    ```bash
    pytest --cov=app --cov-report=term-missing
    ```

You can also test the service manually using the interactive API documentation at `http://localhost:3000/docs`.

## 🛡️ Technical Details

### URL Shortening Algorithm

- Uses `secrets.token_urlsafe(8)` to generate cryptographically secure random codes
- Implements collision detection with retry logic (up to 10 attempts)
- Stores bidirectional mappings (short→long and long→short) for efficient lookups

### Storage Layer

- **Redis** for persistent, high-performance key-value storage
- Separate namespaces for URL mappings (`url:*`) and reverse lookups (`reverse:*`)
- **TTL Support**: URLs automatically expire after 10 minutes (600 seconds)
- Thread-safe operations using Redis atomic commands
- Connection pooling for optimal performance

## 📝 License

See the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

This is a personal learning project, but suggestions and improvements are welcome!

## 🔮 Future Enhancements

- [ ] Custom short URL aliases
- [x] ~~URL expiration/TTL support~~ (Implemented)
- [ ] Analytics and click tracking
- [ ] Rate limiting
- [ ] API authentication
- [ ] Frontend interface