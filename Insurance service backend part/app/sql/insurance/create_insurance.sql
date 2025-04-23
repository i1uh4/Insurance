INSERT INTO insurances (name, description, premium, coverage, duration, category_id)
VALUES (%(name)s, %(description)s, %(premium)s, %(coverage)s, %(duration)s, %(category_id)s)
RETURNING id;