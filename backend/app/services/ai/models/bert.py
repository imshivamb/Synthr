from typing import Dict, Any, Optional
import torch
from transformers import (
    BertForSequenceClassification,
    BertTokenizer,
    BertConfig,
    Trainer,
    TrainingArguments
)
from datasets import Dataset
import os
import json

from .base import BaseAIModel, ModelFactory

class BertAgent(BaseAIModel):
    def __init__(self, model_name: str, num_labels: int = 2, model_size: str = "base", **kwargs):
        super().__init__(
            model_name=model_name,
            model_type="bert",
            **kwargs
        )
        self.model_size = model_size
        self.num_labels = num_labels
        self.max_length = 512
        self.default_training_args = {
            "num_train_epochs": 3,
            "per_device_train_batch_size": 8,
            "per_device_eval_batch_size": 8,
            "learning_rate": 2e-5,
            "warmup_steps": 500,
            "logging_steps": 100,
            "save_steps": 1000,
            "evaluation_strategy": "steps",
            "weight_decay": 0.01
        }
    
    async def load_models(self) -> None:
        """Load BERT model and tokenizer"""
        model_size_map = {
            "base": "bert-base-uncased",
            "large": "bert-large-uncased"
        }
        
        model_name = model_size_map.get(self.model_size, "bert-base-uncased")
        
        self.tokenizer = BertTokenizer.from_pretrained(model_name)
        self.model = BertForSequenceClassification.from_pretrained(model_name, num_labels=self.num_labels)
        self.model.to(self.device)
        
    async def train(self, train_data: Dataset, validation_data: Optional[Dataset] = None, training_args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Train the BERT model"""
        # Validate and prepare training arguments
        validated_args = await self.validate_training_args(training_args or self.default_training_args)
        
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
    
    async def evaluate(self, eval_data: Dataset) -> Dict[str, Any]:
        """Evaluate the model"""
        if not self.is_trained:
            raise ValueError("Model must be trained before evaluation")
        
        trainer = Trainer(
            model=self.model,
            args=TrainingArguments(
                output_dir="./eval",
                per_device_eval_batch_size=8
            )
        )
        
        eval.results = trainer.evaluate(eval_data)
        return eval.results
    
    async def predict(self, input_text: str, raw_output: bool = False) -> Any:
        """Make predictions using the model"""
        inputs = self.tokenizer(
            input_text,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=self.max_length
        ).to(self.device)
        
        # Get predictions
        outputs = self.model(**inputs)
        logits = outputs.logits
        probs = torch.nn.functional.softmax(logits, dim=-1)
        
        if raw_output:
            return {
                "logits": logits.tolist(),
                "probabilities": probs.tolist()
            }
        
        # Return predicted class
        predictions = torch.argmax(probs, dim=-1)
        return predictions.item()
    
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
            "num_labels": self.num_labels,
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
        self.model = BertForSequenceClassification.from_pretrained(
            os.path.join(model_path, "model")
        )
        self.model.to(self.device)
        
        # Load tokenizer
        self.tokenizer = BertTokenizer.from_pretrained(
            os.path.join(model_path, "tokenizer")
        )
        
        # Load config and metrics
        config_path = os.path.join(model_path, "config.json")
        if os.path.exists(config_path):
            with open(config_path, "r") as f:
                config = json.load(f)
                self.num_labels = config.get("num_labels", self.num_labels)
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
        
        if validated["weight_decay"] < 0:
            raise ValueError("weight_decay must be non-negative")
        
        return validated

    async def prepare_training_data(
        self,
        data: Any
    ) -> Dataset:
        """Prepare data for training"""
        if isinstance(data, Dataset):
            return data
            
        # Handle different input types
        if isinstance(data, dict):
            return Dataset.from_dict(data)
        
        raise ValueError("Unsupported data format")

    async def get_training_config(self) -> Dict[str, Any]:
        """Get model's training configuration"""
        return {
            "model_config": self.model.config.to_dict(),
            "max_length": self.max_length,
            "default_training_args": self.default_training_args,
            "vocab_size": len(self.tokenizer),
            "num_labels": self.num_labels,
            "device": self.device
        }

# Register model with factory
ModelFactory.register_model("bert", BertAgent)