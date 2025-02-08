from sqlalchemy import Column, String, Integer, ForeignKey, Numeric, Boolean
from sqlalchemy.orm import relationship
from .base import Base, TimestampedBase

class Review(Base, TimestampedBase):
    __tablename__ = "reviews"

    agent_id = Column(Integer, ForeignKey("agents.id"))
    reviewer_id = Column(Integer, ForeignKey("users.id"))
    agent_creator_id = Column(Integer, ForeignKey("users.id"))
    
    # Review Content
    rating = Column(Numeric(precision=2, scale=1))  # 0.0 to 5.0
    comment = Column(String(1000))
    
    # Review Metadata
    is_verified_purchase = Column(Boolean, default=False)
    is_edited = Column(Boolean, default=False)
    
    # Usage Context
    usage_duration = Column(Integer)  # in days
    usage_context = Column(String(200))
    
    # Relationships
    agent = relationship("Agent", back_populates="reviews")
    reviewer = relationship("User", back_populates="reviews_given", foreign_keys=[reviewer_id])
    agent_creator = relationship("User", back_populates="reviews_received", foreign_keys=[agent_creator_id])