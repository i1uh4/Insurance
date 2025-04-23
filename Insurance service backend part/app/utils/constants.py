# Insurance categories
INSURANCE_CATEGORIES = [
    {"name": "Life Insurance",
     "description": "Insurance that pays out a sum of money either on the death of the insured person or after a set period."},
    {"name": "Health Insurance",
     "description": "Insurance coverage that pays for medical and surgical expenses incurred by the insured."},
    {"name": "Auto Insurance", "description": "Insurance for cars, trucks, motorcycles, and other road vehicles."},
    {"name": "Home Insurance",
     "description": "Insurance that covers losses and damages to an individual's house and assets in the home."},
    {"name": "Travel Insurance", "description": "Insurance that covers the costs and losses associated with traveling."}
]

# Sample insurance products
SAMPLE_INSURANCES = [
    {
        "name": "Term Life Insurance",
        "description": "Provides coverage at a fixed rate of payments for a limited period of time.",
        "premium": 5000,
        "coverage": 1000000,
        "duration": 120,  # 10 years
        "category_id": 1
    },
    {
        "name": "Whole Life Insurance",
        "description": "Permanent life insurance that remains in force for the insured's entire lifetime.",
        "premium": 12000,
        "coverage": 2000000,
        "duration": None,  # Lifetime
        "category_id": 1
    },
    {
        "name": "Individual Health Insurance",
        "description": "Health insurance coverage for an individual that covers medical expenses.",
        "premium": 8000,
        "coverage": 500000,
        "duration": 12,  # 1 year
        "category_id": 2
    },
    {
        "name": "Family Health Insurance",
        "description": "Health insurance that covers the entire family under a single premium.",
        "premium": 15000,
        "coverage": 1000000,
        "duration": 12,  # 1 year
        "category_id": 2
    },
    {
        "name": "Comprehensive Auto Insurance",
        "description": "Covers damages to your vehicle along with third-party liability.",
        "premium": 6000,
        "coverage": 300000,
        "duration": 12,  # 1 year
        "category_id": 3
    },
    {
        "name": "Third-Party Auto Insurance",
        "description": "Covers damages to third-party vehicles and property.",
        "premium": 3000,
        "coverage": 150000,
        "duration": 12,  # 1 year
        "category_id": 3
    },
    {
        "name": "Basic Home Insurance",
        "description": "Covers basic damages to your home due to fire, theft, etc.",
        "premium": 4000,
        "coverage": 500000,
        "duration": 12,  # 1 year
        "category_id": 4
    },
    {
        "name": "Premium Home Insurance",
        "description": "Comprehensive coverage for your home including natural disasters.",
        "premium": 9000,
        "coverage": 1500000,
        "duration": 12,  # 1 year
        "category_id": 4
    },
    {
        "name": "Single Trip Travel Insurance",
        "description": "Coverage for a single trip including medical emergencies and trip cancellation.",
        "premium": 1500,
        "coverage": 100000,
        "duration": 1,  # 1 month
        "category_id": 5
    },
    {
        "name": "Annual Multi-Trip Travel Insurance",
        "description": "Coverage for multiple trips within a year.",
        "premium": 5000,
        "coverage": 300000,
        "duration": 12,  # 1 year
        "category_id": 5
    }
]
