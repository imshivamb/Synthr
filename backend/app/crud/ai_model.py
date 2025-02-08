from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc, func
from fastapi.encoders import jsonable_encoder

from app.crud.base import CRUDBase
from app.models.ai_model import AIModel, ModelType, ModelStatus
from app.schemas.training import ModelCreate, ModelUpdate
from app.core.redis import redis_client

class CRUDAIModel(CRUDBase[AIModel, ModelCreate, ModelUpdate]):
    async def create_model(
        self,
        db: Session,
        *,
        agent_id: int,
        model_type: ModelType,
        architecture: Dict[str, Any],
        training_config: Dict[str, Any]
    ) -> AIModel:
        """Create a new AI model."""
        db_obj = AIModel(
            agent_id=agent_id,
            model_type=model_type,
            architecture=architecture,
            training_config=training_config,
            status=ModelStatus.INITIALIZING
        )
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        
        # Cache the new model
        await self._update_model_caches(db_obj)
        
        return db_obj

    async def update_status(
        self,
        db: Session,
        *,
        model_id: int,
        status: ModelStatus,
        performance_metrics: Optional[Dict[str, Any]] = None
    ) -> Optional[AIModel]:
        """Update model status and metrics."""
        db_obj = await self.get(db, id=model_id)
        if not db_obj:
            return None

        db_obj.status = status
        if performance_metrics:
            db_obj.performance_metrics = performance_metrics
            
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        
        # Update caches
        await self._update_model_caches(db_obj)
        
        return db_obj

    async def get_agent_model(
        self,
        db: Session,
        *,
        agent_id: int
    ) -> Optional[AIModel]:
        """Get AI model for an agent with caching."""
        cache_key = self._get_cache_key(f"agent:{agent_id}")
        
        cached_data = await redis_client.get(cache_key)
        if cached_data:
            return AIModel(**cached_data)
        
        model = db.query(AIModel).filter(AIModel.agent_id == agent_id).first()
        
        if model:
            await redis_client.set(
                cache_key,
                jsonable_encoder(model),
                expire=3600
            )
        
        return model

    async def get_models_by_type(
        self,
        db: Session,
        *,
        model_type: ModelType,
        skip: int = 0,
        limit: int = 100
    ) -> List[AIModel]:
        """Get models by type with caching."""
        cache_key = self._get_cache_key(f"type:{model_type}:{skip}:{limit}")
        
        cached_data = await redis_client.get(cache_key)
        if cached_data:
            return [AIModel(**item) for item in cached_data]
        
        models = (
            db.query(AIModel)
            .filter(AIModel.model_type == model_type)
            .order_by(desc(AIModel.created_at))
            .offset(skip)
            .limit(limit)
            .all()
        )
        
        if models:
            await redis_client.set(
                cache_key,
                jsonable_encoder(models),
                expire=1800
            )
        
        return models

    async def get_model_stats(
        self,
        db: Session,
        *,
        model_type: Optional[ModelType] = None
    ) -> Dict[str, Any]:
        """Get model statistics with caching."""
        cache_key = self._get_cache_key(f"stats:{model_type or 'all'}")
        
        cached_stats = await redis_client.get(cache_key)
        if cached_stats:
            return cached_stats
        
        query = db.query(
            func.count(AIModel.id).label('total_models'),
            func.avg(AIModel.performance_metrics['accuracy'].cast(float)).label('avg_accuracy')
        )
        
        if model_type:
            query = query.filter(AIModel.model_type == model_type)
        
        stats = query.first()._asdict()
        
        # Add status distribution
        status_dist = (
            db.query(
                AIModel.status,
                func.count(AIModel.id).label('count')
            )
            .filter(AIModel.model_type == model_type if model_type else True)
            .group_by(AIModel.status)
            .all()
        )
        
        stats['status_distribution'] = {
            status.value: count for status, count in status_dist
        }
        
        await redis_client.set(cache_key, stats, expire=1800)
        return stats

    async def _update_model_caches(self, model: AIModel) -> None:
        """Update all caches related to an AI model."""
        data = jsonable_encoder(model)
        
        # Update main cache
        await redis_client.set(
            self._get_cache_key(f"id:{model.id}"),
            data,
            expire=3600
        )
        
        # Update agent cache
        await redis_client.set(
            self._get_cache_key(f"agent:{model.agent_id}"),
            data,
            expire=3600
        )
        
        # Clear related caches
        await redis_client.clear_cache(f"{self.cache_prefix}type:*")
        await redis_client.clear_cache(f"{self.cache_prefix}stats:*")

    async def update_weights(
        self,
        db: Session,
        *,
        model_id: int,
        weights_hash: str,
        checkpoint_hash: Optional[str] = None
    ) -> Optional[AIModel]:
        """Update model weights IPFS hashes."""
        db_obj = await self.get(db, id=model_id)
        if not db_obj:
            return None

        db_obj.weights_hash = weights_hash
        if checkpoint_hash:
            db_obj.checkpoint_hash = checkpoint_hash
            
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        
        # Update caches
        await self._update_model_caches(db_obj)
        
        return db_obj

# Create singleton instance
ai_model = CRUDAIModel(AIModel)