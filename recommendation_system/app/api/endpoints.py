from fastapi import APIRouter, HTTPException, status
from typing import List

from app.models.insurance_models import InsuranceRecommendation, InsuranceRecommendationRequest
from app.services.recommendation_service import RecommendationService

router = APIRouter()
recommendation_service = RecommendationService()


@router.post("/recommendations", response_model=List[InsuranceRecommendation])
async def get_recommendations(request: InsuranceRecommendationRequest):
    """
    Get insurance product recommendations based on user profile.
    """
    try:
        recommendations = await recommendation_service.get_recommendations(request)
        return recommendations
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating recommendations: {str(e)}"
        )
