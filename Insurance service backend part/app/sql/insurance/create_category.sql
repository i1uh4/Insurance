INSERT INTO insurance_categories (name, description)
VALUES (%(name)s, %(description)s)
RETURNING id;