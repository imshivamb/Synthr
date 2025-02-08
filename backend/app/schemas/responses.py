from typing import Generic, TypeVar, Optional, List, Any
from pydantic import BaseModel
from .base import BaseSchema

T = TypeVar('T')

class HTTPError(BaseSchema):
    detail: str
    code: Optional[str] = None
    
class SuccessResponse(BaseSchema):
    message: str
    data: Optional[dict] = None
    
class PaginatedResponse(BaseSchema, Generic[T]):
    items: List[T]
    total: int
    page: int
    size: int
    pages: int
    has_next: bool
    has_prev: bool

class ValidationError(BaseSchema):
    loc: List[str]
    msg: str
    type: str

class ErrorResponse(BaseSchema):
    detail: str
    errors: Optional[List[ValidationError]] = None