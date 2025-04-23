INSERT INTO recommendations (user_id, insurance_id, score)
VALUES (%(user_id)s, %(insurance_id)s, %(score)s)
ON CONFLICT (user_id, insurance_id)
DO UPDATE SET score = %(score)s, updated_at = NOW()
RETURNING id;