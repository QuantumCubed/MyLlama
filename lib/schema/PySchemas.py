from pydantic import BaseModel

class OllamaRequest(BaseModel):
    prompt: str