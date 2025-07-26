#!/usr/bin/env python3
"""
Pixella - Core data models
"""

from dataclasses import dataclass, asdict
from typing import Dict, Any, Optional, Tuple
from datetime import datetime


@dataclass
class ImageMetadata:
    """Structured image metadata"""
    filename: str
    size: int
    dimensions: Tuple[int, int]
    format: str
    timestamp: str
    author: Optional[str] = None
    location: Optional[str] = None
    device: Optional[str] = None
    hash: Optional[str] = None


@dataclass
class TamperResult:
    """Tamper detection result"""
    tamper_score: float
    is_tampered: bool
    confidence: float
    anomalies: list
    model_version: str


@dataclass
class ZKProof:
    """Zero-knowledge proof structure"""
    proof: Dict[str, Any]
    public_signals: list
    verification_key: Dict[str, Any]
    circuit_hash: str


@dataclass
class PixellaResult:
    """Complete Pixella processing result"""
    image_hash: str
    metadata: ImageMetadata
    tamper_result: TamperResult
    verification_url: str
    timestamp: str
    zk_proof: Optional[ZKProof] = None
    blockchain_tx: Optional[str] = None
    filecoin_cid: Optional[str] = None
    filecoin_deal_id: Optional[str] = None
