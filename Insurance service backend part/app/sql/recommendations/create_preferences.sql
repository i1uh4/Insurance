INSERT INTO user_preferences (user_id, age, income, occupation, health_condition, family_size)
VALUES (%(user_id)s, %(age)s, %(income)s, %(occupation)s, %(health_condition)s, %(family_size)s)
RETURNING id;