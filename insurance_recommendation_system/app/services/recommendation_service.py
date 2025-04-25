from app.database import execute_sql_file


def generate_recommendations(user_id: int):
    """Generate insurance recommendations based on user preferences"""
    # Get user preferences
    preferences = execute_sql_file(
        "recommendations/get_preferences_by_user.sql",
        {"user_id": user_id}
    )

    if not preferences:
        return []

    preferences = preferences[0]

    # Get all insurance products
    insurances = execute_sql_file("insurance/get_all_insurance.sql")

    # Calculate recommendation scores
    recommendations = []
    for insurance in insurances:
        score = calculate_recommendation_score(preferences, insurance)

        # Store recommendation in database
        execute_sql_file("recommendations/create_recommendation.sql", {
            "user_id": user_id,
            "insurance_id": insurance["id"],
            "score": score
        })

    return True


def calculate_recommendation_score(preferences, insurance):
    """Calculate recommendation score based on user preferences and insurance details"""
    score = 0

    # Age factor
    age = preferences["age"]
    if age < 30:
        if "life" in insurance["name"].lower():
            score += 0.5
        if "health" in insurance["name"].lower():
            score += 0.7
    elif age < 50:
        if "life" in insurance["name"].lower():
            score += 0.8
        if "health" in insurance["name"].lower():
            score += 0.9
    else:
        if "life" in insurance["name"].lower():
            score += 1.0
        if "health" in insurance["name"].lower():
            score += 1.0

    # Income factor
    income = preferences["income"]
    if income < 50000:
        if insurance["premium"] < 5000:
            score += 1.0
        elif insurance["premium"] < 10000:
            score += 0.5
        else:
            score += 0.2
    elif income < 100000:
        if insurance["premium"] < 10000:
            score += 0.8
        elif insurance["premium"] < 20000:
            score += 0.9
        else:
            score += 0.5
    else:
        if insurance["premium"] > 20000:
            score += 0.9

    # Health condition factor
    health_condition = preferences["health_condition"].lower()
    if "excellent" in health_condition:
        if "health" in insurance["name"].lower():
            score += 0.5
    elif "good" in health_condition:
        if "health" in insurance["name"].lower():
            score += 0.7
    else:
        if "health" in insurance["name"].lower():
            score += 1.0

    # Family size factor
    family_size = preferences["family_size"]
    if family_size > 3:
        if "family" in insurance["name"].lower():
            score += 1.0
        if "group" in insurance["name"].lower():
            score += 0.9

    # Normalize score to be between 0 and 1
    score = min(score, 1.0)

    return score
