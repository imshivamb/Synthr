from sqlalchemy import Column, String, Integer, ForeignKey, JSON, Enum
from sqlalchemy.orm import relationship
import enum
from .base import Base, TimestampedBase

class ModelType(str, enum.Enum):
    GPT4O = "gpt4O-mini"
    BERT = "bert"
    T5 = "t5"
    CUSTOM = "custom"

class ModelStatus(str, enum.Enum):
    INITIALIZING = "initializing"
    TRAINING = "training"
    VALIDATING = "validating"
    READY = "ready"
    FAILED = "failed"

class AIModel(Base, TimestampedBase):
    __tablename__ = "ai_models"

    agent_id = Column(Integer, ForeignKey("agents.id"), unique=True)
    model_type = Column(Enum(ModelType), nullable=False)
    version = Column(String(50))
    status = Column(Enum(ModelStatus), default=ModelStatus.INITIALIZING)
    
    # Technical Details
    architecture = Column(JSON)  # Model architecture details
    training_config = Column(JSON)  # Training configuration
    performance_metrics = Column(JSON)  # Training and validation metrics
    
    # Storage
    checkpoint_hash = Column(String(100))  # IPFS hash for model checkpoint
    weights_hash = Column(String(100))  # IPFS hash for model weights
    
    # Relationships
    agent = relationship("Agent", back_populates="model")
    training_jobs = relationship("TrainingJob", back_populates="model")