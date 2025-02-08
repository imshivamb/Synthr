from pydantic import BaseModel, Field
from typing import Optional, Dict
from decimal import Decimal
from .base import BaseSchema, TimestampedSchema
from ..models.transaction import TransactionStatus, TransactionType

class TransactionBase(BaseSchema):
    agent_id: int
    buyer_id: int
    seller_id: int
    amount: Decimal = Field(..., ge=0)
    type: TransactionType

class TransactionCreate(TransactionBase):
    pass

class TransactionUpdate(BaseSchema):
    status: TransactionStatus
    transaction_hash: Optional[str] = None
    block_number: Optional[int] = None
    error_message: Optional[str] = None

class Transaction(TransactionBase, TimestampedSchema):
    id: int
    status: TransactionStatus
    transaction_hash: Optional[str] = None
    block_number: Optional[int] = None
    blockchain_status: Optional[str] = None
    royalty_amount: Optional[Decimal] = None
    gas_fee: Optional[Decimal] = None
    error_message: Optional[str] = None
    metadata: Optional[Dict] = None

class TransactionWithRelations(Transaction):
    agent: "AgentList"
    buyer: "UserPublic"
    seller: "UserPublic"

from .agent import AgentList
from .user import UserPublic