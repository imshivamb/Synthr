from sqlalchemy import Column, String, Boolean, Integer, ForeignKey, Table, JSON
from sqlalchemy.orm import relationship
from .base import Base, TimestampedBase

oauth_accounts = Table(
    'oauth_accounts',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('provider', String(50)),
    Column('provider_user_id', String(255)),
    Column('email', String(255)),
    Column('name', String(255)),
    Column('avatar_url', String(255))
)

class User(Base, TimestampedBase):
    __tablename__ = "users"
    
    # Basic Info
    username = Column(String(100), unique=True, index=True)
    email = Column(String(255), unique=True, index=True)
    
    # Wallet Auth
    wallet_address = Column(String(42), unique=True, index=True)
    nonce = Column(String(255))  # For wallet signature
    
    # OAuth Info
    oauth_accounts = relationship(
        "OAuthAccount",
        secondary=oauth_accounts,
        backref="user"
    )
    
    # Status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    reputation_score = Column(Integer, default=0)
    
    # Profile
    profile = Column(JSON, default=dict)
    preferences = Column(JSON, default=dict)
    
    # Relationships (from previous implementation)
    created_agents = relationship("Agent", back_populates="creator", foreign_keys="Agent.creator_id")
    owned_agents = relationship("Agent", back_populates="owner", foreign_keys="Agent.owner_id")
    sent_transactions = relationship("Transaction", back_populates="buyer", foreign_keys="Transaction.buyer_id")
    received_transactions = relationship("Transaction", back_populates="seller", foreign_keys="Transaction.seller_id")
    reviews_given = relationship("Review", back_populates="reviewer", foreign_keys="Review.reviewer_id")
    reviews_received = relationship("Review", back_populates="agent_creator", foreign_keys="Review.agent_creator_id")