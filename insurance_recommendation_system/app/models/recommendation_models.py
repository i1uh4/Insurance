from pydantic import BaseModel, Field
from typing import Optional, List
from app.database import Base

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


class RecommendationWithInsurance(BaseModel):
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
