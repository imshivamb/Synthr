import json
import httpx
from typing import Dict, Any, Optional, BinaryIO, Tuple
from fastapi import UploadFile, HTTPException
from app.core.config import settings
from .utils import file_validator, file_processor, metadata_processor

class PinataService:
    def __init__(self):
        self.api_key = settings.PINATA_API_KEY
        self.secret_key = settings.PINATA_SECRET_KEY
        self.base_url = "https://api.pinata.cloud"
        self.gateway_url = settings.PINATA_GATEWAY_URL
        
        self.headers = {
            "pinata_api_key": self.api_key,
            "pinata_secret_api_key": self.secret_key
        }

    async def pin_agent_metadata(
        self,
        metadata: Dict[str, Any],
        image_file: Optional[UploadFile] = None,
        model_file: Optional[UploadFile] = None
    ) -> Dict[str, Any]:
        """
        Pin complete agent data (metadata, image, and model) to IPFS
        """
        try:
            # Validate metadata
            await file_validator.validate_metadata(metadata)
            
            # Handle image if provided
            image_result = None
            if image_file:
                # Validate and process image
                await file_validator.validate_image(image_file)
                processed_image = await file_processor.process_image(image_file)
                
                # Upload to IPFS
                image_result = await self.pin_file_to_ipfs(
                    processed_image,
                    metadata={"type": "agent_image"}
                )

            # Handle model file if provided
            model_result = None
            if model_file:
                # Validate model file
                await file_validator.validate_model_file(model_file)
                
                # Save temporarily for processing
                model_path = await file_processor.save_temporary(model_file)
                try:
                    # Upload to IPFS
                    model_result = await self.pin_file_to_ipfs(
                        model_file,
                        metadata={"type": "agent_model"}
                    )
                finally:
                    # Cleanup temporary file
                    await file_processor.cleanup_temporary(model_path)

            # Prepare and pin metadata
            processed_metadata = metadata_processor.prepare_agent_metadata(
                metadata,
                image_uri=image_result['gateway_url'] if image_result else None
            )
            
            # Add model information if available
            if model_result:
                processed_metadata["properties"]["model_uri"] = model_result['gateway_url']
                processed_metadata["properties"]["model_hash"] = model_result['ipfs_hash']

            # Pin metadata
            metadata_result = await self.pin_json_to_ipfs(
                processed_metadata,
                {"type": "agent_metadata"}
            )

            return {
                'metadata_uri': metadata_result['gateway_url'],
                'metadata_hash': metadata_result['ipfs_hash'],
                'image_uri': image_result['gateway_url'] if image_result else None,
                'image_hash': image_result['ipfs_hash'] if image_result else None,
                'model_uri': model_result['gateway_url'] if model_result else None,
                'model_hash': model_result['ipfs_hash'] if model_result else None
            }

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(500, f"Failed to pin agent data: {str(e)}")

    async def pin_file_to_ipfs(
        self,
        file: UploadFile,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Upload and pin file to IPFS"""
        try:
            url = f"{self.base_url}/pinning/pinFileToIPFS"
            
            files = {
                'file': (file.filename, file.file, file.content_type)
            }
            
            if metadata:
                files['pinataMetadata'] = (
                    None, 
                    json.dumps({"keyvalues": metadata}),
                    'application/json'
                )

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    headers=self.headers,
                    files=files
                )
                response.raise_for_status()
                
                result = response.json()
                return {
                    'ipfs_hash': result['IpfsHash'],
                    'pin_size': result['PinSize'],
                    'timestamp': result['Timestamp'],
                    'gateway_url': f"{self.gateway_url}{result['IpfsHash']}"
                }

        except Exception as e:
            raise HTTPException(500, f"Failed to pin file to IPFS: {str(e)}")

    async def pin_json_to_ipfs(
        self,
        json_data: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Pin JSON data to IPFS"""
        try:
            url = f"{self.base_url}/pinning/pinJSONToIPFS"
            
            payload = {
                "pinataContent": json_data
            }
            
            if metadata:
                payload["pinataMetadata"] = {"keyvalues": metadata}

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    headers=self.headers,
                    json=payload
                )
                response.raise_for_status()
                
                result = response.json()
                return {
                    'ipfs_hash': result['IpfsHash'],
                    'pin_size': result['PinSize'],
                    'timestamp': result['Timestamp'],
                    'gateway_url': f"{self.gateway_url}{result['IpfsHash']}"
                }

        except Exception as e:
            raise HTTPException(500, f"Failed to pin JSON to IPFS: {str(e)}")

    async def remove_pin(self, ipfs_hash: str) -> bool:
        """Unpin item from IPFS"""
        try:
            url = f"{self.base_url}/pinning/unpin/{ipfs_hash}"

            async with httpx.AsyncClient() as client:
                response = await client.delete(url, headers=self.headers)
                response.raise_for_status()
                return True

        except Exception as e:
            raise HTTPException(500, f"Failed to unpin from IPFS: {str(e)}")

    async def get_pin_status(self, ipfs_hash: str) -> Dict[str, Any]:
        """Get pin status"""
        try:
            url = f"{self.base_url}/pinning/pinJobs"
            params = {"ipfs_pin_hash": ipfs_hash}

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    url,
                    headers=self.headers,
                    params=params
                )
                response.raise_for_status()
                return response.json()

        except Exception as e:
            raise HTTPException(500, f"Failed to get pin status: {str(e)}")

pinata_service = PinataService()