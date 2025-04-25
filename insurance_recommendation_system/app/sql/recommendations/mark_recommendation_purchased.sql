UPDATE recommendations
SET is_purchased = TRUE, updated_at = NOW()
WHERE id = %(id)s;