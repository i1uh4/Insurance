SELECT r.id, r.user_id, r.insurance_id, r.score, r.is_viewed, r.is_purchased, r.created_at,
       i.name, i.description, i.premium, i.coverage, i.duration, i.category_id,
       c.name as category_name
FROM recommendations r
JOIN insurances i ON r.insurance_id = i.id
JOIN insurance_categories c ON i.category_id = c.id
WHERE r.user_id = %(user_id)s
ORDER BY r.score DESC;