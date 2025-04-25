from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.database import execute_sql_file
from app.models.insurance_models import InsuranceResponse, CategoryResponse
from app.utils.auth import get_current_user

router = APIRouter(
    prefix="/insurance",
    tags=["Insurance"]
)


@router.get("/categories", response_model=List[CategoryResponse])
def get_all_categories(current_user: dict = Depends(get_current_user)):
    categories = execute_sql_file("insurance/get_all_categories.sql")
    return categories


@router.get("/", response_model=List[InsuranceResponse])
def get_all_insurance(current_user: dict = Depends(get_current_user)):
    insurances = execute_sql_file("insurance/get_all_insurance.sql")
    return insurances


@router.get("/{insurance_id}", response_model=InsuranceResponse)
def get_insurance_by_id(insurance_id: int, current_user: dict = Depends(get_current_user)):
    insurance = execute_sql_file("insurance/get_insurance_by_id.sql", {"id": insurance_id})

    if not insurance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Insurance with ID {insurance_id} not found"
        )

    return insurance[0]


@router.get("/category/{category_id}", response_model=List[InsuranceResponse])
def get_insurance_by_category(category_id: int, current_user: dict = Depends(get_current_user)):
    insurances = execute_sql_file("insurance/get_insurance_by_category.sql", {"category_id": category_id})
    return insurances