SELECT id, user_id, age, income, occupation, health_condition, family_size, created_at
FROM user_preferences
WHERE user_id = %(user_id)s;