from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func
from decimal import Decimal
from fastapi.encoders import jsonable_encoder

from app.crud.base import CRUDBase
from app.models.agent import Agent, AgentStatus, AgentCategory
from app.schemas.agent import AgentCreate, AgentUpdate
from app.models.user import User
from app.core.redis import redis_client

class CRUDAgent(CRUDBase[Agent, AgentCreate, AgentUpdate]):
    async def create_with_owner(
        self, 
        db: Session, 
        *, 
        obj_in: AgentCreate, 
        owner_id: int
    ) -> Agent:
        """Create a new agent with owner."""
        obj_in_data = obj_in.model_dump()
        db_obj = Agent(**obj_in_data, owner_id=owner_id)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        
        # Cache the new agent
        await self._update_agent_caches(db_obj)
        
        return db_obj

    async def get_by_token_id(self, db: Session, *, token_id: str) -> Optional[Agent]:
        """Get an agent by token ID with caching."""
        cache_key = self._get_cache_key(f"token:{token_id}")
        
        cached_data = await redis_client.get(cache_key)
        if cached_data:
            return Agent(**cached_data)
        
        db_obj = db.query(Agent).filter(Agent.token_id == token_id).first()
        if db_obj:
            await redis_client.set(
                cache_key,
                jsonable_encoder(db_obj),
                expire=3600
            )
        return db_obj

    async def get_multi_by_owner(
        self, 
        db: Session, 
        *, 
        owner_id: int, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Agent]:
        """Get multiple agents by owner with caching."""
        cache_key = self._get_cache_key(f"owner:{owner_id}:{skip}:{limit}")
        
        cached_data = await redis_client.get(cache_key)
        if cached_data:
            return [Agent(**item) for item in cached_data]
        
        agents = (
            db.query(Agent)
            .filter(Agent.owner_id == owner_id)
            .offset(skip)
            .limit(limit)
            .all()
        )
        
        if agents:
            await redis_client.set(
                cache_key,
                jsonable_encoder(agents),
                expire=1800
            )
        return agents

    async def get_multi_by_category(
        self, 
        db: Session, 
        *, 
        category: AgentCategory, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Agent]:
        """Get multiple agents by category with caching."""
        cache_key = self._get_cache_key(f"category:{category}:{skip}:{limit}")
        
        cached_data = await redis_client.get(cache_key)
        if cached_data:
            return [Agent(**item) for item in cached_data]
        
        agents = (
            db.query(Agent)
            .filter(Agent.category == category)
            .offset(skip)
            .limit(limit)
            .all()
        )
        
        if agents:
            await redis_client.set(
                cache_key,
                jsonable_encoder(agents),
                expire=1800
            )
        return agents

    async def list_agent(
        self, 
        db: Session, 
        *, 
        agent_id: int, 
        price: Decimal
    ) -> Optional[Agent]:
        """List an agent for sale."""
        db_obj = await self.get(db, id=agent_id)
        if not db_obj:
            return None

        db_obj.is_listed = True
        db_obj.price = price
        db_obj.status = AgentStatus.LISTED
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        
        # Update caches
        await self._update_agent_caches(db_obj)
        
        return db_obj

    async def delist_agent(self, db: Session, *, agent_id: int) -> Optional[Agent]:
        """Remove an agent from sale."""
        db_obj = await self.get(db, id=agent_id)
        if not db_obj:
            return None

        db_obj.is_listed = False
        db_obj.status = AgentStatus.DELISTED
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        
        # Update caches
        await self._update_agent_caches(db_obj)
        
        return db_obj

    async def search_agents(
        self,
        db: Session,
        *,
        query: Optional[str] = None,
        category: Optional[AgentCategory] = None,
        min_price: Optional[Decimal] = None,
        max_price: Optional[Decimal] = None,
        status: Optional[AgentStatus] = None,
        creator_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100,
        order_by: str = "created_at",
        order_desc: bool = True
    ) -> List[Agent]:
        """Search agents with caching."""
        # Create unique cache key based on search parameters
        cache_key = self._get_cache_key(
            f"search:{query}:{category}:{min_price}:{max_price}:"
            f"{status}:{creator_id}:{skip}:{limit}:{order_by}:{order_desc}"
        )
        
        cached_data = await redis_client.get(cache_key)
        if cached_data:
            return [Agent(**item) for item in cached_data]
        
        # Build filters
        filters = []
        
        if query:
            filters.append(
                or_(
                    Agent.name.ilike(f"%{query}%"),
                    Agent.description.ilike(f"%{query}%")
                )
            )
        
        if category:
            filters.append(Agent.category == category)
            
        if min_price is not None:
            filters.append(Agent.price >= min_price)
            
        if max_price is not None:
            filters.append(Agent.price <= max_price)
            
        if status:
            filters.append(Agent.status == status)
            
        if creator_id:
            filters.append(Agent.creator_id == creator_id)

        # Base query
        query = db.query(Agent)
        
        # Apply filters
        if filters:
            query = query.filter(and_(*filters))
            
        # Apply ordering
        order_col = getattr(Agent, order_by, Agent.created_at)
        if order_desc:
            order_col = desc(order_col)
        query = query.order_by(order_col)
        
        results = query.offset(skip).limit(limit).all()
        
        if results:
            await redis_client.set(
                cache_key,
                jsonable_encoder(results),
                expire=300
            )
        
        return results

    async def get_agent_stats(self, db: Session, *, agent_id: int) -> Dict[str, Any]:
        """Get agent statistics with caching."""
        cache_key = self._get_cache_key(f"stats:{agent_id}")
        
        cached_stats = await redis_client.get(cache_key)
        if cached_stats:
            return cached_stats
        
        stats = db.query(
            func.count(Agent.id).label('total_sales'),
            func.avg(Agent.average_rating).label('avg_rating'),
            func.sum(Agent.total_uses).label('total_uses')
        ).filter(Agent.id == agent_id).first()._asdict()
        
        await redis_client.set(cache_key, stats, expire=1800)
        return stats

    async def transfer_ownership(
        self, 
        db: Session, 
        *, 
        agent_id: int, 
        new_owner_id: int
    ) -> Optional[Agent]:
        """Transfer agent ownership."""
        db_obj = await self.get(db, id=agent_id)
        if not db_obj:
            return None

        db_obj.owner_id = new_owner_id
        db_obj.is_listed = False
        db_obj.status = AgentStatus.SOLD
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        
        # Update caches
        await self._update_agent_caches(db_obj)
        
        return db_obj

    async def _update_agent_caches(self, agent: Agent) -> None:
        """Update all caches related to an agent."""
        data = jsonable_encoder(agent)
        
        # Update main cache
        await redis_client.set(
            self._get_cache_key(f"id:{agent.id}"),
            data,
            expire=3600
        )
        
        # Update token cache if exists
        if agent.token_id:
            await redis_client.set(
                self._get_cache_key(f"token:{agent.token_id}"),
                data,
                expire=3600
            )
        
        # Clear related caches
        await redis_client.clear_cache(f"{self.cache_prefix}search:*")
        await redis_client.clear_cache(f"{self.cache_prefix}owner:*")
        await redis_client.clear_cache(f"{self.cache_prefix}category:*")
        await redis_client.clear_cache(f"{self.cache_prefix}stats:*")

# Create singleton instance
agent = CRUDAgent(Agent)