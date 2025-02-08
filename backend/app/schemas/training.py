from pydantic import BaseModel, Field
from typing import Optional, Dict, List
from datetime import datetime
from .base import BaseSchema, TimestampedSchema
from ..models.training import TrainingStatus
from ..models.ai_model import ModelType, ModelStatus

class ModelBase(BaseSchema):
    model_type: ModelType
    architecture: Dict = Field(..., description="Model architecture configuration")
    training_config: Dict = Field(..., description="Training configuration")

class ModelCreate(ModelBase):
    agent_id: int

class ModelUpdate(BaseSchema):
    status: Optional[ModelStatus] = None
    performance_metrics: Optional[Dict] = None
    checkpoint_hash: Optional[str] = None
    weights_hash: Optional[str] = None

class Model(ModelBase, TimestampedSchema):
    id: int
    agent_id: int
    status: ModelStatus
    version: str
    performance_metrics: Optional[Dict] = None
    checkpoint_hash: Optional[str] = None
    weights_hash: Optional[str] = None

class TrainingJobBase(BaseSchema):
    agent_id: int
    model_id: int
    training_config: Dict = Field(..., description="Training hyperparameters and settings")

class TrainingJobCreate(TrainingJobBase):
    pass

class TrainingJobUpdate(BaseSchema):
    status: Optional[TrainingStatus] = None
    progress: Optional[float] = None
    current_loss: Optional[float] = None
    current_accuracy: Optional[float] = None
    error_message: Optional[str] = None
    metrics: Optional[Dict] = None

class TrainingJob(TrainingJobBase, TimestampedSchema):
    id: int
    status: TrainingStatus
    epochs_completed: int = 0
    progress: float = 0.0
    current_loss: Optional[float] = None
    current_accuracy: Optional[float] = None
    error_message: Optional[str] = None
    metrics: Optional[Dict] = None
    validation_results: Optional[Dict] = None
    compute_time: Optional[int] = None
    resources_used: Optional[Dict] = None