from typing import List
import os
from app.models.ml_model import InsuranceRecommenderModel
from app.models.insurance_models import InsuranceRecommendation, InsuranceRecommendationRequest

# Use sentence-transformers model which is already installed
MODEL_PATH = os.getenv("MODEL_PATH", "sentence-transformers/all-MiniLM-L6-v2")


class RecommendationService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(RecommendationService, cls).__new__(cls)
            cls._instance.model = InsuranceRecommenderModel(MODEL_PATH)
        return cls._instance

    async def get_recommendations(self, request: InsuranceRecommendationRequest) -> List[InsuranceRecommendation]:
        user_data = request.dict()

        try:
            recommendations = self.model.get_recommendations(user_data)
            return [InsuranceRecommendation(**recommendation) for recommendation in recommendations]
        except Exception as e:
            print(f"Error in recommendation service: {str(e)}")
            raise
