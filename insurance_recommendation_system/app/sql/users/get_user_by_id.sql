SELECT id, name, email, password, is_verified, created_at
FROM users
WHERE id = %(id)s;