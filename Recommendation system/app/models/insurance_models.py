from typing import List, Optional
from pydantic import BaseModel, Field


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


class InsuranceProduct(BaseModel):
    id: str
    name: str
    provider: str
    category: str
    description: str
    min_price: float
    max_price: float
    features: List[str]
    suitable_for: List[str]
    risks_covered: List[str]


class InsuranceRecommendation(BaseModel):
    product_id: str
    product_name: str
    provider: str
    category: str
    description: str
    estimated_price: float
    match_score: float = Field(..., ge=0.0, le=1.0)
    features: List[str]
    suitable_for: List[str]


class RecommendationWithInsurance(InsuranceRecommendation):
    risks_covered: List[str]
    recommendation_reason: str
