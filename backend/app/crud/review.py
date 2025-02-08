from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func
from decimal import Decimal
from fastapi.encoders import jsonable_encoder

from app.crud.base import CRUDBase
from app.models.review import Review
from app.schemas.review import ReviewCreate, ReviewUpdate
from app.core.redis import redis_client

class CRUDReview(CRUDBase[Review, ReviewCreate, ReviewUpdate]):
    async def create_with_user(
        self,
        db: Session,
        *,
        obj_in: ReviewCreate,
        reviewer_id: int,
        agent_creator_id: int
    ) -> Review:
        """Create a new review with user information."""
        db_obj = Review(
            **obj_in.model_dump(),
            reviewer_id=reviewer_id,
            agent_creator_id=agent_creator_id
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        
        # Cache the new review
        await self._update_review_caches(db_obj)
        
        return db_obj

    async def get_agent_reviews(
        self,
        db: Session,
        *,
        agent_id: int,
        skip: int = 0,
        limit: int = 100,
        verified_only: bool = False
    ) -> List[Review]:
        """Get reviews for an agent with caching."""
        cache_key = self._get_cache_key(f"agent:{agent_id}:{verified_only}:{skip}:{limit}")
        
        cached_data = await redis_client.get(cache_key)
        if cached_data:
            return [Review(**item) for item in cached_data]
        
        query = db.query(Review).filter(Review.agent_id == agent_id)
        
        if verified_only:
            query = query.filter(Review.is_verified_purchase == True)
        
        reviews = (
            query
            .order_by(desc(Review.created_at))
            .offset(skip)
            .limit(limit)
            .all()
        )
        
        if reviews:
            await redis_client.set(
                cache_key,
                jsonable_encoder(reviews),
                expire=1800
            )
        
        return reviews

    async def get_user_reviews(
        self,
        db: Session,
        *,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
        as_creator: bool = False
    ) -> List[Review]:
        """Get reviews by or for a user with caching."""
        cache_key = self._get_cache_key(f"user:{user_id}:{as_creator}:{skip}:{limit}")
        
        cached_data = await redis_client.get(cache_key)
        if cached_data:
            return [Review(**item) for item in cached_data]
        
        query = db.query(Review)
        if as_creator:
            query = query.filter(Review.agent_creator_id == user_id)
        else:
            query = query.filter(Review.reviewer_id == user_id)
        
        reviews = (
            query
            .order_by(desc(Review.created_at))
            .offset(skip)
            .limit(limit)
            .all()
        )
        
        if reviews:
            await redis_client.set(
                cache_key,
                jsonable_encoder(reviews),
                expire=1800
            )
        
        return reviews

    async def get_review_stats(
        self,
        db: Session,
        *,
        agent_id: Optional[int] = None,
        user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Get review statistics with caching."""
        cache_key = self._get_cache_key(f"stats:agent{agent_id or ''}:user{user_id or ''}")
        
        cached_stats = await redis_client.get(cache_key)
        if cached_stats:
            return cached_stats
        
        query = db.query(
            func.count(Review.id).label('total_reviews'),
            func.avg(Review.rating).label('average_rating'),
            func.count(Review.id).filter(Review.is_verified_purchase == True).label('verified_reviews')
        )
        
        if agent_id:
            query = query.filter(Review.agent_id == agent_id)
        if user_id:
            query = query.filter(Review.agent_creator_id == user_id)
        
        stats = query.first()._asdict()
        
        # Add rating distribution
        if agent_id or user_id:
            rating_dist = (
                db.query(
                    Review.rating,
                    func.count(Review.id).label('count')
                )
                .filter(Review.agent_id == agent_id if agent_id else Review.agent_creator_id == user_id)
                .group_by(Review.rating)
                .all()
            )
            stats['rating_distribution'] = {
                float(rating): count for rating, count in rating_dist
            }
        
        await redis_client.set(cache_key, stats, expire=1800)
        return stats

    async def _update_review_caches(self, review: Review) -> None:
        """Update all caches related to a review."""
        data = jsonable_encoder(review)
        
        # Update main cache
        await redis_client.set(
            self._get_cache_key(f"id:{review.id}"),
            data,
            expire=3600
        )
        
        # Clear related caches
        await redis_client.clear_cache(f"{self.cache_prefix}agent:*")
        await redis_client.clear_cache(f"{self.cache_prefix}user:*")
        await redis_client.clear_cache(f"{self.cache_prefix}stats:*")

    async def verify_purchase(
        self,
        db: Session,
        *,
        review_id: int,
        is_verified: bool = True
    ) -> Optional[Review]:
        """Mark a review as verified purchase."""
        db_obj = await self.get(db, id=review_id)
        if not db_obj:
            return None
            
        db_obj.is_verified_purchase = is_verified
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        
        # Update caches
        await self._update_review_caches(db_obj)
        
        return db_obj

# Create singleton instance
review = CRUDReview(Review)