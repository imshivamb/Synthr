from typing import Dict, Any
from pydantic import BaseModel, validator
from fastapi import HTTPException
from app.services.ai.models.base import ModelFactory

class TrainingConfig(BaseModel):
    num_train_epochs: int
    batch_size: int
    learning_rate: float
    max_length: int = 512
    warmup_steps: int = 0
    weight_decay: float = 0.01
    gradient_accumulation_steps: int = 1
    
    @validator('num_train_epochs')
    def validate_epochs(cls, v):
        if v <= 0:
            raise ValueError("num_train_epochs must be positive")
        if v > 100:
            raise ValueError("num_train_epochs cannot exceed 100")
        return v
    
    @validator('batch_size')
    def validate_batch_size(cls, v):
        if v <= 0:
            raise ValueError("batch_size must be positive")
        if v > 128:
            raise ValueError("batch_size cannot exceed 128")
        return v
    
    @validator('learning_rate')
    def validate_learning_rate(cls, v):
        if v <= 0:
            raise ValueError("learning_rate must be positive")
        if v > 1:
            raise ValueError("learning_rate cannot exceed 1")
        return v

class TrainingValidator:
    """Validator for training requests and configurations"""
    
    async def validate_training_request(
        self,
        model_type: str,
        training_data: Any,
        config: Dict[str, Any]
    ) -> None:
        """
        Validate complete training request
        Raises HTTPException if validation fails
        """
        try:
            # Validate model type
            self._validate_model_type(model_type)
            
            # Validate training data
            self._validate_training_data(training_data)
            
            # Validate config
            self._validate_config(config)
            
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

    def _validate_model_type(self, model_type: str) -> None:
        """Validate model type exists"""
        available_models = ModelFactory.get_available_models()
        if model_type not in available_models:
            raise ValueError(
                f"Invalid model type. Available types: {available_models}"
            )

    def _validate_training_data(self, training_data: Any) -> None:
        """Validate training data format and size"""
        if training_data is None:
            raise ValueError("Training data cannot be None")
            
        if isinstance(training_data, list):
            if not training_data:
                raise ValueError("Training data list cannot be empty")
            if len(training_data) < 100:
                raise ValueError("Training data must contain at least 100 samples")
                
        elif isinstance(training_data, dict):
            if not training_data:
                raise ValueError("Training data dict cannot be empty")
            if 'text' not in training_data and 'input' not in training_data:
                raise ValueError("Training data must contain 'text' or 'input' key")

    def _validate_config(self, config: Dict[str, Any]) -> None:
        """Validate training configuration"""
        try:
            TrainingConfig(**config)
        except Exception as e:
            raise ValueError(f"Invalid training configuration: {str(e)}")

    async def validate_model_size(
        self,
        model_type: str,
        model_size: str
    ) -> None:
        """Validate model size for type"""
        valid_sizes = {
            "gpt2": ["small", "medium", "large"],
            "bert": ["base", "large"]
        }
        
        if model_type not in valid_sizes:
            raise ValueError(f"Unknown model type: {model_type}")
            
        if model_size not in valid_sizes[model_type]:
            raise ValueError(
                f"Invalid size for {model_type}. "
                f"Valid sizes: {valid_sizes[model_type]}"
            )

    async def validate_resources(
        self,
        config: Dict[str, Any]
    ) -> None:
        """Validate resource requirements"""
        # Calculate approximate memory requirements
        batch_size = config.get('batch_size', 8)
        max_length = config.get('max_length', 512)
        model_size = config.get('model_size', 'base')
        
        # Rough memory estimation in GB
        memory_requirement = (
            batch_size * max_length * 
            (2 if model_size == 'base' else 4)
        ) / 1024
        
        if memory_requirement > 16:  # 16GB limit
            raise ValueError(
                f"Configuration would require approximately "
                f"{memory_requirement:.1f}GB of GPU memory. "
                f"Please reduce batch size or sequence length."
            )

    async def validate_training_duration(
        self,
        config: Dict[str, Any],
        num_samples: int
    ) -> None:
        """Validate estimated training duration"""
        epochs = config.get('num_train_epochs', 3)
        batch_size = config.get('batch_size', 8)
        
        # Rough time estimation in hours
        estimated_time = (
            num_samples * epochs * 0.001 / batch_size
        )  # Very rough estimate
        
        if estimated_time > 24:  # 24 hour limit
            raise ValueError(
                f"Estimated training time of {estimated_time:.1f} hours "
                f"exceeds the 24-hour limit. Please reduce epochs or data size."
            )

    async def validate_data_format(
        self,
        data: Any,
        expected_format: str
    ) -> None:
        """Validate specific data format requirements"""
        if expected_format == "classification":
            if not isinstance(data, dict) or "labels" not in data:
                raise ValueError(
                    "Classification data must include 'labels' field"
                )
            if not all(isinstance(l, (int, str)) for l in data["labels"]):
                raise ValueError(
                    "Classification labels must be integers or strings"
                )
                
        elif expected_format == "generation":
            if not isinstance(data, (list, dict)):
                raise ValueError(
                    "Generation data must be list of texts or dict with 'text' field"
                )
            
        elif expected_format == "sequence":
            if not isinstance(data, dict) or "input" not in data:
                raise ValueError(
                    "Sequence data must include 'input' field"
                )