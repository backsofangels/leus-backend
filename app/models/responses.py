from pydantic import BaseModel

class ReverseResponse(BaseModel):
    long_url: str | None

class ShortenResponse(BaseModel):
    short_url: str