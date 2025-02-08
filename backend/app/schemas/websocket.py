from typing import Optional, Any, Literal
from pydantic import BaseModel
from .base import BaseSchema

class WSMessage(BaseSchema):
    type: str
    data: Any

class TrainingProgress(BaseSchema):
    agent_id: int
    progress: float
    current_loss: Optional[float]
    current_accuracy: Optional[float]
    epoch: int
    status: str
    time_remaining: Optional[int]

class TransactionUpdate(BaseSchema):
    transaction_id: int
    status: str
    block_number: Optional[int]
    confirmation_count: Optional[int]

class WSNotification(BaseSchema):
    type: Literal["info", "success", "warning", "error"]
    title: str
    message: str
    duration: Optional[int] = 5000  # milliseconds

class WSResponse(BaseSchema):
    event: str
    data: Any
    error: Optional[str] = None