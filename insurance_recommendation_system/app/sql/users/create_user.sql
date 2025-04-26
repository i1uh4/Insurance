INSERT INTO users
    (user_name, email, password, is_verified)
VALUES
    (%(name)s, %(email)s, %(password)s, FALSE)
RETURNING id;