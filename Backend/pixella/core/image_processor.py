#!/usr/bin/env python3
"""
Pixella - Core image processing utilities
"""

import os
import hashlib
import logging
import numpy as np
from PIL import Image
from pathlib import Path
from datetime import datetime
from Crypto.Hash import SHA256

from pixella.core.models import ImageMetadata

# Configure logging
logger = logging.getLogger(__name__)


class ImageProcessor:
    """Core image processing utilities"""
    
    def __init__(self):
        self.supported_formats = os.getenv('SUPPORTED_FORMATS', 'jpg,jpeg,png,bmp,webp').split(',')
        self.max_size = int(os.getenv('MAX_IMAGE_SIZE', 10485760))
    
    def load_image(self, image_path: str) -> tuple[Image.Image, ImageMetadata]:
        """Load and validate image"""
        path = Path(image_path)
        
        if not path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")
        
        # Debug logging for format detection
        extension = path.suffix.lower().lstrip('.')
        logger.info(f"File extension: '{extension}', Supported formats: {self.supported_formats}")
        
        if extension not in self.supported_formats:
            raise ValueError(f"Unsupported format: {path.suffix}")
        
        if path.stat().st_size > self.max_size:
            raise ValueError(f"Image too large: {path.stat().st_size} bytes")
        
        # Load image
        image = Image.open(path).convert('RGB')
        
        # Extract metadata
        metadata = ImageMetadata(
            filename=path.name,
            size=path.stat().st_size,
            dimensions=image.size,
            format=image.format or path.suffix.upper().lstrip('.'),
            timestamp=datetime.now().isoformat(),
            hash=self.hash_image(image)
        )
        
        return image, metadata
    
    def hash_image(self, image: Image.Image) -> str:
        """Generate cryptographic hash of image"""
        # Convert to bytes
        img_bytes = np.array(image).tobytes()
        
        # Create SHA256 hash
        hash_obj = SHA256.new()
        hash_obj.update(img_bytes)
        
        return hash_obj.hexdigest()
    
    def extract_features(self, image: Image.Image) -> np.ndarray:
        """Extract image features for analysis"""
        try:
            import cv2  # Import here to avoid circular imports
            
            # Convert PIL image to numpy array
            img_array = np.array(image)
            
            # Convert to grayscale if needed
            if len(img_array.shape) == 3 and img_array.shape[2] == 3:
                gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            else:
                gray = img_array
                
            # Extract features using ORB (Oriented FAST and Rotated BRIEF)
            orb = cv2.ORB_create()
            keypoints, descriptors = orb.detectAndCompute(gray, None)
            
            # If no features found, return empty array
            if descriptors is None:
                return np.array([])
                
            # Flatten and normalize features
            features = descriptors.flatten()
            if len(features) > 0:
                features = features / np.linalg.norm(features)
                
            return features
        except ImportError:
            # For testing environments without cv2
            logger.warning("OpenCV (cv2) not available, using mock features")
            # Return mock features for testing
            return np.random.rand(2048)
