from typing import Dict, Any, Optional, List
import asyncio
from datetime import datetime
import logging
from app.services.ai.models.base import ModelFactory
from app.services.ipfs import pinata_service
from .trainer import ModelTrainer
from .validators import TrainingValidator

logger = logging.getLogger(__name__)

class TrainingPipeline:
    def __init__(self):
        self.validator = TrainingValidator()
        self.active_trainings: Dict[str, ModelTrainer] = {}

    async def start_training(
        self,
        training_id: str,
        model_type: str,
        model_name: str,
        training_data: Any,
        config: Dict[str, Any],
        validation_data: Optional[Any] = None,
        callback_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Start a new training pipeline
        """
        try:
            # Validate training request
            await self.validator.validate_training_request(
                model_type,
                training_data,
                config
            )

            # Create model instance
            model = ModelFactory.create_model(
                model_type=model_type,
                model_name=model_name
            )

            # Initialize trainer
            trainer = ModelTrainer(
                model=model,
                training_id=training_id,
                callback_url=callback_url
            )

            # Store active training
            self.active_trainings[training_id] = trainer

            # Start training in background
            asyncio.create_task(
                self._run_training_pipeline(
                    trainer,
                    training_data,
                    config,
                    validation_data
                )
            )

            return {
                "training_id": training_id,
                "status": "started",
                "model_type": model_type,
                "model_name": model_name,
                "start_time": datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"Failed to start training: {str(e)}")
            raise

    async def _run_training_pipeline(
        self,
        trainer: ModelTrainer,
        training_data: Any,
        config: Dict[str, Any],
        validation_data: Optional[Any] = None
    ):
        """
        Execute the complete training pipeline
        """
        try:
            # Initialize model
            await trainer.initialize_model()

            # Prepare data
            prepared_data = await trainer.prepare_data(
                training_data,
                validation_data
            )

            # Start training
            training_result = await trainer.train(
                prepared_data["train_data"],
                prepared_data.get("validation_data"),
                config
            )

            # Save model to IPFS
            model_files = await trainer.save_model()
            ipfs_result = await pinata_service.pin_file_to_ipfs(
                model_files["model_path"],
                metadata={"type": "ai_model"}
            )

            # Update result with IPFS info
            training_result.update({
                "ipfs_hash": ipfs_result["ipfs_hash"],
                "model_uri": ipfs_result["gateway_url"]
            })

            # Cleanup
            await trainer.cleanup()
            del self.active_trainings[trainer.training_id]

            return training_result

        except Exception as e:
            logger.error(f"Training pipeline failed: {str(e)}")
            await trainer.handle_failure(str(e))
            del self.active_trainings[trainer.training_id]
            raise

    async def get_training_status(
        self,
        training_id: str
    ) -> Dict[str, Any]:
        """
        Get status of a training job
        """
        trainer = self.active_trainings.get(training_id)
        if not trainer:
            return {"status": "not_found"}
        return await trainer.get_status()

    async def stop_training(
        self,
        training_id: str
    ) -> Dict[str, Any]:
        """
        Stop a training job
        """
        trainer = self.active_trainings.get(training_id)
        if not trainer:
            return {"status": "not_found"}

        await trainer.stop()
        del self.active_trainings[training_id]
        return {"status": "stopped"}

    async def list_active_trainings(self) -> List[Dict[str, Any]]:
        """
        List all active training jobs
        """
        return [
            await trainer.get_status()
            for trainer in self.active_trainings.values()
        ]

    async def get_training_metrics(
        self,
        training_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get metrics for a training job
        """
        trainer = self.active_trainings.get(training_id)
        if not trainer:
            return None
        return await trainer.get_metrics()

    async def get_training_logs(
        self,
        training_id: str,
        last_n_lines: int = 100
    ) -> List[str]:
        """
        Get logs for a training job
        """
        trainer = self.active_trainings.get(training_id)
        if not trainer:
            return []
        return await trainer.get_logs(last_n_lines)

training_pipeline = TrainingPipeline()