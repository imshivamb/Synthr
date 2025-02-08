from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func
from decimal import Decimal
from fastapi.encoders import jsonable_encoder

from app.crud.base import CRUDBase
from app.models.transaction import Transaction, TransactionStatus, TransactionType
from app.schemas.transaction import TransactionCreate, TransactionUpdate
from app.core.redis import redis_client

class CRUDTransaction(CRUDBase[Transaction, TransactionCreate, TransactionUpdate]):
    async def get_by_hash(self, db: Session, *, tx_hash: str) -> Optional[Transaction]:
        """Get transaction by blockchain hash."""
        cache_key = self._get_cache_key(f"hash:{tx_hash}")
        
        cached_data = await redis_client.get(cache_key)
        if cached_data:
            return Transaction(**cached_data)
        
        db_obj = db.query(Transaction).filter(Transaction.transaction_hash == tx_hash).first()
        if db_obj:
            await redis_client.set(
                cache_key,
                jsonable_encoder(db_obj),
                expire=3600
            )
        return db_obj

    async def get_user_transactions(
        self,
        db: Session,
        *,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
        type: Optional[TransactionType] = None
    ) -> List[Transaction]:
        """Get user's transactions with caching."""
        cache_key = self._get_cache_key(f"user:{user_id}:{type}:{skip}:{limit}")
        
        cached_data = await redis_client.get(cache_key)
        if cached_data:
            return [Transaction(**item) for item in cached_data]
        
        query = db.query(Transaction).filter(
            or_(
                Transaction.buyer_id == user_id,
                Transaction.seller_id == user_id
            )
        )
        
        if type:
            query = query.filter(Transaction.type == type)
        
        transactions = query.order_by(desc(Transaction.created_at)).offset(skip).limit(limit).all()
        
        if transactions:
            await redis_client.set(
                cache_key,
                jsonable_encoder(transactions),
                expire=1800
            )
        
        return transactions

    async def create_purchase(
        self,
        db: Session,
        *,
        agent_id: int,
        buyer_id: int,
        seller_id: int,
        amount: Decimal,
        tx_hash: str
    ) -> Transaction:
        """Create a purchase transaction."""
        db_obj = Transaction(
            agent_id=agent_id,
            buyer_id=buyer_id,
            seller_id=seller_id,
            amount=amount,
            transaction_hash=tx_hash,
            type=TransactionType.PURCHASE,
            status=TransactionStatus.PENDING
        )
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        
        # Cache the new transaction
        await self._update_transaction_caches(db_obj)
        
        return db_obj

    async def update_status(
        self,
        db: Session,
        *,
        tx_hash: str,
        status: TransactionStatus,
        block_number: Optional[int] = None
    ) -> Optional[Transaction]:
        """Update transaction status."""
        db_obj = await self.get_by_hash(db, tx_hash=tx_hash)
        if not db_obj:
            return None

        db_obj.status = status
        if block_number:
            db_obj.block_number = block_number
            
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        
        # Update caches
        await self._update_transaction_caches(db_obj)
        
        return db_obj

    async def get_transaction_stats(
        self,
        db: Session,
        *,
        user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Get transaction statistics with caching."""
        cache_key = self._get_cache_key(f"stats:{user_id or 'global'}")
        
        cached_stats = await redis_client.get(cache_key)
        if cached_stats:
            return cached_stats
        
        query = db.query(
            func.count(Transaction.id).label('total_transactions'),
            func.sum(Transaction.amount).label('total_volume'),
            func.avg(Transaction.amount).label('average_amount')
        )
        
        if user_id:
            query = query.filter(
                or_(
                    Transaction.buyer_id == user_id,
                    Transaction.seller_id == user_id
                )
            )
        
        stats = query.first()._asdict()
        
        await redis_client.set(cache_key, stats, expire=1800)
        return stats

    async def _update_transaction_caches(self, transaction: Transaction) -> None:
        """Update all caches related to a transaction."""
        data = jsonable_encoder(transaction)
        
        # Update main cache
        await redis_client.set(
            self._get_cache_key(f"id:{transaction.id}"),
            data,
            expire=3600
        )
        
        # Update hash cache
        if transaction.transaction_hash:
            await redis_client.set(
                self._get_cache_key(f"hash:{transaction.transaction_hash}"),
                data,
                expire=3600
            )
        
        # Clear related caches
        await redis_client.clear_cache(f"{self.cache_prefix}user:*")
        await redis_client.clear_cache(f"{self.cache_prefix}stats:*")

    async def get_pending_transactions(self, db: Session) -> List[Transaction]:
        """Get all pending transactions."""
        cache_key = self._get_cache_key("pending")
        
        cached_data = await redis_client.get(cache_key)
        if cached_data:
            return [Transaction(**item) for item in cached_data]
        
        transactions = db.query(Transaction).filter(
            Transaction.status == TransactionStatus.PENDING
        ).all()
        
        if transactions:
            await redis_client.set(
                cache_key,
                jsonable_encoder(transactions),
                expire=300
            )
        
        return transactions

# Create singleton instance
transaction = CRUDTransaction(Transaction)