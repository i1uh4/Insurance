from fastapi import APIRouter, HTTPException, status
from typing import List
import httpx

from app.models.recommendation_models import RecommendationWithInsurance, InsuranceRecommendationRequest

router = APIRouter(
    prefix="/recommendation",
    tags=["Recommendations"]
)

@router.post("/get_recommendations", response_model=List[RecommendationWithInsurance])
async def get_recommendations(request: InsuranceRecommendationRequest):
    """Get recommendations for a user"""
    recommendation_system_url = "http://recommendation_system:8001/api/recommendations"

    async with httpx.AsyncClient() as client:
        try:
            print("Request payload:", request.dict())

            response = await client.post(recommendation_system_url, json=request.dict())
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Error communicating with recommendation system: {exc.response.status_code}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error: {str(e)}"
            )