from sqlalchemy import Column, String, Integer, ForeignKey, Numeric, JSON, Enum, Boolean
from sqlalchemy.orm import relationship
import enum
from .base import Base, TimestampedBase

class AgentStatus(str, enum.Enum):
    DRAFT = "draft"
    TRAINING = "training"
    READY = "ready"
    LISTED = "listed"
    SOLD = "sold"
    DELISTED = "delisted"

class AgentCategory(str, enum.Enum):
    ANALYTICS = "analytics"
    CONTENT = "content"
    DATA_PROCESSING = "data_processing"
    AUTOMATION = "automation"
    TRADING = "trading"
    CREATIVE = "creative"

class Agent(Base, TimestampedBase):
    __tablename__ = "agents"

    # Basic Information
    token_id = Column(String(100), unique=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(String(1000))
    category = Column(Enum(AgentCategory), nullable=False)
    status = Column(Enum(AgentStatus), default=AgentStatus.DRAFT)
    
    # Ownership and Creation
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Pricing and Sales
    price = Column(Numeric(precision=18, scale=8))
    is_listed = Column(Boolean, default=False)
    royalty_percentage = Column(Numeric(precision=5, scale=2), default=2.5)  # Default 2.5%
    
    # Technical Details
    ipfs_hash = Column(String(100))  # For model storage
    agent_metadata = Column(JSON)
    capabilities = Column(JSON)  # List of agent capabilities
    model_parameters = Column(JSON)  # Model configuration
    
    # Statistics
    total_uses = Column(Integer, default=0)
    average_rating = Column(Numeric(precision=3, scale=2), default=0)
    total_ratings = Column(Integer, default=0)
    
    # Relationships
    creator = relationship("User", back_populates="created_agents", foreign_keys=[creator_id])
    owner = relationship("User", back_populates="owned_agents", foreign_keys=[owner_id])
    transactions = relationship("Transaction", back_populates="agent")
    reviews = relationship("Review", back_populates="agent")
    training_jobs = relationship("TrainingJob", back_populates="agent")
    model = relationship("AIModel", back_populates="agent", uselist=False)