from sqlalchemy import Column, String, Integer, ForeignKey, JSON, Enum, Float
from sqlalchemy.orm import relationship
import enum
from .base import Base, TimestampedBase

class TrainingStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class TrainingJob(Base, TimestampedBase):
    __tablename__ = "training_jobs"

    agent_id = Column(Integer, ForeignKey("agents.id"))
    model_id = Column(Integer, ForeignKey("ai_models.id"))
    status = Column(Enum(TrainingStatus), default=TrainingStatus.PENDING)
    
    # Training Details
    epochs_completed = Column(Integer, default=0)
    current_loss = Column(Float)
    current_accuracy = Column(Float)
    training_config = Column(JSON)  # Hyperparameters and settings
    
    # Progress and Results
    progress = Column(Float, default=0)  # 0-100%
    error_message = Column(String(500))
    metrics = Column(JSON)  # Training metrics history
    validation_results = Column(JSON)
    
    # Resource Usage
    compute_time = Column(Integer)  # in seconds
    resources_used = Column(JSON)  # CPU, GPU, Memory usage
    
    # Relationships
    agent = relationship("Agent", back_populates="training_jobs")
    model = relationship("AIModel", back_populates="training_jobs")