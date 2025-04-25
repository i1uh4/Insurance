SELECT id, name, email, password, is_verified, created_at
FROM users
WHERE email = %(email)s;