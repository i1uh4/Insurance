from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.database import Base
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class InsuranceCategory(Base):
    __tablename__ = "insurance_categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Insurance(Base):
    __tablename__ = "insurances"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    premium = Column(Float, nullable=False)
    coverage = Column(Float, nullable=False)
    duration = Column(Integer)  # in months
    category_id = Column(Integer, ForeignKey("insurance_categories.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class CategoryBase(BaseModel):
    name: str
    description: Optional[str] = None


class CategoryCreate(CategoryBase):
    pass


class CategoryResponse(CategoryBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True


class InsuranceBase(BaseModel):
    name: str
    description: Optional[str] = None
    premium: float
    coverage: float
    duration: Optional[int] = None
    category_id: int


class InsuranceCreate(InsuranceBase):
    pass


class InsuranceResponse(InsuranceBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True


class InsuranceWithCategory(InsuranceResponse):
    category: CategoryResponse

    class Config:
        orm_mode = True
