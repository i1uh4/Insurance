SELECT
    i.id as product_id,
    i.name as product_name,
    i.description,
    i.premium,
    i.coverage,
    i.duration_months as duration,
    c.name AS category_name,
    c.description AS category_description,
    'test' as provider
FROM
    insurance_products i
JOIN
    insurance_categories c ON i.category_id = c.id
ORDER BY
    i.id;