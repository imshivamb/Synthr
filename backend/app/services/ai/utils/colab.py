import os
import json
import asyncio
from typing import Dict, Any, Optional, List
import httpx
from google.colab import auth
from google.cloud import storage
from google.oauth2.credentials import Credentials

class ColabManager:
    def __init__(self):
        self.api_url = "https://colab.research.google.com/api/sessions/v1"
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        self.credentials: Optional[Credentials] = None
        self.bucket_name = "synthr-models"

    async def initialize(self) -> None:
        """Initialize Colab connection and GCS credentials"""
        try:
            # Authenticate with Google
            auth.authenticate_user()
            self.credentials = auth.get_credentials()
            
            # Initialize GCS client
            self.storage_client = storage.Client(credentials=self.credentials)
            
            # Ensure bucket exists
            if not self.storage_client.lookup_bucket(self.bucket_name):
                self.storage_client.create_bucket(self.bucket_name)
                
        except Exception as e:
            raise Exception(f"Failed to initialize Colab manager: {str(e)}")

    async def create_training_session(
        self,
        training_id: str,
        model_type: str,
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create new Colab training session"""
        try:
            # Create session
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.api_url}/new",
                    json={
                        "name": f"SYNTHR_Training_{training_id}",
                        "gpu": True,
                        "tpu": False
                    }
                )
                session_info = response.json()
            
            # Store session info
            self.active_sessions[training_id] = {
                "session_id": session_info["id"],
                "status": "created",
                "model_type": model_type,
                "config": config
            }
            
            return session_info
            
        except Exception as e:
            raise Exception(f"Failed to create Colab session: {str(e)}")

    async def upload_training_data(
        self,
        training_id: str,
        data: Any
    ) -> str:
        """Upload training data to GCS"""
        try:
            # Create data file path
            blob_name = f"training_data/{training_id}/data.json"
            bucket = self.storage_client.bucket(self.bucket_name)
            blob = bucket.blob(blob_name)
            
            # Upload data
            blob.upload_from_string(
                json.dumps(data),
                content_type='application/json'
            )
            
            return f"gs://{self.bucket_name}/{blob_name}"
            
        except Exception as e:
            raise Exception(f"Failed to upload training data: {str(e)}")

    async def start_training(
        self,
        training_id: str,
        data_path: str
    ) -> None:
        """Start training in Colab session"""
        session = self.active_sessions.get(training_id)
        if not session:
            raise Exception(f"No active session for training_id: {training_id}")
            
        try:
            # Prepare training code
            training_code = self._generate_training_code(
                session["model_type"],
                session["config"],
                data_path
            )
            
            # Execute in Colab
            async with httpx.AsyncClient() as client:
                await client.post(
                    f"{self.api_url}/{session['session_id']}/execute",
                    json={"code": training_code}
                )
                
            session["status"] = "training"
            
        except Exception as e:
            raise Exception(f"Failed to start training: {str(e)}")

    async def get_training_status(
        self,
        training_id: str
    ) -> Dict[str, Any]:
        """Get training status from Colab"""
        session = self.active_sessions.get(training_id)
        if not session:
            return {"status": "not_found"}
            
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.api_url}/{session['session_id']}/status"
                )
                return response.json()
                
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def download_model(
        self,
        training_id: str,
        local_path: str
    ) -> None:
        """Download trained model from GCS"""
        try:
            bucket = self.storage_client.bucket(self.bucket_name)
            model_prefix = f"models/{training_id}/"
            
            # Download all model files
            for blob in bucket.list_blobs(prefix=model_prefix):
                local_file = os.path.join(
                    local_path,
                    blob.name.replace(model_prefix, '')
                )
                os.makedirs(os.path.dirname(local_file), exist_ok=True)
                blob.download_to_filename(local_file)
                
        except Exception as e:
            raise Exception(f"Failed to download model: {str(e)}")

    async def cleanup_session(
        self,
        training_id: str
    ) -> None:
        """Cleanup Colab session and GCS data"""
        session = self.active_sessions.get(training_id)
        if not session:
            return
            
        try:
            # Stop Colab session
            async with httpx.AsyncClient() as client:
                await client.delete(
                    f"{self.api_url}/{session['session_id']}"
                )
            
            # Cleanup GCS data
            bucket = self.storage_client.bucket(self.bucket_name)
            bucket.delete_blobs(
                blobs=bucket.list_blobs(prefix=f"training_data/{training_id}/")
            )
            bucket.delete_blobs(
                blobs=bucket.list_blobs(prefix=f"models/{training_id}/")
            )
            
            # Remove session info
            del self.active_sessions[training_id]
            
        except Exception as e:
            print(f"Cleanup error for {training_id}: {str(e)}")

    def _generate_training_code(
        self,
        model_type: str,
        config: Dict[str, Any],
        data_path: str
    ) -> str:
        """Generate training code for Colab execution"""
        return f"""
import torch
from transformers import AutoTokenizer, AutoModel
import json

# Load data
with open('{data_path}', 'r') as f:
    training_data = json.load(f)

# Initialize model
model_name = '{model_type}'
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModel.from_pretrained(model_name)

# Training configuration
config = {json.dumps(config, indent=2)}

# Training loop...
        """

colab_manager = ColabManager()