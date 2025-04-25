import os
from pydantic import BaseSettings


class Settings(BaseSettings):
    API_V1_STR: str = "/api"
    PROJECT_NAME: str = "Insurance Recommendation System"

    # Конфигурация модели
    MODEL_PATH: str = os.getenv("MODEL_PATH", "sentence-transformers/all-MiniLM-L6-v2")
    PRODUCTS_DATA_PATH: str = os.getenv("PRODUCTS_DATA_PATH", "/app/model/products_data.json")

    class Config:
        case_sensitive = True


settings = Settings()
