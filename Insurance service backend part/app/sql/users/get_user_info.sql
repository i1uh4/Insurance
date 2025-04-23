SELECT
    u.name, u.email, ui.first_name, ui.last_name, ui.age,
    ui.gender, ui.occupation, ui.income, ui.marital_status,
    ui.has_children, ui.has_vehicle, ui.has_home,
    ui.has_medical_conditions, ui.travel_frequency
FROM users u
LEFT JOIN user_info ui
    ON u.id = ui.user_id
WHERE email = %(email)s;