from fastapi import FastAPI
from app.api.endpoints import router as api_router

app = FastAPI(
    title="Insurance Recommendation System",
    description="API для рекомендации страховых продуктов на основе профиля пользователя"
)

app.include_router(api_router, prefix="/api")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8001, reload=True)
