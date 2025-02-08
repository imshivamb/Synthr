from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc, func
from fastapi.encoders import jsonable_encoder

from app.crud.base import CRUDBase
from app.models.training import TrainingJob, TrainingStatus
from app.models.ai_model import AIModel, ModelType, ModelStatus
from app.schemas.training import TrainingJobCreate, TrainingJobUpdate
from app.core.redis import redis_client

class CRUDTraining(CRUDBase[TrainingJob, TrainingJobCreate, TrainingJobUpdate]):
    async def create_training_job(
        self,
        db: Session,
        *,
        agent_id: int,
        model_id: int,
        training_config: Dict[str, Any]
    ) -> TrainingJob:
        """Create a new training job."""
        db_obj = TrainingJob(
            agent_id=agent_id,
            model_id=model_id,
            training_config=training_config,
            status=TrainingStatus.PENDING
        )
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        
        # Cache the new job
        await self._update_training_caches(db_obj)
        
        return db_obj

    async def update_progress(
        self,
        db: Session,
        *,
        job_id: int,
        progress: float,
        current_loss: Optional[float] = None,
        current_accuracy: Optional[float] = None,
        metrics: Optional[Dict[str, Any]] = None
    ) -> Optional[TrainingJob]:
        """Update training progress."""
        db_obj = await self.get(db, id=job_id)
        if not db_obj:
            return None

        db_obj.progress = progress
        if current_loss is not None:
            db_obj.current_loss = current_loss
        if current_accuracy is not None:
            db_obj.current_accuracy = current_accuracy
        if metrics:
            db_obj.metrics = metrics
            
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        
        # Update caches
        await self._update_training_caches(db_obj)
        
        return db_obj

    async def get_agent_training_jobs(
        self,
        db: Session,
        *,
        agent_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[TrainingJob]:
        """Get training jobs for an agent with caching."""
        cache_key = self._get_cache_key(f"agent:{agent_id}:{skip}:{limit}")
        
        cached_data = await redis_client.get(cache_key)
        if cached_data:
            return [TrainingJob(**item) for item in cached_data]
        
        jobs = (
            db.query(TrainingJob)
            .filter(TrainingJob.agent_id == agent_id)
            .order_by(desc(TrainingJob.created_at))
            .offset(skip)
            .limit(limit)
            .all()
        )
        
        if jobs:
            await redis_client.set(
                cache_key,
                jsonable_encoder(jobs),
                expire=1800
            )
        
        return jobs

    async def get_active_jobs(self, db: Session) -> List[TrainingJob]:
        """Get all active training jobs with caching."""
        cache_key = self._get_cache_key("active")
        
        cached_data = await redis_client.get(cache_key)
        if cached_data:
            return [TrainingJob(**item) for item in cached_data]
        
        jobs = db.query(TrainingJob).filter(
            TrainingJob.status.in_([TrainingStatus.PENDING, TrainingStatus.RUNNING])
        ).all()
        
        if jobs:
            await redis_client.set(
                cache_key,
                jsonable_encoder(jobs),
                expire=300
            )
        
        return jobs

    async def get_training_stats(
        self,
        db: Session,
        *,
        agent_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Get training statistics with caching."""
        cache_key = self._get_cache_key(f"stats:{agent_id or 'global'}")
        
        cached_stats = await redis_client.get(cache_key)
        if cached_stats:
            return cached_stats
        
        query = db.query(
            func.count(TrainingJob.id).label('total_jobs'),
            func.avg(TrainingJob.compute_time).label('avg_compute_time'),
            func.avg(TrainingJob.current_accuracy).label('avg_accuracy')
        )
        
        if agent_id:
            query = query.filter(TrainingJob.agent_id == agent_id)
        
        stats = query.first()._asdict()
        
        await redis_client.set(cache_key, stats, expire=1800)
        return stats

    async def _update_training_caches(self, job: TrainingJob) -> None:
        """Update all caches related to a training job."""
        data = jsonable_encoder(job)
        
        # Update main cache
        await redis_client.set(
            self._get_cache_key(f"id:{job.id}"),
            data,
            expire=3600
        )
        
        # Clear related caches
        await redis_client.clear_cache(f"{self.cache_prefix}agent:*")
        await redis_client.clear_cache(f"{self.cache_prefix}active")
        await redis_client.clear_cache(f"{self.cache_prefix}stats:*")

# Create singleton instance
training = CRUDTraining(TrainingJob)