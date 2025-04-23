from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, users, insurance, recommendations
from app.models import user_models, insurance_models, recommendation_models
from app.database import engine

user_models.Base.metadata.create_all(bind=engine)
insurance_models.Base.metadata.create_all(bind=engine)
recommendation_models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Insurance Recommendation System API",
    description="API for recommending insurance products based on user preferences",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(insurance.router)
app.include_router(recommendations.router)


@app.get("/")
def root():
    return {"message": "Welcome to Insurance Recommendation System API"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="localhost", port=8000, reload=True)
