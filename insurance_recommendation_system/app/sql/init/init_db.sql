-- Таблица пользователей
CREATE TABLE IF NOT EXISTS users (
    id                         SERIAL       PRIMARY KEY,
    user_name                  VARCHAR(255) UNIQUE NOT NULL,
    email                      VARCHAR(255) UNIQUE NOT NULL,
    password                   VARCHAR(255) NOT NULL,
    --
    is_verified                BOOLEAN      NOT NULL DEFAULT FALSE,
    verification_token         VARCHAR(255),
    verification_expires_at    TIMESTAMPTZ,
    created_at                 TIMESTAMPTZ  NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at                 TIMESTAMPTZ  NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_users_is_verified ON users(is_verified);

COMMENT ON TABLE users IS 'Таблица пользователей системы';
COMMENT ON COLUMN users.id IS 'Уникальный идентификатор пользователя';
COMMENT ON COLUMN users.email IS 'Электронная почта пользователя (используется для входа)';
COMMENT ON COLUMN users.password IS 'Хэш пароля пользователя';
COMMENT ON COLUMN users.is_verified IS 'Флаг верификации пользователя по email';
COMMENT ON COLUMN users.verification_token IS 'Токен для подтверждения email';
COMMENT ON COLUMN users.verification_expires_at IS 'Срок действия токена верификации';
COMMENT ON COLUMN users.created_at IS 'Дата и время создания записи';
COMMENT ON COLUMN users.updated_at IS 'Дата и время последнего обновления записи';

-- Таблица профилей пользователей
CREATE TABLE IF NOT EXISTS user_profiles (
    id                         SERIAL       PRIMARY KEY,
    user_id                    INTEGER      NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    --
    first_name                 VARCHAR(100),
    last_name                  VARCHAR(100),
    age                        INTEGER,
    gender                     VARCHAR(20),
    --
    occupation                 VARCHAR(255),
    income                     DECIMAL(15, 2),
    --
    marital_status             VARCHAR(50),
    has_children               BOOLEAN      NOT NULL DEFAULT FALSE,
    --
    has_vehicle                BOOLEAN      NOT NULL DEFAULT FALSE,
    has_home                   BOOLEAN      NOT NULL DEFAULT FALSE,
    --
    has_medical_conditions     BOOLEAN      NOT NULL DEFAULT FALSE,
    --
    travel_frequency           VARCHAR(50),
    --
    created_at                 TIMESTAMPTZ  NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at                 TIMESTAMPTZ  NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_user_profiles_user_id ON user_profiles(user_id);

COMMENT ON TABLE user_profiles IS 'Профили пользователей с личной информацией';
COMMENT ON COLUMN user_profiles.id IS 'Уникальный идентификатор профиля';
COMMENT ON COLUMN user_profiles.user_id IS 'Ссылка на пользователя';
COMMENT ON COLUMN user_profiles.first_name IS 'Имя пользователя';
COMMENT ON COLUMN user_profiles.last_name IS 'Фамилия пользователя';
COMMENT ON COLUMN user_profiles.age IS 'Возраст пользователя';
COMMENT ON COLUMN user_profiles.gender IS 'Пол пользователя';
COMMENT ON COLUMN user_profiles.occupation IS 'Профессия/род деятельности';
COMMENT ON COLUMN user_profiles.income IS 'Годовой доход';
COMMENT ON COLUMN user_profiles.marital_status IS 'Семейное положение';
COMMENT ON COLUMN user_profiles.has_children IS 'Наличие детей';
COMMENT ON COLUMN user_profiles.has_vehicle IS 'Наличие автомобиля';
COMMENT ON COLUMN user_profiles.has_home IS 'Наличие недвижимости';
COMMENT ON COLUMN user_profiles.has_medical_conditions IS 'Наличие медицинских заболеваний';
COMMENT ON COLUMN user_profiles.travel_frequency IS 'Частота путешествий';
COMMENT ON COLUMN user_profiles.created_at IS 'Дата и время создания профиля';
COMMENT ON COLUMN user_profiles.updated_at IS 'Дата и время обновления профиля';

-- Таблица категорий страховых продуктов
CREATE TABLE IF NOT EXISTS insurance_categories (
    id                         SERIAL       PRIMARY KEY,
    name                       VARCHAR(255) NOT NULL,
    description                TEXT,
    --
    created_at                 TIMESTAMPTZ  NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at                 TIMESTAMPTZ  NOT NULL DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE insurance_categories IS 'Категории страховых продуктов';
COMMENT ON COLUMN insurance_categories.id IS 'Уникальный идентификатор категории';
COMMENT ON COLUMN insurance_categories.name IS 'Название категории страхования';
COMMENT ON COLUMN insurance_categories.description IS 'Описание категории страхования';
COMMENT ON COLUMN insurance_categories.created_at IS 'Дата и время создания записи';
COMMENT ON COLUMN insurance_categories.updated_at IS 'Дата и время обновления записи';

-- Таблица страховых продуктов с добавленным столбцом provider
CREATE TABLE IF NOT EXISTS insurance_products (
    id                         SERIAL       PRIMARY KEY,
    category_id                INTEGER      NOT NULL REFERENCES insurance_categories(id) ON DELETE CASCADE,
    name                       VARCHAR(255) NOT NULL,
    description                TEXT,
    provider                   VARCHAR(255) NOT NULL, -- Добавлен столбец provider
    --
    premium                    DECIMAL(15, 2) NOT NULL,
    coverage                   DECIMAL(15, 2) NOT NULL,
    --
    duration_months            INTEGER,
    is_active                  BOOLEAN      NOT NULL DEFAULT TRUE,
    --
    created_at                 TIMESTAMPTZ  NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at                 TIMESTAMPTZ  NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_insurance_products_category_id ON insurance_products(category_id);
CREATE INDEX IF NOT EXISTS idx_insurance_products_is_active ON insurance_products(is_active);
CREATE INDEX IF NOT EXISTS idx_insurance_products_provider ON insurance_products(provider); -- Добавлен индекс для provider

COMMENT ON TABLE insurance_products IS 'Страховые продукты';
COMMENT ON COLUMN insurance_products.id IS 'Уникальный идентификатор страхового продукта';
COMMENT ON COLUMN insurance_products.category_id IS 'Ссылка на категорию страхования';
COMMENT ON COLUMN insurance_products.name IS 'Название страхового продукта';
COMMENT ON COLUMN insurance_products.description IS 'Описание страхового продукта';
COMMENT ON COLUMN insurance_products.provider IS 'Поставщик страхового продукта';
COMMENT ON COLUMN insurance_products.premium IS 'Стоимость страховой премии';
COMMENT ON COLUMN insurance_products.coverage IS 'Размер страхового покрытия';
COMMENT ON COLUMN insurance_products.duration_months IS 'Срок действия страховки в месяцах (NULL для бессрочных)';
COMMENT ON COLUMN insurance_products.is_active IS 'Флаг активности продукта';
COMMENT ON COLUMN insurance_products.created_at IS 'Дата и время создания записи';
COMMENT ON COLUMN insurance_products.updated_at IS 'Дата и время обновления записи';

-- Таблица рекомендаций страховых продуктов
CREATE TABLE IF NOT EXISTS insurance_recommendations (
    id                         SERIAL       PRIMARY KEY,
    user_id                    INTEGER      NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    product_id                 INTEGER      NOT NULL REFERENCES insurance_products(id) ON DELETE CASCADE,
    --
    relevance_score            DECIMAL(5, 4) NOT NULL,
    recommendation_reason      TEXT,
    --
    is_viewed                  BOOLEAN      NOT NULL DEFAULT FALSE,
    is_purchased               BOOLEAN      NOT NULL DEFAULT FALSE,
    --
    created_at                 TIMESTAMPTZ  NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at                 TIMESTAMPTZ  NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, product_id)
);

CREATE INDEX IF NOT EXISTS idx_insurance_recommendations_user_id ON insurance_recommendations(user_id);
CREATE INDEX IF NOT EXISTS idx_insurance_recommendations_relevance_score ON insurance_recommendations(relevance_score);

COMMENT ON TABLE insurance_recommendations IS 'Рекомендации страховых продуктов пользователям';
COMMENT ON COLUMN insurance_recommendations.id IS 'Уникальный идентификатор рекомендации';
COMMENT ON COLUMN insurance_recommendations.user_id IS 'Ссылка на пользователя';
COMMENT ON COLUMN insurance_recommendations.product_id IS 'Ссылка на страховой продукт';
COMMENT ON COLUMN insurance_recommendations.relevance_score IS 'Оценка релевантности продукта для пользователя (0-1)';
COMMENT ON COLUMN insurance_recommendations.recommendation_reason IS 'Причина рекомендации продукта';
COMMENT ON COLUMN insurance_recommendations.is_viewed IS 'Флаг просмотра рекомендации пользователем';
COMMENT ON COLUMN insurance_recommendations.is_purchased IS 'Флаг покупки рекомендованного продукта';
COMMENT ON COLUMN insurance_recommendations.created_at IS 'Дата и время создания рекомендации';
COMMENT ON COLUMN insurance_recommendations.updated_at IS 'Дата и время обновления рекомендации';

-- Таблица для хранения историй просмотров страховых продуктов
CREATE TABLE IF NOT EXISTS product_view_history (
    id                         SERIAL       PRIMARY KEY,
    user_id                    INTEGER      NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    product_id                 INTEGER      NOT NULL REFERENCES insurance_products(id) ON DELETE CASCADE,
    last_time_viewed_at        TIMESTAMPTZ  NOT NULL DEFAULT CURRENT_TIMESTAMP,
    views_count                INTEGER      NOT NULL DEFAULT 0,
    CONSTRAINT unique_user_product_view UNIQUE (user_id, product_id)
);

CREATE INDEX IF NOT EXISTS idx_product_view_history_user_id ON product_view_history(user_id);

COMMENT ON TABLE product_view_history IS 'История просмотров страховых продуктов';
COMMENT ON COLUMN product_view_history.id IS 'Уникальный идентификатор просмотра';
COMMENT ON COLUMN product_view_history.user_id IS 'Ссылка на пользователя';
COMMENT ON COLUMN product_view_history.product_id IS 'Ссылка на страховой продукт';
COMMENT ON COLUMN product_view_history.last_time_viewed_at IS 'Дата и время просмотра';
COMMENT ON COLUMN product_view_history.views_count IS 'Кол-во просмотров страхового продукта';


-- Триггер автоматического создания профиля при регистрации пользователя
CREATE OR REPLACE FUNCTION create_user_profile()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO user_profiles (user_id)
    VALUES (NEW.id);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_create_user_profile
AFTER INSERT ON users
FOR EACH ROW
EXECUTE FUNCTION create_user_profile();


--------------------------

INSERT INTO insurance_categories (name, description) VALUES
    ('Life Insurance', 'Insurance that pays out a sum of money either on the death of the insured person or after a set period.'),
    ('Health Insurance', 'Insurance coverage that pays for medical and surgical expenses incurred by the insured.'),
    ('Auto Insurance', 'Insurance for cars, trucks, motorcycles, and other road vehicles.'),
    ('Home Insurance', 'Insurance that covers losses and damages to an individual''s house and assets in the home.'),
    ('Travel Insurance', 'Insurance that covers the costs and losses associated with traveling.')
ON CONFLICT DO NOTHING;


-- Life Insurance (Страхование жизни)
INSERT INTO insurance_products (category_id, name, description, provider, premium, coverage, duration_months, is_active) VALUES
    -- Сбер Страхование
    ((SELECT id FROM insurance_categories WHERE name = 'Life Insurance'), 'СберЖизнь', 'Программа накопительного страхования жизни с гарантированной выплатой и инвестиционной составляющей', 'Сбер Страхование', 10000.00, 1000000.00, 60, TRUE),
    ((SELECT id FROM insurance_categories WHERE name = 'Life Insurance'), 'Сбер Защита близких', 'Страхование жизни для защиты семьи в случае ухода из жизни застрахованного', 'Сбер Страхование', 5000.00, 2000000.00, 12, TRUE),

    -- Альфа Страхование
    ((SELECT id FROM insurance_categories WHERE name = 'Life Insurance'), 'Альфа-Жизнь', 'Накопительное страхование жизни с возможностью получения дополнительного инвестиционного дохода', 'Альфа Страхование', 15000.00, 3000000.00, 120, TRUE),
    ((SELECT id FROM insurance_categories WHERE name = 'Life Insurance'), 'Альфа-Защита семьи', 'Страхование жизни с выплатой в случае смерти застрахованного', 'Альфа Страхование', 7500.00, 5000000.00, 12, TRUE),

    -- Ингосстрах
    ((SELECT id FROM insurance_categories WHERE name = 'Life Insurance'), 'Инвест-Полис', 'Инвестиционное страхование жизни с возможностью получения дополнительного дохода', 'Ингосстрах', 30000.00, 3000000.00, 36, TRUE),
    ((SELECT id FROM insurance_categories WHERE name = 'Life Insurance'), 'Гарантия будущего', 'Накопительное страхование жизни для формирования целевого капитала', 'Ингосстрах', 20000.00, 2500000.00, 60, TRUE),

    -- Тинькофф Страхование
    ((SELECT id FROM insurance_categories WHERE name = 'Life Insurance'), 'Тинькофф Страхование жизни', 'Страхование жизни с фиксированной выплатой в случае смерти', 'Тинькофф Страхование', 4000.00, 1500000.00, 12, TRUE);

-- Health Insurance (Медицинское страхование)
INSERT INTO insurance_products (category_id, name, description, provider, premium, coverage, duration_months, is_active) VALUES
    -- Сбер Страхование
    ((SELECT id FROM insurance_categories WHERE name = 'Health Insurance'), 'СберЗдоровье', 'Добровольное медицинское страхование с широким покрытием медицинских услуг', 'Сбер Страхование', 30000.00, 2000000.00, 12, TRUE),
    ((SELECT id FROM insurance_categories WHERE name = 'Health Insurance'), 'Сбер Телемедицина', 'Онлайн-консультации с врачами 24/7 и скидки на медицинские услуги', 'Сбер Страхование', 5000.00, 500000.00, 12, TRUE),

    -- Альфа Страхование
    ((SELECT id FROM insurance_categories WHERE name = 'Health Insurance'), 'АльфаСиница', 'Комплексное ДМС с обслуживанием в ведущих клиниках', 'Альфа Страхование', 45000.00, 3000000.00, 12, TRUE),
    ((SELECT id FROM insurance_categories WHERE name = 'Health Insurance'), 'Альфа Защита от несчастных случаев', 'Страхование от несчастных случаев и травм', 'Альфа Страхование', 8000.00, 1000000.00, 12, TRUE),

    -- Ингосстрах
    ((SELECT id FROM insurance_categories WHERE name = 'Health Insurance'), 'ДМС Платинум', 'Премиальное медицинское обслуживание в лучших клиниках', 'Ингосстрах', 60000.00, 5000000.00, 12, TRUE),
    ((SELECT id FROM insurance_categories WHERE name = 'Health Insurance'), 'Антиклещ', 'Страхование от укуса клеща и последствий клещевых инфекций', 'Ингосстрах', 1200.00, 300000.00, 6, TRUE),

    -- РЕСО-Гарантия
    ((SELECT id FROM insurance_categories WHERE name = 'Health Insurance'), 'РЕСО Здоровье', 'Комплексное медицинское страхование для всей семьи', 'РЕСО-Гарантия', 35000.00, 2500000.00, 12, TRUE);

-- Auto Insurance (Автострахование)
INSERT INTO insurance_products (category_id, name, description, provider, premium, coverage, duration_months, is_active) VALUES
    -- Сбер Страхование
    ((SELECT id FROM insurance_categories WHERE name = 'Auto Insurance'), 'Сбер КАСКО', 'Полное страхование автомобиля от всех рисков', 'Сбер Страхование', 50000.00, 1500000.00, 12, TRUE),
    ((SELECT id FROM insurance_categories WHERE name = 'Auto Insurance'), 'Сбер ОСАГО', 'Обязательное страхование автогражданской ответственности', 'Сбер Страхование', 7000.00, 500000.00, 12, TRUE),

    -- Альфа Страхование
    ((SELECT id FROM insurance_categories WHERE name = 'Auto Insurance'), 'Альфа КАСКО Оптимум', 'Оптимальное страхование автомобиля с разумной стоимостью', 'Альфа Страхование', 45000.00, 1200000.00, 12, TRUE),
    ((SELECT id FROM insurance_categories WHERE name = 'Auto Insurance'), 'Альфа ОСАГО+', 'ОСАГО с расширенным покрытием и дополнительными сервисами', 'Альфа Страхование', 9000.00, 600000.00, 12, TRUE),

    -- Ингосстрах
    ((SELECT id FROM insurance_categories WHERE name = 'Auto Insurance'), 'КАСКО Премиум', 'Премиальное страхование автомобиля с максимальным покрытием', 'Ингосстрах', 70000.00, 3000000.00, 12, TRUE),
    ((SELECT id FROM insurance_categories WHERE name = 'Auto Insurance'), 'ОСАГО Стандарт', 'Стандартное ОСАГО с быстрым оформлением', 'Ингосстрах', 6500.00, 400000.00, 12, TRUE),

    -- Тинькофф Страхование
    ((SELECT id FROM insurance_categories WHERE name = 'Auto Insurance'), 'Тинькофф КАСКО', 'Онлайн-страхование автомобиля с удобным мобильным приложением', 'Тинькофф Страхование', 40000.00, 1000000.00, 12, TRUE),
    ((SELECT id FROM insurance_categories WHERE name = 'Auto Insurance'), 'Тинькофф ОСАГО', 'Цифровое ОСАГО с быстрым оформлением онлайн', 'Тинькофф Страхование', 6000.00, 500000.00, 12, TRUE);

-- Home Insurance (Страхование недвижимости)
INSERT INTO insurance_products (category_id, name, description, provider, premium, coverage, duration_months, is_active) VALUES
    -- Сбер Страхование
    ((SELECT id FROM insurance_categories WHERE name = 'Home Insurance'), 'Сбер Страхование квартиры', 'Комплексное страхование квартиры, отделки и имущества', 'Сбер Страхование', 8000.00, 3000000.00, 12, TRUE),
    ((SELECT id FROM insurance_categories WHERE name = 'Home Insurance'), 'Сбер Страхование дома', 'Страхование загородного дома и хозяйственных построек', 'Сбер Страхование', 15000.00, 5000000.00, 12, TRUE),

    -- Альфа Страхование
    ((SELECT id FROM insurance_categories WHERE name = 'Home Insurance'), 'Альфа Квартира', 'Страхование квартиры от всех рисков с защитой отделки', 'Альфа Страхование', 7500.00, 2500000.00, 12, TRUE),
    ((SELECT id FROM insurance_categories WHERE name = 'Home Insurance'), 'Альфа Загородная недвижимость', 'Комплексное страхование загородной недвижимости', 'Альфа Страхование', 20000.00, 7000000.00, 12, TRUE),

    -- Ингосстрах
    ((SELECT id FROM insurance_categories WHERE name = 'Home Insurance'), 'Платинум Дом', 'Премиальное страхование элитной недвижимости', 'Ингосстрах', 30000.00, 10000000.00, 12, TRUE),
    ((SELECT id FROM insurance_categories WHERE name = 'Home Insurance'), 'Экспресс-полис', 'Быстрое страхование квартиры с минимальным набором документов', 'Ингосстрах', 5000.00, 1500000.00, 12, TRUE),

    -- РЕСО-Гарантия
    ((SELECT id FROM insurance_categories WHERE name = 'Home Insurance'), 'РЕСО Дом', 'Страхование дома и имущества с индивидуальным подходом', 'РЕСО-Гарантия', 12000.00, 4000000.00, 12, TRUE);

-- Travel Insurance (Страхование путешественников)
INSERT INTO insurance_products (category_id, name, description, provider, premium, coverage, duration_months, is_active) VALUES
    -- Сбер Страхование
    ((SELECT id FROM insurance_categories WHERE name = 'Travel Insurance'), 'Сбер Путешествия', 'Страхование для выезжающих за рубеж с медицинским покрытием', 'Сбер Страхование', 3000.00, 2000000.00, 1, TRUE),
    ((SELECT id FROM insurance_categories WHERE name = 'Travel Insurance'), 'Сбер Защита в поездке', 'Страхование от несчастных случаев и потери багажа в путешествии', 'Сбер Страхование', 1500.00, 500000.00, 1, TRUE),

    -- Альфа Страхование
    ((SELECT id FROM insurance_categories WHERE name = 'Travel Insurance'), 'АльфаТревел', 'Комплексное страхование путешественников с широким покрытием', 'Альфа Страхование', 4000.00, 3000000.00, 1, TRUE),
    ((SELECT id FROM insurance_categories WHERE name = 'Travel Insurance'), 'Альфа Спорт', 'Страхование для активного отдыха и занятий спортом', 'Альфа Страхование', 5000.00, 2500000.00, 1, TRUE),

    -- Ингосстрах
    ((SELECT id FROM insurance_categories WHERE name = 'Travel Insurance'), 'ИнгоТревел Премиум', 'Премиальное страхование путешественников с расширенным покрытием', 'Ингосстрах', 7000.00, 5000000.00, 1, TRUE),
    ((SELECT id FROM insurance_categories WHERE name = 'Travel Insurance'), 'Инго Мульти', 'Годовой полис для частых путешественников', 'Ингосстрах', 15000.00, 3000000.00, 12, TRUE),

    -- Тинькофф Страхование
    ((SELECT id FROM insurance_categories WHERE name = 'Travel Insurance'), 'Тинькофф Путешествия', 'Онлайн-страхование путешественников с удобным мобильным приложением', 'Тинькофф Страхование', 2500.00, 1500000.00, 1, TRUE),
    ((SELECT id FROM insurance_categories WHERE name = 'Travel Insurance'), 'Тинькофф Отмена поездки', 'Страхование от отмены или прерывания поездки', 'Тинькофф Страхование', 2000.00, 300000.00, 1, TRUE);