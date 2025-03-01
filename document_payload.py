from uuid import uuid4
import json

class DocumentPayload:
    def __init__(self, url: str, text: str, chunk_index: int):
        self.id = str(uuid4())
        self.url = url
        self.text = text
        self.chunk_index = chunk_index

    def to_dict(self):
        return {
            "id": self.id,
            "url": self.url,
            "text": self.text,
            "chunk_index": self.chunk_index
        }
