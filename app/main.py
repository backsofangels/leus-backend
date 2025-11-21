from fastapi import FastAPI
from app.models.requests import ShortenRequest, ReverseRequest
from app.models.responses import ShortenResponse, ReverseResponse

from app.services.shortener import shorten_url, reverse_url
from urllib.parse import urlparse

app = FastAPI()

@app.get("/healthcheck")
async def root():
    return {"message": "Healthcheck"}

@app.post("/short")
async def short(request: ShortenRequest) -> ShortenResponse:
    shortened_url = shorten_url(request.url_to_short)
    return ShortenResponse(
        shortened=shortened_url
    )

@app.post("/reverse")
async def reverse(req: ReverseRequest) -> ReverseResponse:
    short_code = urlparse(req.short_url).path.lstrip("/")
    reversed_url = reverse_url(short_code)
    return ReverseResponse(
        long_url=reversed_url
    )