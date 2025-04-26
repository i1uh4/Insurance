UPDATE user_profiles
SET
    first_name = COALESCE(%(first_name)s, first_name),
    last_name = COALESCE(%(last_name)s, last_name),
    age = COALESCE(%(age)s, age),
    gender = COALESCE(%(gender)s, gender),
    occupation = COALESCE(%(occupation)s, occupation),
    income = COALESCE(%(income)s, income),
    marital_status = COALESCE(%(marital_status)s, marital_status),
    has_children = COALESCE(%(has_children)s, has_children),
    has_vehicle = COALESCE(%(has_vehicle)s, has_vehicle),
    has_home = COALESCE(%(has_home)s, has_home),
    has_medical_conditions = COALESCE(%(has_medical_conditions)s, has_medical_conditions),
    travel_frequency = COALESCE(%(travel_frequency)s, travel_frequency)
WHERE id = %(id)s;

UPDATE users
SET
    user_name = COALESCE(%(user_name)s, user_name),
    updated_at = NOW()
WHERE id = %(id)s;