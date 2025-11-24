from pydantic import BaseModel

class Message(BaseModel):
    text: str
    service: str
    node: str
    container: str