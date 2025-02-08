from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union, Tuple
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import select, func, or_
from app.db.base_class import Base
from app.core.redis import redis_client

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)

class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        """
        CRUD object with default methods to Create, Read, Update, Delete (CRUD).
        """
        self.model = model
        self.cache_prefix = f"synthr:{model.__name__.lower()}:"
    
    def _get_cache_key(self, key: str) -> str:
        """Generate cache key with prefix"""
        return f"{self.cache_prefix}{key}"
        
    async def get(self, db: Session, id: Any) -> Optional[ModelType]:
        """Get a record by ID with caching."""
        cache_key = self._get_cache_key(f"id:{id}")
        
        # Try to get from cache
        cached_data = await redis_client.get(cache_key)
        if cached_data:
            return self.model(**cached_data)
        
        # Get from database
        db_obj = db.query(self.model).filter(self.model.id == id).first()
        if db_obj:
            await redis_client.set(
                cache_key,
                jsonable_encoder(db_obj),
                expire=3600
            )
        return db_obj
    
    async def get_multi(self, db: Session, *, skip: int = 0, limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[ModelType]:
        """Get multiple records with optional filters and caching."""
        filter_key = "_".join(f"{k}:{v}" for k, v in (filters or {}).items())
        cache_key = self._get_cache_key(f"list:{skip}:{limit}:{filter_key}")
        
        cached_data = await redis_client.get(cache_key)
        if cached_data:
            return [self.model(**item) for item in cached_data]
        
        query = db.query(self.model)
        
        if filters:
            filter_conditions = []
            for key, value in filters.items():
                if hasattr(self.model, key):
                    if isinstance(value, (list, tuple)):
                        filter_conditions.append(getattr(self.model, key).in_(value))
                    else:
                        filter_conditions.append(getattr(self.model, key) == value)
            if filter_conditions:
                query = query.filter(*filter_conditions)
        
        db_objs = query.offset(skip).limit(limit).all()
        
        if db_objs:
            await redis_client.set(
                cache_key,
                jsonable_encoder(db_objs),
                expire=3600
            )
        return db_objs
    
    async def get_count(self, db: Session, filters: Optional[Dict[str, Any]] = None) -> int:
        """Get total count of records with optional filters and caching."""
        filter_key = "_".join(f"{k}:{v}" for k, v in (filters or {}).items())
        cache_key = self._get_cache_key(f"count:{filter_key}")
        
        cached_count = await redis_client.get(cache_key)
        if cached_count is not None:
            return int(cached_count)
        
        query = db.query(func.count(self.model.id))
        
        if filters:
            filter_conditions = []
            for key, value in filters.items():
                if hasattr(self.model, key):
                    if isinstance(value, (list, tuple)):
                        filter_conditions.append(getattr(self.model, key).in_(value))
                    else:
                        filter_conditions.append(getattr(self.model, key) == value)
            if filter_conditions:
                query = query.filter(*filter_conditions)
        
        count = query.scalar()
        await redis_client.set(cache_key, count, expire=3600)
        return count

    async def create(self, db: Session, *, obj_in: CreateSchemaType) -> ModelType:
        """Create a new record and invalidate relevant caches."""
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        
        # Clear list and count caches
        await redis_client.clear_cache(f"{self.cache_prefix}list:*")
        await redis_client.clear_cache(f"{self.cache_prefix}count:*")
        
        # Cache the new object
        cache_key = self._get_cache_key(f"id:{db_obj.id}")
        await redis_client.set(
            cache_key,
            jsonable_encoder(db_obj),
            expire=3600
        )
        
        return db_obj
    
    async def update(self, db: Session, *, db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        """Update a record and update cache."""
        obj_data = jsonable_encoder(db_obj)
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)
        
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        
        # Update cache
        cache_key = self._get_cache_key(f"id:{db_obj.id}")
        await redis_client.set(
            cache_key,
            jsonable_encoder(db_obj),
            expire=3600
        )
        
        # Clear list caches
        await redis_client.clear_cache(f"{self.cache_prefix}list:*")
        
        return db_obj
    
    async def remove(self, db: Session, *, id: int) -> ModelType:
        """Delete a record and clear caches."""
        obj = db.query(self.model).get(id)
        db.delete(obj)
        db.commit()
        
        # Clear all related caches
        await redis_client.clear_cache(f"{self.cache_prefix}*")
        
        return obj
    
    async def exists(self, db: Session, id: int) -> bool:
        """Check if a record exists with caching."""
        cache_key = self._get_cache_key(f"exists:{id}")
        
        cached_exists = await redis_client.get(cache_key)
        if cached_exists is not None:
            return bool(int(cached_exists))
        
        exists = db.query(
            db.query(self.model).filter(self.model.id == id).exists()
        ).scalar()
        
        await redis_client.set(cache_key, int(exists), expire=3600)
        return exists
        
    async def get_by_ids(self, db: Session, *, ids: List[int]) -> List[ModelType]:
        """Get multiple records by their IDs with caching."""
        results = []
        uncached_ids = []

        for id in ids:
            cache_key = self._get_cache_key(f"id:{id}")
            cached_data = await redis_client.get(cache_key)
            if cached_data:
                results.append(self.model(**cached_data))
            else:
                uncached_ids.append(id)
        
        # Get uncached items from database
        if uncached_ids:
            db_objs = (
                db.query(self.model)
                .filter(self.model.id.in_(uncached_ids))
                .all()
            )
            
            # Cache the results
            for obj in db_objs:
                cache_key = self._get_cache_key(f"id:{obj.id}")
                await redis_client.set(
                    cache_key,
                    jsonable_encoder(obj),
                    expire=3600
                )
                results.append(obj)
        
        return sorted(results, key=lambda x: ids.index(x.id))
    
    async def bulk_create(
        self, 
        db: Session, 
        *, 
        objs_in: List[CreateSchemaType]
    ) -> List[ModelType]:
        """Create multiple records at once."""
        db_objs = []
        for obj_in in objs_in:
            obj_in_data = jsonable_encoder(obj_in)
            db_obj = self.model(**obj_in_data)
            db_objs.append(db_obj)
        
        db.add_all(db_objs)
        db.commit()
        for obj in db_objs:
            db.refresh(obj)
            
        # Clear list and count caches
        await redis_client.clear_cache(f"{self.cache_prefix}list:*")
        await redis_client.clear_cache(f"{self.cache_prefix}count:*")
        
        # Cache new objects
        for obj in db_objs:
            cache_key = self._get_cache_key(f"id:{obj.id}")
            await redis_client.set(
                cache_key,
                jsonable_encoder(obj),
                expire=3600
            )
        
        return db_objs

    async def bulk_update(
        self, 
        db: Session, 
        *, 
        objs: List[Tuple[ModelType, UpdateSchemaType]]
    ) -> List[ModelType]:
        """Update multiple records at once."""
        updated_objs = []
        for db_obj, obj_in in objs:
            updated_obj = await self.update(db, db_obj=db_obj, obj_in=obj_in)
            updated_objs.append(updated_obj)
        return updated_objs