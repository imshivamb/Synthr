from typing import Dict, Any, Optional, List
import os
import json
import asyncio
import logging
from datetime import datetime
import httpx
from app.services.ai.models.base import BaseAIModel

logger = logging.getLogger(__name__)

class ModelTrainer:
    def __init__(self, model: BaseAIModel, training_id: str, callback_url: Optional[str] = None):
        self.model = model
        self.training_id = training_id
        self.callback_url = callback_url
        self.status = "initialized"
        self.start_time = None
        self.end_time = None
        self.metrics = {}
        self.logs = []
        self._stop_requested = False
        
    async def initialize_model(self) -> None:
        """ Initialize the model and train it """
        try:
            await self.model.load_model()
            self.log("Model initialized successfully")
        except Exception as e:
            self.log(f"Model initialization failed: {str(e)}", level="ERROR")
            raise
        
    async def prepare_data(self, training_data: Any, validation_data: Optional[Any] = None) -> Dict[str, Any]:
        """ Prepare data for training """
        try:
            train_data = await self.model.prepare_training_data(training_data)
            val_data = None
            if validation_data:
                val_data = await self.model.prepare_training_data(validation_data)

            self.log("Data preparation completed")
            return {
                "train_data": train_data,
                "validation_data": val_data
            }
        except Exception as e:
            self.log(f"Data preparation failed: {str(e)}", level="ERROR")
            raise
        
    async def train(self, train_data: Any, validation_data: Optional[Any] = None, config: Dict[str, Any] = None) -> Dict[str, Any]:
        """ Execute training """
        try:
            self.start_time = datetime.utcnow()
            self.status = "training"
            self.log("Training started")
            
            # Starting training
            training_task = asyncio.create_task(self.model.train(train_data, validation_data, config))
            # Monitor training
            while not training_task.done():
                if self._stop_requested:
                    training_task.cancel()
                    self.log("Training stopped by user")
                    break
                await asyncio.sleep(1)

            if not training_task.cancelled():
                self.metrics = await training_task

            self.end_time = datetime.utcnow()
            self.status = "completed"
            self.log("Training completed")

            # Send callback if URL provided
            if self.callback_url:
                await self._send_callback({"status": "completed", "metrics": self.metrics})

            return {
                "status": self.status,
                "metrics": self.metrics,
                "training_time": (self.end_time - self.start_time).total_seconds()
            }

        except asyncio.CancelledError:
            self.status = "stopped"
            return {"status": "stopped"}
        except Exception as e:
            self.log(f"Training failed: {str(e)}", level="ERROR")
            self.status = "failed"
            raise
        
    async def save_model(self) -> Dict[str, str]:
        """Save trained model"""
        try:
            save_path = f"models/{self.training_id}"
            paths = await self.model.save_model(save_path)
            self.log("Model saved successfully")
            return paths
        except Exception as e:
            self.log(f"Failed to save model: {str(e)}", level="ERROR")
            raise

    async def stop(self) -> None:
        """Stop training"""
        self._stop_requested = True
        self.status = "stopping"
        self.log("Stop requested by user")

    async def cleanup(self) -> None:
        """Cleanup resources"""
        try:
            # Cleanup temporary files
            if os.path.exists(f"models/{self.training_id}"):
                os.remove(f"models/{self.training_id}")
            self.log("Cleanup completed")
        except Exception as e:
            self.log(f"Cleanup failed: {str(e)}", level="ERROR")

    async def get_status(self) -> Dict[str, Any]:
        """Get current training status"""
        return {
            "training_id": self.training_id,
            "status": self.status,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "metrics": self.metrics
        }

    async def get_metrics(self) -> Dict[str, Any]:
        """Get training metrics"""
        return self.metrics

    async def get_logs(self, last_n_lines: int = 100) -> List[str]:
        """Get training logs"""
        return self.logs[-last_n_lines:]

    async def handle_failure(self, error_message: str) -> None:
        """Handle training failure"""
        self.status = "failed"
        self.log(f"Training failed: {error_message}", level="ERROR")
        if self.callback_url:
            await self._send_callback({
                "status": "failed",
                "error": error_message
            })

    def log(self, message: str, level: str = "INFO") -> None:
        """Add log entry"""
        timestamp = datetime.utcnow().isoformat()
        log_entry = f"[{timestamp}] [{level}] {message}"
        self.logs.append(log_entry)
        logger.info(log_entry)

    async def _send_callback(self, data: Dict[str, Any]) -> None:
        """Send callback to URL if provided"""
        if not self.callback_url:
            return

        try:
            async with httpx.AsyncClient() as client:
                await client.post(
                    self.callback_url,
                    json={
                        "training_id": self.training_id,
                        **data
                    }
                )
        except Exception as e:
            self.log(f"Callback failed: {str(e)}", level="ERROR")