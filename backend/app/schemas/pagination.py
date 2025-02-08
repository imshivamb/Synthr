from typing import Optional, List, Generic, TypeVar
from pydantic import BaseModel, Field
from .base import BaseSchema

T = TypeVar('T')

class PaginationParams(BaseSchema):
    page: int = Field(default=1, ge=1, description="Page number")
    size: int = Field(default=10, ge=1, le=100, description="Items per page")
    sort_by: Optional[str] = None
    sort_desc: bool = False

class PageInfo(BaseSchema):
    total: int
    page: int
    size: int
    pages: int
    has_next: bool
    has_prev: bool

class PaginatedData(BaseModel, Generic[T]):
    data: List[T]
    page_info: PageInfo