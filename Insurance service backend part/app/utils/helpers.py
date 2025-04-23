import random
from app.database import execute_sql_file
from app.utils.constants import INSURANCE_CATEGORIES, SAMPLE_INSURANCES


def seed_database():
    """Seed the database with initial data"""
    # Seed insurance categories
    for category in INSURANCE_CATEGORIES:
        execute_sql_file("insurance/create_category.sql", {
            "name": category["name"],
            "description": category["description"]
        })

    # Seed insurance products
    for insurance in SAMPLE_INSURANCES:
        execute_sql_file("insurance/create_insurance.sql", {
            "name": insurance["name"],
            "description": insurance["description"],
            "premium": insurance["premium"],
            "coverage": insurance["coverage"],
            "duration": insurance["duration"],
            "category_id": insurance["category_id"]
        })

    return True


def generate_random_recommendations(user_id: int, count: int = 5):
    """Generate random recommendations for testing"""
    # Get all insurance products
    insurances = execute_sql_file("insurance/get_all_insurance.sql")

    # Select random insurances
    selected_insurances = random.sample(insurances, min(count, len(insurances)))

    # Create recommendations
    for insurance in selected_insurances:
        score = random.uniform(0.5, 1.0)
        execute_sql_file("recommendations/create_recommendation.sql", {
            "user_id": user_id,
            "insurance_id": insurance["id"],
            "score": score
        })

    return True
