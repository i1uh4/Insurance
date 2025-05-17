from fastapi import APIRouter, HTTPException, status
from app.database import execute_sql_file
from app.models.recommendation_models import (RecommendationWithInsurance, InsuranceRecommendationRequest,
                                              UserCheckInfo, SuccessResponse)
import os
import httpx
from typing import List
from dotenv import load_dotenv

load_dotenv()

router = APIRouter(
    prefix="/recommendation",
    tags=["Recommendations"]
)


@router.post("/check_recommendation", response_model=SuccessResponse)
async def check_recommendation(request: UserCheckInfo):
    """Set a flag that user already checked for a product"""
    
    user = execute_sql_file("users/get_user_by_email.sql", {"email": request.user_email}, read_only=False)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User with this email not found"
        )

    sql_params = {"user_id": user[0]["id"], "product_id": request.product_id}

    
    execute_sql_file("insurances/insert_product_view.sql", sql_params, read_only=False)

    return SuccessResponse()


@router.post("/get_recommendations", response_model=List[RecommendationWithInsurance])
async def get_recommendations(request: InsuranceRecommendationRequest):
    """Get recommendations for a user"""
    recommendation_system_url = os.getenv('RECOMMENDATION_API_URL')

    if not recommendation_system_url:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="RECOMMENDATION_API_URL environment variable is not set"
        )

    async with httpx.AsyncClient() as client:
        try:
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
