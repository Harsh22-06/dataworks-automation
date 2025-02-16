from pydantic import BaseModel
from typing import Optional, Dict

class TaskRequest(BaseModel):
    task: str
    parameters: Optional[Dict] = None

class TaskResponse(BaseModel):
    status: str
    result: Optional[Dict] = None
    