from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, users, recommendations
from app.models import user_models, recommendation_models
from app.database import engine

user_models.Base.metadata.create_all(bind=engine)
recommendation_models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Insurance Recommendation System API",
    description="API for recommending insurance products based on user preferences",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(recommendations.router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="localhost", port=8000, reload=True)
