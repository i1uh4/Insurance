-- Таблица пользователей
CREATE TABLE IF NOT EXISTS users (
    id                         SERIAL       PRIMARY KEY,
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
    updated_at                 TIMESTAMPTZ  NOT NULL DEFAULT CURRENT_TIMESTAMP,
    profile_completed          BOOLEAN      NOT NULL DEFAULT FALSE
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
COMMENT ON COLUMN user_profiles.profile_completed IS 'Флаг заполненности профиля';

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

-- Таблица страховых продуктов
CREATE TABLE IF NOT EXISTS insurance_products (
    id                         SERIAL       PRIMARY KEY,
    category_id                INTEGER      NOT NULL REFERENCES insurance_categories(id) ON DELETE CASCADE,
    name                       VARCHAR(255) NOT NULL,
    description                TEXT,
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

COMMENT ON TABLE insurance_products IS 'Страховые продукты';
COMMENT ON COLUMN insurance_products.id IS 'Уникальный идентификатор страхового продукта';
COMMENT ON COLUMN insurance_products.category_id IS 'Ссылка на категорию страхования';
COMMENT ON COLUMN insurance_products.name IS 'Название страхового продукта';
COMMENT ON COLUMN insurance_products.description IS 'Описание страхового продукта';
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
    viewed_at                  TIMESTAMPTZ  NOT NULL DEFAULT CURRENT_TIMESTAMP,
    view_duration_seconds      INTEGER
);

CREATE INDEX IF NOT EXISTS idx_product_view_history_user_id ON product_view_history(user_id);

COMMENT ON TABLE product_view_history IS 'История просмотров страховых продуктов';
COMMENT ON COLUMN product_view_history.id IS 'Уникальный идентификатор просмотра';
COMMENT ON COLUMN product_view_history.user_id IS 'Ссылка на пользователя';
COMMENT ON COLUMN product_view_history.product_id IS 'Ссылка на страховой продукт';
COMMENT ON COLUMN product_view_history.viewed_at IS 'Дата и время просмотра';
COMMENT ON COLUMN product_view_history.view_duration_seconds IS 'Длительность просмотра в секундах';

-- Таблица для хранения приобретенных страховых полисов
CREATE TABLE IF NOT EXISTS insurance_policies (
    id                         SERIAL       PRIMARY KEY,
    user_id                    INTEGER      NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    product_id                 INTEGER      NOT NULL REFERENCES insurance_products(id) ON DELETE RESTRICT,
    --
    policy_number              VARCHAR(50)  UNIQUE NOT NULL,
    premium_paid               DECIMAL(15, 2) NOT NULL,
    coverage_amount            DECIMAL(15, 2) NOT NULL,
    --
    start_date                 DATE         NOT NULL,
    end_date                   DATE,
    --
    status                     VARCHAR(50)  NOT NULL DEFAULT 'active',
    --
    created_at                 TIMESTAMPTZ  NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at                 TIMESTAMPTZ  NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Основные индексы для работы с полисами
CREATE INDEX IF NOT EXISTS idx_insurance_policies_user_id ON insurance_policies(user_id);
CREATE INDEX IF NOT EXISTS idx_insurance_policies_status ON insurance_policies(status);

COMMENT ON TABLE insurance_policies IS 'Приобретенные страховые полисы';
COMMENT ON COLUMN insurance_policies.id IS 'Уникальный идентификатор полиса';
COMMENT ON COLUMN insurance_policies.user_id IS 'Ссылка на пользователя-страхователя';
COMMENT ON COLUMN insurance_policies.product_id IS 'Ссылка на страховой продукт';
COMMENT ON COLUMN insurance_policies.policy_number IS 'Номер страхового полиса';
COMMENT ON COLUMN insurance_policies.premium_paid IS 'Оплаченная страховая премия';
COMMENT ON COLUMN insurance_policies.coverage_amount IS 'Сумма страхового покрытия';
COMMENT ON COLUMN insurance_policies.start_date IS 'Дата начала действия полиса';
COMMENT ON COLUMN insurance_policies.end_date IS 'Дата окончания действия полиса (NULL для бессрочных)';
COMMENT ON COLUMN insurance_policies.status IS 'Статус полиса (active, expired, cancelled)';
COMMENT ON COLUMN insurance_policies.created_at IS 'Дата и время создания записи';
COMMENT ON COLUMN insurance_policies.updated_at IS 'Дата и время обновления записи';

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


INSERT INTO insurance_categories (name, description) VALUES
    ('Life Insurance', 'Insurance that pays out a sum of money either on the death of the insured person or after a set period.'),
    ('Health Insurance', 'Insurance coverage that pays for medical and surgical expenses incurred by the insured.'),
    ('Auto Insurance', 'Insurance for cars, trucks, motorcycles, and other road vehicles.'),
    ('Home Insurance', 'Insurance that covers losses and damages to an individual''s house and assets in the home.'),
    ('Travel Insurance', 'Insurance that covers the costs and losses associated with traveling.')
ON CONFLICT DO NOTHING;


INSERT INTO insurance_products (name, description, premium, coverage, duration_months, category_id) VALUES
    ('Term Life Insurance', 'Provides coverage at a fixed rate of payments for a limited period of time.', 5000, 1000000, 120, 1),
    ('Whole Life Insurance', 'Permanent life insurance that remains in force for the insured''s entire lifetime.', 12000, 2000000, NULL, 1),
    ('Individual Health Insurance', 'Health insurance coverage for an individual that covers medical expenses.', 8000, 500000, 12, 2),
    ('Family Health Insurance', 'Health insurance coverage for the entire family under a single premium.', 15000, 1000000, 12, 2),
    ('Comprehensive Auto Insurance', 'Covers damages to your vehicle along with third-party liability.', 6000, 300000, 12, 3),
    ('Third-Party Auto Insurance', 'Covers damages to third-party vehicles and property.', 3000, 150000, 12, 3),
    ('Basic Home Insurance', 'Covers basic damages to your home due to fire, theft, etc.', 4000, 500000, 12, 4),
    ('Premium Home Insurance', 'Comprehensive coverage for your home including natural disasters.', 9000, 1500000, 12, 4),
    ('Single Trip Travel Insurance', 'Coverage for a single trip including medical emergencies and trip cancellation.', 1500, 100000, 1, 5),
    ('Annual Multi-Trip Travel Insurance', 'Coverage for multiple trips within a year.', 5000, 300000, 12, 5)
ON CONFLICT DO NOTHING;