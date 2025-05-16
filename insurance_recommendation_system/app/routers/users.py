from fastapi import APIRouter, Depends, HTTPException
from app.database import execute_sql_file, get_slave_db
from app.models.user_models import UserResponse, UserInfoResponse, UserInfoRequest, UserUpdate
from app.utils.auth import get_current_user
from sqlalchemy.orm import Session

router = APIRouter(
    prefix="/user",
    tags=["Users"]
)


@router.post("/info", response_model=UserInfoResponse)
def get_current_user_info(request: UserInfoRequest):
    """Get user information"""
    email = request.email

    # Используем реплику для операций чтения
    user_info = execute_sql_file("users/get_user_info.sql", {"email": email}, read_only=True)

    if not user_info:
        raise HTTPException(status_code=404, detail="User not found")

    user = user_info[0]

    return {
        "user_name": user["user_name"],
        "email": user["email"],
        "first_name": user["first_name"],
        "last_name": user["last_name"],
        "age": user["age"],
        "gender": user["gender"],
        "occupation": user["occupation"],
        "income": user["income"],
        "marital_status": user["marital_status"],
        "has_children": user["has_children"],
        "has_vehicle": user["has_vehicle"],
        "has_home": user["has_home"],
        "has_medical_conditions": user["has_medical_conditions"],
        "travel_frequency": user["travel_frequency"]
    }


@router.put("/update_info", response_model=UserResponse)
def update_user_info(user_data: UserUpdate, current_user: dict = Depends(get_current_user)):
    """Update user info"""
    expected_fields = [
        "user_name", "first_name", "last_name", "age", "gender", "occupation",
        "income", "marital_status", "has_children", "has_vehicle", "has_home",
        "has_medical_conditions", "travel_frequency"
    ]

    sql_params = {**user_data.dict(exclude_unset=True), "id": current_user["id"]}

    for key in expected_fields:
        sql_params.setdefault(key, None)

    # Используем мастер для операций записи
    execute_sql_file("users/update_user_info.sql", sql_params)

    # После обновления данных, получаем их из мастера, а не из реплики
    updated_user = execute_sql_file("users/get_user_by_id.sql", {"id": current_user["id"]}, read_only=False)[0]

    return {
        "id": updated_user["id"],
        "user_name": updated_user["user_name"],
        "email": updated_user["email"],
        "is_verified": updated_user["is_verified"],
        "created_at": updated_user["created_at"]
    }