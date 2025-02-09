from typing import Dict, Any, Optional
import torch
from transformers import (
    GPT2LMHeadModel,
    GPT2Tokenizer,
    GPT2Config,
    Trainer,
    TrainingArguments
)
from datasets import Dataset
import os
import json

from .base import BaseAIModel, ModelFactory

class GPT2Agent(BaseAIModel):
    def __init__(
        self,
        model_name: str,
        model_size: str = "small",
        **kwargs
    ):
        super().__init__(
            model_name=model_name,
            model_type="gpt2",
            **kwargs
        )
        self.model_size = model_size
        self.max_length = 1024
        self.default_training_args = {
            "num_train_epochs": 3,
            "per_device_train_batch_size": 4,
            "per_device_eval_batch_size": 4,
            "learning_rate": 5e-5,
            "warmup_steps": 500,
            "logging_steps": 100,
            "save_steps": 1000,
            "evaluation_strategy": "steps"
        }
        
    async def load_model(self):
        """Load GPT-2 model and tokenizer"""
        model_size_map = {
            "small": "gpt2",
            "medium": "gpt2-medium",
            "large": "gpt2-large"
        }
        
        model_name = model_size_map.get(self.model_size, "gpt2")
        
        self.tokenizer = GPT2Tokenizer.from_pretrained(model_name)
        self.model = GPT2LMHeadModel.from_pretrained(model_name)
        
        # Add padding token if it doesn't exist
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
            self.model.config.pad_token_id = self.tokenizer.pad_token_id
        
        self.model.to(self.device)
        
    async def train(
        self,
        train_data: Dataset,
        validation_data: Optional[Dataset] = None,
        training_args: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Train the GPT-2 model"""
        # Validate and prepare training arguments
        validated_args = await self.validate_training_args(
            training_args or self.default_training_args
        )
        
        # Prepare training arguments
        training_config = TrainingArguments(
            output_dir=f"checkpoints/{self.model_name}",
            **validated_args
        )
        
        # Initialize trainer
        trainer = Trainer(
            model=self.model,
            args=training_config,
            train_dataset=train_data,
            eval_dataset=validation_data,
        )
        
        # Train the model
        train_result = trainer.train()
        
        # Save training metrics
        self.training_metrics = {
            "train_loss": train_result.training_loss,
            "train_steps": train_result.global_step,
            "train_runtime": train_result.metrics["train_runtime"],
        }
        
        if validation_data:
            eval_results = trainer.evaluate()
            self.training_metrics.update(eval_results)
        
        self.is_trained = True
        return self.training_metrics

    async def evaluate(
        self,
        eval_data: Dataset
    ) -> Dict[str, Any]:
        """Evaluate the model"""
        if not self.is_trained:
            raise ValueError("Model must be trained before evaluation")
        
        trainer = Trainer(
            model=self.model,
            args=TrainingArguments(
                output_dir="./eval",
                per_device_eval_batch_size=4
            )
        )
        
        eval_results = trainer.evaluate(eval_data)
        return eval_results

    async def predict(
        self,
        input_text: str,
        max_length: Optional[int] = None,
        temperature: float = 0.7,
        top_p: float = 0.9
    ) -> str:
        """Generate text using the model"""
        inputs = self.tokenizer(
            input_text,
            return_tensors="pt",
            padding=True,
            truncation=True
        ).to(self.device)
        
        max_length = max_length or self.max_length
        
        outputs = self.model.generate(
            inputs.input_ids,
            max_length=max_length,
            temperature=temperature,
            top_p=top_p,
            num_return_sequences=1,
            pad_token_id=self.tokenizer.pad_token_id
        )
        
        return self.tokenizer.decode(
            outputs[0],
            skip_special_tokens=True
        )

    async def save_model(
        self,
        save_path: str
    ) -> Dict[str, str]:
        """Save model and tokenizer"""
        os.makedirs(save_path, exist_ok=True)
        
        # Save model
        model_path = os.path.join(save_path, "model")
        self.model.save_pretrained(model_path)
        
        # Save tokenizer
        tokenizer_path = os.path.join(save_path, "tokenizer")
        self.tokenizer.save_pretrained(tokenizer_path)
        
        # Save configuration and metrics
        config = {
            "model_name": self.model_name,
            "model_type": self.model_type,
            "model_size": self.model_size,
            "training_metrics": self.training_metrics
        }
        
        config_path = os.path.join(save_path, "config.json")
        with open(config_path, "w") as f:
            json.dump(config, f)
        
        return {
            "model": model_path,
            "tokenizer": tokenizer_path,
            "config": config_path
        }

    async def load_from_pretrained(
        self,
        model_path: str
    ) -> None:
        """Load from pretrained weights"""
        # Load model
        self.model = GPT2LMHeadModel.from_pretrained(
            os.path.join(model_path, "model")
        )
        self.model.to(self.device)
        
        # Load tokenizer
        self.tokenizer = GPT2Tokenizer.from_pretrained(
            os.path.join(model_path, "tokenizer")
        )
        
        # Load config and metrics
        config_path = os.path.join(model_path, "config.json")
        if os.path.exists(config_path):
            with open(config_path, "r") as f:
                config = json.load(f)
                self.training_metrics = config.get("training_metrics", {})
                self.is_trained = True

    async def validate_training_args(
        self,
        training_args: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate training arguments"""
        validated = self.default_training_args.copy()
        validated.update(training_args)
        
        # Validate specific arguments
        if validated["num_train_epochs"] <= 0:
            raise ValueError("num_train_epochs must be positive")
        
        if validated["learning_rate"] <= 0:
            raise ValueError("learning_rate must be positive")
        
        return validated

    async def prepare_training_data(
        self,
        data: Any
    ) -> Dataset:
        """Prepare data for training"""
        if isinstance(data, Dataset):
            return data
            
        # Handle different input types
        if isinstance(data, list):
            return Dataset.from_dict({"text": data})
        
        raise ValueError("Unsupported data format")

    async def get_training_config(self) -> Dict[str, Any]:
        """Get model's training configuration"""
        return {
            "model_config": self.model.config.to_dict(),
            "max_length": self.max_length,
            "default_training_args": self.default_training_args,
            "vocab_size": len(self.tokenizer),
            "device": self.device
        }

# Register model with factory
ModelFactory.register_model("gpt2", GPT2Agent)