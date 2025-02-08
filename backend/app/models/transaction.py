from sqlalchemy import Column, String, Integer, ForeignKey, Numeric, JSON, Enum
from sqlalchemy.orm import relationship
import enum
from .base import Base, TimestampedBase

class TransactionStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"

class TransactionType(str, enum.Enum):
    PURCHASE = "purchase"
    ROYALTY = "royalty"
    REFUND = "refund"

class Transaction(Base, TimestampedBase):
    __tablename__ = "transactions"

    # Transaction Details
    agent_id = Column(Integer, ForeignKey("agents.id"))
    buyer_id = Column(Integer, ForeignKey("users.id"))
    seller_id = Column(Integer, ForeignKey("users.id"))
    
    # Financial Details
    amount = Column(Numeric(precision=18, scale=8), nullable=False)
    royalty_amount = Column(Numeric(precision=18, scale=8))
    gas_fee = Column(Numeric(precision=18, scale=8))
    
    # Transaction Status and Type
    status = Column(Enum(TransactionStatus), default=TransactionStatus.PENDING)
    type = Column(Enum(TransactionType), default=TransactionType.PURCHASE)
    
    # Blockchain Details
    transaction_hash = Column(String(66), unique=True)
    block_number = Column(Integer)
    blockchain_status = Column(String(50))
    
    # Additional Data
    tx_metadata = Column(JSON)
    error_message = Column(String(500))
    
    # Relationships
    agent = relationship("Agent", back_populates="transactions")
    buyer = relationship("User", back_populates="sent_transactions", foreign_keys=[buyer_id])
    seller = relationship("User", back_populates="received_transactions", foreign_keys=[seller_id])