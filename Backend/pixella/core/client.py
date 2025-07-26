#!/usr/bin/env python3
"""
Pixella - Main client orchestrating all components
"""

import os
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
from PIL import Image

from langchain_core.runnables import RunnableLambda, RunnablePassthrough

from pixella.core.models import ImageMetadata, TamperResult, ZKProof, PixellaResult
from pixella.core.image_processor import ImageProcessor
from pixella.core.zk_proof import ZKProofGenerator
from pixella.ai.groq_accelerator import GroqAccelerator
from pixella.ai.tamper_detector import TamperDetector
from pixella.blockchain.anchor import BlockchainAnchor
from pixella.storage.filecoin import FilecoinStorage

# Configure logging
logger = logging.getLogger(__name__)


class PixellaClient:
    """Main Pixella client orchestrating all components"""
    
    def __init__(self):
        self.groq = GroqAccelerator()
        self.image_processor = ImageProcessor()
        self.tamper_detector = TamperDetector(self.groq)
        self.zk_generator = ZKProofGenerator()
        self.blockchain = BlockchainAnchor()
        self.filecoin = FilecoinStorage()
        
        # Build LangChain pipeline
        self.pipeline = self._build_pipeline()
    
    def _build_pipeline(self):
        """Build LangChain processing pipeline"""
        # Create a sequential pipeline where each step passes its output to the next step
        load_image = RunnableLambda(self._load_image)
        
        # Extract features depends on image_data
        extract_features = RunnableLambda(self._extract_features)
        
        # Detect tampering depends on image_data and features
        detect_tampering = RunnableLambda(self._detect_tampering)
        
        # Generate proof depends on image_data
        generate_proof = RunnableLambda(self._generate_proof)
        
        # Commit to blockchain depends on zk_proof and image_data
        commit_blockchain = RunnableLambda(self._commit_to_blockchain)
        
        # Store on Filecoin depends on zk_proof, tamper_result, and image_data
        store_filecoin = RunnableLambda(self._store_on_filecoin)
        
        # Create final result depends on all previous steps
        create_result = RunnableLambda(self._create_result)
        
        # Build the sequential pipeline
        return (
            RunnablePassthrough()
            | load_image
            | extract_features
            | detect_tampering
            | generate_proof
            | commit_blockchain
            | store_filecoin
            | create_result
        )
    
    async def _load_image(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Load and process image"""
        image_path = inputs.get("image_path")
        if not image_path:
            logger.error("Image path not provided in inputs")
            raise ValueError("Image path not provided")
            
        logger.info(f"Loading image from path: {image_path}")
        
        # Check if file exists
        if not os.path.exists(image_path):
            logger.error(f"Image file does not exist: {image_path}")
            raise FileNotFoundError(f"Image file not found: {image_path}")
            
        # Check if file is readable
        if not os.access(image_path, os.R_OK):
            logger.error(f"Image file is not readable: {image_path}")
            raise PermissionError(f"Cannot read image file: {image_path}")
            
        # Check file size
        file_size = os.path.getsize(image_path)
        logger.info(f"Image file size: {file_size} bytes")
        
        try:
            image, metadata = self.image_processor.load_image(image_path)
            logger.info(f"Successfully loaded image: {metadata.filename}, hash: {metadata.hash}")
            # Return all inputs plus the new data
            return {**inputs, "image": image, "metadata": metadata}
        except Exception as e:
            logger.error(f"Failed to load image: {str(e)}")
            raise ValueError(f"Image not loaded: {str(e)}")
    
    async def _extract_features(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Extract features from image"""
        logger.info("Starting feature extraction")
        
        # In sequential pipeline, inputs should contain image and metadata from previous step
        image = inputs.get("image")
        metadata = inputs.get("metadata")
        
        if image is None:
            logger.error("No image object available for feature extraction")
            raise ValueError("Image not available for feature extraction")
            
        if metadata is None:
            logger.error("No metadata available for feature extraction")
            raise ValueError("Metadata not available for feature extraction")
            
        logger.info(f"Extracting features for image: {metadata.filename}")
        features = self.image_processor.extract_features(image)
        logger.info(f"Feature extraction complete, extracted {len(features) if features is not None else 0} features")
        
        # Pass through all inputs and add features
        return {**inputs, "features": features}
    
    async def _detect_tampering(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Detect image tampering"""
        logger.info("Starting tampering detection")
        
        # In sequential pipeline, inputs should contain image, metadata, and features from previous steps
        image = inputs.get("image")
        metadata = inputs.get("metadata")
        features = inputs.get("features")
        
        if image is None:
            logger.error("No image object available for tampering detection")
            raise ValueError("Image not available for tampering detection")
            
        if features is None:
            logger.error("No features available for tampering detection")
            raise ValueError("Features not available for tampering detection")
            
        if metadata is None:
            logger.error("No metadata available for tampering detection")
            raise ValueError("Metadata not available for tampering detection")
            
        logger.info(f"Detecting tampering for image: {metadata.filename}")
        tamper_result = await self.tamper_detector.detect_tampering(image, features)
        logger.info(f"Tampering detection complete: is_tampered={tamper_result.is_tampered}, score={tamper_result.tamper_score}")
        
        # Pass through all inputs and add tamper_result
        return {**inputs, "tamper_result": tamper_result}
    
    async def _generate_proof(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Generate ZK proof"""
        logger.info("Starting ZK proof generation")
        
        # In sequential pipeline, inputs should contain metadata from previous steps
        metadata = inputs.get("metadata")
        
        if metadata is None:
            logger.error("No metadata available for ZK proof generation")
            raise ValueError("Image metadata not available")
        
        image_hash = metadata.hash
        logger.info(f"Generating ZK proof for image hash: {image_hash}")
        
        try:
            zk_proof = await self.zk_generator.generate_proof(image_hash, metadata)
            logger.info(f"ZK proof generation complete: circuit_hash={zk_proof.circuit_hash}")
            # Pass through all inputs and add zk_proof
            return {**inputs, "zk_proof": zk_proof}
        except Exception as e:
            logger.error(f"Failed to generate ZK proof: {str(e)}")
            raise
    
    async def _commit_to_blockchain(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Commit proof to blockchain"""
        logger.info("Starting blockchain commit")
        
        # In sequential pipeline, inputs should contain zk_proof and metadata from previous steps
        zk_proof = inputs.get("zk_proof")
        metadata = inputs.get("metadata")
        
        if zk_proof is None:
            logger.warning("No ZK proof available for blockchain commit, skipping")
            # Still pass through all inputs even if we skip this step
            return {**inputs, "blockchain_tx": None}
            
        if metadata is None:
            logger.warning("No metadata available for blockchain commit, skipping")
            # Still pass through all inputs even if we skip this step
            return {**inputs, "blockchain_tx": None}
        
        logger.info(f"Committing proof to blockchain for image hash: {metadata.hash}")
        try:
            tx_hash = await self.blockchain.commit_proof(zk_proof, metadata.hash)
            logger.info(f"Blockchain commit complete: tx_hash={tx_hash}")
            # Pass through all inputs and add blockchain_tx
            return {**inputs, "blockchain_tx": tx_hash}
        except Exception as e:
            logger.error(f"Failed to commit to blockchain: {str(e)}")
            # Don't raise exception, just return None to continue pipeline
            # Still pass through all inputs
            return {**inputs, "blockchain_tx": None}
    
    async def _store_on_filecoin(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Store proof on Filecoin"""
        logger.info("Starting Filecoin storage")
        
        # In sequential pipeline, inputs should contain zk_proof, tamper_result, and metadata from previous steps
        zk_proof = inputs.get("zk_proof")
        tamper_result = inputs.get("tamper_result")
        metadata = inputs.get("metadata")
        
        if zk_proof is None:
            logger.warning("No ZK proof available for Filecoin storage, skipping")
            # Still pass through all inputs even if we skip this step
            return {**inputs, "filecoin_data": None}
            
        if tamper_result is None:
            logger.warning("No tamper result available for Filecoin storage, skipping")
            # Still pass through all inputs even if we skip this step
            return {**inputs, "filecoin_data": None}
            
        if metadata is None:
            logger.warning("No metadata available for Filecoin storage, skipping")
            # Still pass through all inputs even if we skip this step
            return {**inputs, "filecoin_data": None}
        
        logger.info(f"Storing proof on Filecoin for image hash: {metadata.hash}")
        
        proof_data = {
            "image_hash": metadata.hash,
            "tamper_result": {
                "score": tamper_result.tamper_score,
                "is_tampered": tamper_result.is_tampered,
                "confidence": tamper_result.confidence,
                "model_version": tamper_result.model_version
            },
            "zk_proof": {
                "public_signals": zk_proof.public_signals,
                "circuit_hash": zk_proof.circuit_hash
            },
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            filecoin_data = await self.filecoin.store_proof(proof_data, metadata.hash)
            logger.info(f"Filecoin storage complete: cid={filecoin_data.get('cid')}, deal_id={filecoin_data.get('deal_id')}")
            # Pass through all inputs and add filecoin_data
            return {**inputs, "filecoin_data": filecoin_data}
        except Exception as e:
            logger.error(f"Failed to store on Filecoin: {str(e)}")
            # Don't raise exception, just return None to continue pipeline
            # Still pass through all inputs
            return {**inputs, "filecoin_data": None}
    
    async def _create_result(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Create final result"""
        logger.info("Creating final result")
        
        # Log available inputs for debugging
        logger.debug(f"Available inputs keys: {list(inputs.keys())}")
        
        # In sequential pipeline, inputs should contain all data from previous steps
        metadata = inputs.get("metadata")
        tamper_result = inputs.get("tamper_result")
        zk_proof = inputs.get("zk_proof")
        blockchain_tx = inputs.get("blockchain_tx")
        filecoin_data = inputs.get("filecoin_data")
        
        # Check required data
        if metadata is None:
            logger.error("No metadata available for result creation")
            raise ValueError("Image metadata not available")
            
        if tamper_result is None:
            logger.error("No tamper result available for result creation")
            raise ValueError("Tamper result not available")
        
        logger.info(f"Creating result for image hash: {metadata.hash}")
        verification_url = f"https://verify.pixella.ai/{metadata.hash}"
        
        # Extract Filecoin CID and deal ID if available
        filecoin_cid = None
        filecoin_deal_id = None
        if filecoin_data:
            filecoin_cid = filecoin_data.get("cid")
            filecoin_deal_id = filecoin_data.get("deal_id")
            logger.info(f"Filecoin data included: cid={filecoin_cid}, deal_id={filecoin_deal_id}")
        else:
            logger.warning("No Filecoin data available for result")
            
        # Create result object
        try:
            result = PixellaResult(
                image_hash=metadata.hash,
                metadata=metadata,
                tamper_result=tamper_result,
                verification_url=verification_url,
                timestamp=datetime.now().isoformat(),
                zk_proof=zk_proof,
                blockchain_tx=blockchain_tx,
                filecoin_cid=filecoin_cid,
                filecoin_deal_id=filecoin_deal_id
            )
            logger.info(f"Result created successfully for image: {metadata.filename}")
            # Return only the result in the final step
            return {"result": result}
        except Exception as e:
            logger.error(f"Failed to create result: {str(e)}")
            raise
    
    async def process_image(self, image_path: str) -> PixellaResult:
        """Process image and generate authenticity proof"""
        try:
            inputs = {"image_path": image_path}
            result = await self.pipeline.ainvoke(inputs)
            return result["result"]
        except Exception as e:
            logger.error(f"Image processing error: {e}")
            raise
