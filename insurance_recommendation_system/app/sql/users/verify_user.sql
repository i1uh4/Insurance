UPDATE users
SET is_verified = TRUE, updated_at = NOW()
WHERE id = %(id)s;