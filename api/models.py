"""
Data models for the Real Estate Investment Analysis API.
These are not database models but data transfer objects.
"""

from dataclasses import dataclass
from typing import List, Dict, Optional, Any
from datetime import datetime


@dataclass
class Property:
    """Data model representing a real estate property"""
    id: str
    source: str
    url: str
    title: str
    description: Optional[str] = None
    price: Optional[float] = None
    price_history: Optional[List[Dict[str, Any]]] = None
    property_type: Optional[str] = None
    operation_type: Optional[str] = None
    size: Optional[float] = None
    rooms: Optional[int] = None
    bathrooms: Optional[int] = None
    floor: Optional[int] = None
    has_elevator: Optional[bool] = None
    condition: Optional[str] = None
    year_built: Optional[int] = None
    features: Optional[List[str]] = None
    energy_cert: Optional[str] = None
    address: Optional[str] = None
    neighborhood: Optional[str] = None
    district: Optional[str] = None
    city: Optional[str] = None
    province: Optional[str] = None
    postal_code: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    first_detected: Optional[datetime] = None
    last_updated: Optional[datetime] = None
    is_new: Optional[bool] = None
    days_listed: Optional[int] = None
    price_per_sqm: Optional[float] = None
    investment_score: Optional[float] = None


@dataclass
class InvestmentOpportunity:
    """Data model representing an investment opportunity"""
    property_id: str
    source: str
    title: str
    price: float
    size: float
    city: str
    neighborhood: Optional[str] = None
    property_type: Optional[str] = None
    operation_type: Optional[str] = None
    investment_score: float = 0.0
    price_per_sqm: Optional[float] = None
    avg_area_price_per_sqm: Optional[float] = None
    price_difference: Optional[float] = None  # Percentage difference from average
    estimated_roi: Optional[float] = None  # Estimated Return on Investment
    comparable_count: Optional[int] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    url: Optional[str] = None
