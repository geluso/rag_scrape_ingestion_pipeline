from uuid import uuid4
import json

class DocumentPayload:
    def __init__(self, title: str, url: str, text: str):
        self.id = str(uuid4())
        self.title = title
        self.url = url
        self.text = text

    def to_metadata(self):
        return {
            "id": self.id,
            "url": self.url,
            "title": self.title,
        }

    def to_dict(self):
        return {
            "id": self.id,
            "url": self.url,
            "title": self.title,
            "text": self.text
        }

    def to_json(self):
        jj = json.dumps(self.to_dict())
        print("json:", jj)
        return jj