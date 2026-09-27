from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from pydantic import BaseModel

class TaskRequest(BaseModel):
    task: str
    context: Optional[Dict[str, Any]] = None

class TaskResponse(BaseModel):
    result: str
    tokens_used: int = 0
    worker_name: str
    success: bool = True
    error: Optional[str] = None

class BaseAgent(ABC):
    def __init__(self, name: str, model: str, api_key: str):
        self.name = name
        self.model = model
        self.api_key = api_key

    @abstractmethod
    async def process(self, request: TaskRequest) -> TaskResponse:
        pass
