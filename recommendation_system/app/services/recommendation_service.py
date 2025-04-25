from typing import List, Dict, Any
import os
from app.models.ml_model import InsuranceRecommenderModel
from app.models.insurance_models import InsuranceRecommendationRequest, RecommendationWithInsurance

MODEL_PATH = os.getenv("MODEL_PATH", "sentence-transformers/all-MiniLM-L6-v2")
PRODUCTS_DATA_PATH = os.getenv("PRODUCTS_DATA_PATH", "/app/model/products_data.json")


class RecommendationService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(RecommendationService, cls).__new__(cls)
            cls._instance.model = InsuranceRecommenderModel(MODEL_PATH, PRODUCTS_DATA_PATH)
        return cls._instance

    async def get_recommendations(self, request: InsuranceRecommendationRequest) -> List[RecommendationWithInsurance]:
        user_data = request.dict()

        try:
            recommendations = self.model.get_recommendations(user_data)

            return [RecommendationWithInsurance(**recommendation) for recommendation in recommendations]
        except Exception as e:
            print(f"Ошибка в сервисе рекомендаций: {str(e)}")
            return []
