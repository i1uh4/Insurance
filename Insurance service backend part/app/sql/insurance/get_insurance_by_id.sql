SELECT i.id, i.name, i.description, i.premium, i.coverage, i.duration, i.category_id, i.created_at,
       c.name as category_name, c.description as category_description
FROM insurances i
JOIN insurance_categories c ON i.category_id = c.id
WHERE i.id = %(id)s;