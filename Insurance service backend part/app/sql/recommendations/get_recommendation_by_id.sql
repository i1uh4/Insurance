SELECT id, user_id, insurance_id, score, is_viewed, is_purchased, created_at
FROM recommendations
WHERE id = %(id)s;