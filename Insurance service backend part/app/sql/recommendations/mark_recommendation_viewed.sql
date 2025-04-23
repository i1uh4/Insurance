UPDATE recommendations
SET is_viewed = TRUE, updated_at = NOW()
WHERE id = %(id)s;