from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class InsuranceRecommendationRequest(BaseModel):
    age: int
    gender: str
    occupation: str
    income: float
    marital_status: str
    has_children: bool
    has_vehicle: bool
    has_home: bool
    has_medical_conditions: bool
    travel_frequency: str


class InsuranceCategory(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    created_at: Optional[datetime] = None


class InsuranceProduct(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    premium: float
    coverage: float
    duration: Optional[int] = None
    category_id: int
    category_name: str
    category_description: Optional[str] = None
    provider: str = "Unknown Provider"
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    features: List[str] = []
    suitable_for: List[str] = []
    risks_covered: List[str] = []


class InsuranceRecommendation(BaseModel):
    product_id: int
    product_name: str
    provider: str
    category_name: str
    description: Optional[str] = None
    premium: float
    coverage: float
    duration: Optional[int] = None
    estimated_price: float
    match_score: float = Field(..., ge=0.0, le=1.0)
    recommendation_reason: str
    features: List[str] = []
    suitable_for: List[str] = []
    risks_covered: List[str] = []
