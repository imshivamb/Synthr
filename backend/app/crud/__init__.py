from .user import user
from .agent import agent
from .transaction import transaction
from .training import training
from .review import review
from .ai_model import ai_model

# Export all CRUD instances
__all__ = [
    "user",
    "agent",
    "transaction",
    "training",
    "review",
    "ai_model"
]