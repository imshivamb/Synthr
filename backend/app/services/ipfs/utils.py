import io
import json
from typing import List, Set, Dict, Any, Optional
from fastapi import UploadFile, HTTPException
from PIL import Image
import aiofiles
import os

# Constants
MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB
MAX_MODEL_SIZE = 100 * 1024 * 1024  # 100MB
ALLOWED_IMAGE_TYPES = {'image/jpeg', 'image/png', 'image/gif'}
ALLOWED_MODEL_TYPES = {'.h5', '.pkl', '.pt', '.pth', '.onnx', '.pb'}

class FileValidator:
    @staticmethod
    async def validate_image(file: UploadFile) -> bool:
        """Validate image file"""
        if not file.content_type in ALLOWED_IMAGE_TYPES:
            raise HTTPException(400, "Invalid image format")

        # Check file size
        file.file.seek(0, 2)  # Seek to end
        size = file.file.tell()
        file.file.seek(0)  # Reset position
        
        if size > MAX_IMAGE_SIZE:
            raise HTTPException(400, "Image too large")

        try:
            # Verify it's a valid image
            img = Image.open(file.file)
            img.verify()
            file.file.seek(0)
            return True
        except Exception as e:
            raise HTTPException(400, "Invalid image file")

    @staticmethod
    async def validate_model_file(file: UploadFile) -> bool:
        """Validate AI model file"""
        extension = os.path.splitext(file.filename)[1].lower()
        if extension not in ALLOWED_MODEL_TYPES:
            raise HTTPException(400, "Invalid model format")

        # Check file size
        file.file.seek(0, 2)
        size = file.file.tell()
        file.file.seek(0)
        
        if size > MAX_MODEL_SIZE:
            raise HTTPException(400, "Model file too large")

        return True

    @staticmethod
    async def validate_metadata(metadata: Dict[str, Any]) -> bool:
        """Validate agent metadata"""
        required_fields = {
            'name', 'description', 'category', 'capabilities', 
            'model_type', 'version'
        }
        
        if not all(field in metadata for field in required_fields):
            raise HTTPException(400, "Missing required metadata fields")

        # Validate specific fields
        if not isinstance(metadata.get('capabilities'), list):
            raise HTTPException(400, "Capabilities must be a list")

        if len(metadata.get('name', '')) < 3:
            raise HTTPException(400, "Name too short")

        if len(metadata.get('description', '')) < 10:
            raise HTTPException(400, "Description too short")

        return True

class FileProcessor:
    @staticmethod
    async def process_image(file: UploadFile) -> UploadFile:
        """Process and optimize image for IPFS"""
        img = Image.open(file.file)
        
        # Convert to RGB if RGBA
        if img.mode == 'RGBA':
            img = img.convert('RGB')
        
        # Resize if too large
        max_size = (1024, 1024)
        if img.size[0] > max_size[0] or img.size[1] > max_size[1]:
            img.thumbnail(max_size, Image.LANCZOS)
        
        # Save optimized image
        output = io.BytesIO()
        img.save(output, format='JPEG', quality=85, optimize=True)
        output.seek(0)
        
        # Create new UploadFile
        processed_file = UploadFile(
            filename=file.filename,
            file=output,
            content_type='image/jpeg'
        )
        
        return processed_file

    @staticmethod
    async def save_temporary(file: UploadFile) -> str:
        """Save file temporarily and return path"""
        temp_dir = "temp"
        os.makedirs(temp_dir, exist_ok=True)
        
        file_path = os.path.join(temp_dir, file.filename)
        async with aiofiles.open(file_path, 'wb') as out_file:
            content = await file.read()
            await out_file.write(content)
        
        return file_path

    @staticmethod
    async def cleanup_temporary(file_path: str):
        """Clean up temporary file"""
        if os.path.exists(file_path):
            os.remove(file_path)

class MetadataProcessor:
    @staticmethod
    def prepare_agent_metadata(
        metadata: Dict[str, Any],
        image_uri: Optional[str] = None
    ) -> Dict[str, Any]:
        """Prepare agent metadata for IPFS"""
        processed = {
            "name": metadata["name"],
            "description": metadata["description"],
            "image": image_uri or metadata.get("image", ""),
            "category": metadata["category"],
            "capabilities": metadata["capabilities"],
            "properties": {
                "model_type": metadata["model_type"],
                "version": metadata["version"],
                "created_at": metadata.get("created_at", ""),
                "updated_at": metadata.get("updated_at", ""),
            },
            "attributes": [
                {"trait_type": "Category", "value": metadata["category"]},
                {"trait_type": "Model Type", "value": metadata["model_type"]},
                {"trait_type": "Version", "value": metadata["version"]}
            ]
        }
        
        # Add capabilities as attributes
        for capability in metadata["capabilities"]:
            processed["attributes"].append({
                "trait_type": "Capability",
                "value": capability
            })
        
        return processed

file_validator = FileValidator()
file_processor = FileProcessor()
metadata_processor = MetadataProcessor()