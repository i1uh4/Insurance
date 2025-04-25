from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Boolean, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import datetime

Base = declarative_base()


class RecommendationModel(Base):
    __tablename__ = "recommendation_models"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    version = Column(String)
    description = Column(Text)
    parameters = Column(JSON)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    is_active = Column(Boolean, default=False)

    recommendations = relationship("Recommendation", back_populates="model")


class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    insurance_id = Column(Integer, index=True)
    score = Column(Float)
    model_id = Column(Integer, ForeignKey("recommendation_models.id"))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    model = relationship("RecommendationModel", back_populates="recommendations")