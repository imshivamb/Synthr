from typing import Any, Dict, Optional, Union, List
from sqlalchemy.orm import Session
from sqlalchemy import select, or_
from fastapi.encoders import jsonable_encoder

from app.crud.base import CRUDBase
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.redis import redis_client

class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    async def get_by_wallet(self, db: Session, *, wallet_address: str) -> Optional[User]:
        """Get a user by wallet address with caching."""
        cache_key = self._get_cache_key(f"wallet:{wallet_address}")
        
        cached_data = await redis_client.get(cache_key)
        if cached_data:
            return User(**cached_data)
        
        db_obj = db.query(User).filter(User.wallet_address == wallet_address).first()
        if db_obj:
            await redis_client.set(
                cache_key,
                jsonable_encoder(db_obj),
                expire=3600
            )
        return db_obj
    
    async def get_by_username(self, db: Session, *, username: str) -> Optional[User]:
        """Get a user by username with caching."""
        cache_key = self._get_cache_key(f"username:{username}")
        
        cached_data = await redis_client.get(cache_key)
        if cached_data:
            return User(**cached_data)
        
        db_obj = db.query(User).filter(User.username == username).first()
        if db_obj:
            await redis_client.set(
                cache_key,
                jsonable_encoder(db_obj),
                expire=3600
            )
        return db_obj

    
    async def create_with_wallet(self, db: Session, *, wallet_address: str) -> User:
        """Create a new user with wallet address."""
        db_obj = User(wallet_address=wallet_address, is_active=True)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        
        # Cache the new user
        cache_key = self._get_cache_key(f"wallet:{wallet_address}")
        await redis_client.set(
            cache_key,
            jsonable_encoder(db_obj),
            expire=3600
        )
        
        return db_obj
    
    async def update_nonce(self, db: Session, *, user_id: int, nonce: str) -> User:
        """Update user's authentication nonce."""
        db_obj = await self.get(db, id=user_id)
        if not db_obj:
            return None

        db_obj.nonce = nonce
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        
        # Update caches
        await self._update_user_caches(db_obj)
        
        return db_obj
    
    async def get_user_stats(self, db: Session, *, user_id: int) -> Dict[str, Any]:
        """Get user's statistics with caching."""
        cache_key = self._get_cache_key(f"stats:{user_id}")
        
        cached_stats = await redis_client.get(cache_key)
        if cached_stats:
            return cached_stats
        
        user = await self.get(db, id=user_id)
        if not user:
            return {}

        stats = {
            "total_agents_created": len(user.created_agents),
            "total_agents_owned": len(user.owned_agents),
            "total_transactions": len(user.sent_transactions) + len(user.received_transactions),
            "average_rating": await self._calculate_average_rating(user),
            "total_revenue": await self._calculate_total_revenue(user)
        }
        
        await redis_client.set(cache_key, stats, expire=1800)  # 30 minutes
        return stats
    
    async def _update_user_caches(self, user: User) -> None:
        """Update all caches related to a user."""
        data = jsonable_encoder(user)
        
        # Update main cache
        await redis_client.set(
            self._get_cache_key(f"id:{user.id}"),
            data,
            expire=3600
        )
        
        # Update wallet cache
        if user.wallet_address:
            await redis_client.set(
                self._get_cache_key(f"wallet:{user.wallet_address}"),
                data,
                expire=3600
            )
        
        # Update username cache
        if user.username:
            await redis_client.set(
                self._get_cache_key(f"username:{user.username}"),
                data,
                expire=3600
            )
        
        # Clear related caches
        await redis_client.clear_cache(f"{self.cache_prefix}search:*")
        await redis_client.clear_cache(f"{self.cache_prefix}stats:{user.id}")

    async def _calculate_average_rating(self, user: User) -> float:
        """Calculate user's average rating."""
        total_ratings = sum(len(agent.reviews) for agent in user.created_agents)
        if total_ratings == 0:
            return 0.0
        
        total_score = sum(
            sum(review.rating for review in agent.reviews)
            for agent in user.created_agents
        )
        return round(total_score / total_ratings, 2)

    async def _calculate_total_revenue(self, user: User) -> float:
        """Calculate user's total revenue."""
        return sum(float(tx.amount) for tx in user.received_transactions)


    
    async def search_users(
        self, 
        db: Session, 
        *, 
        query: str,
        skip: int = 0,
        limit: int = 10
    ) -> List[User]:
        """Search users with caching."""
        cache_key = self._get_cache_key(f"search:{query}:{skip}:{limit}")
        
        cached_results = await redis_client.get(cache_key)
        if cached_results:
            return [User(**user_data) for user_data in cached_results]
        
        results = (
            db.query(User)
            .filter(
                or_(
                    User.username.ilike(f"%{query}%"),
                    User.wallet_address.ilike(f"%{query}%")
                )
            )
            .offset(skip)
            .limit(limit)
            .all()
        )
        
        if results:
            await redis_client.set(
                cache_key,
                jsonable_encoder(results),
                expire=300
            )
        
        return results
        
    def is_username_taken(self, db: Session, *, username: str) -> bool:
        """
        Check if a username is already taken.
        """
        return db.query(
            db.query(User)
            .filter(User.username == username)
            .exists()
        ).scalar()

    def deactivate(self, db: Session, *, user_id: int) -> User:
        """
        Deactivate a user account.
        """
        db_obj = self.get(db, id=user_id)
        db_obj.is_active = False
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

user = CRUDUser(User)