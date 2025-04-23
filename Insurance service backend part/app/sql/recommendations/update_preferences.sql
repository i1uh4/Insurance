UPDATE user_preferences
SET age = %(age)s,
    income = %(income)s,
    occupation = %(occupation)s,
    health_condition = %(health_condition)s,
    family_size = %(family_size)s,
    updated_at = NOW()
WHERE user_id = %(user_id)s;