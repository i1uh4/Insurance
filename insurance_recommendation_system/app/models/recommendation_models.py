from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.sql import func
from app.database import Base
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# SQLAlchemy Models
class UserPreference(Base):
    __tablename__ = "user_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    age = Column(Integer)
    income = Column(Float)
    occupation = Column(String)
    health_condition = Column(String)
    family_size = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    insurance_id = Column(Integer, ForeignKey("insurances.id"))
    score = Column(Float)
    is_viewed = Column(Boolean, default=False)
    is_purchased = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


# Pydantic Models
class PreferenceBase(BaseModel):
    age: int
    income: float
    occupation: str
    health_condition: str
    family_size: int


class PreferenceCreate(PreferenceBase):
    pass


class PreferenceResponse(PreferenceBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        orm_mode = True


class RecommendationBase(BaseModel):
    user_id: int
    insurance_id: int
    score: float
    is_viewed: Optional[bool] = False
    is_purchased: Optional[bool] = False


class RecommendationCreate(RecommendationBase):
    pass


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

class RecommendationResponse(RecommendationBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True


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