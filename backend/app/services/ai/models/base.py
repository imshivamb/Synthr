from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
import torch
from transformers import PreTrainedModel, PreTrainedTokenizer

class BaseAIModel(ABC):
    """Base class for all AI models in the system"""
    
    def __init__(
        self,
        model_name: str,
        model_type: str,
        tokenizer: Optional[PreTrainedTokenizer] = None,
        model: Optional[PreTrainedModel] = None,
        device: str = "cuda" if torch.cuda.is_available() else "cpu"
    ):
        self.model_name = model_name
        self.model_type = model_type
        self.tokenizer = tokenizer
        self.model = model
        self.device = device
        self.is_trained = False
        self.training_metrics = {}
        
    @abstractmethod
    async def load_model(self) -> None:
        """Load the model and tokenizer"""
        pass
    
    @abstractmethod
    async def train(
        self,
        train_data: Any,
        validation_data: Optional[Any] = None,
        training_args: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Train the model"""
        pass
    
    @abstractmethod
    async def evaluate(
        self,
        eval_data: Any
    ) -> Dict[str, Any]:
        """Evaluate the model"""
        pass

    @abstractmethod
    async def predict(
        self,
        input_data: Any
    ) -> Any:
        """Make predictions"""
        pass

    @abstractmethod
    async def save_model(
        self,
        save_path: str
    ) -> Dict[str, str]:
        """Save model and tokenizer"""
        pass

    @abstractmethod
    async def load_from_pretrained(
        self,
        model_path: str
    ) -> None:
        """Load from pretrained weights"""
        pass

    async def get_model_info(self) -> Dict[str, Any]:
        """Get model information"""
        return {
            "model_name": self.model_name,
            "model_type": self.model_type,
            "device": self.device,
            "is_trained": self.is_trained,
            "training_metrics": self.training_metrics,
            "model_parameters": self.get_parameter_count() if self.model else None
        }

    def get_parameter_count(self) -> Dict[str, int]:
        """Get model parameter count"""
        if not self.model:
            return {"total": 0, "trainable": 0}

        total_params = sum(p.numel() for p in self.model.parameters())
        trainable_params = sum(
            p.numel() for p in self.model.parameters() if p.requires_grad
        )
        
        return {
            "total": total_params,
            "trainable": trainable_params
        }

    @abstractmethod
    async def validate_training_args(
        self,
        training_args: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate training arguments"""
        pass

    @abstractmethod
    async def prepare_training_data(
        self,
        data: Any
    ) -> Any:
        """Prepare data for training"""
        pass

    @abstractmethod
    async def get_training_config(self) -> Dict[str, Any]:
        """Get model's training configuration"""
        pass

class ModelFactory:
    """Factory for creating AI models"""
    
    _models: Dict[str, type] = {}

    @classmethod
    def register_model(cls, model_type: str, model_class: type):
        """Register a new model type"""
        cls._models[model_type] = model_class

    @classmethod
    def create_model(
        cls,
        model_type: str,
        model_name: str,
        **kwargs
    ) -> BaseAIModel:
        """Create a model instance"""
        if model_type not in cls._models:
            raise ValueError(f"Unknown model type: {model_type}")
        
        model_class = cls._models[model_type]
        return model_class(model_name=model_name, **kwargs)

    @classmethod
    def get_available_models(cls) -> List[str]:
        """Get list of registered model types"""
        return list(cls._models.keys())