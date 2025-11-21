from pydantic import BaseModel

class ShortenRequest(BaseModel): 
    long_url: str

class ReverseRequest(BaseModel):
    short_url: str