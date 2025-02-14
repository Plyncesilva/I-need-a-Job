from typing import List, Dict, Any
from dataclasses import dataclass
import json

@dataclass
class Message:
    role: str
    content: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            'role': self.role,
            'content': self.content
        }

@dataclass
class RequestBody:
    model: str
    messages: List[Message]
    max_tokens: int

@dataclass
class BatchRequest:
    custom_id: str
    method: str
    url: str
    body: RequestBody

    @classmethod
    def from_messages(cls, id: str, messages: List[Message]) -> 'BatchRequest':
        return BatchRequest(
            id,
            "POST",
            "/v1/chat/completions",
            RequestBody("gpt-4o", messages, 16000)
        )

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BatchRequest':
        messages = [Message(**msg) for msg in data['body']['messages']]
        body = RequestBody(
            model=data['body']['model'],
            messages=messages,
            max_tokens=data['body']['max_tokens']
        )
        return cls(
            custom_id=data['custom_id'],
            method=data['method'],
            url=data['url'],
            body=body
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            'custom_id': self.custom_id,
            'method': self.method,
            'url': self.url,
            'body': {
                'model': self.body.model,
                'messages': [{'role': msg.role, 'content': msg.content} for msg in self.body.messages],
                'max_tokens': self.body.max_tokens
            }
        }
    
    def __str__(self) -> str:
        return json.dumps(self.to_dict())